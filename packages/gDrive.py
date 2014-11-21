#!/usr/bin/python
from auth import authorization
from perm import permissions
from files import files
from fileHandler import fileHandler
from processor import processor


# shared object for filehandling
myFileHandler = fileHandler()

class gDrive(object):
	"""docstring for gDrive"""
	def __init__(self, userId):
		super(gDrive, self).__init__()
		
		self.userId = userId
		
		self.auth = authorization(self)
		self.perm = permissions(self)
		self.file = files(self)

		self.fileHandler = myFileHandler
		self.processor = processor(self, myFileHandler)
		# print self.fileHandler

def main():
	"""docstring for main"""
	pass

if __name__ == '__main__':
	main()