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


import json
import uuid
import tasklib.task as tlib
import os.path
import subprocess

uda_config_list = [
    {'uda.Arena.type': 'string'},
    {'uda.Arena.label': 'Arena'},
    {'uda.ArenaTaskID.type': 'numeric'},
    {'uda.ArenaTaskID.label': 'ArenaTaskID'},
]

tw_attrs_editable = [
    'depends',
    'description',
    'due',
    'end',
    'imask',
    'mask',
    'parent',
    'priority',
    'project',
    'recur',
    'scheduled',
    'start',
    'status',
    'tags',
    'until',
    'wait',
]

tw_attrs_special = [
    'annotations',
]

tw_attrs_read_only = [
    'id',
    'entry',
    'urgency',
    'uuid',
    'modified'
]


class SharedTask(object):
    """ A Task that can be shared in an arena."""

    def __init__(self, tw_task, arena=None):
        self.tw_task = tw_task
        self.Arena = arena
        self._ArenaTaskID = None

    def _get_arena(self):
        return self._Arena

    def _set_arena(self, value):
        self._Arena = value
        if value:
            self.tw_task['Arena'] = self.Arena.name
            if not self.ArenaTaskID:
                self.ArenaTaskID = uuid.uuid4().__int__()
        else:
            self.remove()

    Arena = property(_get_arena, _set_arena)

    def _get_arena_task_id(self):
        return self.tw_task['ArenaTaskID']

    def _set_arena_task_id(self, value):
        self.tw_task['ArenaTaskID'] = value

    ArenaTaskID = property(_get_arena_task_id, _set_arena_task_id)

    def remove(self):
        self.tw_task['Arena'] = ''
        self.tw_task['ArenaTaskID'] = ''

    def last_modified(self):
        return self.tw_task['modified'] if self.tw_task['modified'] else self.tw_task['entry']

    def update(self, other):
        for field in tw_attrs_editable:
            if self.tw_task[field] != other.tw_task[field]:
                self.tw_task[field] = other.tw_task[field]

    def different_fields(self, other):
        result = []
        for field in tw_attrs_editable:
            if self.tw_task[field] != other.tw_task[field]:
                result.append(field)
        return result

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.ArenaTaskID == other.ArenaTaskID
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str({'Arena': self.Arena.name, 'ArenaTaskID:': self.ArenaTaskID, 'tw_task': self.tw_task.__dict__})

    def __str__(self):
        return str(self.__repr__())

    def save(self):
        try:
            self.tw_task.save()
            return 1
        except:
            return 0


class EnhancedTaskWarrior(object):
    def __init__(self, tw, arena):
        self.tw = tw
        self.arena = arena
        for uda in uda_config_list:
            self.tw.config.update(uda)

    def tasks(self, pattern):
        return [SharedTask(task, self.arena) for task in
                self.tw.tasks.filter(' '.join(pattern))]

    def add_task(self, task):
        t = SharedTask(tlib.Task(self.tw), self.arena)
        for field in tw_attrs_editable:
            t.tw_task[field] = task.tw_task[field]
        return t


class TaskArena(object):
    """ A project that is shared with others. """

    def __init__(self, arena_name='', ldata='/', rdata='/'):
        self._local_data = None
        self._remote_data = None
        self.tw_local = None
        self.tw_remote = None
        self.name = arena_name
        self.local_data = ldata
        self.remote_data = rdata
        self.SyncManager = SyncManager(self)

    def get_local_data(self):
        return self._local_data

    def set_local_data(self, ldata):
        self._local_data = ldata
        self.tw_local = EnhancedTaskWarrior(tlib.TaskWarrior(data_location=ldata), self)

    local_data = property(get_local_data, set_local_data)

    def get_remote_data(self):
        return self._remote_data

    def set_remote_data(self, rdata):
        self._remote_data = rdata
        self.tw_remote = EnhancedTaskWarrior(tlib.TaskWarrior(data_location=rdata), self)

    remote_data = property(get_remote_data, set_remote_data)

    def get_json(self):
        return self.__repr__()

    def set_json(self, data):
        self.name = data['name']
        self.local_data = data['local_data']
        self.remote_data = data['remote_data']

    json = property(get_json, set_json)

    def __repr__(self):
        return {'name': self.name, 'local_data': self.local_data, 'remote_data': self.remote_data}

    def __str__(self):
        return str(self.__repr__())

    def add(self, pattern):
        tasks = self.tw_local.tasks(pattern)
        for ta_task in tasks:
            ta_task.save()
        return tasks

    def remove(self, pattern):
        tasks = self.tw_local.tasks([pattern, 'Arena:' + self.name])
        for ta_task in tasks:
            ta_task.remove()
            ta_task.save()
        return tasks

    def sync(self):
        self.SyncManager.generate_synclist()
        self.SyncManager.suggest_conflict_resolution()
        self.SyncManager.let_user_check_and_modify_synclist()
        self.SyncManager.carry_out_sync()


class TaskEmperor(object):
    """ A class to handle all your TaskArenas """

    def __init__(self):
        self.arenas = []
        self.configfile = None

    def load(self, configfile):
        self.configfile = configfile
        if os.path.isfile(self.configfile):
            f = open(self.configfile)
            try:
                self.json = json.load(f)
                return 'loaded'
            except:
                return 'empty'
        else:
            open(self.configfile, 'w+')
            return 'new'

    def save(self):
        f = open(self.configfile, 'w+')
        json.dump(self.json, f)

    def get_json(self):
        return {'arenas': [p.json for p in self.arenas]}

    def set_json(self, data):
        self.arenas = []
        for json_project in data['arenas']:
            arena = TaskArena()
            arena.json = json_project
            self.arenas.append(arena)

    json = property(get_json, set_json)

    def __repr__(self):
        return {'configfile': self.configfile,
                'arenas': [p.__repr__() for p in self.arenas]}

    def __str__(self):
        return str(self.__repr__())

    def create_arena(self, arena_id, ldata, rdata):
        if arena_id not in [p.name for p in self.arenas]:
            arena = TaskArena(arena_id, ldata, rdata)
            self.arenas.append(arena)
            return arena

    def delete_arena(self, arena):
        arena.remove('')
        self.arenas.remove(arena)

    def find(self, arena_name):
        for arena in self.arenas:
            if arena.name == arena_name:
                return arena
