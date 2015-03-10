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

from arena import TaskEmperor, uda_config_list
from sync import SyncManager
import subprocess
import os


class IOManager(object):

    valid_commands = [
        'install',
        'uninstall',
        'create',
        'delete',
        'list',
        'add',
        'remove',
        'delete',
        'sync',
    ]

    def __init__(self, show_output=True, seplength=75):
        self.show_output = show_output
        self.seplength = seplength
        self.TaskEmperor = TaskEmperor()
        self.configfile = os.path.expanduser("~") + "\\task_arena_config"

    @staticmethod
    def formatted_print(t):
        print(u'{0:6}   {1:25}   {2:20}   {3:10}\n'.format(t[0][0:6], t[1][0:25], t[2][0:20], t[3][0:10]))

    @staticmethod
    def newlines(num):
        if num:
            print("\n" * (num - 1))

    @staticmethod
    def get_input(msg, pre_blanks=0, post_blanks=0):
        IOManager.newlines(pre_blanks)
        data = raw_input(msg)
        IOManager.newlines(post_blanks)
        return data

    @staticmethod
    def execute_command(command_args):
        p = subprocess.Popen(command_args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.communicate(input='y\n')

    def send_message(self, msg, pre_blanks=0, post_blanks=0):
        if self.show_output:
            IOManager.newlines(pre_blanks)
            print(msg)
            IOManager.newlines(post_blanks)

    def print_separator(self):
        self.send_message("-" * self.seplength)

    def process_command_args(self, args):
        if args.command in IOManager.valid_commands:
            self.call_emperor()
            eval('self.'+args.command+'(args)')
        else:
            self.send_message("Invalid command supplied.")

    def call_emperor(self):
        load_result = self.TaskEmperor.load(self.configfile)
        if load_result == 'loaded':
            self.send_message("Arenas loaded.")
        elif load_result == 'empty':
            self.send_message("Warning: Config file " + self.configfile + " is empty or corrupt.")
        elif load_result == 'new':
            self.send_message("New arena config created at " + self.configfile)

    def install(self, args):
        for uda in uda_config_list:
            IOManager.execute_command(['task', 'config', uda.keys()[0], uda[uda.keys()[0]]])
        self.send_message("TaskArena installed.")

    def uninstall(self, args):
        for uda in reversed(uda_config_list):
            IOManager.execute_command(['task', 'config', uda.keys()[0]])
        os.remove(self.configfile)
        self.send_message("TaskArena uninstalled.")

    def create(self, args):
        self.send_message("Creating new Arena...", 1, 1)
        name = self.get_input('Enter a name: ')
        ldata = self.get_input('Enter local data.location: ')
        rdata = self.get_input('Enter remote data.location: ')
        if self.TaskEmperor.create_arena(name, ldata, rdata):
            self.send_message("Arena " + name + " created.")
            self.TaskEmperor.save()
        else:
            self.send_message("Arena " + name + " already exists!")

    def list(self, args):
        if self.TaskEmperor.arenas:
            self.send_message("The following arenas are available:", 1)
            for arena in self.TaskEmperor.arenas:
                self.send_message("arena : " + arena.name, 1)
                self.send_message("local : " + arena.local_data)
                self.send_message("remote: " + arena.remote_data, 0, 1)

    def get_arena(self, args):
        if args.arena:
            arena = self.TaskEmperor.find(args.arena)
            if arena:
                return arena
            else:
                self.send_message("Arena " + args.arena + " not found.")
        else:
            self.send_message("You must supply an ArenaTaskID.")

    def add(self, args):
        arena = self.get_arena(args)
        if arena:
            arena.add(args.filter.split())
            self.send_message("Tasks added.")

    def remove(self, args):
        arena = self.get_arena(args)
        if arena:
            arena.remove(args.filter)
            self.send_message("Tasks removed from " + arena.name + " .")

    def delete(self, args):
        arena = self.get_arena(args)
        if arena:
            self.TaskEmperor.delete_arena(arena)
            self.TaskEmperor.save()
            self.send_message("Arena " + arena.name + " deleted.")

    def sync(self, args):
        arena = self.get_arena(args)
        if arena:
            sm = SyncManager(arena)
            sm.generate_synclist()
            sm.suggest_conflict_resolution()
            sm.synclist = self.let_user_check_and_modify_synclist(sm.synclist, arena)
            if sm.synclist:
                sm.carry_out_sync()
                self.send_message("Sync complete.", 1, 1)

    def sync_preview(self, synclist):
        self.print_separator()
        IOManager.formatted_print(('', 'Task', 'LastModified', 'Suggestion'))
        self.print_separator()
        for e in synclist:
            IOManager.formatted_print(('Local', e.local_description, e.local_last_modified, ''))
            IOManager.formatted_print(('Remote', e.remote_description, e.remote_last_modified, e.suggestion))
            self.print_separator()
        return IOManager.get_input("Do you want to sync (a)ll, sync (m)anually or (c)ancel? (a/m/c) ", 1)

    def sync_choice(self, e):
        if e.local_task:
            self.send_message("Task Description: " + e.local_task.tw_task['description'])
            self.send_message("ArenaTaskID     : " + e.local_task.ArenaTaskID)
            if e.remote_task:
                self.send_message("Task exists in both repositories.", 1, 1)
                self.send_message("Last modified (local) : " + e.local_last_modified)
                self.send_message("Last modified (remote): " + e.remote_last_modified)
                self.send_message("Suggesting to " + e.suggestion + ".", 1, 1)
                self.send_message("This would cause the following modifications:", 0, 1)
                for field in e.fields:
                    local_field = str(e.local_task.tw_task[field]) if e.local_task.tw_task[field] else '(empty)'
                    remote_field = str(e.remote_task.tw_task[field]) if e.remote_task.tw_task[field] else '(empty)'
                    self.send_message(field + ": " + local_field + (
                        " -> " if e.suggestion == 'UPLOAD' else ' <- ') + remote_field)
                result = IOManager.get_input("Do you want to (u)pload, (d)ownload, (s)kip or (c)ancel sync? (u/d/s/c) ",
                                             1)
            else:
                self.send_message("This task does not yet exist on remote. Suggestion: " + e.suggestion, 1)
                result = IOManager.get_input("Do you want to (u)pload, (s)kip or (c)ancel sync? (u/s/c) ", 1)
        else:
            self.print_separator()
            self.send_message("Description: " + e.remote_task.tw_task['description'])
            self.send_message("ArenaTaskID: " + e.remote_task.ArenaTaskID)
            self.send_message("This task does not yet exist on local.", 1)
            result = IOManager.get_input("Do you want to (d)ownload, (s)kip or (c)ancel sync? (d/s/c) ", 1)
        return result

    def let_user_check_and_modify_synclist(self, synclist, arena):
        if synclist:
            self.send_message("Suggesting the following sync operations on " + arena.name + "...", 1, 2)
            sync_command = self.sync_preview(synclist)
            if sync_command == 'a':
                for elem in synclist:
                    elem.action = elem.suggestion
            elif sync_command == 'm':
                self.send_message("Starting manual sync...", 1, 1)
                for elem in synclist:
                    self.print_separator()
                    sc = self.sync_choice(elem)
                    if sc == 'u':
                        elem.action = 'UPLOAD'
                        self.send_message("Task will be uploaded.", 1)
                    elif sc == 'd':
                        elem.action = 'DOWNLOAD'
                        self.send_message("Task will be downloaded.", 1)
                    elif sc == 's':
                        elem.action = 'SKIP'
                        self.send_message("Task skipped.", 1)
                    elif sc == 'c':
                        self.send_message("Sync canceled.", 0, 1)
                        synclist = []
                        break
            return synclist
        else:
            self.send_message("Arena " + arena.name + " is in sync.")
