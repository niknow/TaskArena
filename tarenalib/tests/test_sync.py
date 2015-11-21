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
import tasklib.task as tlib

from tarenalib.sync import SyncElement, SyncManager, SyncIOManager
from tarenalib.arena import SharedTask, TaskArena
from tarenalib.io import IOManager

from io import StringIO
import sys


def last_modified_mock():
    last_modified_mock.c += 1
    return last_modified_mock.c
last_modified_mock.c = 0


class TestSyncManager(unittest.TestCase):

    def setUp(self):
        self.patcher1 = patch('tasklib.task.TaskWarrior')
        self.MockClass1 = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def create_shared_task(self, arena, description):
        shared_task = SharedTask(tlib.Task(tlib.TaskWarrior()))
        shared_task.Arena = arena
        shared_task.tw_task['description'] = description
        return shared_task

    def test_create_synclist(self):
        arena = TaskArena('my_arena', 'local', 'remote')
        ltask1 = self.create_shared_task(arena, 'paint walls')
        ltask2 = self.create_shared_task(arena, 'clean floor')
        rtask1 = self.create_shared_task(arena, 'paint ceilling')
        rtask2 = self.create_shared_task(arena, 'clean floor')
        ltask1.ArenaTaskID = 1
        rtask1.ArenaTaskID = 1
        local_tasks = [ltask1, ltask2]
        remote_tasks = [rtask1, rtask2]
        sm = SyncManager(arena, IOManager(False))
        sm.generate_synclist(local_tasks, remote_tasks)
        num_uploads = len([e for e in sm.synclist if e.suggestion == 'UPLOAD'])
        num_downloads = len([e for e in sm.synclist if e.suggestion == 'DOWNLOAD'])
        num_conflicts = len([e for e in sm.synclist if e.suggestion == 'CONFLICT'])
        self.assertEqual(num_uploads, 1)
        self.assertEqual(num_downloads, 1)
        self.assertEqual(num_conflicts, 1)

    @patch.object(SharedTask, 'last_modified', side_effect=last_modified_mock)
    def test_suggest_conflict_resolution(self, mock_last_modified):
        arena = TaskArena('my_arena', 'local', 'remote')
        ltask1 = self.create_shared_task(arena, 'paint walls')
        ltask2 = self.create_shared_task(arena, 'clean floor')
        ltask3 = self.create_shared_task(arena, 'do dishes')
        rtask1 = self.create_shared_task(arena, 'paint ceilling')
        rtask2 = self.create_shared_task(arena, 'clean floor')
        rtask3 = self.create_shared_task(arena, 'do dishes')
        ltask1.ArenaTaskID = 1
        ltask2.ArenaTaskID = 2
        ltask3.ArenaTaskID = 4
        rtask1.ArenaTaskID = 3
        rtask2.ArenaTaskID = 2
        rtask3.ArenaTaskID = 4
        rtask3.tw_task['priority'] = 'H'
        synclist = [SyncElement(ltask1, None, None, 'UPLOAD'),
                    SyncElement(ltask2, rtask2, ltask2.different_fields(rtask2), 'CONFLICT'),
                    SyncElement(None, rtask1, None, 'DOWNLOAD'),
                    SyncElement(ltask3, rtask3, ltask3.different_fields(rtask3), 'CONFLICT')]
        sm = SyncManager(arena, IOManager(False))
        sm.synclist = synclist
        sm.suggest_conflict_resolution()
        num_total = len(sm.synclist)
        num_uploads = len([x for x in sm.synclist if x.suggestion == 'UPLOAD'])
        num_downloads = len([x for x in sm.synclist if x.suggestion == 'DOWNLOAD'])
        self.assertEqual(num_total, 3)
        self.assertEqual(num_uploads, 1)
        self.assertEqual(num_downloads, 2)

    @patch.object(SharedTask, 'save')
    def test_carry_out_sync(self, mock_save):
        arena = TaskArena('my_arena', 'local', 'remote')
        ltask1 = self.create_shared_task(arena, 'paint walls')
        ltask3 = self.create_shared_task(arena, 'do dishes')
        rtask1 = self.create_shared_task(arena, 'paint ceilling')
        rtask3 = self.create_shared_task(arena, 'do dishes')
        ltask1.ArenaTaskID = 1
        ltask3.ArenaTaskID = 4
        rtask1.ArenaTaskID = 3
        rtask3.ArenaTaskID = 4
        rtask3.tw_task['priority'] = 'H'
        synclist = [SyncElement(ltask1, None, None, None, 'UPLOAD'),
                    SyncElement(None, rtask1, None, None, 'DOWNLOAD'),
                    SyncElement(ltask3, rtask3, None, None, 'DOWNLOAD')]
        sm = SyncManager(arena, IOManager(False))
        sm.synclist = synclist
        sm.carry_out_sync()
        self.assertEqual(synclist[0].local_task, synclist[0].remote_task)
        self.assertEqual(synclist[1].local_task, synclist[1].remote_task)
        self.assertEqual(synclist[2].local_task, synclist[2].remote_task)
        self.assertEqual(synclist[2].local_task.tw_task['priority'],
                         synclist[2].remote_task.tw_task['priority'])


class TestSyncElement(unittest.TestCase):

    def test_create(self):
        se = SyncElement()
        self.assertEqual(type(se), SyncElement)

    @patch('tasklib.task.Task', new=dict)
    def test_local_description(self):
        se = SyncElement()
        self.assertEqual(se.local_description, '')
        se.local_task = SharedTask(tlib.Task())
        se.local_task.tw_task['description'] = 'foo'
        self.assertEqual(se.local_description, 'foo')

    @patch('tasklib.task.Task', new=dict)
    def test_remote_description(self):
        se = SyncElement()
        self.assertEqual(se.remote_description, '')
        se.remote_task = SharedTask(tlib.Task())
        se.remote_task.tw_task['description'] = 'foo'
        self.assertEqual(se.remote_description, 'foo')

    @patch('tasklib.task.Task', new=dict)
    def test_last_modified(self):
        se = SyncElement()
        self.assertEqual(se.local_last_modified, '')
        se.local_task = SharedTask(tlib.Task())
        se.local_task.last_modified = lambda: 'now'
        self.assertEqual(se.local_last_modified, 'now')


class TestSyncIOManager(unittest.TestCase):

    def setUp(self):
        self.old_stdout = sys.stdout
        self.mystdout = StringIO()
        sys.stdout = self.mystdout
        self.iom = IOManager(show_output=False)

    def tearDown(self):
        sys.stdout = self.old_stdout

    def test_create(self):
        siom = SyncIOManager(self.iom)

    @patch('tarenalib.sync.SyncElement', new=dict)
    @patch.object(IOManager, 'get_input', new=lambda a, b: 'y')
    def test_sync_preview(self):
        siom = SyncIOManager(self.iom)
        synclist = [SyncElement()]
        self.assertEqual(siom.sync_preview(synclist), 'y')

    @patch('builtins.input', side_effect=['y', 'y'])
    @patch('tasklib.task.Task', new=dict)
    def test_sync_choice(self, mock_input):
        siom = SyncIOManager(self.iom)
        e = SyncElement()
        self.assertEqual(siom.sync_choice(e), None)

    @patch.object(SyncIOManager, 'sync_preview', new=lambda a, b: 'a')
    def test_user_checks_synclist(self):
        siom = SyncIOManager(self.iom)
        siom.user_checks_synclist(None, 'foo')
        result = siom.user_checks_synclist([SyncElement(suggestion='UPLOAD')], 'foo')
        self.assertEqual(result[0].action, 'UPLOAD')
