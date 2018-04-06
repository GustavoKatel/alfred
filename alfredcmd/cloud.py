import pyrebase
import getpass
import keyring
import keyrings.alt
import datetime
import os
import hashlib

from alfredcmd.alfred_exception import AlfredException

config = {
    'apiKey': 'AIzaSyDmHxXmsMsIaTj4b5GWIwBKnpV2OQY3tRg',
    'authDomain': 'alfredcmd.firebaseapp.com',
    'databaseURL': 'https://alfredcmd.firebaseio.com',
    'projectId': 'alfredcmd',
    'storageBucket': 'alfredcmd.appspot.com',
    'messagingSenderId': '67896557508',
}

class Cloud(object):

    def __init__(self):
        # The pycrypto encrypted keyring asks for a password in every launch
        if isinstance(keyring.get_keyring(), keyrings.alt.file.EncryptedKeyring):
            keyring.set_keyring(keyrings.alt.file.PlaintextKeyring())

        self._firebase = pyrebase.initialize_app(config)

        self._user = None
        self._tokenCreation = None

    def getUser(self):
        return self._user

    def getUID(self):
        if self._user is None:
            return None

        if 'users' in self._user and len(self._user['users']) > 0:
            return self._user['users'][0]['localId']

        return None

    def login(self):
        auth = self._firebase.auth()

        if self._hasCredentials():
            if self._hasValidToken():
                token = self._getCredentials()[0]
                try:
                    self._user = auth.get_account_info(token)
                except Exception as err:
                    raise self._parseException(err)
                return
            else:
                refreshToken = self._getCredentials()[1]
                cred = auth.refresh(refreshToken)
                self._user = auth.get_account_info(cred['idToken'])
                self._saveCredentials(cred['idToken'], cred['refreshToken'])
                return


        email = input('Email: ')
        password = getpass.getpass()

        if password.strip() == '':
            raise AlfredException('Password cannot be empty')

        try:
            cred = auth.sign_in_with_email_and_password(email, password)
            self._user = auth.get_account_info(cred['idToken'])
            self._saveCredentials(cred['idToken'], cred['refreshToken'])
        except Exception as e:
            raise self._parseException(e)

    def register(self):
        email = input('Email: ')
        if email.strip() == '':
            raise AlfredException('Missing email')

        password = getpass.getpass()
        confirmPassword = getpass.getpass('Confirm password:')
        if password != confirmPassword:
            raise AlfredException('Passwords do not match')
        if password.strip() == '':
            raise AlfredException('Password cannot be blank')

        auth = self._firebase.auth()
        try:
            cred = auth.create_user_with_email_and_password(email, password)
            self._user = auth.get_account_info(cred['idToken'])
        except Exception as e:
            raise self._parseException(e)

        self._saveCredentials(cred['idToken'], cred['refreshToken'])
        print('\nUser created')

    def logout(self):
        self._user = None
        self._saveCredentials('', '')

    def sync(self, config, configFile):
        self.login()

        token = self._getCredentials()[0]

        storage = self._firebase.storage()

        rootPath = '/users/'+self.getUID()

        # Upload Alfred config
        self._syncFile('alfred.toml', configFile, rootPath, storage, token)

        # sync assets
        if 'sync' in config and 'assets' in config['sync']:
            for fname in config['sync']['assets']:
                fname = os.path.expanduser(fname)
                if not os.path.exists(fname):
                    print('{} does not exist. Skipping...'.format(fname))
                elif os.path.isdir(fname):
                    self._syncPath('.', fname, rootPath+'/assets', storage, token)
                elif os.path.isfile(fname):
                    self._syncPath('.', fname, rootPath+'/assets', storage, token)


    def _syncPath(self, remotePath, absPath, rootPath, storage, token):
        for (dirpath, _, filenames) in os.walk(absPath):
            for fname in filenames:
                absFileName = os.path.join(dirpath, fname)
                self._syncFile(absFileName, absFileName, rootPath, storage, token, encodeRemotePath=True)

    def _syncFile(self, remotePath, absPath, rootPath, storage, token, encodeRemotePath=False):

        if encodeRemotePath:
            m = hashlib.sha256(bytes(remotePath, 'utf8'))
            remotePathEnc = m.hexdigest()
            remotePathEnc = remotePathEnc.replace('=', '#')
            print('sha256: '+remotePathEnc)
        else:
            remotePathEnc = remotePath

        if not os.path.exists(absPath):
            try:
                print('downloading {} to {} ...'.format(remotePath, absPath))
                storage.child(rootPath).child(remotePathEnc).get(token)
                storage.child(rootPath).child(remotePathEnc).download(absPath, token)
                return
            except Exception as e:
                raise self._parseException(e, absPath)

        try:
            print('uploading {} ...'.format(absPath))
            storage.child(rootPath).child(remotePathEnc).put(absPath, token)
        except Exception as e:
            raise self._parseException(e, remotePath)

    def _hasValidToken(self):
        creation = self._getCredentials()[2]
        delta = datetime.datetime.now() - creation

        # tokens are only valid for 1h
        return delta.total_seconds() < 3600

    def _hasCredentials(self):
        token = self._getCredentials()[0]
        return token != None and token != ''

    def _saveCredentials(self, token, refreshToken):
        self._tokenCreation = datetime.datetime.today()
        creation = str(self._tokenCreation)

        keyring.set_password('alfredcmd', 'token', token)
        keyring.set_password('alfredcmd', 'refreshToken', refreshToken)
        keyring.set_password('alfredcmd', 'creation', creation)

    def _getCredentials(self):
        token = keyring.get_password('alfredcmd', 'token')
        if token is None or token == '':
            return ('', '', '')

        refreshToken = keyring.get_password('alfredcmd', 'refreshToken')
        if refreshToken is None or refreshToken == '':
            return ('', '', '')

        creation = keyring.get_password('alfredcmd', 'creation')
        if creation is None or creation == '':
            return ('', '', '')

        creation = datetime.datetime.strptime(
            creation, "%Y-%m-%d %H:%M:%S.%f")

        return (token, refreshToken, creation)

    def _parseException(self, e, *args, **kwargs):
        if 'INVALID_EMAIL' in str(e):
            return AlfredException('Invalid email')
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
