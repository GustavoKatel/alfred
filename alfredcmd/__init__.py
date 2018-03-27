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
        if len(args) >= 1:
            if args[0] == '@help':
                if len(args) > 1:
                    return self.processHelpCommand(args)
                else:
                    print('help')
                return 0
            elif args[0] == '@list':
                self.listCommands()
                return 0

        return self.processCommand(args)

    def listCommands(self):
        cmds = self._config['command']

        for cmdName in cmds.iterkeys():
            cmd = self._getCommand(cmdName)
            print('$ al '+cmdName)
            print('> {}'.format(cmd['exec']))
            if 'help' in cmd:
                print('\t'.format(cmd['help']))
            print('\tformat: {}'.format(cmd['format']))
            print('\ttype: {}'.format(cmd['type']))
            print('\techo: {}'.format(cmd['echo']))
            print('')

    def _getCommand(self, cmdName):
        try:
            cmd = self._config['command'][cmdName]
        except KeyError:
            raise Exception('no command')

        cmd.setdefault('format', True)
        cmd.setdefault('type', 'shell')
        cmd.setdefault('echo', False)
        return cmd

    def processCommand(self, args):
        cmd = self._getCommand(args[0])

        if cmd['type'] == 'shell':
            self._executeShell(cmd, args[1:])
        elif cmd['type'] == 'python':
            self._executePy(cmd, args[1:])
        else:
            raise Exception('Invalid command type: {}'.format(cmd['type']))

    def processHelpCommand(self, args):
        cmd = self._getCommand(args[0])

        try:
            print(cmd['help'])
        except KeyError:
            print(cmd['exec'])

    def _buildArgDict(self, args):
        argsDict = defaultdict(unicode)
        for i, arg in enumerate(args):
            argsDict[i] = arg

        # variables
        for key, value in self._config['variables'].items():
            argsDict[key] = value

        argsDict['@'] = ' '.join(args)
        argsDict['#'] = len(args)
        argsDict['env'] = os.environ

        return argsDict

    def _executePy(self, cmd, args):
        if 'type' in cmd and not cmd['type'] == 'python':
            raise Exception('Invalid command type. Expected "python" Received: {}'.format(cmd['type']))

        argsDict = self._buildArgDict(args)

        cmdLine = cmd['exec']
        try:
            filename, funcname = cmdLine.split('::')
        except ValueError:
            raise Exception('Invalid execution of python script "{}". Please use the format: "script.py::FuncName"'.format(cmdLine))

        filename = os.path.expanduser(filename)
        import module_importer
        module = module_importer.importModuleFromFile('script', filename)
        if not hasattr(module, funcname):
            raise Exception('Function "{}" was not found in module "{}"'.format(funcname, filename))

        try:
            func = getattr(module, funcname)
            func(argsDict)
        except Exception as e:
            raise Exception('Error trying to execute module', e)


    def _executeShell(self, cmd, args):
        if 'type' in cmd and not cmd['type'] == 'shell':
            raise Exception('Invalid command type. Expected "shell" Received: {}'.format(cmd['type']))

        argsDict = self._buildArgDict(args)

        cmdLine = cmd['exec']
        if 'format' in cmd and cmd['format']:
            fmt = AlfredFormatter()
            cmdLine = fmt.format(cmdLine, argsDict)

        if 'echo' in cmd and cmd['echo']:
            print('> {}'.format(cmdLine))

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