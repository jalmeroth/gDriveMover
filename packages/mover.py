#!/usr/bin/python
import json
import requests

class gDriveMover(object):
	"""docstring for gDriveMover"""
	def __init__(self, source = None, sourceFolder = None, target = None, targetFolder = None):
		super(gDriveMover, self).__init__()
		
		self.source = source
		self.target = target
		
		print 10*"=", "Initializing gDriveMover", 10*"="
		self.sourceFolder = sourceFolder
		self.targetFolder = targetFolder
		
		self.maxThreads = 5
		
	def createWorkFolder(self, gDriveObj, title="gDriveMover"):
		"""docstring for createWorkFolder"""
		raw_input("Press ENTER to create a new working directory...")
		file = gDriveObj.file.insert(title=title)
		# print json.dumps(file)
		fileId = file.get('id')
		# print "Created Folder", fileId, title
		return fileId
		
	def createSourceFolder(self):
		"""docstring for createSourceFolder"""
		print 10*"=", "createSourceFolder"
		return self.createWorkFolder(self.source)
		
	def createTargetFolder(self):
		"""docstring for createTargetFolder"""
		print 10*"=", "createTargetFolder"
		return self.createWorkFolder(self.target)
	
	def searchMode1(self):
		# find items, which the sourceId has access to
		query = "("
		query += "'" + self.source.userId + "' in owners OR "
		query += "'" + self.source.userId + "' in writers OR "
		query += "'" + self.source.userId + "' in readers"
		query += ") AND "
		
		# ... and you do not own
		query += "NOT ('"+ self.target.userId + "' in owners) AND "
		
		# ... and it is not trashed
		query += "trashed != true"
		# print query
		
		items = self.target.file.search(q = query)
		# print json.dumps(items)
		return items
		
	def copyFiles(self, gDriveObj, files, switch):
		"""docstring for copyFiles"""
		# print 10*"=", "copyFiles"
		
		if switch == "copyFilesSource":
			newFiles = self.target.fileHandler.copyFiles
		else:
			newFiles = self.target.fileHandler.newFiles
		
		result = True
		length = len(files)
		
		# copy files on gDriveObj, chunked
		for i in range(0, length, self.maxThreads):
			print 10*"=", "copyFiles", i, "/", length
			
			items = files[i:i+self.maxThreads]
			# print json.dumps(items)
			results = gDriveObj.file.makeCopy(items)
			
			for fileId in results:
				
				r = results[fileId]
				
				if r.status_code == requests.codes.ok:
					
					newFile = r.json()
					newFileId = newFile.get('id')
					newFileName = newFile.get('title')
					
					print "Copied:", newFileId, newFileName
					
					newFiles[fileId] = newFile
					
				else:
					print "FAIL:", r.status_code, fileId
					result = False
			
			if switch == "copyFilesSource":
				self.target.fileHandler.copyFiles = newFiles 
			else:
				self.target.fileHandler.newFiles = newFiles
			
		if result == True:
			print "Done."
		
		return result
		
	def copyFilesSource(self):
		"""docstring for copyFilesSource"""

		print 10*"=", "copyFilesSource", 10*"="

		files = self.source.fileHandler.files
		copyFiles = self.source.fileHandler.copyFiles

		newFiles = []

		if self.sourceFolder:
			parents = [{'id':self.sourceFolder}]
		else:
			parents = []
		
		# find files that have not been copied on source
		for fileId in files:

			if not fileId in copyFiles:

				aFile = files.get(fileId)
				fileName = aFile.get('title', 'Untitled')
				
				item = {
					'id': fileId,
					'title': fileName,
					'parents': parents
				}
				
				newFiles.append(item)
			else:
				pass

		print "Going to copy", len(newFiles), "files on source."
		
		return self.copyFiles(self.source, newFiles, 'copyFilesSource')

	def copyFilesTarget(self, copyFiles = None):
		
		print 10*"=", "copyFilesTarget", 10*"="
		result = True

		if not copyFiles:
			copyFiles = self.target.fileHandler.files

		newFiles = self.target.fileHandler.newFiles
		foldersNew = self.target.fileHandler.newFolders
		
		finalFiles = []
		
		# find files that have not been copied on target
		for fileId in copyFiles:

			if not fileId in newFiles:

				aFile = copyFiles.get(fileId)
				parents = aFile.get('parents')

				addParents = []
				
				for parent in parents:
					parentId = parent.get('id')
					newParent = foldersNew.get(parentId)

					if newParent:
						newParentId = newParent.get('id')
						addParents.append({'id': newParentId})
				
				if len(addParents) == 0:
					addParents.append({'id': self.targetFolder})
				
				item = aFile
				item['parents'] = addParents
				
				finalFiles.append(item)
			else:
				# print "Skipping:", fileId
				pass
		
		print "Going to copy", len(finalFiles), "files on target."

		return self.copyFiles(self.target, finalFiles, 'copyFilesTarget')

	def createFolders(self):
		"""docstring for createFolders"""

		print 10*"=", "createFolders", 10*"="
		result = True
		
		folders = self.target.fileHandler.folders
		newFolders = self.target.fileHandler.newFolders

		createFolders = []

		if self.targetFolder:
			parents = [{'id':self.targetFolder}]
		else:
			parents = []
		
		# find folders that have not been created on target
		for folderId in folders:
			
			if not folderId in newFolders:

				folderName = folders[folderId].get('title')
				
				item = {
					'id': folderId,
					'title': folderName,
					'parents': parents
				}
				createFolders.append(item)
			else:
				pass
		
		length = len(createFolders)
		
		# create new folders on target, chunked
		for i in range(0, length, self.maxThreads):
			print "createFolders", i, "/", length
			
			items = createFolders[i:i+self.maxThreads]
			results = self.target.file.insertFiles(items)
			
			for folderId in results:
				
				r = results[folderId]
				
				if r.status_code == requests.codes.ok:
					
					newFolder = r.json()
					newFolderId = newFolder.get('id')
					newFolderName = newFolder.get('title')
					
					print "Created:",newFolderId, newFolderName
					
					newFolders[folderId] = newFolder
				
				else:
					print "FAIL:", r.status_code, folderId
					result = False
			
			self.target.fileHandler.newFolders = newFolders
			
		if result == True:
			print "Done."

		return result

	def moveFolders(self):
		"""docstring for moveFolders"""
		
		print 10 * "=", "moveFolders", 10*"="
		
		result = True
		
		folders = self.target.fileHandler.folders
		foldersNew = self.target.fileHandler.newFolders

		moveFolders = []

		if self.targetFolder:
			removeParents = [self.targetFolder]
		else:
			removeParents = []
		
		# find folders that have not been moved on target
		for folderId in folders:

			folder = folders.get(folderId)

			if folderId in foldersNew:
				
				newFolder = foldersNew.get(folderId)
							
				if newFolder:
					
					newFolderId = newFolder.get('id')
					newFolderMoved = newFolder.get('moved', False)
					
					if not newFolderMoved:
						
						parents = folder.get('parents')
						addParents = []
						
						for aParent in parents:
							parentId = aParent.get('id')
							newParent = foldersNew.get(parentId)
							
							if newParent: # parent found in foldersNew
								newParentId = newParent.get('id')
								addParents.append(newParentId)
						
						# print folder.get('title'), parents, addParents

						if len(addParents) > 0:
							# print "Folder", newFolderId, "Parents", addParents
						
							item = {
								'folderId': folderId,
								'newFolderId': newFolderId,
								'addParents': addParents,
								'removeParents': removeParents
							}

							moveFolders.append(item)
						else:
							# set folders moved, that remain in target folder root
							self.target.processor.setNewFolderMoved(folderId)
		
		length = len(moveFolders)
		# move folders on target, chunked
		for i in range(0, length, self.maxThreads):
			print "moveFolders", i, "/", length
			
			items = moveFolders[i:i+self.maxThreads]
			results = self.target.file.updateFiles(items)
			
			for folderId in results:
				
				r = results[folderId]
				
				if r.status_code == requests.codes.ok:
					
					newFolder = r.json()
					newFolderId = newFolder.get('id')
					newFolderName = newFolder.get('title')
					
					print "Moved:",newFolderId, newFolderName
					
					self.target.processor.setNewFolderMoved(folderId)
				
				else:
					print "FAIL:", r.status_code, folderId
					result = False
			
			self.target.fileHandler.newFolders = foldersNew
			
		if result == True:
			print "Done."
		
		return result

	def fixPermissions(self, gDriveObj, fileId, userId, permRole):
		"""docstring for fixPermissions"""
		myDrive = gDriveObj
	
		permId = myDrive.perm.getIdForEmail(userId)
		# print permId
	
		permission = myDrive.perm.get(fileId, permId)
		# print permission
	
		newPerm = {
			'role': permRole,
			'type': 'user',
			'id': permId
		}
	
		if 'error' in permission:
			
			if permission['error']['code'] == 404:
			
				result = myDrive.perm.insert(fileId, **newPerm)
			
				if result == newPerm:
					print "Done."
				else:
					print result
			
		elif permission.get('id') == permId:
				
				roles = ('owner', 'writer', 'reader')
				
				role = permission.get('role')
				newRole = newPerm.get('role')
				
				if role in roles and newRole in roles:
					
					roleIndex = roles.index(role)
					newRoleIndex = roles.index(newRole)
					
					if roleIndex <= newRoleIndex:
						pass
						# print "Role:", role, roles.index(role), roles.index(newPerm.get('role')), "ok"
					else:
						result = myDrive.perm.update(fileId, permId, role=newPerm.get('role'))
						
						if result == newPerm:
							print "Done."
						else:
							print result
		else:
			print "perm", fileId, json.dumps(permission)

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
		
		self.fixPermissions(self.source, self._sourceFolder, self.target.userId, 'reader')

		print "Source:", self.sourceFolder, self.source.file.getName(self.sourceFolder)
	
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
		
		self.fixPermissions(self.target, self._targetFolder, self.target.userId, 'writer')

		print "Target:", self.targetFolder, self.target.file.getName(self.targetFolder)

def main():
	pass

if __name__ == '__main__':
	main()