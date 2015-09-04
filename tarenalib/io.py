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

from tarenalib.arena import TaskEmperor, uda_config_list
from tarenalib.sync import SyncManager
import subprocess
import os


class IOManager(object):
    def __init__(self, show_output=True, seplength=75):
        self.show_output = show_output
        self.seplength = seplength
        self.TaskEmperor = TaskEmperor()
        self.configfile = os.path.expanduser("~") + "\\task_arena_config"

    @staticmethod
    def formatted_print(t):
        print(u'{0:6}   {1:25}   {2:20}   {3:10}'.format(t[0][0:6], t[1][0:25], t[2][0:20], t[3][0:10]))

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
        if args.command in TaskArenaCommandManager.command_list():
            self.call_emperor()
            eval(TaskArenaCommandManager.command_dict()[args.command])
        else:
            self.send_message("Invalid command supplied.")

    def call_emperor(self):

        #  if os.path.isfile(self.configfile):
        #     f = open(self.configfile)
        #     try:
        #         self.json = json.load(f)
        #         return 'loaded'
        #     except:
        #         return 'empty'
        # else:
        #     open(self.configfile, 'w+')
        #     return 'new'

        load_result = self.TaskEmperor.load(self.configfile)
        if load_result == 'loaded':
            self.send_message("Arenas loaded.")
        elif load_result == 'empty':
            self.send_message("Warning: Config file " + self.configfile + " is empty or corrupt.")
        elif load_result == 'new':
            self.send_message("New arena config created at " + self.configfile)



    def get_arena(self, args):
        if args.arena:
            arena = self.TaskEmperor.find(args.arena)
            if arena:
                return arena
            else:
                self.send_message("Arena " + args.arena + " not found.")
        else:
            self.send_message("You must supply an arena.")



    def list_tasks(self, args, data_location):
        arena = self.get_arena(args)
        if arena:
            p = subprocess.Popen(['task',
                                  'rc.data.location:' + eval('arena.' + data_location),
                                  'Arena:' + arena.name,
                                  args.filter],
                                 stderr=subprocess.PIPE)
            p.communicate()



