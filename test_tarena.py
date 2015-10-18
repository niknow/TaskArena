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
from tarena import (
    install,
    uninstall,
    create,
    delete,
    ls,
    add,
    remove,
    sync,
)


class TestTArena(unittest.TestCase):

    def setUp(self):
        self.runner = runner = CliRunner()

    def test_install(self):
        result = self.runner.invoke(install)
        assert result.exit_code == 0

    def test_uninstall(self):
        result = self.runner.invoke(uninstall)
        assert result.exit_code == 0

    def test_create(self):
        result = self.runner.invoke(create)
        assert result.exit_code == 0

    def test_delete(self):
        result = self.runner.invoke(delete, ['housework'])
        assert result.exit_code == 0

    def test_ls(self):
        result = self.runner.invoke(ls)
        assert result.exit_code == 0

    def test_add(self):
        result = self.runner.invoke(add, ['housework', 'pro:housework'])
        assert result.exit_code == 0

    def test_remove(self):
        result = self.runner.invoke(remove, ['housework', 'pro:housework'])
        assert result.exit_code == 0

    def test_sync(self):
        result = self.runner.invoke(sync)
        assert result.exit_code == 0
