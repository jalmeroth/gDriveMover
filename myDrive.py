#!/usr/bin/python
import os
import json
import requests


class myDrive(object):
	"""docstring for myDrive"""
	def __init__(self, source = None, sourceFolder = None, target = None, targetFolder = None):
		super(myDrive, self).__init__()
		
		self.source = source
		self.sourceFolder = sourceFolder
		self.target = target
		self.targetFolder = targetFolder
		
		self.file_files = 'myDrive_files.json'
		self.file_files_new = 'myDrive_files_new.json'
		self.file_folders = 'myDrive_folders.json'
		self.file_folders_new = 'myDrive_folders_new.json'
		
		self.maxThreads = 5
	
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
		
		print 10*"=", "listFilesFolders", 10*"="
		
		folders = self.folders()
		files = self.files()
		
		foldersNew = self.foldersNew()
		filesNew = self.filesNew()

		for folder in folders:
			folderId = folder['id']
			if not foldersNew.has_key(folderId):
				foldersNew[folderId] = folder

		self.save(foldersNew, self.file_folders_new)

		fields = "id,parents(id,isRoot),title"

		for folder in folders:
			for parent in folder['parents']:
				parentId = parent.get('id')
				if not foldersNew.has_key(parentId):
					# print "Trying to looking up extra info:", parentId
					try:
						parentItem = self.source.fileGet(parentId, fields=fields)
					except:
						parentItem = {
							"id": parentId,
							"parents": [],
							"title": parentId
						}
					foldersNew[parentId] = parentItem

		self.save(foldersNew, self.file_folders_new)
		# print "Folders from Folders", len(foldersNew)

		fields = "id,title"
		for file in files:
			fileId = file.get('id')
			if not filesNew.has_key(fileId):
				filesNew[fileId] = file
			for parent in file['parents']:
				parentId = parent.get('id')
				if not foldersNew.has_key(parentId):
					# print "Trying to looking up extra info:", parentId
					try:
						parentItem = self.source.fileGet(parentId, fields=fields)
					except:
						parentItem = {
							"id": parentId,
							"title": parentId
						}
					foldersNew[parentId] = parentItem
					# ignore parents of parents of public files
					foldersNew[parentId]['parents'] = []

		self.save(filesNew, self.file_files_new)
		self.save(foldersNew, self.file_folders_new)
		# print "Need to create", len(foldersNew), "folders at all."
		print "Done."
		
	def copyFilesSource(self):
		"""docstring for copyFilesSource"""

		print 10*"=", "copyFilesSource", 10*"="
		result = True

		filesNew = self.filesNew()
		
		newFiles = []
		
		# find files that have not been copied on source
		for fileId in filesNew:
			file = filesNew[fileId]
			
			if self.sourceFolder:
				parents = [{'id':self.sourceFolder}]
			else:
				parents = []
			
			if not file.has_key('new'):
				fileName = file.get('title')
				
				item = {
					'fileId': fileId,
					'title': fileName,
					'parents': parents
				}
				
				newFiles.append(item)
			else:
				pass
		
		length = len(newFiles)
		
		# copy files on source, chunked
		for i in range(0, length, self.maxThreads):
			print 10*"=", "copyFilesSource", i, "/", length
			
			items = newFiles[i:i+self.maxThreads]
			results = self.source.makeCopy(items)
			
			for fileId in results:
				
				r = results[fileId]
				
				if r.status_code == requests.codes.ok:
					
					newFile = r.json()
					newFileId = newFile.get('id')
					newFileName = newFile.get('title')
					
					print "Copied:", newFileId, newFileName
					
					filesNew[fileId]['new'] = newFile
				
				else:
					print "FAIL:", r.status_code, fileId
					result = False
			
			self.save(filesNew, self.file_files_new)
			
		if result == True:
			print "Done."
		
		return result

	def copyFilesTarget(self):
		
		print 10*"=", "copyFilesTarget", 10*"="
		result = True

		filesNew = self.filesNew()
		foldersNew = self.foldersNew()
		
		finalFiles = []
		
		# find files that have not been copied on target
		for fileId in filesNew:
			file = filesNew[fileId]
			# print "file", file
			if file.has_key('new') and not file.has_key('finale'):
				fileName = file.get('title')
				parents = file.get('parents')
				
				newFile = file.get('new')
				newFileId = newFile.get('id')
				
				addParents = []
				
				for parent in parents:
					parentId = parent.get('id')
					newParent = foldersNew[parentId].get('new')
					if newParent:
						newParentId = newParent.get('id')
						addParents.append({'id': newParentId})
				
				if len(addParents) == 0:
					addParents.append({'id': self.targetFolder})
				
				item = {
					'fileId': fileId,
					'newFileId': newFileId,
					'title': fileName,
					'parents': addParents
				}
				
				finalFiles.append(item)
			else:
				# print "Skipping:", fileId
				pass
		
		length = len(finalFiles)
		
		# copy files on source, chunked
		for i in range(0, length, self.maxThreads):
			print 10*"=", "copyFilesTarget", i, "/", length
			
			items = finalFiles[i:i+self.maxThreads]
			results = self.target.makeCopy(items)
			
			for fileId in results:
				
				r = results[fileId]
				
				if r.status_code == requests.codes.ok:
					
					newFile = r.json()
					newFileId = newFile.get('id')
					newFileName = newFile.get('title')
					
					print "Copied:", newFileId, newFileName
					
					filesNew[fileId]['finale'] = newFile
				
				else:
					print "FAIL:", r.status_code, fileId
					result = False
			
			self.save(filesNew, self.file_files_new)
			
		if result == True:
			print "Done."
		
		return result

	def createFolders(self):
		"""docstring for createFolders"""

		print 10*"=", "createFolders", 10*"="
		result = True
		
		foldersNew = self.foldersNew()
		newFolders = []
		
		# find folders that have not been created on target
		for folderId in foldersNew:
			
			if not foldersNew[folderId].has_key('new'):
				folderName = foldersNew[folderId].get('title')
				
				if self.targetFolder:
					parents = [{'id':self.targetFolder}]
				else:
					parents = []
					
				item = {
					'id': folderId,
					'title': folderName,
					'parents': parents
				}
				newFolders.append(item)
			else:
				pass
		
		length = len(newFolders)
		
		# create new folders on target, chunked
		for i in range(0, length, self.maxThreads):
			print 10*"=", "createFolders", i, "/", length
			
			items = newFolders[i:i+self.maxThreads]
			results = self.target.insertFiles(items)
			
			for folderId in results:
				
				r = results[folderId]
				
				if r.status_code == requests.codes.ok:
					
					newFolder = r.json()
					newFolderId = newFolder.get('id')
					newFolderName = newFolder.get('title')
					
					print "Created:",newFolderId, newFolderName
					
					foldersNew[folderId]['new'] = newFolder
				
				else:
					print "FAIL:", r.status_code, folderId
					result = False
			
			self.save(foldersNew, self.file_folders_new)
			
		if result == True:
			print "Done."
		return result

	def moveFolders(self):
		"""docstring for moveFolders"""
		
		print 10 * "=", "moveFolders", 10*"="
		
		result = True
		
		folders = self.folders()
		foldersNew = self.foldersNew()
		moveFolders = []
		
		# find folders that have not been moved on target
		for aFolder in folders:
			
			folderId = aFolder.get('id')
			folder = foldersNew.get(folderId)
			
			if folder:
				newFolder = folder.get('new')
				
				if newFolder:
					
					newFolderId = newFolder['id']
					newFolderMoved = newFolder.get('moved', False)
					
					if not newFolderMoved:
						
						parents = folder.get('parents')
						addParents = []
						
						for aParent in parents:
							parentId = aParent.get('id')
							parent = foldersNew.get(parentId)
							
							if parent: # parent found in foldersNew
								newParent = parent.get('new')
								
								if newParent: # parent has a copy on target
									newParentId = newParent.get('id')
									addParents.append(newParentId)
						
						if len(addParents) > 0:
							# print "Folder", newFolderId, "Parents", addParents
						
							if self.targetFolder:
								removeParents = [self.targetFolder]
							else:
								removeParents = []
						
							item = {
								'folderId': folderId,
								'newFolderId': newFolderId,
								'addParents': addParents,
								'removeParents': removeParents
							}
							moveFolders.append(item)
		
		length = len(moveFolders)
		# move folders on target, chunked
		for i in range(0, length, self.maxThreads):
			print 10*"=", "moveFolders", i, "/", length
			
			items = moveFolders[i:i+self.maxThreads]
			results = self.target.updateFiles(items)
			
			for folderId in results:
				
				r = results[folderId]
				
				if r.status_code == requests.codes.ok:
					
					newFolder = r.json()
					newFolderId = newFolder.get('id')
					newFolderName = newFolder.get('title')
					
					print "Moved:",newFolderId, newFolderName
					
					foldersNew[folderId]['new']['moved'] = True
				
				else:
					print "FAIL:", r.status_code, folderId
					result = False
			
			self.save(foldersNew, self.file_folders_new)
			
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
		self.save(items, self.file_files)
		return items

	def files(self):
		"""docstring for files"""
		file = os.path.join(_work_dir(), self.file_files)

		if os.path.exists(file):
			return self.load(self.file_files)
		else:
			return self.retrieveFiles()

	def retrieveFolders(self, source = True):
		"""save all folders to JSON file"""
		if source:
			items = self.source.retrieve_all_folders()
		else:
			items = self.target.retrieve_all_folders()
		print "Found", len(items), "folders"
		self.save(items, self.file_folders)
		return items
			
	def folders(self):
		"""docstring for folders"""
		file = os.path.join(_work_dir(), self.file_folders)

		if os.path.exists(file):
			return self.load(self.file_folders)
		else:
			return self.retrieveFolders()
	
	def foldersNew(self):
		"""docstring for foldersNew"""
		file = os.path.join(_work_dir(), self.file_folders_new)

		if os.path.exists(file):
			return self.load(self.file_folders_new)
		else:
			return {}

	def filesNew(self):
		"""docstring for filesNew"""
		file = os.path.join(_work_dir(), self.file_files_new)

		if os.path.exists(file):
			return self.load(self.file_files_new)
		else:
			return {}

def _work_dir():
	"""docstring for _work_dir"""
	return os.path.dirname(os.path.realpath(__file__))

def main():
	"""docstring for main"""
	pass

if __name__ == '__main__':
	main()