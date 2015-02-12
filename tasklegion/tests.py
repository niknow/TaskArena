# -*- coding: utf-8 -*-

# TaskLegion - Adding collaborative functionality to TaskWarrior
# Copyright (C) 2015  Nikolai Nowaczyk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import tempfile
from time import sleep
import unittest
import shutil
import os
from legionlib import TaskGeneral, SyncElement, SharedTask, SyncManager
from tasklib.task import Task


class TaskLegionTest(unittest.TestCase):

    #--- test setup and rear down ---
    def setUp(self):
        self.LocalDir = tempfile.mkdtemp(dir='.')
        self.RemoteDir = tempfile.mkdtemp(dir='.')
        self.ConfigFileLocal = tempfile.mkstemp(dir='.')
        self.ConfigFileRemote = tempfile.mkstemp(dir='.')
        self.TG_local = TaskGeneral(self.ConfigFileLocal[1], False)
        self.TG_remote = TaskGeneral(self.ConfigFileRemote[1], False)
        self.lid = "RefurbishHouse"

    def tearDown(self):
        shutil.rmtree(self.LocalDir)
        shutil.rmtree(self.RemoteDir)
        os.close(self.ConfigFileLocal[0])
        os.remove(self.ConfigFileLocal[1])
        os.close(self.ConfigFileRemote[0])
        os.remove(self.ConfigFileRemote[1])

    #--- helper functions ---

    def create_local_legion(self):
        legion = self.TG_local.create_legion(self.lid, self.LocalDir, self.RemoteDir)
        self.TG_local.save()
        return legion

    def create_remote_legion(self):
        legion = self.TG_local.create_legion(self.lid, self.RemoteDir, self.LocalDir)
        self.TG_remote.save()
        return legion

    def create_task(self, warrior, description):
        task = Task(warrior)
        task['description'] = description
        task.save()
        return task

    def create_synclist(self, legion):
        ltask1 = SharedTask(self.create_task(legion.tw_local.tw, 'paint walls'), legion)
        ltask2 = SharedTask(self.create_task(legion.tw_local.tw, 'clean floor'), legion)
        rtask1 = SharedTask(self.create_task(legion.tw_remote.tw, 'paint ceiling'), legion)
        rtask2 = SharedTask(self.create_task(legion.tw_remote.tw, 'clean floor'), legion)
        synclist = []
        synclist.append(SyncElement(ltask1, None, None, 'UPLOAD'))
        synclist.append(SyncElement(ltask2, rtask2, ltask2.different_fields(rtask2), 'CONFLICT'))
        synclist.append(SyncElement(None, rtask1, None, 'DOWNLOAD'))
        return synclist


    #--- tests ---

    #class TaskGeneral
    def test_create_legion(self):
        legion = self.create_local_legion()
        self.assertEqual(self.TG_local.find(self.lid), legion)

    def test_delete_legion(self):
        legion = self.create_local_legion()
        self.TG_local.delete_legion(legion)
        self.assertEqual(self.TG_local.find(self.lid), None)

    def test_find_legion(self):
        legion = self.TG_local.find(self.lid)
        found = self.TG_local.find(self.lid)
        self.assertEqual(legion, found)

    #class TaskLegion
    def test_create_add_local_task(self):
        legion = self.create_local_legion()
        task_description = 'paint walls'
        self.create_task(legion.tw_local.tw, task_description)
        legion.add(task_description)
        loaded_task = legion.tw_local.tasks(['Legion:'+self.lid, task_description])[0]
        self.assertEqual(task_description, loaded_task.tw_task['description'])

    def test_remove_local_task(self):
        legion = self.create_local_legion()
        task_description = 'paint walls'
        self.create_task(legion.tw_local.tw, task_description)
        legion.add(task_description)
        legion.remove(task_description)
        loaded_task = legion.tw_local.tasks(['Legion:'+self.lid, task_description])
        self.assertEqual(loaded_task, [])

    def test_create_add_remote_task(self):
        remote_legion = self.create_remote_legion()
        task_description = "paint ceiling"
        self.create_task(remote_legion.tw_local.tw, task_description)
        remote_legion.add(task_description)
        loaded_task = remote_legion.tw_local.tasks(['Legion:'+self.lid, task_description])[0]
        self.assertEqual(task_description, loaded_task.tw_task['description'])

    def test_remove_remote_task(self):
        remote_legion = self.create_remote_legion()
        task_description = 'paint ceiling'
        self.create_task(remote_legion.tw_local.tw, task_description)
        remote_legion.add(task_description)
        remote_legion.remove(task_description)
        loaded_task = remote_legion.tw_local.tasks(['Legion:'+self.lid, task_description])
        self.assertEqual(loaded_task, [])

    #class SyncManager
    def test_create_synclist(self):
        legion = self.create_local_legion()
        task_description = 'paint walls'
        self.create_task(legion.tw_local.tw, task_description)
        legion.add(task_description)
        task_description = 'clean floor'
        self.create_task(legion.tw_local.tw, task_description)
        legion.add(task_description)
        remote_legion = self.create_remote_legion()
        task_description = 'paint ceiling'
        self.create_task(remote_legion.tw_local.tw, task_description)
        remote_legion.add(task_description)
        task_description = 'clean floor'
        self.create_task(remote_legion.tw_local.tw, task_description)
        remote_legion.add(task_description)
        ltask = legion.tw_local.tasks('clean floor')[0]
        rtask = remote_legion.tw_local.tasks('clean floor')[0]
        ltask.LegionID = 1
        rtask.LegionID = 1
        ltask.save()
        rtask.save()
        legion.SyncManager.generate_synclist()
        num_uploads = len([e for e in legion.SyncManager.synclist if e.suggestion == 'UPLOAD'])
        num_downloads = len([e for e in legion.SyncManager.synclist if e.suggestion == 'DOWNLOAD'])
        num_conflicts = len([e for e in legion.SyncManager.synclist if e.suggestion == 'CONFLICT'])
        self.assertEqual(num_uploads, 1)
        self.assertEqual(num_downloads, 1)
        self.assertEqual(num_conflicts, 1)

    def test_suggest_conflict_resolution(self):
        legion = self.create_local_legion()
        synclist = self.create_synclist(legion)
        syncmanager = SyncManager(legion)
        syncmanager.synclist = synclist
        syncmanager.suggest_conflict_resolution()
        num_uploads = len([x for x in syncmanager.synclist if x.suggestion == 'UPLOAD'])
        num_downloads = len([x for x in syncmanager.synclist if x.suggestion == 'DOWNLOAD'])
        num_conflicts = len([x for x in syncmanager.synclist if x.suggestion == 'CONFLICT'])
        self.assertEqual(num_uploads, 2)
        self.assertEqual(num_downloads, 1)
        self.assertEqual(num_conflicts, 0)


#if __name__ == '__main__':
#    unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(TaskLegionTest)
unittest.TextTestRunner(verbosity=2).run(suite)
