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


import sys
import unittest
from io import StringIO
from unittest.mock import patch
from click.testing import CliRunner
import os
from tarenalib.io import IOManager


class TestIOManager(unittest.TestCase):

    def setUp(self):
        self.old_stdout = sys.stdout
        self.mystdout = StringIO()
        sys.stdout = self.mystdout

    def tearDown(self):
        sys.stdout = self.old_stdout

    def test_formatted_print(self):
        t = ('Local', 'do dishes', '2014-01-01', 'UPLOAD')
        IOManager.formatted_print(t)
        line = "Local    do dishes                   2014-01-01" \
               + "             UPLOAD    \n"
        self.assertEqual(self.mystdout.getvalue(), line)

    def test_newlines(self):
        IOManager.newlines(3)
        self.assertEqual(self.mystdout.getvalue(), "\n\n\n")

    @patch('builtins.input', return_value='foo')
    def test_get_input(self, mock_input):
        result = IOManager.get_input('test', 1, 2)
        self.assertEqual(result, 'foo')

    def test_create_io_manager(self):
        iom = IOManager()
        self.assertEqual(type(iom), IOManager)
        self.assertEqual(iom.seplength, 75)
        self.assertEqual(iom.show_output, True)
        self.assertNotEqual(iom.configfile_name, None)

    def test_send_message(self):
        iom = IOManager()
        iom.send_message('test', 1, 2)
        self.assertEqual(self.mystdout.getvalue(), '\ntest\n\n\n')
        iom.show_output=False
        iom.send_message('test')
        self.assertEqual(self.mystdout.getvalue(), '\ntest\n\n\n')

    def test_print_seperator(self):
        iom = IOManager()
        iom.print_separator()
        self.assertEqual(self.mystdout.getvalue(), "-" * 75 + "\n")

    def test_get_save_task_emperor(self):
        runner = CliRunner()
        sys.stdout = self.old_stdout
        with runner.isolated_filesystem():
            config_file_name = os.path.join(os.getcwd(), 'config_file')
            self.assertEqual(os.path.isfile(config_file_name), False)
            iom = IOManager(False, 75, config_file_name)
            iom.get_task_emperor()
            self.assertEqual(os.path.isfile(config_file_name), True)
            iom = IOManager(False, 75, config_file_name)
            te = iom.get_task_emperor()
            arena = te.create_arena('foo', 'local', 'remote')
            iom.save_task_emperor(te)
            iom = IOManager(False, 75, config_file_name)
            te = iom.get_task_emperor()
            self.assertEqual(len(te.arenas), 1)
            self.assertEqual(arena.name, te.arenas[0].name)
            self.assertEqual(arena.local_data, te.arenas[0].local_data)
            self.assertEqual(arena.remote_data, te.arenas[0].remote_data)


