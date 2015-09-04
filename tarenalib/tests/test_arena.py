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


import unittest
from unittest.mock import patch
from io import StringIO

from tarenalib.arena import TaskEmperor, TaskArena, EnhancedTaskWarrior, SharedTask, tw_attrs_editable
import tasklib.task as tlib


class TestSharedTask(unittest.TestCase):

    def setUp(self):
        self.patcher1 = patch('tasklib.task.TaskWarrior')
        self.MockClass1 = self.patcher1.start()
        self.patcher2 = patch('tasklib.task.Task', new=dict)
        self.MockClass2 = self.patcher2.start()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_create_shared_task(self):
        shared_task = SharedTask(tlib.Task(tlib.TaskWarrior()))
        self.assertEqual(type(shared_task), SharedTask)

    def test_arena_setting(self):
        arena = TaskArena('my_arena', 'local', 'remote')
        shared_task = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task.Arena = arena
        self.assertEqual(shared_task.tw_task['Arena'], 'my_arena')
        self.assertIsNotNone(shared_task.ArenaTaskID)
        shared_task.Arena = ''
        self.assertEqual(shared_task.Arena, '')
        self.assertEqual(shared_task.ArenaTaskID, '')

    def test_arena_task_id_setting(self):
        shared_task = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task.ArenaTaskID = 'abc'
        self.assertEqual(shared_task.tw_task['ArenaTaskID'], 'abc')

    def test_remove(self):
        shared_task = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task.tw_task['Arena'] = 'my_arena'
        shared_task.tw_task['ArenaTaskID'] = 'abc'
        shared_task.remove()
        self.assertEqual(shared_task.tw_task['Arena'], '')
        self.assertEqual(shared_task.tw_task['ArenaTaskID'], '')

    def test_last_modified(self):
        shared_task = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task.tw_task['modified'] = ''
        shared_task.tw_task['entry'] = 'entered'
        self.assertEqual(shared_task.last_modified(), 'entered')
        shared_task.tw_task['modified'] = 'last_week'
        self.assertEqual(shared_task.last_modified(), 'last_week')

    def test_update_shared_task(self):
        shared_task1 = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task2 = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task1.tw_task = {attr: '' for attr in tw_attrs_editable}
        shared_task2.tw_task = {attr: '' for attr in tw_attrs_editable}
        shared_task2.tw_task['description'] = 'paint ceilling'
        shared_task2.tw_task['project'] = 'foo'
        shared_task2.tw_task['priority'] = 'h'
        shared_task1.update(shared_task2)
        self.assertEqual(shared_task1.tw_task['description'], shared_task1.tw_task['description'])
        self.assertEqual(shared_task1.tw_task['project'], shared_task1.tw_task['project'])
        self.assertEqual(shared_task1.tw_task['priority'], shared_task1.tw_task['priority'])

    def test_different_fields(self):
        shared_task1 = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task2 = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task1.tw_task = {attr: '' for attr in tw_attrs_editable}
        shared_task2.tw_task = {attr: '' for attr in tw_attrs_editable}
        shared_task2.tw_task['description'] = 'paint ceilling'
        shared_task2.tw_task['project'] = 'foo'
        shared_task2.tw_task['priority'] = 'h'
        fields = shared_task1.different_fields(shared_task2)
        self.assertEqual(u'description' in fields, True)
        self.assertEqual(u'project' in fields, True)
        self.assertEqual(u'priority' in fields, True)
        self.assertEqual(u'due' in fields, False)


class TestEnhancedTaskWarrior(unittest.TestCase):
    def setUp(self):
        self.patcher1 = patch('tasklib.task.TaskWarrior')
        self.MockClass1 = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_create_etw(self):
        tw = tlib.TaskWarrior()
        etw = EnhancedTaskWarrior(tw, 'B')
        self.assertEqual(type(etw), EnhancedTaskWarrior)


class TestTaskArena(unittest.TestCase):
    def setUp(self):
        self.patcher1 = patch('tasklib.task.TaskWarrior')
        self.MockClass1 = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_create_arena(self):
        arena = TaskArena()
        self.assertEqual(type(arena), TaskArena)

    def test_local_data(self):
        arena = TaskArena()
        arena.local_data = 'local'
        self.assertEqual(arena.local_data, 'local')

    def test_remote_data(self):
        arena = TaskArena()
        arena.remote_data = 'remote'
        self.assertEqual(arena.remote_data, 'remote')

    def test_json(self):
        arena = TaskArena()
        arena.local_data = 'local'
        arena.remote_data = 'remote'
        arena.name = 'my_arena'
        data = {'remote_data': 'remote', 'local_data': 'local', 'name': 'my_arena'}
        self.assertEqual(arena.json, data)
        arena.json = data
        self.assertEqual(arena.local_data, 'local')
        self.assertEqual(arena.remote_data, 'remote')
        self.assertEqual(arena.name, 'my_arena')


class TestTaskEmperor(unittest.TestCase):
    def setUp(self):
        self.patcher1 = patch('tasklib.task.TaskWarrior')
        self.MockClass1 = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_create_task_emperor(self):
        task_emperor = TaskEmperor()
        self.assertEqual(type(task_emperor), TaskEmperor)

    def test_create_emperor(self):
        task_emperor = TaskEmperor()
        arena = task_emperor.create_arena('my_arena', '\A', '\B')
        self.assertEqual(task_emperor.arenas[0], arena)

    def test_delete_arena(self):
        task_emperor = TaskEmperor()
        arena = task_emperor.create_arena('my_arena', '\A', '\B')
        task_emperor.delete_arena(arena)
        self.assertEqual(task_emperor.arenas, [])

    def test_find_arena(self):
        task_emperor = TaskEmperor()
        arena = task_emperor.create_arena('my_arena', '\A', '\B')
        found = task_emperor.find('my_arena')
        self.assertEqual(arena, found)

    def test_save_load(self):
        task_emperor = TaskEmperor()
        f = StringIO()
        task_emperor.create_arena('my_arena', '\A', '\B')
        json_data = task_emperor.json
        task_emperor.save(f)
        f.seek(0, 0)
        task_emperor.load(f)
        self.assertEqual(task_emperor.json, json_data)
