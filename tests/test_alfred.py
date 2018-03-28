#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""Tests for `alfred` package."""

import pytest
import os
import io

from alfredcmd import Alfred, AlfredException
from alfredcmd import cli


@pytest.fixture
def configfile(tmpdir):
    p = tmpdir.mkdir("config").join(".alfred.toml")
    p.write("""[variables]
mode='debug'
test=true
overridenKey='abc'

[function.func1]
exec="echo test1"

[command.echoAll]
exec="echo {@}"
help="This is just a test"
echo=true

[command.echoLen]
exec="echo {#} > {0}"
help="This is just a test"
echo=true

[command.echoInvert]
exec="echo {2} {1} > {0}"
help="This is just a test"
echo=true

[command.formatFalse]
exec="echo {2} {1} {0}"
help="This is just a test"
format=false

[command.echoenv]
exec="echo env: {env[ALFRED_TEST]} %userprofile% %ALFRED_TEST%"
help="This is just a test"

[command.execarg]
exec='echo dummy > {@}'

[command.v]
exec="vim"

[command.nofmt]
exec="echo 'Do not format this str: {str}"
format=false

[command.invalidKey]
exec="echo '{key}' > {@}"

[command.nammed]
exec='echo value={myKey} > {0}'

[command.over]
exec='echo value={overridenKey} > {0}'
""")
    p.check()
    return p.strpath

@pytest.fixture
def al(configfile):
    rfd, wfd = os.pipe()
    w = os.fdopen(wfd, 'w', -1)
    return Alfred(config=configfile, procFds=(None, w, w))

def test_read_config(al):
    """Test the config file parsing"""
    assert 'variables' in al._config
    assert 'test' in al._config['variables']
    assert al._config['variables']['test']

    assert 'command' in al._config
    assert len(al._config['command'].keys()) > 0

def test_exec_command_with_args(tmpdir, al):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['execarg', fname])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == 'dummy\n'

def test_formatter_all_args(al, tmpdir):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['echoAll', '1 2 3 4 5 > ' + fname])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == '1 2 3 4 5\n'

def test_formatter_len_arg(al, tmpdir):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['echoLen', fname, '1', '2', '3', '4', '5'])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == '6\n'

def test_formatter_numeric_arg(al, tmpdir):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['echoInvert', fname, 'a', 'b'])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == 'b a\n'

def test_formatter_invalid_key(al, tmpdir):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['invalidKey', fname])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == '\n'

def test_no_config_file(tmpdir):
    tmpfile = tmpdir.join('test.txt')
    al = Alfred(config=tmpfile.strpath)
    assert al._config is not None

def test_no_command(al):
    with pytest.raises(AlfredException):
        al.run(['noCmd'])

def test_nammed_key(al, tmpdir):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['nammed', fname, '--myKey=123'])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == 'value=123\n'

def test_nammed_bool_key(al, tmpdir):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['nammed', fname, '--myKey'])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == 'value=True\n'

def test_overriden_key(al, tmpdir):
    tmpfile = tmpdir.join('test.txt')
    fname = tmpfile.strpath
    al.run(['over', fname, '--overridenKey=123'])
    assert tmpfile.check()
    assert '\n'.join(tmpfile.readlines()) == 'value=123\n'

def test_load_func(al):
    assert al._config['function']['func1']

def test_execute_func(al):
    out = al.executeFunction('func1', [])
    assert out == 'test1'
