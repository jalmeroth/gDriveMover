#!/usr/bin/python
import os
import json
import requests
import urllib
import Queue
import time
from urlRequest import URLRequestThread


class permissions(object):
	"""docstring for permissions"""
	def __init__(self, gDriveObj):
		super(permissions, self).__init__()
		self.auth = gDriveObj.auth
		self.fields = 'id,role,type'
	
	def update(self, fileId, permissionId, **kwargs):
		"""docstring for insert"""
		params = {
			'transferOwnership': kwargs.get('sendNotificationEmails', False),
			'fields': kwargs.get('fields', self.fields)
		}
		
		headers = {
			"Content-Type": "application/json",
		}
		
		headers.update(self.auth.headers())
		
		payload = {
			'role': kwargs.get('role')
		}
		
		# fileId = kwargs.get('fileId')
		url = 'https://www.googleapis.com/drive/v2/files/' + fileId + '/permissions/' + permissionId + '?' + urllib.urlencode(params)
		
		r = requests.put(url, headers=headers, data=json.dumps(payload))
		
		data = r.json()
		return data
	
	def insert(self, fileId, **kwargs):
		"""docstring for insert"""
		params = {
			'emailMessage': kwargs.get('emailMessage'),
			'sendNotificationEmails': kwargs.get('sendNotificationEmails', False),
			'fields': kwargs.get('fields', self.fields)
		}
		
		headers = {
			"Content-Type": "application/json",
		}
		
		headers.update(self.auth.headers())
		
		payload = {
			'role': kwargs.get('role'),
			'type': kwargs.get('type'),
			'id': kwargs.get('id')
		}
		
		# fileId = kwargs.get('fileId')
		url = 'https://www.googleapis.com/drive/v2/files/' + fileId + '/permissions?' + urllib.urlencode(params)
		
		r = requests.post(url, headers=headers, data=json.dumps(payload))
		
		data = r.json()
		return data
	
	def getIdForEmail(self, email):
		"""docstring for getIdForEmail"""
		url = 'https://www.googleapis.com/drive/v2/permissionIds/' + email
		
		r = requests.get(url, headers=self.auth.headers())
		
		data = r.json()
		return data.get('id')
		
	def get(self, fileId, permissionId):
		"""docstring for get"""
		url = 'https://www.googleapis.com/drive/v2/files/' + fileId + '/permissions/' + permissionId
		
		r = requests.get(url, headers=self.auth.headers())
		
		data = r.json()
		return data

def main():
	"""docstring for main"""
	pass

if __name__ == '__main__':
	main()