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


from click.testing import CliRunner
import unittest
from tarenalib.arena import uda_config_list
from tarena import cli
from tasklib.task import TaskWarrior, Task
import os


cmd = ['--file', 'taconfig']
cmd_dummy_arena = ['--file', 'taconfig', 'create',
                   '--name', 'foo',
                   '--ldata', 'local',
                   '--rdata', 'remote']


class TestTArena(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_install(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['install'])
        assert result.exit_code == 0

    def test_uninstall(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['uninstall'])
        assert result.exit_code == 0

    def test_create(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, cmd_dummy_arena)
        assert result.exit_code == 0

    def test_delete(self):
        with self.runner.isolated_filesystem():
            self.runner.invoke(cli, cmd_dummy_arena)
            result_delete = self.runner.invoke(cli, cmd + ['delete', 'foo'])
            result_check = self.runner.invoke(cli, cmd + ['arenas'])
            assert result_delete.exit_code == 0
            assert 'No arenas found' in result_check.output

    def test_arenas(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, cmd + ['arenas'])
            assert 'No arenas found' in result.output
            self.runner.invoke(cli, cmd_dummy_arena)
            result = self.runner.invoke(cli, cmd + ['arenas'])
            assert 'foo' in result.output
            assert result.exit_code == 0

    def test_add(self):
        with self.runner.isolated_filesystem():
            dloc = '/cygdrive/c'+os.getcwd().replace('\\', '/')[2:] \
                   + '/local'
            tw = TaskWarrior(dloc)
            t = Task(tw)
            description = 'do dishes'
            t['description'] = description
            t.save()
            self.runner.invoke(cli, cmd_dummy_arena)
            self.runner.invoke(cli, cmd + ['add', 'foo', description])
            for uda in uda_config_list:
                tw.config.update({uda[0]: uda[1]})
            assert len(tw.tasks.filter('Arena:foo')) == 1

    def test_remove(self):
        with self.runner.isolated_filesystem():
            dloc = '/cygdrive/c'+os.getcwd().replace('\\', '/')[2:] \
                   + '/local'
            tw = TaskWarrior(dloc)
            t = Task(tw)
            description = 'do dishes'
            t['description'] = description
            t.save()
            self.runner.invoke(cli, cmd_dummy_arena)
            self.runner.invoke(cli, cmd + ['add', 'foo', description])
            self.runner.invoke(cli, cmd + ['remove', 'foo', description])
            for uda in uda_config_list:
                tw.config.update({uda[0]: uda[1]})
            assert len(tw.tasks.filter('Arena:foo')) == 0

    def test_sync(self):
        with self.runner.isolated_filesystem():
            cwd = '/cygdrive/c'+os.getcwd().replace('\\', '/')[2:]
            dloc = cwd + '/local'
            dremote = cwd + '/remote'
            tw_local = TaskWarrior(dloc)
            tw_remote = TaskWarrior(dremote)
            t = Task(tw_local)
            description = 'do dishes'
            t['description'] = description
            t.save()
            self.runner.invoke(cli, cmd_dummy_arena)
            self.runner.invoke(cli, cmd + ['add', 'foo', description])
            result = self.runner.invoke(cli, cmd + ['sync', 'foo'], input='a\n')
            assert len(tw_remote.tasks.filter()) == 1
