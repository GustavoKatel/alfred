==========
Alfred Cmd
==========


.. image:: https://img.shields.io/pypi/v/alfredcmd.svg
        :target: https://pypi.python.org/pypi/alfredcmd

.. image:: https://img.shields.io/travis/GustavoKatel/alfredcmd.svg
        :target: https://travis-ci.org/GustavoKatel/alfredcmd

.. image:: https://readthedocs.org/projects/alfredcmd/badge/?version=latest
        :target: https://alfredcmd.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Create portable custom commands and scripts.

This is currently in beta, but usable.

Usage
------

All the config are located in :code:`$USER/.alfred/alfred.toml`

Config
~~~~~~

.. code-block:: toml

    [variables]
    mode="debug"

    [function.branch]
    exec="git rev-parse --abbrev-ref HEAD"

    [command.st]
    exec="git status"

    [command.cc]
    exec="git commit -a {@}"

    [command.push]
    exec="git push {@}"

    [command.b]
    exec="echo {branch()}"

    [command.pythonCall]
    exec="~/.alfred/myscript.py::myFunction"
    type="python"

Run
~~~

.. code-block:: console

    $ alfred st
    $ al cc


Variables
~~~~~~~~~

Variables are predefined values that can be injected in commands and functions

Example:

.. code-block:: toml

    [variables]
    mode="debug"

    [command.print]
    exec="echo {mode}"


Commands
~~~~~~~~

Predefined commands that will be executed by Alfred

Commands are defined like this

.. code-block:: toml

    [command.COMMAND_NAME]
    exec="EXECUTION_LINE"
    type="shell"
    format=true
    echo=false
    help="HELP INFO"

Where:
- **COMMAND_NAME** is the alias that Alfred will use to identify that command in the cli

- **EXECUTION_LINE** is the code that will be called. Alfred accepts multiline entries, which
will be wrapped in a script file and executed with the default shell executor.

- **type** the type of the command. Alfred currently accepts `shell` and `python` command types

- **format** marks if the instance should apply the formatter in the exec line or not.
If false, the placeholders `{}` will not be interpreted

- **echo** marks if the instance should print the command that will be executed before executing it

- **help** a descriptive message that will be showed in `alfred @list`

Functions
~~~~~~~~~

Functions can be created to enhance command execution during format time and are defined like this:

.. code-block:: toml

    [function.FUNCTION_NAME]
    exec="EXECUTION_LINE"
    format=true

Where:

- **FUNCTION_NAME** is the alias that Alfred will use to identify that function in the formatter

- **EXECUTION_LINE** is the code that will be called. Currently Alfred only accepts one-line shell commands in functions.

- **format** marks if the instance should apply the formatter in the exec line or not.
If false, the placeholders `{}` will not be interpreted


Built-in Alfred commands
~~~~~~~~~~~~~~~~~~~~~~~~

- `al[fred] @help` Show help
- `al[fred] @list` List all commands
- `al[fred] @version` Show version

Installation
------------

Stable release
~~~~~~~~~~~~~~

To install Alfred, run this command in your terminal:

.. code-block:: console

    $ pip install alfredcmd

This is the preferred method to install Alfred, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
~~~~~~~~~~~~~

The sources for Alfred can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/GustavoKatel/alfredcmd

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/GustavoKatel/alfredcmd/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/GustavoKatel/alfredcmd
.. _tarball: https://github.com/GustavoKatel/alfredcmd/tarball/master


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
