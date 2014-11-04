#!/usr/bin/python
import os
import json
import requests
import urllib
import Queue
import time
from urlRequest import URLRequestThread

class gDrive(object):
	"""docstring for gDrive"""
	def __init__(self, user_id):
		super(gDrive, self).__init__()
		self.user_id = user_id
		self.file_name = 'gDrive.json'
		self.prefs = self._settings
		self.beer = self.refresh()
	
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
			
	def tokenInfo(self, token):
		"""docstring for tokenInfo"""
		token_info = self.prefs.get("token_info", "https://www.googleapis.com/oauth2/v1/tokeninfo")
		
		params = {
			"access_token": token
		}
		
		r = requests.get(token_info, params=params)
		
		if r.status_code == requests.codes.ok:
			return r.json()

	@property
	def beer(self):
		if hasattr(self, '_beerDead'):
			timeNow = int(time.time())
			if(self._beerDead > timeNow):
				# print "Giving beer"
				return self._beer
		
	@beer.setter
	def beer(self, token):
		# print "Receiving beer"
		self._beer = token
		fiveMin = 5 * 60
		expires_in = int(self.tokenInfo(token).get('expires_in'))
		timeNow = int(time.time())
		self._beerDead = timeNow + expires_in - fiveMin
		# print self._beerDead

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
	
	def searchFiles(self, token = None, q = None, fields = None):
		"""docstring for searchFiles"""
		
		maxResults = 1000
		
		if token:
			print "Fetching next", maxResults, "items with token", token
		
		if q == None:
			q = "mimeType != 'application/vnd.google-apps.folder' AND trashed != true"
			
		if fields == None:
			fields = "items(id,parents(id,isRoot),title),nextPageToken"
			
		url = 'https://www.googleapis.com/drive/v2/files'
		
		if not self.beer:
			self.beer = self.refresh()

		# print "beer:", self.beer
	
		headers = {
			"Authorization": "Bearer " + self.beer
		}
	
		params = {
			"pageToken": token,
			"q": q,
			"maxResults": maxResults,
			"fields": fields
		}

		r = requests.get(url, headers=headers, params=params)
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data
		else:
			r.raise_for_status()
		
	def retrieve_all_files(self, q = None):
		"""docstring for retrieve_all_files"""
		
		token = None
		result = []
		
		while True:
			
			data = self.searchFiles(token=token, q = q)
			
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
		
		return self.searchFiles(token=token, q=q)
	
	def retrieve_all_folders(self, q = None):
		"""docstring for retrieve_all_folders"""
		
		token = None
		result = []
		
		while True:
			
			data = self.searchFolders(token=token, q=q)
			
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
		
		if not self.beer:
			self.beer = self.refresh()

		headers = {
			"Authorization": "Bearer " + self.beer
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

	def makeCopy(self, items, fields = None):
		"""docstring for makeCopy"""
		
		if fields == None:
			fields = "id,parents(id,isRoot),title"
		
		if not self.beer:
			self.beer = self.refresh()
		
		params = {
			"fields": fields
		}
		
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer " + self.beer
		}
		# print headers
		threads = []
		q = Queue.Queue()
		
		for item in items:
			# print item
			fileId = item.get('fileId')
			newFileId = item.get('newFileId')
			
			if newFileId:
				copyId = newFileId
			else:
				copyId = fileId
			
			title = item.get('title')
			parents = item.get('parents', [])
			
			payload = {
				"title": title,
				"parents": parents
			}
			# print payload
			
			url = "https://www.googleapis.com/drive/v2/files/" + copyId + "/copy?" + urllib.urlencode(params)
			# print url
		
			new_thread = URLRequestThread(
				q,
				"POST",
				url,
				headers=headers,
				data=json.dumps(payload)
			)
			
			new_thread.setName(fileId)
			threads.append(new_thread)
			new_thread.start()

		for t in threads:
			t.join()
		
		result = {}
		
		while not q.empty():
			
			index, data = q.get()
			result[index] = data
				
		return result

	def updateFiles(self, items, fields = None):
		"""docstring for updateFiles"""
		if fields == None:
			fields = "id,parents(id,isRoot),title"
		
		if not self.beer:
			self.beer = self.refresh()

		headers = {
			"Authorization": "Bearer " + self.beer
		}
	
		threads = []
		q = Queue.Queue()
		
		for item in items:
			# print item
			folderId = item.get('folderId')
			newFolderId = item.get('newFolderId')
			addParents = item.get('addParents', [])
			removeParents = item.get('removeParents', [])
			
			params = {
				"addParents": ",".join(addParents),
				"removeParents": ",".join(removeParents),
				"fields": fields
			}
			# print newFolderId
			url = 'https://www.googleapis.com/drive/v2/files/' + newFolderId
			
			new_thread = URLRequestThread(
				q,
				"PUT",
				url,
				headers=headers,
				params=params
			)
			
			new_thread.setName(folderId)
			threads.append(new_thread)
			new_thread.start()

		for t in threads:
			t.join()
		
		result = {}
		
		while not q.empty():
			
			index, data = q.get()
			result[index] = data
				
		return result

	def insertFiles(self, items, fields = None):
		"""docstring for insertFiles"""
		
		if fields == None:
			fields = "id,parents(id,isRoot),title"
		
		params = {
			"fields": fields
		}

		url = "https://www.googleapis.com/drive/v2/files?" + urllib.urlencode(params)
		# print url

		if not self.beer:
			self.beer = self.refresh()

		# print "beer:", self.beer

		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer " + self.beer
		}
		# print headers

		threads = []
		q = Queue.Queue()
		
		for item in items:
			itemId = item.get('id')
			title = item.get('title', 'Untitled')
			parents = item.get('parents', [])
			mimeType = item.get('mimeType', 'application/vnd.google-apps.folder')
	
			payload = {
				"title": title,
				"parents": parents,
				"mimeType": mimeType
			}
			# print payload
	
			new_thread = URLRequestThread(
				q,
				"POST",
				url,
				headers=headers,
				data=json.dumps(payload)
			)

			new_thread.setName(itemId)
			threads.append(new_thread)
			new_thread.start()

		for t in threads:
			t.join()
		
		result = {}
		
		while not q.empty():
			
			index, data = q.get()
			result[index] = data
				
		return result

def _work_dir():
	"""docstring for _work_dir"""
	return os.path.dirname(os.path.realpath(__file__))

def main():
	"""docstring for main"""
	pass

if __name__ == '__main__':
	main()