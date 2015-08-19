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

from tarenalib.sync import SyncElement, SyncManager
from tarenalib.arena import SharedTask


class TestSyncManager(unittest.TestCase):

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
        sm = SyncManager(arena)
        sm.generate_synclist()
        num_uploads = len([e for e in sm.synclist if e.suggestion == 'UPLOAD'])
        num_downloads = len([e for e in sm.synclist if e.suggestion == 'DOWNLOAD'])
        num_conflicts = len([e for e in sm.synclist if e.suggestion == 'CONFLICT'])
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
        synclist = [SyncElement(ltask1, None, None, 'UPLOAD'),
                    SyncElement(ltask2, rtask2, ltask2.different_fields(rtask2), 'CONFLICT'),
                    SyncElement(None, rtask1, None, 'DOWNLOAD')]
        syncmanager.synclist = synclist
        syncmanager.suggest_conflict_resolution()
        num_uploads = len([x for x in syncmanager.synclist if x.suggestion == 'UPLOAD'])
        num_downloads = len([x for x in syncmanager.synclist if x.suggestion == 'DOWNLOAD'])
        self.assertEqual(num_uploads, 1)
        self.assertEqual(num_downloads, 1)

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
        for elem in syncmanager.synclist:
            self.assertEqual(elem.local_task.ArenaTaskID, elem.local_task.ArenaTaskID)
