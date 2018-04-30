# -*- coding: utf-8 -*-
from alfredcmd.cloud import CloudProvider, CloudException
from alfredcmd import AlfredException
import os
from dropbox.exceptions import ApiError, AuthError
import dropbox
from dropbox.files import WriteMode


class CloudProviderDropbox(CloudProvider):
    def __init__(self, config):
        super().__init__('dropbox', config)

        env_name = 'AL_DROPBOX_ACCESS_TOKEN'
        if 'dropbox' in config and 'access_token_env_name' in config['dropbox']:
            env_name = config['dropbox'].get('access_token_env_name', 'AL_DROPBOX_ACCESS_TOKEN')

        self._token = os.environ.get(env_name, None)
        if self._token is None:
            raise AlfredException('Please set Dropbox token in the environment variable {}'.format(env_name))

        self._dbx = dropbox.Dropbox(self._token)

        # # Check that the access token is valid
        # try:
        #     self._dbx.users_get_current_account()
        # except AuthError as err:
        #     raise CloudException('Invalid Dropbox Token')


    def is_loggedin(self):
        '''
        Return True if this provider has a valid login state
        @return bool
        '''
        return self._token is not None


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
        return {}


    def push_file(self, filename):
        '''
        Upload a file to this provider

        @param filename str The name of the file. This is the same
            as specified by the user in the assets config
        @raise CloudException
        '''
        pass


    def get_file(self, filename):
        '''
        Download a file from this provider

        @param filename str The name of the file. This is the same
            as specified by the user in the assets config
        @raise CloudException
        '''
        pass
