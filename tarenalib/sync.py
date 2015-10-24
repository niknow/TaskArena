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

from tarenalib.io import IOManager


class SyncManager(object):
    def __init__(self, arena, io_manager):
        self.arena = arena
        self.synclist = []
        self.siom = SyncIOManager(io_manager)

    @property
    def synclist_not_skipped(self):
        return [e for e in self.synclist if e.suggestion != 'SKIP']

    def generate_synclist(self, local_tasks, remote_tasks):
        for ltask in local_tasks:
            rtask = next((t for t in remote_tasks if t == ltask), None)
            if rtask:
                self.synclist.append(SyncElement(
                    ltask,
                    rtask,
                    ltask.different_fields(rtask),
                    'CONFLICT'))
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

    def process_user_modified_synclist(self):
        self.synclist = self.siom.user_checks_synclist(self.synclist, self.arena)
        if self.synclist:
            self.carry_out_sync()
            self.siom.iom.send_message("Sync complete.", 1, 1)

    def sync(self):
        self.generate_synclist(self.arena.get_local_tasks(),
                               self.arena.get_remote_tasks())
        self.suggest_conflict_resolution()
        self.process_user_modified_synclist()

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


class SyncIOManager(object):

    def __init__(self, iom):
        self.iom = iom

    def sync_preview(self, synclist):
        self.iom.print_separator()
        IOManager.formatted_print(('', 'Task', 'LastModified', 'Suggestion'))
        self.iom.print_separator()
        for e in synclist:
            IOManager.formatted_print(('Local', e.local_description, e.local_last_modified, ''))
            IOManager.formatted_print(('Remote', e.remote_description, e.remote_last_modified, e.suggestion))
            self.iom.print_separator()
        return IOManager.get_input("Do you want to sync (a)ll, sync (m)anually or (c)ancel? (a/m/c) ", 1)

    def sync_choice(self, e):
        if e.local_task:
            self.iom.send_message("Task Description: " + e.local_task.tw_task['description'])
            self.iom.send_message("ArenaTaskID     : " + e.local_task.ArenaTaskID)
            if e.remote_task:
                self.iom.send_message("Task exists in both repositories.", 1, 1)
                self.iom.send_message("Last modified (local) : " + e.local_last_modified)
                self.iom.send_message("Last modified (remote): " + e.remote_last_modified)
                self.iom.send_message("Suggesting to " + e.suggestion + ".", 1, 1)
                self.iom.send_message("This would cause the following modifications:", 0, 1)
                for field in e.fields:
                    local_field = str(e.local_task.tw_task[field]) if e.local_task.tw_task[field] else '(empty)'
                    remote_field = str(e.remote_task.tw_task[field]) if e.remote_task.tw_task[field] else '(empty)'
                    self.iom.send_message(field + ": " + local_field + (
                        " -> " if e.suggestion == 'UPLOAD' else ' <- ') + remote_field)
                result = IOManager.get_input("Do you want to (u)pload, (d)ownload, (s)kip or (c)ancel sync? (u/d/s/c) ",
                                             1)
            else:
                self.iom.send_message("This task does not yet exist on remote. Suggestion: " + e.suggestion, 1)
                result = IOManager.get_input("Do you want to (u)pload, (s)kip or (c)ancel sync? (u/s/c) ", 1)
        else:
            self.iom.print_separator()
            self.iom.send_message("Description: " + e.remote_task.tw_task['description'])
            self.iom.send_message("ArenaTaskID: " + e.remote_task.ArenaTaskID)
            self.iom.send_message("This task does not yet exist on local.", 1)
            result = IOManager.get_input("Do you want to (d)ownload, (s)kip or (c)ancel sync? (d/s/c) ", 1)
        return result

    def user_checks_synclist(self, synclist, arena):
        if synclist:
            self.iom.send_message("Suggesting the following sync operations on " + arena.name + "...", 1, 2)
            sync_command = self.sync_preview(synclist)
            if sync_command == 'a':
                for elem in synclist:
                    elem.action = elem.suggestion
            elif sync_command == 'm':
                self.iom.send_message("Starting manual sync...", 1, 1)
                for elem in synclist:
                    self.iom.print_separator()
                    sc = self.sync_choice(elem)
                    if sc == 'u':
                        elem.action = 'UPLOAD'
                        self.iom.send_message("Task will be uploaded.", 1)
                    elif sc == 'd':
                        elem.action = 'DOWNLOAD'
                        self.iom.send_message("Task will be downloaded.", 1)
                    elif sc == 's':
                        elem.action = 'SKIP'
                        self.iom.send_message("Task skipped.", 1)
                    elif sc == 'c':
                        self.iom.send_message("Sync canceled.", 0, 1)
                        synclist = []
                        break
            return synclist
        else:
            self.iom.send_message("Arena " + arena.name + " is in sync.")
