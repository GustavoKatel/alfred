# -*- coding: utf-8 -*-
from alfredcmd.cloud import CloudProvider


class CloudProviderDropbox(CloudProvider):
    def __init__(self):
        super().__init__('dropbox')

    def get_login_url(self, redirect_callback_url):
        '''
        Return this provider login url. Redirect callback url is provided
        to the oath to make sure alfred register the login

        @param redirect_callback_url str
        '''
        return 'dropbox.com/?callback={}'.format(redirect_callback_url)


    def on_login_callback(self, data):
        '''
        Called when the user finished the login
        '''
        pass


    def is_loggedin(self):
        '''
        Return True if this provider has a valid login state
        @return bool
        '''
        return True


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
