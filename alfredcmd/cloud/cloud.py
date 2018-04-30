# -*- coding: utf-8 -*-
import pyrebase
import datetime
import os
import hashlib
import tempfile

from alfredcmd.alfred_exception import AlfredException

firebase_config = {
    'apiKey': 'AIzaSyDmHxXmsMsIaTj4b5GWIwBKnpV2OQY3tRg',
    'authDomain': 'alfredcmd.firebaseapp.com',
    'databaseURL': 'https://alfredcmd.firebaseio.com',
    'projectId': 'alfredcmd',
    'storageBucket': 'alfredcmd.appspot.com',
    'messagingSenderId': '67896557508',
}

class Cloud(object):

    def __init__(self, config):
        self._config = config

        self._firebase = pyrebase.initialize_app(firebase_config)

        # self._tempDir = tempfile.TemporaryDirectory()
        self._tempDir = tempfile.mkdtemp()

        if 'sync' in self._config:
            provider_name = self._config['sync'].get('provider', 'dropbox')

            if provider_name == 'dropbox':
                from alfredcmd.cloud.providers import CloudProviderDropbox
                self._provider = CloudProviderDropbox()
            else:
                self._provider = None


    def login(self):
        if self._provider is None:
            raise AlfredException('No provider specified')

        login_url = self._provider.get_login_url('CALLBACK')
        print(login_url)


    def sync(self, configFile):
        if self._provider is None:
            raise AlfredException('No provider specified')

        print('Using provider: {}'.format(self._provider.name))

        if not self._provider.is_loggedin():
            raise AlfredException('Not logged in. Please @login')

        # Upload Alfred config
        self._sync_file('alfred.toml', configFile)

        # sync assets
        if 'sync' in self._config and 'assets' in self._config['sync']:
            print('syncing assets...')
            for fname in self._config['sync']['assets']:
                abs_name = os.path.expanduser(fname)

                if not os.path.exists(abs_name):
                    print('{} does not exist. Skipping...'.format(fname))

                elif os.path.isdir(abs_name):
                    self._sync_dir(abs_name)

                else:
                    self._sync_file(fname, abs_name)


    def _sync_dir(self, path):
        for root, dirs, files in os.walk(path):
            for fname in files:
                self._sync_file(fname, os.path.join(root, fname))


    def _sync_file(self, filename, abs_name):
        print('Syncing {} ({})...'.format(filename, abs_name))


    def _md5FromFile(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


    def _parseException(self, e, *args, **kwargs):
        if 'INVALID_EMAIL' in str(e):
            return AlfredException('Invalid email')
        if 'INVALID_PASSWORD' in str(e):
            return AlfredException('Invalid password')
        elif 'MISSING_EMAIL' in str(e):
            return AlfredException('Missing email')
        elif 'EMAIL_NOT_FOUND' in str(e):
            return AlfredException('Email not found')
        elif 'MISSING_PASSWORD' in str(e):
            return AlfredException('Password cannot be blank')
        elif 'WEAK_PASSWORD' in str(e):
            return AlfredException('Weak password. Password should be at least 6 characters')
        elif 'USER_NOT_FOUND' in str(e):
            return AlfredException('Invalid credentials. Please logout')
        elif 'Not Found.  Could not get object' in str(e):
            fname = ''
            if len(args) > 0:
                fname = ' "{}"'.format(args[0])
            return AlfredException('Could not locate remote file' + fname)
        else:
            return AlfredException(e)
