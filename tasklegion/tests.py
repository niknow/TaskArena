# -*- coding: utf-8 -*-
import tempfile
import unittest
import shutil
from legionlib import TaskGeneral, TaskLegion, SharedTask
from tasklib.task import Task


class TaskLegionTest(unittest.TestCase):

    def setUp(self):
        self.lid = "BuildHouse"
        self.LocalDir = '/cygdrive/d/temp/legionunittest/Local'
        self.RemoteDir = '/cygdrive/d/temp/legionunittest/Remote'
        self.ConfigFile = "D:\\temp\\legionunittest\\configfile"
        self.TG = TaskGeneral(self.ConfigFile)

    def tearDown(self):
        #shutil.rmtree(self.LocalDir)
        #shutil.rmtree(self.RemoteDir)
        #shutil.rmtree(self.ConfigFile)
        pass


    def test_CreateLegion(self):
        TP = TaskLegion(self.lid, self.LocalDir, self.RemoteDir)
        self.TG.create_legion(TP)
        self.TG.save()
        print self.TG.configfile
        self.assertEqual(self.TG.find(self.lid), TP)

    def test_CreateAndAddTask(self):
        legion = self.TG.find(self.lid)
        task = Task(legion.tw_local.tw)
        task_description = 'paint walls'
        task['description'] = task_description
        task.save()
        legion.add(task_description)
        self.assertNotEqual(type(legion),type(None),type(legion))

    # def test_DeleteLegion(self):
    #     legion = self.TG.find(self.lid)
    #     self.TG.delete_legion(legion)
    #     self.assertEqual(self.TG.find(self.lid), None)




#if __name__ == '__main__':
#    unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(TaskLegionTest)
unittest.TextTestRunner(verbosity=2).run(suite)
