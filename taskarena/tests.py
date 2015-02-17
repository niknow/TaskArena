# -*- coding: utf-8 -*-

# TaskArena - Adding collaborative functionality to TaskWarrior
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
import unittest
import shutil
import os
from arenalib import TaskGeneral, SyncElement, SharedTask, SyncManager, EnhancedTaskWarrior
from tasklib.task import Task


class TaskArenaTest(unittest.TestCase):
    # --- test setup and rear down ---
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

    # --- helper functions ---

    def create_local_arena(self):
        arena = self.TG_local.create_arena(self.lid, self.LocalDir, self.RemoteDir)
        self.TG_local.save()
        return arena

    def create_remote_arena(self):
        arena = self.TG_remote.create_arena(self.lid, self.RemoteDir, self.LocalDir)
        self.TG_remote.save()
        return arena

    def create_task(self, warrior, description):
        task = Task(warrior)
        task['description'] = description
        task.save()
        return task

    # --- tests ---

    # class TaskGeneral
    def test_create_arena(self):
        arena = self.create_local_arena()
        self.assertEqual(self.TG_local.find(self.lid), arena)

    def test_delete_arena(self):
        arena = self.create_local_arena()
        self.TG_local.delete_arena(arena)
        self.assertEqual(self.TG_local.find(self.lid), None)

    def test_find_arena(self):
        arena = self.TG_local.find(self.lid)
        found = self.TG_local.find(self.lid)
        self.assertEqual(arena, found)

    # class TaskArena
    def test_create_add_local_task(self):
        arena = self.create_local_arena()
        task_description = 'paint walls'
        self.create_task(arena.tw_local.tw, task_description)
        arena.add(task_description)
        loaded_task = arena.tw_local.tasks(['Arena:' + self.lid, task_description])[0]
        self.assertEqual(task_description, loaded_task.tw_task['description'])

    def test_remove_local_task(self):
        arena = self.create_local_arena()
        task_description = 'paint walls'
        self.create_task(arena.tw_local.tw, task_description)
        arena.add(task_description)
        arena.remove(task_description)
        loaded_task = arena.tw_local.tasks(['Arena:' + self.lid, task_description])
        self.assertEqual(loaded_task, [])

    def test_create_add_remote_task(self):
        remote_arena = self.create_remote_arena()
        task_description = "paint ceiling"
        self.create_task(remote_arena.tw_local.tw, task_description)
        remote_arena.add(task_description)
        loaded_task = remote_arena.tw_local.tasks(['Arena:' + self.lid, task_description])[0]
        self.assertEqual(task_description, loaded_task.tw_task['description'])

    def test_remove_remote_task(self):
        remote_arena = self.create_remote_arena()
        task_description = 'paint ceiling'
        self.create_task(remote_arena.tw_local.tw, task_description)
        remote_arena.add(task_description)
        remote_arena.remove(task_description)
        loaded_task = remote_arena.tw_local.tasks(['Arena:' + self.lid, task_description])
        self.assertEqual(loaded_task, [])

    # class SyncManager
    def test_create_synclist(self):
        arena = self.create_local_arena()
        task_description = 'paint walls'
        self.create_task(arena.tw_local.tw, task_description)
        arena.add(task_description)
        task_description = 'clean floor'
        self.create_task(arena.tw_local.tw, task_description)
        arena.add(task_description)
        remote_arena = self.create_remote_arena()
        task_description = 'paint ceiling'
        self.create_task(remote_arena.tw_local.tw, task_description)
        remote_arena.add(task_description)
        task_description = 'clean floor'
        self.create_task(remote_arena.tw_local.tw, task_description)
        remote_arena.add(task_description)
        ltask = arena.tw_local.tasks('clean floor')[0]
        rtask = remote_arena.tw_local.tasks('clean floor')[0]
        ltask.ArenaTaskID = 1
        rtask.ArenaTaskID = 1
        ltask.save()
        rtask.save()
        arena.SyncManager.generate_synclist()
        num_uploads = len([e for e in arena.SyncManager.synclist if e.suggestion == 'UPLOAD'])
        num_downloads = len([e for e in arena.SyncManager.synclist if e.suggestion == 'DOWNLOAD'])
        num_conflicts = len([e for e in arena.SyncManager.synclist if e.suggestion == 'CONFLICT'])
        self.assertEqual(num_uploads, 1)
        self.assertEqual(num_downloads, 1)
        self.assertEqual(num_conflicts, 1)

    def test_suggest_conflict_resolution(self):
        arena = self.create_local_arena()
        syncmanager = SyncManager(arena)
        ltask1 = SharedTask(self.create_task(arena.tw_local.tw, 'paint walls'), arena)
        ltask2 = SharedTask(self.create_task(arena.tw_local.tw, 'clean floor'), arena)
        rtask1 = SharedTask(self.create_task(arena.tw_remote.tw, 'paint ceiling'), arena)
        rtask2 = SharedTask(self.create_task(arena.tw_remote.tw, 'clean floor'), arena)
        synclist = [SyncElement(ltask1, None, None, 'UPLOAD', 'UPLOAD'),
                    SyncElement(ltask2, rtask2, ltask2.different_fields(rtask2), 'CONFLICT', 'UPLOAD'),
                    SyncElement(None, rtask1, None, 'DOWNLOAD', 'DOWNLOAD'), ]
        syncmanager.synclist = synclist
        syncmanager.suggest_conflict_resolution()
        num_uploads = len([x for x in syncmanager.synclist if x.suggestion == 'UPLOAD'])
        num_downloads = len([x for x in syncmanager.synclist if x.suggestion == 'DOWNLOAD'])
        num_conflicts = len([x for x in syncmanager.synclist if x.suggestion == 'CONFLICT'])
        self.assertEqual(num_uploads, 2)
        self.assertEqual(num_downloads, 1)
        self.assertEqual(num_conflicts, 0)

    def test_carry_out_sync(self):
        arena = self.create_local_arena()
        syncmanager = SyncManager(arena)
        ltask1 = SharedTask(self.create_task(arena.tw_local.tw, 'paint walls'), arena)
        ltask2 = SharedTask(self.create_task(arena.tw_local.tw, 'clean floor'), arena)
        rtask1 = SharedTask(self.create_task(arena.tw_remote.tw, 'paint ceiling'), arena)
        rtask2 = SharedTask(self.create_task(arena.tw_remote.tw, 'clean floor'), arena)
        ltask2.tw_task['priority'] = 'h'
        ltask2.save()
        synclist = [SyncElement(ltask1, None, None, 'UPLOAD', 'UPLOAD'),
                    SyncElement(ltask2, rtask2, ltask2.different_fields(rtask2), 'CONFLICT', 'UPLOAD'),
                    SyncElement(None, rtask1, None, 'DOWNLOAD', 'DOWNLOAD'), ]
        syncmanager.synclist = synclist
        syncmanager.carry_out_sync()
        self.assertEqual(len(arena.tw_remote.tasks(['paint walls'])), 1)
        self.assertEqual(len(arena.tw_remote.tasks(['clean floor'])), 1)
        self.assertEqual(len(arena.tw_remote.tasks(['clean floor', 'pri:h'])), 1)
        self.assertEqual(len(arena.tw_local.tasks(['clean floor'])), 1)

    # class EnhancedTaskWarrior
    def test_tasks(self):
        arena = self.create_local_arena()
        etw = EnhancedTaskWarrior(arena.tw_local.tw, arena)
        task1 = self.create_task(etw.tw, 'paint walls')
        task2 = self.create_task(etw.tw, 'clean floor')
        task3 = self.create_task(etw.tw, 'paint ceilling')
        task2['project'] = 'foo'
        task3['priority'] = 'h'
        task3['project'] = 'bar'
        task1.save()
        task2.save()
        task3.save()
        self.assertEqual(type(etw.tasks(['paint walls'])[0]), SharedTask)
        self.assertEqual(len(etw.tasks(['paint walls'])), 1)
        self.assertEqual(len(etw.tasks(['pro:foo'])), 1)
        self.assertEqual(len(etw.tasks(['pri:h', 'pro:bar'])), 1)

    def test_add_task(self):
        arena = self.create_local_arena()
        etw = EnhancedTaskWarrior(arena.tw_local.tw, arena)
        task = self.create_task(etw.tw, 'paint walls')
        task['priority'] = 'h'
        task['project'] = 'foo'
        etw.add_task(SharedTask(task, arena))
        self.assertEqual(len(etw.tasks(['paint walls', 'pri:h', 'pro:foo'])), 1)

    # class SharedTask
    def test_create_shared_task(self):
        arena = self.create_local_arena()
        task = self.create_task(arena.tw_local.tw, 'paint walls')
        shared_task = SharedTask(task, arena)
        self.assertEqual(shared_task.Arena.ID, arena.ID)
        self.assertNotEqual(shared_task.ArenaTaskID, None)

    def test_remove_shared_task(self):
        arena = self.create_local_arena()
        task = self.create_task(arena.tw_local.tw, 'paint walls')
        shared_task = SharedTask(task, arena)
        shared_task.save()
        shared_task.remove()
        self.assertEqual(shared_task.tw_task['Arena'], '')
        self.assertEqual(shared_task.tw_task['ArenaTaskID'], '')

    def test_update_shared_task(self):
        arena = self.create_local_arena()
        task = self.create_task(arena.tw_local.tw, 'paint walls')
        shared_task1 = SharedTask(task, arena)
        shared_task2 = SharedTask(task, arena)
        shared_task2.tw_task['description'] = 'paint ceilling'
        shared_task2.tw_task['project'] = 'foo'
        shared_task2.tw_task['priority'] = 'h'
        shared_task1.update(shared_task2)
        self.assertEqual(shared_task1.tw_task['description'], shared_task1.tw_task['description'])
        self.assertEqual(shared_task1.tw_task['project'], shared_task1.tw_task['project'])
        self.assertEqual(shared_task1.tw_task['priority'], shared_task1.tw_task['priority'])

    def test_different_fields(self):
        arena = self.create_local_arena()
        shared_task1 = SharedTask(self.create_task(arena.tw_local.tw, 'paint walls'), arena)
        shared_task2 = SharedTask(self.create_task(arena.tw_local.tw, 'paint walls'), arena)
        shared_task2.tw_task['description'] = 'paint ceilling'
        shared_task2.tw_task['project'] = 'foo'
        shared_task2.tw_task['priority'] = 'h'
        fields = shared_task1.different_fields(shared_task2)
        self.assertEqual(u'description' in fields, True)
        self.assertEqual(u'project' in fields, True)
        self.assertEqual(u'priority' in fields, True)
        self.assertEqual(u'due' in fields, False)


# if __name__ == '__main__':
# unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(TaskArenaTest)
unittest.TextTestRunner(verbosity=2).run(suite)
