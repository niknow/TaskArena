# -*- coding: utf-8 -*-
#! /usr/bin/python

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


import argparse
import subprocess
from arenalib import *


def execute_command(command_args):
    p = subprocess.Popen(command_args,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate(input='y\n')


parser = argparse.ArgumentParser()
parser.add_argument("command", help="command you want to issue")
parser.add_argument("arena", nargs='?', default='', help="arena you want to issue commands in")
parser.add_argument("filter", nargs='?', default='', help="taskwarrior filter you want to restrict your command to")
args = parser.parse_args()

TE = TaskEmperor()
io = TE.IOManager

if args.command:
    configfile = os.path.expanduser("~") + "\\task_arena_config"
    TE.configfile = configfile
    if args.command == 'install':
        for uda in uda_config_list:
            execute_command(['task', 'config', uda.keys()[0], uda[uda.keys()[0]]])
        io.send_message("TaskArena installed.")
    elif args.command == 'uninstall':
        for uda in reversed(uda_config_list):
            execute_command(['task', 'config', uda.keys()[0]])
        os.remove(configfile)
        io.send_message("TaskArena uninstalled.")
    elif args.command == 'create':
        io.send_message("Creating new Arena...")
        name = io.get_input('Enter a name: ')
        ldata = io.get_input('Enter local data.location: ')
        rdata = io.get_input('Enter remote data.location: ')
        TE.create_arena(name, ldata, rdata)
        TE.save()
    elif args.command == 'list':
        if TE.arenas:
            io.send_message("The following arenas are available:", 1, 1)
            for arena in TE.arenas:
                io.send_message("arena : " + arena.name)
                io.send_message("local : " + arena.local_data)
                io.send_message("remote: " + arena.remote_data)
    elif args.command in ['add', 'remove', 'delete', 'sync']:
        if args.arena:
            arena = TE.find(args.arena)
            if arena:
                if args.command == 'add':
                    arena.add(args.filter)
                elif args.command == 'remove':
                    arena.remove(args.filter)
                elif args.command == 'delete':
                    TE.delete_arena(arena)
                elif args.command == 'sync':
                    arena.sync()
            else:
                io.send_message("Arena " + args.arena + " not found.")
        else:
            io.send_message("You must supply an ArenaTaskID.")
else:
    io.send_message("No command supplied.")
