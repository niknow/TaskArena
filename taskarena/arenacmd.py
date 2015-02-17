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


import argparse
import subprocess
from legionlib import *


def execute_command(command_args):
    p = subprocess.Popen(command_args,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate(input='y\n')


parser = argparse.ArgumentParser()
parser.add_argument("command", help="command you want to issue")
parser.add_argument("legion", nargs='?', default='', help="legion you want to issue command to")
parser.add_argument("filter", nargs='?', default='', help="taskwarrior filter you want to restrict your command to")
args = parser.parse_args()

if args.command:
    configfile = os.path.expanduser("~") + "\\.legionrc"
    TG = TaskGeneral(configfile)
    if args.command == 'install':
        for uda in uda_config_list:
            execute_command(['task', 'config', uda.keys()[0], uda[uda.keys()[0]]])
        print "TaskLegion installed."
    elif args.command == 'uninstall':
        for uda in reversed(uda_config_list):
            execute_command(['task', 'config', uda.keys()[0]])
        os.remove(configfile)
        print "TaskLegion uninstalled."
    elif args.command == 'create':
        print "Creating new Legion..."
        ID = raw_input('Enter an ID: ')
        ldata = raw_input('Enter local data.location: ')
        rdata = raw_input('Enter remote data.location: ')
        TG.create_arena(ID, ldata, rdata)
        TG.save()
    elif args.command == 'list':
        if TG.arenas:
            print "The following legions are available:\n"
            for legion in TG.arenas:
                print "Legion: " + legion.ID
                print "local: " + legion.local_data
                print "remote: " + legion.remote_data
    elif args.command in ['add', 'remove', 'delete', 'sync']:
        if args.legion:
            legion = TG.find(args.legion)
            if legion:
                if args.command == 'add':
                    legion.add(args.filter)
                elif args.command == 'remove':
                    legion.remove(args.filter)
                elif args.command == 'delete':
                    TG.delete_arena(legion)
                elif args.command == 'sync':
                    legion.sync()
            else:
                print "Legion " + args.legion + " not found."
        else:
            print "You must supply a LegionID."
else:
    print "No command supplied."
