#!/usr/bin/python
from oauth2 import auth
from helper import load, save
from files import files
from processor2 import processor

# from auth import authorization
# from perm import permissions
# from files import files
# from fileHandler import fileHandler


# shared object for filehandling
# myFileHandler = fileHandler()

DIR_SETTINGS = "./settings/"

class user(object):
    """docstring for user"""
    def __init__(self, user_Id, impersonation = False):
        super(user, self).__init__()
        
        self.user_Id = user_Id
        self.impersonation = impersonation
        
        if self.impersonation:
            self.file_prefs = (DIR_SETTINGS + 'gDrivePro.json')
            prefs = load(self.file_prefs)
            # client_id = prefs.get('client_id', None) or raw_input('Please enter the id for your Google API client: ')
            # client_secret = prefs.get('client_secret', None) or raw_input('Please enter the secret for your Google API client: ')
            # scope = ["https://www.googleapis.com/auth/drive"]
            tokens = prefs.get('tokens')
            
            data = load(DIR_SETTINGS + 'oauth2service.json')
            private_key = data.get('private_key')
            client_email = data.get('client_email')
            scope = ['https://www.googleapis.com/auth/drive']
            self.auth = auth.ServiceAuthenticator(client_email, private_key, scope, tokens)
            
        else:
            pass
        
        self.file = files(self)
        self.proc = processor(self)
        
        # self.auth = authorization(self)
        # self.perm = permissions(self)
        # self.fileHandler = myFileHandler
        # self.processor = processor(self, myFileHandler)
        # print self.fileHandler
        
    def headers(self):
        """docstring for headers"""
        headers = {
            "Authorization": "Bearer " + str(self.auth.Bearer(self.user_Id))
        }
        save(self.auth.prefs, self.file_prefs)
        return headers
    
    @property
    def user_Id(self):
        """docstring for user_Id"""
        if self.impersonation:
            return self._user_Id
        else:
            return self._user_Id

    @user_Id.setter
    def user_Id(self, user_Id):
        """docstring for user_Id"""
        self._user_Id = user_Id

def main():
    """docstring for main"""
    pass

if __name__ == '__main__':
    main()