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

import os
import shutil
import tempfile
import unittest
from tarenalib.arena import TaskEmperor, SharedTask, EnhancedTaskWarrior


class TestSharedTask(unittest.TestCase):

    def test_create_shared_task(self):
        arena = self.create_local_arena()
        task = self.create_task(arena.tw_local.tw, 'paint walls')
        shared_task = SharedTask(task, arena)
        self.assertEqual(shared_task.Arena.name, arena.name)
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


class TestEnhancedTaskWarrior(unittest.TestCase):

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
        stask = SharedTask(task, arena)
        etw.add_task(stask)
        stask.save()
        self.assertEqual(len(etw.tasks(['paint walls', 'pri:h', 'pro:foo'])), 1)


class TestTaskArena(unittest.TestCase):

    def setUp(self):
        self.LocalDir = tempfile.mkdtemp(dir='.')
        self.RemoteDir = tempfile.mkdtemp(dir='.')
        self.ConfigFileLocal = tempfile.mkstemp(dir='.')
        self.ConfigFileRemote = tempfile.mkstemp(dir='.')
        self.TE_local = TaskEmperor()
        self.TE_local.load(self.ConfigFileLocal[1])
        self.TE_remote = TaskEmperor()
        self.TE_remote.load(self.ConfigFileRemote[1])
        self.arena_name = "RefurbishHouse"

    def tearDown(self):
        shutil.rmtree(self.LocalDir)
        shutil.rmtree(self.RemoteDir)
        os.close(self.ConfigFileLocal[0])
        os.remove(self.ConfigFileLocal[1])
        os.close(self.ConfigFileRemote[0])
        os.remove(self.ConfigFileRemote[1])

    def create_local_arena(self):
        arena = self.TE_local.create_arena(self.arena_name, self.LocalDir, self.RemoteDir)
        self.TE_local.save()
        return arena

    def create_remote_arena(self):
        arena = self.TE_remote.create_arena(self.arena_name, self.RemoteDir, self.LocalDir)
        self.TE_remote.save()
        return arena

    def create_task(self, warrior, description):
        task = TaskEmperor(warrior)
        task['description'] = description
        task.save()
        return task

    def test_create_add_local_task(self):
        arena = self.create_local_arena()
        task_description = 'paint walls'
        self.create_task(arena.tw_local.tw, task_description)
        arena.add(task_description)
        loaded_task = arena.tw_local.tasks(['Arena:' + self.arena_name, task_description])[0]
        self.assertEqual(task_description, loaded_task.tw_task['description'])

    def test_remove_local_task(self):
        arena = self.create_local_arena()
        task_description = 'paint walls'
        self.create_task(arena.tw_local.tw, task_description)
        arena.add(task_description)
        arena.remove(task_description)
        loaded_task = arena.tw_local.tasks(['Arena:' + self.arena_name, task_description])
        self.assertEqual(loaded_task, [])

    def test_create_add_remote_task(self):
        remote_arena = self.create_remote_arena()
        task_description = "paint ceiling"
        self.create_task(remote_arena.tw_local.tw, task_description)
        remote_arena.add(task_description)
        loaded_task = remote_arena.tw_local.tasks(['Arena:' + self.arena_name, task_description])[0]
        self.assertEqual(task_description, loaded_task.tw_task['description'])

    def test_remove_remote_task(self):
        remote_arena = self.create_remote_arena()
        task_description = 'paint ceiling'
        self.create_task(remote_arena.tw_local.tw, task_description)
        remote_arena.add(task_description)
        remote_arena.remove(task_description)
        loaded_task = remote_arena.tw_local.tasks(['Arena:' + self.arena_name, task_description])
        self.assertEqual(loaded_task, [])


class TestTaskEmperor(unittest.TestCase):

    def test_create_arena(self):
        arena = self.create_local_arena()
        self.assertEqual(self.TE_local.find(self.arena_name), arena)

    def test_delete_arena(self):
        arena = self.create_local_arena()
        self.TE_local.delete_arena(arena)
        self.assertEqual(self.TE_local.find(self.arena_name), None)

    def test_find_arena(self):
        arena = self.TE_local.find(self.arena_name)
        found = self.TE_local.find(self.arena_name)
        self.assertEqual(arena, found)


