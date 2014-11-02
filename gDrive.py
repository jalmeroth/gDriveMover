#!/usr/bin/python
import os
import json
import requests
import urllib


class gDrive(object):
	"""docstring for gDrive"""
	def __init__(self, user_id):
		super(gDrive, self).__init__()
		self.user_id = user_id
		self.file_name = 'gDrive.json'
		self.prefs = self._settings
		self.bear = self.refresh()
	
	def authorize(self):
		"""docstring for authorize"""
		auth_uri = self.prefs.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth')
		
		params = {
			"scope": self.prefs.get('scope', 'https://www.googleapis.com/auth/drive'),
			"redirect_uri": self.prefs.get('redirect_uri', 'urn:ietf:wg:oauth:2.0:oob'),
			"response_type": self.prefs.get('response_type', 'code'),
			"client_id": self.prefs.get('client_id', None),
			"access_type": self.prefs.get('access_type', 'offline')
		}
		
		print 10*"=", "Authorizing account:", self.user_id, 10*"="
		print "Go to the following link in your browser:"
		print auth_uri + "?" + urllib.urlencode(params)
		
		code = raw_input("Enter verification code: ")
		data = self.exchangeCode(code)
		
		# print "access_token", data.get('access_token', None)
		# print "refresh_token", data.get('refresh_token', None)

		tokens = self.prefs.get('refresh_token', {}) # all existing tokens
		tokens.update({self.user_id: data.get('refresh_token', None)})
		
		self.prefs['refresh_token'] = tokens
		self._settings = self.prefs
		
		return data.get('access_token', None)
		
	def exchangeCode(self, code):
		"""docstring for exchangeCode"""
		token_uri = self.prefs.get('token_uri', 'https://accounts.google.com/o/oauth2/token')
		
		payload = {
			"code": code,
			"client_id": self.prefs.get('client_id', None),
			"client_secret": self.prefs.get('client_secret', None),
			"redirect_uri": self.prefs.get('redirect_uri', 'urn:ietf:wg:oauth:2.0:oob'),
			"grant_type": "authorization_code"
		}
		
		r = requests.post(token_uri, data=payload)
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data
		else:
			r.raise_for_status()

	def refresh(self):
		"""docstring for refresh"""
		token_uri = self.prefs.get("token_uri", "https://accounts.google.com/o/oauth2/token")
		
		refresh_token = self.prefs.get("refresh_token", None)
		
		if refresh_token:
			token = refresh_token.get(self.user_id)
		else:
			return self.authorize()
		
		payload = {
			"refresh_token": token,
			"client_id": self.prefs.get("client_id", None),
			"client_secret": self.prefs.get("client_secret", None),
			"grant_type": "refresh_token"
		}
		
		r = requests.post(token_uri, data=payload)
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data.get('access_token', None)
		else:
			return self.authorize()

	@property
	def _settings(self):
		"""docstring for _settings"""
		file = os.path.join(_work_dir(), self.file_name)
		data = {}
		
		if os.path.exists(file):
			with open(file, "r") as preferences:
				data = json.load(preferences)
		
		return data
	
	@_settings.setter
	def _settings(self, prefs):
		"""docstring for _settings"""
		with open(_work_dir() + os.sep + self.file_name, 'w+') as preferences:
			json.dump(prefs, preferences)
	
	def searchFiles(self, corpus="DEFAULT", token = None, q = None, fields = None):
		"""docstring for searchFiles"""
		
		if token:
			print token
		
		if q == None:
			# q = "mimeType != 'application/vnd.google-apps.folder' AND trashed != true"
			q = "mimeType != 'application/vnd.google-apps.folder' AND trashed != true"
			
		if fields == None:
			fields = "items(id,parents(id,isRoot),title),nextPageToken"
			
		url = 'https://www.googleapis.com/drive/v2/files'
		
		if not self.bear:
			self.bear = self.refresh()

		# print "Bear:", self.bear
	
		headers = {
			"Authorization": "Bearer " + self.bear
		}
	
		# "corpus": corpus,
		params = {
			"pageToken": token,
			"q": q,
			"fields": fields
		}

		r = requests.get(url, headers=headers, params=params)
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data
		else:
			r.raise_for_status()
		
	def retrieve_all_files(self):
		"""docstring for retrieve_all_files"""
		
		token = None
		result = []
		
		while True:
			
			data = self.searchFiles(token=token)
			
			token = data.get('nextPageToken', None)
			# print "Token", token
			
			items = data.get('items', [])
			# print "Found", len(items), "items"
			
			result.extend(items)
			
			if not token:
				break
		
		return result

	def searchFolders(self, token = None, q = None):
		"""docstring for searchFolder"""
		
		if token:
			print token
		
		if q == None:
			q = "mimeType = 'application/vnd.google-apps.folder' AND trashed != true"
		
		return self.searchFiles(q=q, token=token)
	
	def retrieve_all_folders(self):
		"""docstring for retrieve_all_folders"""
		
		token = None
		result = []
		
		while True:
			
			data = self.searchFolders(token=token)
			
			token = data.get('nextPageToken', None)
			# print "Token", token
			
			items = data.get('items', [])
			# print "Found", len(items), "items"
			
			result.extend(items)
			
			if not token:
				break
		
		return result

	def fileGet(self, fileId, fields = None):
		"""docstring for fileGet"""
		
		url = 'https://www.googleapis.com/drive/v2/files/' + fileId
		
		if not self.bear:
			self.bear = self.refresh()

		headers = {
			"Authorization": "Bearer " + self.bear
		}
	
		params = {
			"fileId": fileId,
			"fields": fields
		}

		r = requests.get(url, headers=headers, params=params)
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data
		else:
			r.raise_for_status()
			
	def getName(self, fileId):
		"""docstring for getName"""
		return self.fileGet(fileId, 'title').get('title', None)

	def makeCopy(self, fileId, title = None, parents = [], fields = None):
		"""docstring for makeCopy"""
		
		if title == None:
			title = self.getName(fileId)

		if fields == None:
			fields = "id,parents(id,isRoot),title"

		params = {
			"visibility": "PRIVATE",
			"fields": fields
		}
		
		url = "https://www.googleapis.com/drive/v2/files/" + fileId + "/copy?" + urllib.urlencode(params)
		# print url
		
		if not self.bear:
			self.bear = self.refresh()
		# else:
		# 	print "Bear:", self.bear
	
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer " + self.bear
		}
		# print headers

		payload = {
			"title": title,
			"parents": parents
		}
		# print payload
		
		r = requests.post(url, headers=headers, data=json.dumps(payload))
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data
		else:
			if r.status_code == 401:
				print "Refreshing token..."
				self.bear = self.refresh()
			print r.status_code, r.text
			r.raise_for_status()
			
	def updateFile(self, fileId, addParents, removeParents, fields = None):
		"""docstring for updateFile"""

		if fields == None:
			fields = "id,parents(id,isRoot),title"
		
		url = 'https://www.googleapis.com/drive/v2/files/' + fileId
		
		if not self.bear:
			self.bear = self.refresh()

		headers = {
			"Authorization": "Bearer " + self.bear
		}
	
		params = {
			"addParents": ",".join(addParents),
			"removeParents": ",".join(removeParents),
			"fields": fields
		}

		r = requests.put(url, headers=headers, params=params)
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data
		else:
			r.raise_for_status()

	def insertFile(self, title = "Untitled", parents = [], fType = None, fields = None):
		"""docstring for insertFile"""
		
		if fType == None:
			fType = "application/vnd.google-apps.folder"
			
		if fields == None:
			fields = "id,parents(id,isRoot),title"
		
		params = {
			"fields": fields
		}
		
		url = "https://www.googleapis.com/drive/v2/files?" + urllib.urlencode(params)
		# print url
		
		if not self.bear:
			self.bear = self.refresh()

		# print "Bear:", self.bear
	
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer " + self.bear
		}
		# print headers

		payload = {
		  "title": title,
		  "parents": parents,
		  "mimeType": fType
		}
		# print payload
		
		r = requests.post(url, headers=headers, data=json.dumps(payload))
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data
		else:
			r.raise_for_status()

def _work_dir():
	"""docstring for _work_dir"""
	return os.path.dirname(os.path.realpath(__file__))

def main():
	"""docstring for main"""
	pass

if __name__ == '__main__':
	main()