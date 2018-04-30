# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import keyring
import keyrings.alt


class CloudProvider(ABC):
    '''
    Defines a Cloud Provider api. All providers should extend this class
    The provider is also responsible for mapping the local file names to
    internal remote file names
    '''
    _name = ''

    def __init__(self, name):
        self.name = name

        # The pycrypto encrypted keyring asks for a password in every launch
        # if isinstance(keyring.get_keyring(), keyrings.alt.file.EncryptedKeyring):
        keyring.set_keyring(keyrings.alt.file.PlaintextKeyring())


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, n):
        self._name = n


    @abstractmethod
    def get_login_url(self, redirect_callback_url):
        '''
        Return this provider login url. Redirect callback url is provided
        to the oath to make sure alfred register the login

        @param redirect_callback_url str
        '''
        pass


    @abstractmethod
    def on_login_callback(self, data):
        '''
        Called when the user finished the login
        '''
        pass


    @abstractmethod
    def is_loggedin(self):
        '''
        Return True if this provider has a valid login state
        @return bool
        '''
        pass


    @abstractmethod
    def get_file_metadata(self, filename):
        '''
        Return the specified file metadata from the
        inner provider. The only required metadata
        to be returned is the attribute `updated` which
        is a timestamp of the last updated date time

        @param filename str The name of the file. This is the same
            as specified by the user in the assets config
        @return dict With the all the file metadata
        '''
        pass


    @abstractmethod
    def push_file(self, filename):
        '''
        Upload a file to this provider

        @param filename str The name of the file. This is the same
            as specified by the user in the assets config
        @raise CloudException
        '''
        pass


    @abstractmethod
    def get_file(self, filename):
        '''
        Download a file from this provider

        @param filename str The name of the file. This is the same
            as specified by the user in the assets config
        @raise CloudException
        '''
        pass


    def save_credentials(self, token, refreshToken):
        '''
        Utility method to save credentials in the alfred
        default keyring
        '''
        self._tokenCreation = datetime.datetime.today()
        creation = str(self._tokenCreation)

        keyring.set_password('alfredcmd', 'token', token)
        keyring.set_password('alfredcmd', 'refreshToken', refreshToken)
        keyring.set_password('alfredcmd', 'creation', creation)


    def get_credentials(self):
        '''
        Utility method to retrieve credentials from the alfred
        default keyring
        '''
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
