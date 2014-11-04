#!/usr/bin/python
from gDrive import gDrive
from myDrive import myDrive


def main():
	"""docstring for main"""

	########## Start editing here ##########

	source = gDrive('checker86@gmail.com')
	sourceFolder = '<enter folder id here>'
	target = gDrive('firstname.lastname@cool-company.com')
	targetFolder = '<enter folder id here>'

	########## Stop editing here ##########

	# setup myDrive config
	cDrive = myDrive(
		source = source,
		sourceFolder = sourceFolder,
		target = target,
		targetFolder = targetFolder
	)
	
	# create an index of files and folders
	cDrive.listFilesFolders()
	raw_input("Press Enter to continue...")
	
	# create all folders first
	if cDrive.createFolders():
		# move folders into hierarchy
		if cDrive.moveFolders():
			pass
		else:
			print "Could not move all folders. Please try again."
	else:
		print "Could not create all folders. Please try again."

	raw_input("Press Enter to copy files on source...")

	errorCounter = 0
	while not cDrive.copyFilesSource():
		errorCounter += 1
		if errorCounter >= 2:
			print "Giving up."
			return

	raw_input("Press Enter to copy files on target...")
	
	errorCounter = 0
	while not cDrive.copyFilesTarget():
		errorCounter += 1
		if errorCounter >= 2:
			print "Giving up."
			return
	
	return

if __name__ == '__main__':
	main()
