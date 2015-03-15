TaskArena
=======

A tool adding collaborative functionality to TaskWarrior.

**Project status:** Experimental.

**Warning:** Before trying out TaskArena it is strongly suggested that you create a backup of your TaskWarrior database.

Installation
-------

* Clone this repo::

    git clone https://github.com/niknow/TaskArena.git

* Switch into TaskArena and install the python library::

    cd TaskArena
    python setup.py install

* Move the `arenacmd.py` into your local `bin` folder and rename it to `tarena`::

    mv arenacmd.py usr/bin/tarena

* Now, TaskArena can install itself by::

    tarena install

This creates some entries in the `taskrc` of your TaskWarrior, which are neccessary so that TaskArena can interact with TaskWarrior.

List of Commands
-------
A list of possible commands can be generated via `tarena cmdlist`::

    install      installs TaskArena
    uninstall    uninstalls TaskArena
    create       creates a new arena
    delete       deletes an arena
    list         lists all arenas
    add          adds a task to an arena
    remove       removes a task from an
    local        lists all local task of an arena
    remote       lists all remote tasks of an arena
    sync         syncs an arena
    cmdlist      creates a list of all commands

A more detailled explaination of the various commands can be found in the following tutorial.

Tutorial
-------

The general syntax of `tarena` can be read by typing::

    tarena -h

We will walk you through it in the following.

Creating a new arena
~~~~~~~
To start working on tasks collaboratively, you first have to create an arena, in which you can put them::

    tarena create

You will be asked for a name for your arena. The name should be the common theme of the tasks you want to work on together, for instance the name of a project.
Next you will be asked for a local and a remote folder. The local folder should be the path of your usual local TaskWarrior database. The remote folder should be a new folder that you can share with your collaborators, for instance a folder in your Dropbox.

**Warning:** By giving `tarena` the path to your local TaskWarrior database, you automatically give it read and write permissions to this database. Since this project is in an experimental state, we again strongly advise you to make a backup of this folder first.

Managing arenas
~~~~~~~
You can create as many arenas as you like (as long as their names are unique). A list of all arenas can be produced via::

    tarena list

You could delete your arena by::

    tarena delete <arena>


Putting tasks into an arena
~~~~~~~
You can put tasks from your TaskWarrior into your arena::

    tarena add <arena> <filter>

Here `<arena>` should be the name of your arena and `<filter>` can be any TaskWarrior filter. For instance, if you have tasks like this::

    ID DESCRIPTION
     1 cut the lawn
     2 tidy up cellar

You can add the first one to your `housework` arena via::

    tarena add housework 1

If they are part of a project, i.e. if your task report looks like this::

    ID DESCRIPTION    PROJECT
     1 cut the lawn   housework
     2 tidy up cellar housework

You can also add them via::

    tarena add housework project:housework

The filter can be as complex as you like::

    tarena add housework project:housework +garden due.before:1month


Managing tasks in an arena
~~~~~~~
You can remove tasks from an arena in the same fashion. For instance::

    tarena remove housework 1

would remove the task with ID 1.

You can see a list of all local tasks in your arena via::

    tarena local housework

You can see a list of all remote tasks in your arena via::

    tarena remote housework


Syncinc tasks
~~~~~~~
So far, everything we did happened in your local TaskWarrior database. To actually share it, you use::

    tarena sync <arena>

So, to synchronize your `housework`::

    tarena sync housework

A dialog will walk you through the synchronization. In the end, only the tasks belonging to your arena will be synchronized with the remote folder.

Actually working together
~~~~~~~
To actually work together, you have to give your collaborator access to your remote folder, for instance by sharing that folder via Dropbox. Your collaborator has to create an arena with the same name and specify his local TaskWarrior folder as well as his remote folder in his Dropbox. In order for him to get your tasks, he has to perform an ordinary sync::

    tarena sync houework


A technical hint
-------
Technically, the installation of TaskArena adds some *User Defined Attributes (UDA)* to your TaskWarrior. After you have added a task to an arena you can see them via::

    task 1 info

assuming that the task with ID 1 has been added. TaskWarrior will display all information it has on the task and (among other things)::

    ...
    Arena         housework
    ArenaTaskID   156139121905747781424456029047977931020

The UDAs `Arena` and `ArenaTaskID` are used by `tarena` to interact with TaskWarrior.


Uninstallation
-------
To remove TaskArena one has to undo all the steps of the installation in reverse order.

* Remove the entries in the `taskrc` via::

    tarena uninstall

* Remove the command line interface by deleting `tarena` from your local `bin` folder::

    rm tarena

* Uninstall the python library by deleting all its files. You can get a list of these via::

    python setup.py install --record files.txt
    cat files.txt

