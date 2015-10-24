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


import click
from tarenalib.arena import uda_config_list
from tarenalib.io import IOManager
from tarenalib.sync import SyncManager
import subprocess
import locale

iom = IOManager()

def execute_command(command_args):
    p = subprocess.Popen(command_args,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
    encoding = locale.getdefaultlocale()[1]
    p.communicate(input='y\n'.encode(encoding))


@click.group()
@click.option('--file')
def cli(file):
    iom.configfile_name = file


@cli.command(help='Installs TaskArena.')
def install():
    for uda in uda_config_list:
        execute_command(['task', 'config', uda[0], uda[1]])
    iom.send_message('Installation successful.')
    return 0


@cli.command(help='Uninstalls TaskArena.')
def uninstall():
    for uda in uda_config_list:
        execute_command(['task', 'config', uda[0]])
    iom.send_message('Uninstallation successful.')
    return 0


@cli.command(help='Creates a new arena.')
def create():
    te = iom.get_task_emperor()
    if te:
        iom.send_message("Creating new Arena:")
        name = iom.get_input('Enter a name: ')
        ldata = iom.get_input('Enter local data.location: ')
        rdata = iom.get_input('Enter remote data.location: ')
        if te.create_arena(name, ldata, rdata):
            iom.send_message("Arena " + name + " created.")
            iom.save_task_emperor(te)
        else:
            iom.send_message("Arena " + name + " already exists!")
        return 0


class FoundArena(object):

    def __init__(self, arena, task_emperor, sync_manager):
        self.arena = arena
        self.te = task_emperor
        self.sm = sync_manager


def find_arena(ctx, param, value):
    te = iom.get_task_emperor()
    arena = te.find(value)
    if not arena:
        iom.send_message("Arena " + value + " not found.")
        return None
    else:
        return FoundArena(arena, te,  SyncManager(arena, iom))


@cli.command(help='Deletes ARENA.')
@click.argument('found_arena', callback=find_arena)
def delete(found_arena):
    if found_arena:
        found_arena.te.delete_arena(found_arena.arena)
        iom.save_task_emperor(found_arena.te)
        iom.send_message("Arena " + found_arena.arena.name + " deleted.")


@cli.command(help='Lists all arenas.')
def arenas():
    te = iom.get_task_emperor()
    if te.arenas:
        iom.send_message("The following arenas are available:", 1)
        for arena in te.arenas:
            iom.send_message(arena.name, 1)
            iom.send_message("local : " + arena.local_data)
            iom.send_message("remote: " + arena.remote_data, 0, 1)
    else:
        iom.send_message("No arenas found.")


@cli.command(help='Adds tasks matching PATTERN to ARENA.')
@click.argument('found_arena', callback=find_arena)
@click.argument('pattern', nargs=-1)
def add(found_arena, pattern):
    if found_arena:
        found_arena.arena.tw_local.add_tasks_matching_pattern(pattern)
        iom.send_message("Tasks added.")


@cli.command(help='Removes tasks matching PATTERN from ARENA.')
@click.argument('found_arena', callback=find_arena)
@click.argument('pattern', nargs=-1)
def remove(found_arena, pattern):
    if found_arena:
        found_arena.arena.tw_local.remove_tasks_matching_pattern(pattern)
        iom.send_message("Tasks removed from " + found_arena.arena.name + ".")


@cli.command(help='Lists all local tasks matching PATTERN from ARENA.')
@click.argument('found_arena', callback=find_arena)
@click.argument('pattern', nargs=-1)
def local(found_arena, pattern):
    if found_arena:
        list_tasks(found_arena.arena, pattern, found_arena.arena.local_data)


@cli.command(help='Lists all remote tasks matching PATTERN from ARENA.')
@click.argument('found_arena', callback=find_arena)
@click.argument('pattern', nargs=-1)
def remote(found_arena, pattern):
    if found_arena:
        list_tasks(found_arena.arena, pattern, found_arena.arena.remote_data)


def list_tasks(arena, pattern, data_location):
    p = subprocess.Popen(
        ['task',
         'rc.data.location:' + data_location,
         'Arena:' + arena.name,
         pattern],
        stderr=subprocess.PIPE
    )
    p.communicate()


@cli.command(help='Synchronizes ARENA')
@click.argument('found_arena', callback=find_arena)
def sync(found_arena):
    if found_arena:
        found_arena.sm.sync()


if __name__ == '__main__':
    cli()
