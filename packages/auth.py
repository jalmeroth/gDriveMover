#!/usr/bin/python
import os
import json
import requests
import urllib
import time
from helper import work_dir

class authorization(object):
	"""docstring for authorization"""
	def __init__(self, gDriveObj):
		super(authorization, self).__init__()
		self.userId = gDriveObj.userId
		self.file_name = 'gDrive.json'
		self.prefs = self._settings
		self.beer = self.refresh()
		
	def authorize(self):
		"""docstring for authorize
		
		More info: https://developers.google.com/accounts/docs/OAuth2InstalledApp
		"""
		auth_uri = self.prefs.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth')
		
		params = {
			"scope": self.prefs.get('scope', 'https://www.googleapis.com/auth/drive'),
			"redirect_uri": self.prefs.get('redirect_uri', 'urn:ietf:wg:oauth:2.0:oob'),
			"response_type": self.prefs.get('response_type', 'code'),
			"client_id": self.prefs.get('client_id'),
			"access_type": self.prefs.get('access_type', 'offline')
		}
		
		longUri = auth_uri + "?" + urllib.urlencode(params)
		shortUri = self.shorten(longUri)

		print 10*"=", "Authorizing account:", self.userId, 10*"="
		print "Go to the following link in your browser:", shortUri if shortUri else longUri
		
		code = raw_input("Enter verification code: ")
		data = self.exchangeCode(code)

		tokens = self.prefs.get('refresh_token', {}) # all existing tokens

		# TODO: validate the account ID for this token
		tokens.update({self.userId: data.get('refresh_token')})
		
		self.prefs['refresh_token'] = tokens
		self._settings = self.prefs
		
		return data.get('access_token')
		
	def exchangeCode(self, code):
		"""docstring for exchangeCode"""
		token_uri = self.prefs.get('token_uri', 'https://accounts.google.com/o/oauth2/token')
		
		payload = {
			"code": code,
			"client_id": self.prefs.get('client_id'),
			"client_secret": self.prefs.get('client_secret'),
			"redirect_uri": self.prefs.get('redirect_uri', 'urn:ietf:wg:oauth:2.0:oob'),
			"grant_type": "authorization_code"
		}
		
		r = requests.post(token_uri, data=payload)
		
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data

	def refresh(self):
		"""docstring for refresh"""
		token_uri = self.prefs.get("token_uri", "https://accounts.google.com/o/oauth2/token")
		
		refresh_token = self.prefs.get("refresh_token")
		
		if not refresh_token:
			# need to authorize first
			return self.authorize()
		else:

			token = refresh_token.get(self.userId)

			if not token:
				# need to authorize this userId first
				return self.authorize()

			else:

				payload = {
					"refresh_token": token,
					"client_id": self.prefs.get("client_id"),
					"client_secret": self.prefs.get("client_secret"),
					"grant_type": "refresh_token"
				}
				
				r = requests.post(token_uri, data=payload)
				
				if r.status_code == requests.codes.ok:
					data = r.json()
					return data.get('access_token')

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
			data = r.json()
			# print json.dumps(data)
			return data

	def headers(self):
		"""docstring for headers"""
		headers = {
			"Authorization": "Bearer " + self.beer
		}
		return headers

	@property
	def beer(self):
		if hasattr(self, '_beerDead'):
			timeNow = int(time.time())
			if(self._beerDead > timeNow):
				# print "Giving beer"
				return self._beer
		else:
			return self.refresh()
		
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
		file = os.path.join(work_dir(), self.file_name)
		data = {}
		
		if os.path.exists(file):
			with open(file, "r") as preferences:
				data = json.load(preferences)
		else:
			print 10*"=", "Client setup", 10*"="
			
			client_id = raw_input('Please enter the id for your Google API client: ')
			client_secret = raw_input('Please enter the secret for your Google API client: ')
			
			data = {
				"access_type": "offline",
				"auth_uri": "https://accounts.google.com/o/oauth2/auth",
				"client_id": client_id,
				"client_secret": client_secret,
				"redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
				"refresh_token": {},
				"response_type": "code",
				"scope": "https://www.googleapis.com/auth/drive",
				"token_info": "https://www.googleapis.com/oauth2/v1/tokeninfo",
				"token_uri": "https://accounts.google.com/o/oauth2/token"
			}
			
			self._settings = data
		
		return data
	
	@_settings.setter
	def _settings(self, prefs):
		"""docstring for _settings"""
		with open(work_dir() + os.sep + self.file_name, 'w+') as preferences:
			json.dump(prefs, preferences)
	
	def shorten(self, longUrl):
		"""Find documentation here: https://developers.google.com/url-shortener/v1/getting_started#shorten"""
		
		uri = 'https://www.googleapis.com/urlshortener/v1/url'
		
		headers = {
			'Content-Type': 'application/json'
		}
		
		payload = {
			'longUrl': longUrl
		}
		
		r = requests.post(uri, headers=headers, data=json.dumps(payload))
		data = r.json()
		
		return data.get('id')

def main():
	"""docstring for main"""
	pass

if __name__ == '__main__':
	main()