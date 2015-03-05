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


class SyncManager(object):
    def __init__(self, arena):
        self.arena = arena
        self.synclist = []

    @property
    def synclist_not_skipped(self):
        return [e for e in self.synclist if e.suggestion != 'SKIP']

    def generate_synclist(self):
        local_tasks = self.arena.tw_local.tasks('')
        remote_tasks = self.arena.tw_remote.tasks('')
        for ltask in local_tasks:
            rtask = next((t for t in remote_tasks if t == ltask), None)
            if rtask:
                self.synclist.append(SyncElement(ltask, rtask, ltask.different_fields(rtask), 'CONFLICT'))
            else:
                self.synclist.append(SyncElement(ltask, None, None, 'UPLOAD'))
        for rtask in remote_tasks:
            if rtask not in local_tasks:
                self.synclist.append(SyncElement(None, rtask, None, 'DOWNLOAD'))

    def suggest_conflict_resolution(self):
        simplified_synclist = []
        for e in self.synclist:
            if e.suggestion == 'CONFLICT':
                if e.fields:
                    if e.local_task.last_modified() >= e.remote_task.last_modified():
                        e.suggestion = 'UPLOAD'
                    else:
                        e.suggestion = 'DOWNLOAD'
                    simplified_synclist.append(e)
            else:
                simplified_synclist.append(e)
        self.synclist = simplified_synclist

    def let_user_check_and_modify_synclist(self):
        if self.synclist:
            self.arena.IOManager.send_message("Suggesting the following sync operations on " + self.arena.name + "...",
                                              1, 2)
            sync_command = self.arena.IOManager.sync_preview(self.synclist)
            if sync_command == 'a':
                for elem in self.synclist:
                    elem.action = elem.suggestion
            elif sync_command == 'm':
                self.arena.IOManager.send_message("Starting manual sync...", 1, 1)
                for elem in self.synclist:
                    self.arena.IOManager.print_separator()
                    sc = self.arena.IOManager.sync_choice(elem)
                    if sc == 'u':
                        elem.action = 'UPLOAD'
                        self.arena.IOManager.send_message("Task uploaded.", 1)
                    elif sc == 'd':
                        elem.action = 'DOWNLOAD'
                        self.arena.IOManager.send_message("Task downloaded.", 1)
                    elif sc == 's':
                        elem.action = 'SKIP'
                        self.arena.IOManager.send_message("Task skipped.", 1)
                    elif sc == 'c':
                        self.arena.IOManager.send_message("Sync canceled.", 0, 1)
                        self.synclist = []
                        break
        else:
            self.arena.IOManager.send_message("Arena " + self.arena.name + " is in sync.")

    def carry_out_sync(self):
        for elem in self.synclist:
            if elem.action == 'UPLOAD':
                if elem.remote_task:
                    elem.remote_task.update(elem.local_task)
                else:
                    elem.remote_task = self.arena.tw_remote.add_task(elem.local_task)
                    elem.remote_task.ArenaTaskID = elem.local_task.ArenaTaskID
                elem.remote_task.save()
            elif elem.action == 'DOWNLOAD':
                if elem.local_task:
                    elem.local_task.update(elem.remote_task)
                else:
                    elem.local_task = self.arena.tw_local.add_task(elem.remote_task)
                    elem.local_task.ArenaTaskID = elem.remote_task.ArenaTaskID
                elem.local_task.save()
        if self.synclist:
            self.arena.IOManager.send_message("Sync complete.", 1, 1)

    def __repr__(self):
        return str({'arena:': self.arena.__str__(),
                    'synclist:': [e.__str__() for e in self.synclist]})

    def __str__(self):
        return str({'arena:': self.arena.__str__(),
                    'synclist:': [e.__str__() for e in self.synclist]})


class SyncElement(object):
    def __init__(self, ltask=None, rtask=None, fields=None, suggestion='', action=''):
        self.local_task = ltask
        self.remote_task = rtask
        self.suggestion = suggestion
        self.action = action
        self.fields = fields

    @property
    def local_description(self):
        return self.local_task.tw_task['description'] if self.local_task else ''

    @property
    def remote_description(self):
        return self.remote_task.tw_task['description'] if self.remote_task else ''

    @property
    def local_last_modified(self):
        return str(self.local_task.last_modified()) if self.local_task else ''

    @property
    def remote_last_modified(self):
        return str(self.remote_task.last_modified()) if self.remote_task else ''

    def __repr__(self):
        return {'local_task': self.local_task.__repr__(),
                'remote_task:': self.remote_task.__repr__(),
                'suggestion:': self.suggestion,
                'action:': self.action,
                'fields:': self.fields}

    def __str__(self):
        return str({'local_task': self.local_task,
                    'remote_task:': self.remote_task,
                    'suggestion:': self.suggestion,
                    'action:': self.action,
                    'fields:': self.fields})

