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


import json
import uuid
import tasklib.task as tlib
import os.path


uda_config_list = [
    {'uda.Legion.type': 'string'},
    {'uda.Legion.label': 'Legion'},
    {'uda.LegionID.type': 'numeric'},
    {'uda.LegionID.label': 'LegionID'},
]

seplength = 75


class SharedTask(object):
    """ A Task that can be shared in a legion."""

    def __init__(self, tw_task, lgn=None):
        self.tw_task = tw_task
        self.Legion = lgn
        self._LegionID = None

    def _get_legion(self):
        return self._Legion

    def _set_legion(self, value):
        self._Legion = value
        if value:
            self.tw_task['Legion'] = self.Legion.ID
            if not self.LegionID:
                self.LegionID = uuid.uuid4().__int__()
        else:
            self.remove()

    Legion = property(_get_legion, _set_legion)

    def _get_legion_id(self):
        return self.tw_task['LegionID']

    def _set_legion_id(self, value):
        self.tw_task['LegionID'] = value

    LegionID = property(_get_legion_id, _set_legion_id)

    def remove(self):
        self.tw_task['Legion'] = ''
        self.tw_task['LegionID'] = ''

    def last_modified(self):
        return self.tw_task['modified'] if self.tw_task['modified'] else self.tw_task['entry']

    def update(self, other):
        for k, v in self.tw_task._data.iteritems():
            if not k in self.tw_task.read_only_fields:
                self.tw_task[k] = other.tw_task[k]
        for k, v in other.tw_task._data.iteritems():
            if not k in self.tw_task.read_only_fields:
                self.tw_task[k] = other.tw_task[k]

    def different_fields(self, other):
        result = []
        for k, v in self.tw_task._data.iteritems():
            if not k in self.tw_task.read_only_fields:
                if self.tw_task[k] != other.tw_task[k]:
                    result.append(k)
        for k, v in other.tw_task._data.iteritems():
            if not k in self.tw_task.read_only_fields:
                if self.tw_task[k] != other.tw_task[k]:
                    if not k in result:
                        result.append(k)
        return result

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.LegionID == other.LegionID
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str({'Legion': self.Legion.ID, 'LegionID:': self.LegionID, 'tw_task': self.tw_task.__dict__})

    def __str__(self):
        return str(self.__repr__())

    def save(self):
        try:
            self.tw_task.save()
        except:
            print "Saving failed."


class EnhancedTaskWarrior(object):
    def __init__(self, tw, lgn):
        self.tw = tw
        self.legion = lgn
        for uda in uda_config_list:
            self.tw.config.update(uda)

    def tasks(self, pattern):
        return [SharedTask(task, self.legion) for task in
                self.tw.tasks.filter(' '.join(pattern))]

    # todo: can this be done with tasklib already?
    def add_task(self, task):
        t = SharedTask(tlib.Task(self.tw), self.legion)
        for k, v in task.tw_task._data.iteritems():
            if not k in task.tw_task.read_only_fields:
                t.tw_task[k] = v
        t.save()


class TaskLegion(object):
    """ A project that is shared with others. """

    def __init__(self, lid='', ldata='/', rdata='/', iomanager=None):
        self._local_data = None
        self._remote_data = None
        self.tw_local = None
        self.tw_remote = None
        self.ID = lid
        self.local_data = ldata
        self.remote_data = rdata
        self.IOManager = iomanager

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
        self.ID = data['ID']
        self.local_data = data['local_data']
        self.remote_data = data['remote_data']

    json = property(get_json, set_json)

    def __repr__(self):
        return {'ID': self.ID, 'local_data': self.local_data, 'remote_data': self.remote_data}

    def __str__(self):
        return str(self.__repr__())

    def add(self, pattern):
        for ta_task in self.tw_local.tasks(pattern):
            ta_task.save()
        self.IOManager.send_message("Tasks added.")

    def remove(self, pattern):
        for ta_task in self.tw_local.tasks([pattern, 'Legion:' + self.ID]):
            ta_task.remove()
            ta_task.save()
        self.IOManager.send_message("Tasks removed from " + self.ID + " .")

    def sync(self):

        def sync_choice(e):
            if e.local_task:
                self.IOManager.send_message("Task Description: " + e.local_task.tw_task['description'])
                self.IOManager.send_message("LegionID        : " + e.local_task.LegionID)
                if e.remote_task:
                    self.IOManager.send_message("\nTask exists in both repositories.\n")
                    self.IOManager.send_message("Last modified (local) : " + e.local_last_modified)
                    self.IOManager.send_message("Last modified (remote): " + e.remote_last_modified)

                    self.IOManager.send_message("\nSuggesting to " + e.suggestion + ".\n")
                    self.IOManager.send_message("This would cause the following modifications: \n")
                    for field in e.fields:
                        local_field = str(e.local_task.tw_task[field]) if e.local_task.tw_task[field] else '(empty)'
                        remote_field = str(e.remote_task.tw_task[field]) if e.remote_task.tw_task[field] else '(empty)'
                        self.IOManager.send_message(field + ": " + local_field + (
                            " -> " if e.suggestion == 'UPLOAD' else ' <- ') + remote_field)

                    result = raw_input("\nDo you want to (u)pload, (d)ownload, (s)kip or (c)ancel sync? (u/d/s/c) ")
                else:
                    self.IOManager.send_message("\n")
                    self.IOManager.send_message("This task does not yet exist on remote. Suggestion: " + e.suggestion)
                    result = raw_input("\nDo you want to (u)pload, (s)kip or (c)ancel sync? (u/s/c) ")
            else:
                self.IOManager.send_message("-" * seplength)
                self.IOManager.send_message("Description: " + e.remote_task.tw_task['description'])
                self.IOManager.send_message("LegionID: " + e.remote_task.LegionID)
                self.IOManager.send_message("\n")
                self.IOManager.send_message("This task does not yet exist on local.")
                result = raw_input("\nDo you want to (d)ownload, (s)kip or (c)ancel sync? (d/s/c) ")
            return result

        def formatted_print(t):
            print "{0:6}   {1:25}   {2:20}   {3:10}\n".format(t[0][0:6], t[1][0:25], t[2][0:20], t[3][0:10])

        def sync_preview(slist):
            self.IOManager.send_message("-" * seplength)
            formatted_print(('', 'Task', 'LastModified', 'Suggestion'))
            print "-" * seplength
            for e in slist:
                formatted_print(('Local', e.local_description, e.local_last_modified, ''))
                formatted_print(('Remote', e.remote_description, e.remote_last_modified, e.suggestion))
                self.IOManager.send_message("-" * seplength)

            return raw_input("\nDo you want to sync (a)ll, sync (m)anually or (c)ancel? (a/m/c) ")

        # get sync data
        local_tasks = self.tw_local.tasks('')
        remote_tasks = self.tw_remote.tasks('')
        new_local_tasks = [task for task in local_tasks if not task in remote_tasks]
        new_remote_tasks = [task for task in remote_tasks if not task in local_tasks]
        synclist = []
        # find sync conflicts and add to synclist
        for ltask in local_tasks:
            if ltask in remote_tasks:
                for rtask in remote_tasks:
                    if ltask == rtask:
                        if ltask.different_fields(rtask):
                            conflict = SyncElement(ltask, rtask, ltask.different_fields(rtask))
                            if ltask.last_modified() >= rtask.last_modified():
                                conflict.suggestion = 'UPLOAD'
                            else:
                                conflict.suggestion = 'DOWNLOAD'
                            synclist.append(conflict)
        # add new local tasks to synclist
        for task in new_local_tasks:
            upload = SyncElement(task, None, None, 'UPLOAD')
            synclist.append(upload)
        # add new remote tasks to synclist
        for task in new_remote_tasks:
            download = SyncElement(None, task, None, 'DOWNLOAD')
            synclist.append(download)
        # present synclist and allow modifications
        if synclist:
            self.IOManager.send_message("\nSuggesting the following sync operations on " + self.ID + "...\n\n")
            sync_command = sync_preview(synclist)
            if sync_command == 'a':
                for elem in synclist:
                    elem.action = elem.suggestion
            elif sync_command == 'm':
                self.IOManager.send_message("\nStarting manual sync...\n")
                for elem in synclist:
                    self.IOManager.send_message("-" * seplength)
                    sc = sync_choice(elem)
                    if sc == 'u':
                        elem.action = 'UPLOAD'
                        self.IOManager.send_message("\nTask uploaded.")
                    elif sc == 'd':
                        elem.action = 'DOWNLOAD'
                        self.IOManager.send_message("\nTask downloaded.")
                    elif sc == 'c':
                        self.IOManager.send_message("Sync canceled.\n")
                        synclist = []
                        break
            # carry out sync
            for elem in synclist:
                if elem.action == 'UPLOAD':
                    if elem.remote_task:
                        elem.remote_task.update(elem.local_task)
                        elem.remote_task.save()
                    else:
                        self.tw_remote.add_task(elem.local_task)
                elif elem.action == 'DOWNLOAD':
                    if elem.local_task:
                        elem.local_task.update(elem.remote_task)
                        elem.local_task.save()
                    else:
                        self.tw_local.add_task(elem.remote_task)
            self.IOManager.send_message("\nSync complete.\n")
        else:
            self.IOManager.send_message("Legion " + self.ID + " is in sync.\n")


class SyncElement():
    def __init__(self, ltask=None, rtask=None, fields=None, suggestion='', action=''):
        self.local_task = ltask
        self.remote_task = rtask
        self.suggestion = suggestion
        self.action = action
        self.fields = fields

    @property
    def local_description(self):
        return self.local_task.tw_task['description'] if self.local_task else ''

    @property
    def remote_description(self):
        return self.remote_task.tw_task['description'] if self.remote_task else ''

    @property
    def local_last_modified(self):
        return str(self.local_task.last_modified()) if self.local_task else ''

    @property
    def remote_last_modified(self):
        return str(self.remote_task.last_modified()) if self.remote_task else ''


class IOManager(object):

    def __init__(self, show_output=True):
        self.show_output = show_output

    def send_message(self, msg):
        if self.show_output:
            print msg


class TaskGeneral(object):
    """ A class to handle all your TaskLegions """

    def __init__(self, cfile, output=True):
        self.legions = []
        self.IOManager = IOManager(output)
        self.configfile = cfile
        self.load(cfile)

    def load(self, cfile):
        if os.path.isfile(cfile):
            f = open(cfile)
            try:
                self.json = json.load(f)
                self.IOManager.send_message("Legions loaded.")
            except:
                self.IOManager.send_message("Warning: Config file " + cfile + " is empty or corrupt.")
        else:
            open(cfile, 'w+')
            self.IOManager.send_message("New .legionrc created at " + cfile)

    def save(self):
        f = open(self.configfile, 'w+')
        json.dump(self.json, f)
        self.IOManager.send_message("Task General saved.")

    def get_json(self):
        return {'legions': [p.json for p in self.legions]}

    def set_json(self, data):
        self.legions = []
        for json_project in data['legions']:
            lgn = TaskLegion()
            lgn.json = json_project
            lgn.IOManager = self.IOManager
            self.legions.append(lgn)

    json = property(get_json, set_json)

    def __repr__(self):
        return {'configfile': self.configfile,
                'legions': [p.__repr__() for p in self.legions]}

    def __str__(self):
        return str(self.__repr__())

    def create_legion(self, lid, ldata, rdata):
        if id in [p.ID for p in self.legions]:
            self.IOManager.send_message("Legion " + id + " already exists!")
        else:
            lgn = TaskLegion(lid, ldata, rdata, self.IOManager)
            self.legions.append(lgn)
            self.IOManager.send_message("Legion " + lgn.ID + " created.")
        return lgn

    def delete_legion(self, lgn):
        lgn.remove('')
        self.legions.remove(lgn)
        self.save()
        self.IOManager.send_message("Legion " + lgn.ID + " deleted.")

    def find(self, lid):
        for lgn in self.legions:
            if lgn.ID == lid:
                return lgn
