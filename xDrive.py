#!/usr/bin/python
import os
import json


class xDrive(object):
	"""docstring for xDrive"""
	def __init__(self, source = None, sourceFolder = None, target = None, targetFolder = None):
		super(xDrive, self).__init__()
		self.source = source
		self.sourceFolder = sourceFolder
		self.target = target
		self.targetFolder = targetFolder
	
	def save(self, data, filename):
		"""docstring for save"""
		file = os.path.join(_work_dir(), filename)
		with open(file, "w+") as jsonFile:
			json.dump(data, jsonFile)
	
	def load(self, filename):
		"""docstring for load"""
		file = os.path.join(_work_dir(), filename)
		with open(file,"r") as jsonFile:
			return json.load(jsonFile)
	
	def listFilesFolders(self):
		"""docstring for listFilesFolders"""
		
		print 10*"=", "listFilesFolders"
		
		folders = self.folders()
		files = self.files()
		
		# print len(folders), len(files)
		
		everything = self.everything()

		for folder in folders:
			folderId = folder['id']
			if not everything.has_key(folderId):
				everything[folderId] = folder

		self.save(everything, 'xDrive_all.json')

		fields = "id,parents(id,isRoot),title"

		for folder in folders:
			for parent in folder['parents']:
				parentId = parent.get('id')
				if not everything.has_key(parentId):
					# print "Trying to looking up extra info:", parentId
					try:
						parentItem = self.source.fileGet(parentId, fields=fields)
					except:
						parentItem = {
							"id": parentId,
							"parents": [],
							"title": parentId
						}
					everything[parentId] = parentItem

		self.save(everything, 'xDrive_all.json')
		# print "Folders from Folders", len(everything)

		fields = "id,title"
		for file in files:
			for parent in file['parents']:
				parentId = parent.get('id')
				if not everything.has_key(parentId):
					# print "Trying to looking up extra info:", parentId
					try:
						parentItem = self.source.fileGet(parentId, fields=fields)
					except:
						parentItem = {
							"id": parentId,
							"title": parentId
						}
					everything[parentId] = parentItem
					# ignore parents of parents of public files
					everything[parentId]['parents'] = []

		self.save(everything, 'xDrive_all.json')
		# print "Need to create", len(everything), "folders at all."

	def everything(self):
		"""docstring for everything"""
		filename = 'xDrive_all.json'
		file = os.path.join(_work_dir(), filename)

		if os.path.exists(file):
			return self.load(filename)
		else:
			return {}
		
	def copyFiles(self):
		"""docstring for copyFiles"""

		print 10*"=", "copyFiles"
		result = True

		files = self.files()
		everything = self.everything()
		
		for i in range(len(files)):

			file = files[i]
			fileId = file.get('id')

			# print "file", file
			if not file.has_key('new'):

				fileName = file.get('title')
				# print fileName

				addParents = [{'id': self.sourceFolder}]
					
				print "copyFiles", fileId, fileName, addParents
				
				try:
					newFile = self.source.makeCopy(fileId, fileName, addParents)
					files[i]['new'] = newFile
				except:
					print "ERROR:", fileId, fileName, addParents
					result = False
					
			else:
				# print "Skipping:", fileId
				pass
		
		self.save(files, 'xDrive_files.json')

		if result == True:
			print "Done."

		return result

	def copyFilesTarget(self):
		
		print 10*"=", "copyFilesTarget"
		result = True

		files = self.files()
		everything = self.everything()
		
		for i in range(len(files)):
			# print "file", file
			if files[i].has_key('new') and not files[i].has_key('finale'):
				file = files[i]
				fileId = file.get('id')
				fileName = file.get('title')
				parents = file.get('parents')
				
				newFile = files[i].get('new')
				newFileId = newFile.get('id')
				
				addParents = []

				for parent in parents:

					parentId = parent.get('id')
					newParentId = everything[parentId]['new']['id']
					addParents.append({'id': newParentId})

				if len(addParents) == 0:
					addParents.append({'id': self.targetFolder})
					
				print "copyFiles", newFileId, fileName, addParents
				
				try:
					finalFile = self.target.makeCopy(newFileId, fileName, addParents)
					files[i]['finale'] = finalFile
				except:
					print "ERROR:", fileId, fileName, addParents
					result = False
					
			else:
				# print "Skipping:", fileId
				pass

		self.save(files, 'xDrive_files.json')

		if result == True:
			print "Done."

		return result

	def createFolders(self):
		"""docstring for createFolders"""

		print 10*"=", "createFolders"
		result = True
		
		everything = self.everything()
		for folderId in everything:

			if not everything[folderId].has_key('new'):

				folderName = everything[folderId]['title']
				print "Creating:", folderId, folderName

				try:
					if self.targetFolder:
						parents = [{'id':self.targetFolder}]
					else:
						parents = []
					
					newFolder = self.target.insertFile(everything[folderId]['title'], parents)
					newFolderId = newFolder.get('id')
					newFolderName = newFolder.get('title')

					print "Created:",newFolderId, newFolderName

					everything[folderId]['new'] = newFolder
				except:
					print "ERROR:", folderId, folderName
					result = False

			else:
				# print "Skipping:", folderId
				pass

		self.save(everything, 'xDrive_all.json')

		if result == True:
			print "Done."
			
		return result

	def moveFolders(self):
		"""docstring for moveFolders"""

		print 10*"=", "moveFolders"

		result = True
		
		folders = self.folders()
		everything = self.everything()
		
		for folder in folders:
			folderId = folder.get('id')
			
			if everything.has_key(folderId):

				newFolder = everything[folderId]['new']
				newFolderId = newFolder['id']
				newFolderMoved = newFolder.get('moved', False)
				
				if not newFolderMoved:
					parents = folder.get('parents')
					addParents = []
		
					for parent in parents:
				
						parentId = parent.get('id')
						newParentId = everything[parentId]['new']['id']
						addParents.append(newParentId)
				
					if len(addParents) > 0:
						print "Folder", newFolderId, "Parents", addParents

						if self.targetFolder:
							removeParents = [self.targetFolder]
						else:
							removeParents = []

						try:
							self.target.updateFile(newFolderId, addParents, removeParents)
							everything[folderId]['new']['moved'] = True
						except:
							print "Could not move:", newFolderId
							result = False
			else:
				print "Found new folder:", folderId

		self.save(everything, 'xDrive_all.json')

		if result == True:
			print "Done."
			
		return result

	def retrieveFiles(self, source = True):
		"""save all files to JSON file"""
		if source:
			items = self.source.retrieve_all_files()
		else:
			items = self.target.retrieve_all_files()
			
		print "Found", len(items), "files"
		self.save(items, 'xDrive_files.json')
		return items

	def files(self):
		"""docstring for files"""
		filename = 'xDrive_files.json'
		file = os.path.join(_work_dir(), filename)

		if os.path.exists(file):
			return self.load(filename)
		else:
			return self.retrieveFiles()

	def retrieveFolders(self, source = True):
		"""save all folders to JSON file"""
		if source:
			items = self.source.retrieve_all_folders()
		else:
			items = self.target.retrieve_all_folders()
		print "Found", len(items), "folders"
		self.save(items, 'xDrive_folders.json')
		return items
			
	def folders(self):
		"""docstring for folders"""
		filename = 'xDrive_folders.json'
		file = os.path.join(_work_dir(), filename)

		if os.path.exists(file):
			return self.load(filename)
		else:
			return self.retrieveFolders()

def _work_dir():
	"""docstring for _work_dir"""
	return os.path.dirname(os.path.realpath(__file__))

def main():
	"""docstring for main"""
	pass

if __name__ == '__main__':
	main()