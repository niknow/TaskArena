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

from tarenalib.arena import TaskEmperor
import os


class IOManager(object):

    def __init__(self, show_output=True, seplength=75, configfile_name=None):
        self.show_output = show_output
        self.seplength = seplength
        self.configfile_name = configfile_name

    @staticmethod
    def formatted_print(t):
        print(u'{0:6}   {1:25}   {2:20}   {3:10}'.format(
            t[0][0:6], t[1][0:25], t[2][0:20], t[3][0:10]
            )
        )

    @staticmethod
    def newlines(num):
        if num:
            print("\n" * (num - 1))

    @staticmethod
    def get_input(msg, pre_blanks=0, post_blanks=0):
        IOManager.newlines(pre_blanks)
        data = input(msg)
        IOManager.newlines(post_blanks)
        return data

    def _get_configfile_name(self):
        return self._configfile_name

    def _set_configfile_name(self, value):
        if value:
            self._configfile_name = value
        else:
            self._configfile_name = os.path.join(
                os.path.expanduser("~"),
                "task_arena_config")

    configfile_name = property(_get_configfile_name, _set_configfile_name)

    def send_message(self, msg, pre_blanks=0, post_blanks=0):
        if self.show_output:
            IOManager.newlines(pre_blanks)
            print(msg)
            IOManager.newlines(post_blanks)

    def print_separator(self):
        self.send_message("-" * self.seplength)

    def get_task_emperor(self):
        te = TaskEmperor()
        if os.path.isfile(self.configfile_name):
            f = open(self.configfile_name, 'r')
            self.send_message("Configfile found at: %s" % self.configfile_name)
            if te.load(f):
                self.send_message("Configfile loaded.")
            else:
                self.send_message("Configfile corrupt.")
                return None
        else:
            f = open(self.configfile_name, 'w+')
            self.send_message("New configfile created at: %s" % self.configfile_name)
            te.save(f)
            self.send_message("Configfile saved.")
        f.close()
        return te

    def save_task_emperor(self, te):
        f = open(self.configfile_name, 'w+')
        te.save(f)
        self.send_message("Saved.")
        f.close()
