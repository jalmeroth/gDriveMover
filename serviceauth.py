#!/usr/bin/env python
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
    
    impersonation = True
    
    for source_user_Id in accounts:
        target_user_Id = accounts[source_user_Id]
        
        source_user = user(source_user_Id, impersonation)
        target_user = user(target_user_Id, impersonation)
        
        source_files = source_user.files
        target_files = target_user.files
        
        save(source_files.search(), DIR_CACHE + 'preflight_source_' + source_user_Id + '.json')
        save(target_files.search(), DIR_CACHE + 'preflight_target_' + target_user_Id + '.json')

if __name__ == '__main__':
    main()