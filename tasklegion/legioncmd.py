# -*- coding: utf-8 -*-


# TaskLegion - Adding collaborative functionality to TaskWarrior
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


import sys
import subprocess
from legionlib import *


def execute_command(command_args):
    p = subprocess.Popen(command_args,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate(input='y\n')


if len(sys.argv) > 1:
    command = sys.argv[1]
    configfile = os.path.expanduser("~") + "\\.legionrc"
    TG = TaskGeneral(configfile)
    if command == 'install':
        for uda in uda_config_list:
            execute_command(['task', 'config', uda.keys()[0], uda[uda.keys()[0]]])
        print "TaskLegion installed."
    elif command == 'uninstall':
        for uda in reversed(uda_config_list):
            execute_command(['task', 'config', uda.keys()[0]])
        os.remove(configfile)
        print "TaskLegion uninstalled."
    elif command == 'create':
        print "Creating new Legion..."
        ID = raw_input('Enter an ID: ')
        ldata = raw_input('Enter local data.location: ')
        rdata = raw_input('Enter remote data.location: ')
        TP = TaskLegion(ID, ldata, rdata)
        TG.create_legion(TP)
        TG.save()
    elif command == 'list':
        if TG.legions:
            print "The following legions are available:\n"
            for legion in TG.legions:
                print "Legion: " + legion.ID
                print "local: " + legion.local_data
                print "remote: " + legion.remote_data
    elif command in ['add', 'remove', 'delete', 'sync']:
        if len(sys.argv) > 2:
            supplied_pattern = sys.argv[3:]
            project = TG.find(sys.argv[2])
            if project:
                if command == 'add':
                    project.add(supplied_pattern)
                elif command == 'remove':
                    project.remove(supplied_pattern)
                elif command == 'delete':
                    TG.delete_legion(project)
                elif command == 'sync':
                    project.sync()
            else:
                print "Legion " + sys.argv[2] + " not found."
        else:
            print "You must supply a LegionID."
else:
    print "No command supplied."
