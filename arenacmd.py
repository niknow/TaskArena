#!/usr/bin/python

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
from tarenalib.arenalib import IOManager

parser = argparse.ArgumentParser()
parser.add_argument("command", help="command you want to issue")
parser.add_argument("arena", nargs='?', default='', help="arena you want to issue commands in")
parser.add_argument("filter", nargs='?', default='', help="taskwarrior filter you want to restrict your command to")
args = parser.parse_args()

IO = IOManager()
IO.process_commands(args)

