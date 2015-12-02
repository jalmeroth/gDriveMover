#!/usr/bin/env python
import logging
import requests

from packages.helper import save
from packages.gDrive2 import user

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """docstring for main"""
    
    accounts = {
        'source@example.com': 'target@example.com'
    }
    
    impersonation = True
    
    for source_user_Id in accounts:
        target_user_Id = accounts[source_user_Id]
        
        source_user = user(source_user_Id, impersonation)
        target_user = user(target_user_Id, impersonation)
        
        source_files = source_user.files
        target_files = target_user.files
        
        save(source_files.search(), './Cache/preflight_source_' + source_user_Id + '.json')
        save(target_files.search(), './Cache/preflight_target_' + target_user_Id + '.json')

if __name__ == '__main__':
    main()