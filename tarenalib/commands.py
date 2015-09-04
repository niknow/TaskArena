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

from abc import ABCMeta, abstractmethod

from tarenalib.arena import uda_config_list


class TaskArenaCommand(object):
    """ An abstract class representing a TaskArenaCommand
    """

    __metaclass__ = ABCMeta

    def __init__(self, io_manager=None, command='', args=True, helptext=''):
        self.IOManager = io_manager
        self.command = command
        self.args = args
        self.helptext = helptext

    @abstractmethod
    def execute(self):
        pass

    def function_string(self):
        if self.args:
            return 'self._tarena_' + self.command + '(args)'
        else:
            return 'self._tarena_' + self.command + '()'


class Install(TaskArenaCommand):

    def __init__(self, io_manager):
        TaskArenaCommand.__init__(
            io_manager=io_manager,
            command='install',
            args=False,
            helptext='installs TaskArena')

    def execute(self):
        for uda in uda_config_list:
            self.IOManager.execute_command(['task', 'config', uda.keys()[0], uda[uda.keys()[0]]])
        self.IOManager.send_message("TaskArena installed.")


class Uninstall(TaskArenaCommand):

    def __init__(self, io_manager):
        TaskArenaCommand.__init__(
            io_manager=io_manager,
            command='install',
            args=False,
            helptext='installs TaskArena')

    def execute(self):
        for uda in uda_config_list:
            self.IOManager.execute_command(['task', 'config', uda.keys()[0], uda[uda.keys()[0]]])
        self.IOManager.send_message("TaskArena installed.")


class TaskArenaCommandManager(object):
    valid_commands = [
        TaskArenaCommand('install', False, 'installs TaskArena'),
        TaskArenaCommand('uninstall', False, 'uninstalls TaskArena'),
        TaskArenaCommand('create', False, 'creates a new arena'),
        TaskArenaCommand('delete', True, 'deletes an arena'),
        TaskArenaCommand('list', False, 'lists all arenas'),
        TaskArenaCommand('add', True, 'adds a task to an arena'),
        TaskArenaCommand('remove', True, 'removes a task from an'),
        TaskArenaCommand('local', True, 'lists all local task of an arena'),
        TaskArenaCommand('remote', True, 'lists all remote tasks of an arena'),
        TaskArenaCommand('sync', True, 'syncs an arena'),
        TaskArenaCommand('cmdlist', False, 'creates a list of all commands'),
    ]

    @staticmethod
    def command_list():
        return [c.command for c in TaskArenaCommandManager.valid_commands]

    @staticmethod
    def command_dict():
        d = {}
        for c in TaskArenaCommandManager.valid_commands:
            d[c.command] = c.function_string()
        return d


def _tarena_uninstall(self):
    for uda in reversed(uda_config_list):
        IOManager.execute_command(['task', 'config', uda.keys()[0]])
    os.remove(self.configfile)
    self.send_message("TaskArena uninstalled.")


def _tarena_create(self):
    self.send_message("Creating new Arena...", 1, 1)
    name = self.get_input('Enter a name: ')
    ldata = self.get_input('Enter local data.location: ')
    rdata = self.get_input('Enter remote data.location: ')
    if self.TaskEmperor.create_arena(name, ldata, rdata):
        self.send_message("Arena " + name + " created.")
        self.TaskEmperor.save()  # todo enter file handle here
    else:
        self.send_message("Arena " + name + " already exists!")


def _tarena_list(self):
    if self.TaskEmperor.arenas:
        self.send_message("The following arenas are available:", 1)
        for arena in self.TaskEmperor.arenas:
            self.send_message("arena : " + arena.name, 1)
            self.send_message("local : " + arena.local_data)
            self.send_message("remote: " + arena.remote_data, 0, 1)


def _tarena_add(self, args):
    arena = self.get_arena(args)
    if arena:
        arena.tw_local.add_tasks_matching_pattern(args.filter.split())
        self.send_message("Tasks added.")


def _tarena_remove(self, args):
    arena = self.get_arena(args)
    if arena:
        arena.tw_local.remove_tasks_matching_pattern(args.filter)
        self.send_message("Tasks removed from " + arena.name + " .")


def _tarena_delete(self, args):
    arena = self.get_arena(args)
    if arena:
        self.TaskEmperor.delete_arena(arena)
        self.TaskEmperor.save()
        self.send_message("Arena " + arena.name + " deleted.")


def _tarena_sync(self, args):
    arena = self.get_arena(args)
    if arena:
        sm = SyncManager(arena)
        sm.generate_synclist()
        sm.suggest_conflict_resolution()
        sm.synclist = self.let_user_check_and_modify_synclist(sm.synclist, arena)
        if sm.synclist:
            sm.carry_out_sync()
            self.send_message("Sync complete.", 1, 1)


def _tarena_local(self, args):
    self.list_tasks(args, 'local_data')


def _tarena_remote(self, args):
    self.list_tasks(args, 'remote_data')

    def _tarena_cmdlist(self):
        self.send_message('TaskArena Commandlist', 1, 1)

    for c in TaskArenaCommandManager.valid_commands:
        print(u'  {0:10}   {1:25}'.format(c.command, c.helptext))