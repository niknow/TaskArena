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

iom = IOManager()

@click.group()
def cli():
    pass


@cli.command(help='Installs TaskArena.')
def install():
    iom.send_message('Installing...')


@cli.command(help='Uninstalls TaskArena.')
def uninstall():
    click.echo('Uninstalling')
    pass


@cli.command(help='Creates a new arena.')
def create():
    pass


@cli.command(help='Deletes an arena.')
@click.argument('name')
def delete(name):
    pass


@cli.command(help='Lists all arenas.')
def list(self):
    pass


@cli.command(help='Adds tasks to an arena.')
def add():
 pass


@cli.command(help='Removes tasks from an arena.')
def remove():
    pass


@cli.command(help='Synchronizes an arena')
def sync():
    pass


if __name__ == '__main__':
    cli()
