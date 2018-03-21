# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""Top-level package for Alfred."""

__author__ = """Gustavo Sampaio"""
__email__ = 'gbritosampaio@gmail.com'
__version__ = '0.1.0'

import os
import sys
import io
import string
import toml
import subprocess
from collections import defaultdict


class Alfred:
    def __init__(self, config=None, procFds=(sys.stdin, sys.stdout, sys.stderr)):
        if config is None:
            home = os.path.expanduser("~")
            self._configFile = os.path.join(home, '.alfred.toml')
        else:
            self._configFile = config
        self._loadConfig()
        self._procFds = procFds

    def _loadConfig(self):
        with io.open(self._configFile, mode='r', encoding='utf-8') as f:
            self._config = toml.load(f)
            self._config.setdefault('variables', {})

    def run(self, args):
        if len(args) >= 1 and args[0] == 'help':
            if len(args) > 1:
                return self.processHelpCommand(args)
            else:
                print 'help'
            return 0

        return self.processCommand(args)

    def _getCommand(self, args):
        if len(args) == 0:
            return 0

        cmdName = args[0]

        try:
            cmd = self._config['command'][cmdName]
        except KeyError:
            raise Exception('no command')

        cmd.setdefault('format', True)
        return cmd

    def processCommand(self, args):
        cmd = self._getCommand(args)

        self._execute(cmd, args[1:])

    def processHelpCommand(self, args):
        cmd = self._getCommand(args[1:])

        try:
            print cmd['help']
        except KeyError:
            print cmd['exec']

    def _execute(self, cmd, args):
        argsDict = defaultdict(unicode)
        for i, arg in enumerate(args):
            argsDict[i] = arg

        # variables
        for key, value in self._config['variables'].items():
            argsDict[key] = value

        argsDict['@'] = ' '.join(args)
        argsDict['#'] = len(args)
        argsDict['env'] = os.environ

        cmdLine = cmd['exec']
        if 'format' in cmd and cmd['format']:
            fmt = AlfredFormatter()
            cmdLine = fmt.format(cmdLine, argsDict)

        if 'echo' in cmd and cmd['echo']:
            print cmdLine

        process = subprocess.Popen(
            cmdLine,
            stdin=self._procFds[0],
            stdout=self._procFds[1],
            stderr=self._procFds[2],
            shell=True)
        process.communicate()
        if process.poll() is None:
            raise Exception('Error executing %r' % args)


class AlfredFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        return args[0][key]
