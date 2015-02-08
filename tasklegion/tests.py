# -*- coding: utf-8 -*-
import tempfile
import unittest
import shutil
import os
from legionlib import TaskGeneral, TaskLegion, SharedTask
from tasklib.task import Task


class TaskLegionTest(unittest.TestCase):

    def setUp(self):
        self.LocalDir = tempfile.mkdtemp(dir='.')
        self.RemoteDir = tempfile.mkdtemp(dir='.')
        self.ConfigFile = tempfile.mkstemp(dir='.')
        self.TG = TaskGeneral(self.ConfigFile[1], False)
        self.lid = "BuildHouse"

    def tearDown(self):
        shutil.rmtree(self.LocalDir)
        shutil.rmtree(self.RemoteDir)
        os.close(self.ConfigFile[0])
        os.remove(self.ConfigFile[1])

    def test_create_legion(self):
        tp = self.TG.create_legion(self.lid, self.LocalDir, self.RemoteDir)
        self.TG.save()
        self.assertEqual(self.TG.find(self.lid), tp)

    def test_delete_legion(self):
        self.TG.create_legion(self.lid, self.LocalDir, self.RemoteDir)
        self.TG.save()
        legion = self.TG.find(self.lid)
        self.TG.delete_legion(legion)
        self.assertEqual(self.TG.find(self.lid), None)

    def test_create_and_add_task(self):
        self.TG.create_legion(self.lid, self.LocalDir, self.RemoteDir)
        self.TG.save()
        legion = self.TG.find(self.lid)
        task = Task(legion.tw_local.tw)
        task_description = 'paint walls'
        task['description'] = task_description
        task.save()
        legion.add(task_description)
        loaded_task = legion.tw_local.tasks(['Legion:'+self.lid, task_description])[0]
        self.assertEqual(task_description, loaded_task.tw_task['description'])

    def test_remove_task(self):
        self.TG.create_legion(self.lid, self.LocalDir, self.RemoteDir)
        self.TG.save()
        legion = self.TG.find(self.lid)
        task = Task(legion.tw_local.tw)
        task_description = 'paint walls'
        task['description'] = task_description
        task.save()
        legion.add(task_description)
        legion.remove(task_description)
        loaded_task = legion.tw_local.tasks(['Legion:'+self.lid, task_description])
        self.assertEqual(loaded_task, [])






#if __name__ == '__main__':
#    unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(TaskLegionTest)
unittest.TextTestRunner(verbosity=2).run(suite)
