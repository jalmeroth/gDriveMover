#!/usr/bin/python
from gDrive import gDrive
from myDrive import myDrive


def main():
	"""docstring for main"""
	
	setupComplete = False
	sourceMail = raw_input("Please enter the email address of your source account: ")
	
	if sourceMail:
		targetMail = raw_input("Please enter the email address of your target account: ")
	
		if targetMail:
			source = gDrive(sourceMail)
			target = gDrive(targetMail)
		
			if source and target:
				sourceId = raw_input('Please enter the folderId of your source folder: ')
			
				if sourceId:
					targetId = raw_input('Please enter the folderId of your target folder: ')
				
					if targetId:
						sourceData = source.fileGet(sourceId, "id,title")
						targetData = target.fileGet(targetId, "id,title")
					
						if sourceData and targetData:
							unknown = 'Unknown'
						
							sourceName = sourceData.get('title', unknown)
							targetName = targetData.get('title', unknown)
						
							sourceFolder = sourceData.get('id')
							targetFolder = targetData.get('id')
						
							if sourceName != unknown and targetName != unknown:
								print 10*"=", "Using folders"
								print "Source:", sourceName
								print "Target:", targetName
								setupComplete = True
	
	if setupComplete:
		
		retryMaximum = 3
		
		mover = myDrive(
			source = source,
			sourceFolder = sourceFolder,
			target = target,
			targetFolder = targetFolder
		)
		
		
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
			
			raw_input("Press Enter to copy files on target...")
			
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
	main()