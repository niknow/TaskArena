# -*- coding: utf-8 -*-
import tempfile
import unittest
import shutil
import os
from legionlib import TaskGeneral, TaskLegion, SharedTask
from tasklib.task import Task


class TaskLegionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.LocalDir = tempfile.mkdtemp(dir='.')
        cls.RemoteDir = tempfile.mkdtemp(dir='.')
        cls.ConfigFile = tempfile.mkstemp(dir='.')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.LocalDir)
        shutil.rmtree(cls.RemoteDir)
        os.close(cls.ConfigFile[0])
        os.remove(cls.ConfigFile[1])
        #pass

    def setUp(self):
        self.TG = TaskGeneral(TaskLegionTest.ConfigFile[1])
        self.lid = "BuildHouse"

    def test_1_create_legion(self):
        TP = TaskLegion(self.lid, TaskLegionTest.LocalDir, TaskLegionTest.RemoteDir)
        self.TG.create_legion(TP)
        self.TG.save()
        self.assertEqual(self.TG.find(self.lid), TP)

    def test_2_create_and_add_task(self):
        legion = self.TG.find(self.lid)
        task = Task(legion.tw_local.tw)
        task_description = 'paint walls'
        task['description'] = task_description
        task.save()
        legion.add(task_description)
        loaded_task = legion.tw_local.tasks(['Legion:'+self.lid,task_description])[0]
        self.assertNotEqual(task_description,loaded_task.tw_task)

    def test_3_delete_legion(self):
        legion = self.TG.find(self.lid)
        self.TG.delete_legion(legion)
        self.assertEqual(self.TG.find(self.lid), None)




#if __name__ == '__main__':
#    unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(TaskLegionTest)
unittest.TextTestRunner(verbosity=2).run(suite)
