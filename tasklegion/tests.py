# -*- coding: utf-8 -*-

import tempfile
import unittest
import shutil
import os
from legionlib import TaskGeneral, TaskLegion, SharedTask
from tasklib.task import Task


class TaskLegionTest(unittest.TestCase):

    #called before every test
    def setUp(self):
        self.LocalDir = tempfile.mkdtemp(dir='.')
        self.RemoteDir = tempfile.mkdtemp(dir='.')
        self.ConfigFileLocal = tempfile.mkstemp(dir='.')
        self.ConfigFileRemote = tempfile.mkstemp(dir='.')
        self.TG_local = TaskGeneral(self.ConfigFileLocal[1], False)
        self.TG_remote = TaskGeneral(self.ConfigFileRemote[1], False)
        self.lid = "RefurbishHouse"

    #called after every test
    def tearDown(self):
        shutil.rmtree(self.LocalDir)
        shutil.rmtree(self.RemoteDir)
        os.close(self.ConfigFileLocal[0])
        os.remove(self.ConfigFileLocal[1])
        os.close(self.ConfigFileRemote[0])
        os.remove(self.ConfigFileRemote[1])

    #helper functions

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

    #unittests

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
        synclist = legion.SyncManager.generate_synclist()
        num_uploads = len([e for e in synclist if e.suggestion == 'UPLOAD'])
        num_downloads = len([e for e in synclist if e.suggestion == 'DOWNLOAD'])
        self.assertEqual([num_uploads, num_downloads], [2, 1])


#if __name__ == '__main__':
#    unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(TaskLegionTest)
unittest.TextTestRunner(verbosity=2).run(suite)
