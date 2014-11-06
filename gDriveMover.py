#!/usr/bin/python
import os
import json
import requests
import gDrive


class gDriveMover(object):
	"""docstring for gDriveMover"""
	def __init__(self, source = None, sourceFolder = None, target = None, targetFolder = None):
		super(gDriveMover, self).__init__()
		
		self.source = source
		self.target = target
		
		self.sourceFolder = sourceFolder
		self.targetFolder = targetFolder
		
		self.file_files = 'files.json'
		self.file_files_new = 'files_new.json'
		self.file_folders = 'folders.json'
		self.file_folders_new = 'folders_new.json'
		
		self.maxThreads = 5
		
	def save(self, data, filename):
		"""docstring for save"""
		file = os.path.join(_work_dir(), filename)
		with open(file, "w+") as jsonFile:
			json.dump(data, jsonFile)
	
	def load(self, filename):
		"""docstring for load"""
		file = os.path.join(_work_dir(), filename)
		if os.path.exists(file):
			with open(file,"r") as jsonFile:
				return json.load(jsonFile)
		else:
			return {}
	
	def retrieveFiles(self):
		"""save all files to JSON file"""
		items = self.source.file.retrieve_all_files()
		self.files = items
		print "Fetched", len(items), "files"
		return items

	def retrieveFolders(self):
		"""save all folders to JSON file"""
		items = self.source.file.retrieve_all_folders()
		self.folders = items
		print "Found", len(items), "folders"
		return items
		
	def createWorkFolder(self, gDriveObj, title="gDriveMover"):
		"""docstring for createWorkFolder"""
		file = gDriveObj.file.insert(title=title)
		# print json.dumps(file)
		fileId = file.get('id')
		# print fileId
		return fileId
		
	def createSourceFolder(self):
		"""docstring for createSourceFolder"""
		print 10*"=", "createSourceFolder"
		return self.createWorkFolder(self.source)
		
	def createTargetFolder(self):
		"""docstring for createTargetFolder"""
		print 10*"=", "createTargetFolder"
		return self.createWorkFolder(self.target)
	
	def listFilesFolders(self):
		"""docstring for listFilesFolders"""
		print 10*"=", "listFilesFolders", 10*"="
		
		folders = self.folders
		files = self.files
		
		foldersNew = self.foldersNew
		filesNew = self.filesNew
		
		for folder in folders:
			folderId = folder['id']
			if not foldersNew.has_key(folderId):
				foldersNew[folderId] = folder
		
		self.foldersNew = foldersNew
		
		fields = "id,parents(id,isRoot),title"
		
		for folder in folders:
			for parent in folder['parents']:
				parentId = parent.get('id')
				if not foldersNew.has_key(parentId):
					# print "Trying to looking up extra info:", parentId
					try:
						parentItem = self.source.file.fileGet(parentId, fields=fields)
					except:
						parentItem = {
							"id": parentId,
							"parents": [],
							"title": parentId
						}
					foldersNew[parentId] = parentItem
		
		self.foldersNew = foldersNew
		
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
						parentItem = self.source.file.fileGet(parentId, fields=fields)
					except:
						parentItem = {
							"id": parentId,
							"title": parentId
						}
					foldersNew[parentId] = parentItem
					# ignore parents of parents of public files
					foldersNew[parentId]['parents'] = []

		self.filesNew = filesNew
		self.foldersNew = foldersNew
		# print "Need to create", len(foldersNew), "folders at all."
		print "Done."
		
	def copyFiles(self, gDriveObj, files, key):
		"""docstring for copyFiles"""
		# print 10*"=", "copyFiles"
		
		newFiles = self.filesNew
		
		result = True
		length = len(files)
		
		# copy files on gDriveObj, chunked
		for i in range(0, length, self.maxThreads):
			print 10*"=", "copyFiles", i, "/", length
			
			items = files[i:i+self.maxThreads]
			results = gDriveObj.file.makeCopy(items)
			
			for fileId in results:
				
				r = results[fileId]
				
				if r.status_code == requests.codes.ok:
					
					newFile = r.json()
					newFileId = newFile.get('id')
					newFileName = newFile.get('title')
					
					print "Copied:", newFileId, newFileName
					
					newFiles[fileId][key] = newFile
					
				else:
					print "FAIL:", r.status_code, fileId
					result = False
			
			self.filesNew = newFiles
			
		if result == True:
			print "Done."
		
		return result
		
	def copyFilesSource(self):
		"""docstring for copyFilesSource"""
		print 10*"=", "copyFilesSource", 10*"="
		result = True

		filesNew = self.filesNew
		
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
		
		return self.copyFiles(self.source, newFiles, 'new')

	def copyFilesTarget(self):
		
		print 10*"=", "copyFilesTarget", 10*"="
		result = True

		filesNew = self.filesNew
		foldersNew = self.foldersNew
		
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
		
		return self.copyFiles(self.target, finalFiles, 'finale')

	def createFolders(self):
		"""docstring for createFolders"""

		print 10*"=", "createFolders", 10*"="
		result = True
		
		foldersNew = self.foldersNew
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
			results = self.target.file.insertFiles(items)
			
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
			
			self.foldersNew = foldersNew
			
		if result == True:
			print "Done."
		return result

	def moveFolders(self):
		"""docstring for moveFolders"""
		
		print 10 * "=", "moveFolders", 10*"="
		
		result = True
		
		folders = self.folders
		foldersNew = self.foldersNew
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
			results = self.target.file.updateFiles(items)
			
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
			
			self.foldersNew = foldersNew
			
		if result == True:
			print "Done."
		
		return result

	@property
	def sourceFolder(self):
		"""docstring for sourceFolder"""
		# print "sourceFolderId", self._sourceFolder
		return self._sourceFolder
	
	@sourceFolder.setter
	def sourceFolder(self, folderId):
		"""docstring for sourceFolder"""
		# print "sourceFolderId", folderId
		if folderId:
			self._sourceFolder = folderId
		else:
			self._sourceFolder = self.createSourceFolder()
	
	@property
	def targetFolder(self):
		"""docstring for targetFolder"""
		# print "targetFolderId", self._targetFolder
		return self._targetFolder
	
	@targetFolder.setter
	def targetFolder(self, folderId):
		"""docstring for targetFolder"""
		# print "targetFolderId", folderId
		if folderId:
			self._targetFolder = folderId
		else:
			self._targetFolder = self.createTargetFolder()

	@property
	def files(self):
		"""docstring for files"""
		file = os.path.join(_work_dir(), self.file_files)
		
		if os.path.exists(file): # load files from disk
			files = self.load(self.file_files)
		else: # fetch from API
			files = self.retrieveFiles()
			
		return files
		
	@files.setter
	def files(self, items):
		"""docstring for files"""
		self.save(items, self.file_files)
			
	@property
	def folders(self):
		"""docstring for folders"""
		file = os.path.join(_work_dir(), self.file_folders)

		if os.path.exists(file): # load files from disk
			folders = self.load(self.file_folders)
		else: # fetch from API
			folders = self.retrieveFolders()
		
		return folders
	
	@folders.setter
	def folders(self, items):
		self.save(items, self.file_folders)
	
	@property
	def filesNew(self):
		"""docstring for filesNew"""
		return self.load(self.file_files_new)
	
	@filesNew.setter
	def filesNew(self, items):
		"""docstring for filesNew"""
		self.save(items, self.file_files_new)
	
	@property
	def foldersNew(self):
		"""docstring for foldersNew"""
		return self.load(self.file_folders_new)
	
	@foldersNew.setter
	def foldersNew(self, items):
		self.save(items, self.file_folders_new)
	
def _work_dir():
	"""docstring for _work_dir"""
	return os.path.dirname(os.path.realpath(__file__))

def main():
	"""docstring for main"""
	
	setupComplete = False
	
	sourceMail = raw_input("Please enter the email address of your source account: ")
	targetMail = raw_input("Please enter the email address of your target account: ")
	
	if targetMail and sourceMail:
		
		source = gDrive.drive(sourceMail)
		target = gDrive.drive(targetMail)
		
		if source and target:
			setupComplete = True
	
	if setupComplete:
		
		retryMaximum = 3
		
		sourceFolder = None
		targetFolder = None
		
		mover = gDriveMover(
			source = source,
			sourceFolder = sourceFolder,
			target = target,
			targetFolder = targetFolder
		)
		
		print 10*"=", "Using folders", 10*"="
		print "Source:", mover.sourceFolder
		print "Target:", mover.targetFolder
		# return
		
		########## Start: listFilesFolders
		
		# create an index of files and folders
		mover.listFilesFolders()
		
		########## End: listFilesFolders
		
		raw_input("Press Enter to create folders on target...")
		
		########## Start: createFolders
		
		done = False
		retries = 0
		
		while not done and retries < retryMaximum:
			# create all new folders on target
			done = mover.createFolders()
			if not done:
				retries += 1
				print "Retrying..."
		
		########## End: createFolders
		
		if done:
			########## Start: moveFolders
		
			done = False
			retries = 0
		
			while not done and retries < retryMaximum:
				# move folders into hierarchy on target
				done = mover.moveFolders()
				if not done:
					retries += 1
					print "Retrying..."
			
			if done:
				pass
			else:
				print "Could not move all folders within", retryMaximum, "attempts."
				print "Giving up. Please run this script again."
				return
		
			########## End: moveFolders
		else:
			print "Could not create all folders within", retryMaximum, "attempts."
			print "Giving up. Please run this script again."
			return
		
		raw_input("Press Enter to copy files on source...")

		########## Start: copyFilesSource
	
		done = False
		retries = 0
	
		while not done and retries < retryMaximum:
			# create a copy of all files on source
			done = mover.copyFilesSource()
			if not done:
				retries += 1
				print "Retrying..."
		
		if done:
			
			# raw_input("Press Enter to copy files on target...")
			
			########## Start: copyFilesTarget
			
			done = False
			retries = 0
			
			while not done and retries < retryMaximum:
				# create a copy of all files on target
				done = mover.copyFilesTarget()
				if not done:
					retries += 1
					print "Retrying..."
			
			if done:
				pass
			else:
				print "Could not copy all files on target within", retryMaximum, "attempts."
				print "Giving up. Please run this script again."
				return
			
			########## End: copyFilesTarget
			
		else:
			print "Could not copy all files on source within", retryMaximum, "attempts."
			print "Giving up. Please run this script again."
			return
	
		########## End: copyFilesSource

if __name__ == '__main__':
	try:
		main()
	except (KeyboardInterrupt, SystemExit):
		print "Quitting."