# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""Top-level package for Alfred."""

__author__ = """Gustavo Sampaio"""
__email__ = 'gbritosampaio@gmail.com'
__version__ = '0.1.7'

import os
import sys
import io
import string
import toml
import subprocess
import re
from collections import defaultdict

class AlfredException(Exception):
    pass

class Alfred:
    def __init__(self, config=None, procFds=(sys.stdin, sys.stdout, sys.stderr)):
        if config is None:
            home = os.path.expanduser("~")
            self._configFile = os.path.join(home, '.alfred', 'alfred.toml')
        else:
            self._configFile = config
        self._loadConfig()
        self._procFds = procFds

        self._defaultShellExecutor = 'bash'

    def _loadConfig(self):
        try:
            with io.open(self._configFile, mode='r', encoding='utf-8') as f:
                self._config = toml.load(f)
        except IOError as e:
            # config file not found. Use defaults
            self._config = dict()
        except toml.TomlDecodeError as e:
            raise AlfredException('invalid config file')
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
            elif args[0] == '@version':
                print('v{}'.format(__version__))
                return 0

        return self.processCommand(args)

    def listCommands(self):
        cmds = self._config['command']

        for cmdName in cmds.keys():
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
            raise AlfredException('no command "{}"\n\nYou can create it in ~/.alfred/alfred.toml'.format(cmdName))

        cmd.setdefault('format', True)
        cmd.setdefault('type', 'shell')
        cmd.setdefault('echo', False)
        return cmd

    def _getFunction(self, funcName):
        try:
            func = self._config['function'][funcName]
        except KeyError:
            raise AlfredException('no function "{}"\n\nYou can create it in ~/.alfred/alfred.toml'.format(funcName))

        func.setdefault('format', True)
        func.setdefault('type', 'shell')
        func.setdefault('echo', False)
        return func

    def processCommand(self, args):
        cmd = self._getCommand(args[0])

        if cmd['type'] == 'shell':
            self._executeShell(cmd, args[1:])
        elif cmd['type'] == 'python':
            self._executePy(cmd, args[1:])
        else:
            raise AlfredException('Invalid command type: {}'.format(cmd['type']))

    def processHelpCommand(self, args):
        cmd = self._getCommand(args[0])

        try:
            print(cmd['help'])
        except KeyError:
            print(cmd['exec'])

    def _buildArgDict(self, args):
        argsDict = defaultdict(str)
        # variables
        for key, value in self._config['variables'].items():
            argsDict[key] = value

        positionalIndex = 0
        for i, arg in enumerate(args):

            if arg.startswith('--'):
                # Make sure we have a key
                if len(arg) > 2:
                    pack = arg[2:].split('=')
                    if len(pack) == 1:
                        # No value associated. Assume this is a bool
                        argsDict[pack[0]] = True
                    else:
                        # Key/value pair
                        argsDict[pack[0]] = pack[1]
            else:
                argsDict[positionalIndex] = arg
                positionalIndex += 1

        argsDict['@'] = ' '.join(args)
        argsDict['#'] = len(args)
        argsDict['env'] = os.environ

        return argsDict

    def _executePy(self, cmd, args):
        if 'type' in cmd and not cmd['type'] == 'python':
            raise AlfredException('Invalid command type. Expected "python" Received: {}'.format(cmd['type']))

        argsDict = self._buildArgDict(args)

        cmdLine = cmd['exec']
        try:
            filename, funcname = cmdLine.split('::')
        except ValueError:
            raise AlfredException('Invalid execution of python script "{}". Please use the format: "script.py::FuncName"'.format(cmdLine))

        filename = os.path.expanduser(filename)
        import module_importer
        module = module_importer.importModuleFromFile('script', filename)
        if not hasattr(module, funcname):
            raise AlfredException('Function "{}" was not found in module "{}"'.format(funcname, filename))

        try:
            func = getattr(module, funcname)
            func(argsDict)
        except Exception as e:
            raise AlfredException('Error trying to execute module', e)

    def _executeShell(self, cmd, args):
        if 'type' in cmd and not cmd['type'] == 'shell':
            raise AlfredException('Invalid command type. Expected "shell" Received: {}'.format(cmd['type']))

        argsDict = self._buildArgDict(args)

        cmdLine = cmd['exec']
        if 'format' in cmd and cmd['format']:
            fmt = AlfredFormatter(self)
            cmdLine = fmt.format(cmdLine, argsDict)

        if 'echo' in cmd and cmd['echo']:
            print('> {}'.format(cmdLine))

        if cmdLine.count('\n') > 0:
            import tempfile
            fhos, scriptfile = tempfile.mkstemp(prefix='alfred-tmp-')
            with io.open(fhos, mode='w') as fh:
                fh.write(cmdLine)
            cmdLine = '{} {}'.format(self._defaultShellExecutor, scriptfile)

        self._spawnShell(cmdLine)

    def _spawnShell(self, cmdLine, pipeStdout=False):
        if pipeStdout == True:
            stdout = subprocess.PIPE
        else:
            stdout = self._procFds[1]

        process = subprocess.run(
            cmdLine,
            stdin=self._procFds[0],
            stdout=stdout,
            stderr=self._procFds[2],
            shell=True)

        if pipeStdout == True:
            out = str(process.stdout, 'utf-8')
        else:
            out = None

        return out

    def executeFunction(self, funcName, args):
        rfd, wfd = os.pipe()
        func = self._getFunction(funcName)
        out = self._spawnShell(func['exec'], pipeStdout=True)
        # remove trailing line-break
        out = out[:-1]
        return out

class AlfredFormatter(string.Formatter):
    def __init__(self, alfred):
        self.alfred = alfred

    def get_value(self, key, args, kwargs):
        # function
        if isinstance(key, str):
            match = re.match('(\w+)\((.*)\)', key)
            if match is not None:
                funcArgs = match.group(2).split(',')
                return self.alfred.executeFunction(match.group(1), funcArgs)
        return args[0][key]
