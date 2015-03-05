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
    def __init__(self, show_output=True, seplength=75):
        self.show_output = show_output
        self.seplength = seplength
        self.TaskEmperor = TaskEmperor()

    @staticmethod
    def formatted_print(t):
        print("{0:6}   {1:25}   {2:20}   {3:10}\n".format(t[0][0:6], t[1][0:25], t[2][0:20], t[3][0:10]))

    @staticmethod
    def newlines(num):
        if num:
            print("\n" * (num - 1))

    @staticmethod
    def get_input(msg, pre_blanks=0, post_blanks=0):
        print("\n" * pre_blanks)
        data = raw_input(msg)
        print("\n" * post_blanks)
        return data

    @staticmethod
    def execute_command(command_args):
        p = subprocess.Popen(command_args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.communicate(input='y\n')

    def process_command_args(self, args):
        configfile = os.path.expanduser("~") + "\\task_arena_config"
        load_result = self.TaskEmperor.load(configfile)
        if load_result == 'loaded':
            self.send_message("Arenas loaded.")
        elif load_result == 'empty':
            self.send_message("Warning: Config file " + configfile + " is empty or corrupt.")
        elif load_result == 'new':
            self.send_message("New arena config created at " + configfile)
        if args.command == 'install':
            for uda in uda_config_list:
                IOManager.execute_command(['task', 'config', uda.keys()[0], uda[uda.keys()[0]]])
            self.send_message("TaskArena installed.")
        elif args.command == 'uninstall':
            for uda in reversed(uda_config_list):
                IOManager.execute_command(['task', 'config', uda.keys()[0]])
            os.remove(configfile)
            self.send_message("TaskArena uninstalled.")
        elif args.command == 'create':
            self.send_message("Creating new Arena...")
            name = self.get_input('Enter a name: ')
            ldata = self.get_input('Enter local data.location: ')
            rdata = self.get_input('Enter remote data.location: ')
            if self.TaskEmperor.create_arena(name, ldata, rdata):
                self.send_message("Arena " + name + " created.")
                self.TaskEmperor.save()
            else:
                self.send_message("Arena " + name + " already exists!")
        elif args.command == 'list':
            if self.TaskEmperor.arenas:
                self.send_message("The following arenas are available:", 1, 1)
                for arena in self.TaskEmperor.arenas:
                    self.send_message("arena : " + arena.name)
                    self.send_message("local : " + arena.local_data)
                    self.send_message("remote: " + arena.remote_data)
        elif args.command in ['add', 'remove', 'delete', 'sync']:
            if args.arena:
                arena = self.TaskEmperor.find(args.arena)
                if arena:
                    if args.command == 'add':
                        arena.add(args.filter)
                        self.send_message("Tasks added.")
                    elif args.command == 'remove':
                        arena.remove(args.filter)
                        self.send_message("Tasks removed from " + arena.name + " .")
                    elif args.command == 'delete':
                        self.TaskEmperor.delete_arena(arena)
                        self.TaskEmperor.save()
                        self.send_message("Arena " + arena.name + " deleted.")
                    elif args.command == 'sync':
                        sm = SyncManager(arena)
                        sm.generate_synclist()
                        sm.suggest_conflict_resolution()
                        sm.let_user_check_and_modify_synclist()
                        if sm.synclist:
                            sm.carry_out_sync()
                            self.send_message("Sync complete.", 1, 1)
                else:
                    self.send_message("Arena " + args.arena + " not found.")
            else:
                self.send_message("You must supply an ArenaTaskID.")

    def send_message(self, msg, pre_blanks=0, post_blanks=0):
        if self.show_output:
            IOManager.newlines(pre_blanks)
            print(msg)
            IOManager.newlines(post_blanks)

    def print_separator(self):
        self.send_message("-" * self.seplength)

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
