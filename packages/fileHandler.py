#!/usr/bin/python
import os
import json
from helper import work_dir, load, save

class fileHandler(object):
	"""docstring for fileHandler"""
	def __init__(self):
		super(fileHandler, self).__init__()
		
		# define filenames
		self.file_files = 'files.json'
		self.file_folders = 'folders.json'
		self.file_copyFiles = 'copyFiles.json'
		self.file_newFiles = 'newFiles.json'
		self.file_newFolders = 'newFolders.json'

		# initialize variables
		self.files = load(self.file_files)
		self.folders = load(self.file_folders)
		self.copyFiles = load(self.file_copyFiles)
		self.newFiles = load(self.file_newFiles)
		self.newFolders = load(self.file_newFolders)

	def __del__(self):
		self.writeFilesToDisk()
	
	def writeFilesToDisk(self):
		# print 10*"=", "writeFilesToDisk"
		save(self.files, self.file_files)
		save(self.folders, self.file_folders)
		save(self.copyFiles, self.file_copyFiles)
		save(self.newFiles, self.file_newFiles)
		save(self.newFolders, self.file_newFolders)

	@property
	def files(self):
		"""docstring for files"""
		return self._files
		
	@files.setter
	def files(self, data):
		# print "Set files", data
		self._files = data
	
	@property
	def folders(self):
		"""docstring for folders"""
		return self._folders
		
	@folders.setter
	def folders(self, data):
		# print "Set folders", data
		self._folders = data
	
	@property
	def copyFiles(self):
		return self._copyFiles

	@copyFiles.setter
	def copyFiles(self, data):
		self._copyFiles = data

	@property
	def newFiles(self):
		return self._newFiles

	@newFiles.setter
	def newFiles(self, data):
		self._newFiles = data

	@property
	def newFolders(self):
		return self._newFolders

	@newFolders.setter
	def newFolders(self, data):
		# print "newFolders", data
		self._newFolders = data

def main():
	pass

if __name__ == '__main__':
	main()