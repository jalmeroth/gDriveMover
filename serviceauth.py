#!/usr/bin/env python
import json
import logging

from packages.helper import load, save
from packages.gDrive2 import user

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DIR_SETTINGS = "./settings/"
DIR_CACHE = "./cache/"

def main():
    """docstring for main"""
    
    accounts = load(DIR_SETTINGS + 'accounts.json')
    
    refresh = True
    impersonation = True
    
    for source_user_Id in accounts:
        target_user_Id = accounts[source_user_Id]

        source_user = user(source_user_Id, impersonation)
        target_user = user(target_user_Id, impersonation)
        
        if refresh:
            source_files = source_user.file.search()
            target_files = target_user.file.search()

            save(source_files, DIR_CACHE + 'preflight_source_' + source_user_Id + '.json')
            save(target_files, DIR_CACHE + 'preflight_target_' + target_user_Id + '.json')
        else:
            source_files = load(DIR_CACHE + 'preflight_source_' + source_user_Id + '.json')
            target_files = load(DIR_CACHE + 'preflight_target_' + target_user_Id + '.json')
    
        files, folders = source_user.proc.processFilesFolders(source_files)
        print json.dumps(files)
        print json.dumps(folders)

if __name__ == '__main__':
    main()