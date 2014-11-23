#!/usr/bin/python
import sys
import json
import argparse

from packages.mover import gDriveMover
from packages.gDrive import gDrive
from packages.helper import validEmail, save, unlink


def main():
	"""docstring for main"""
	
	# initialize Arg-parser
	parser = argparse.ArgumentParser()
	
	# setup Arg-parser
	parser.add_argument('--sourceMail', type=str, help='Email address of your source account')
	parser.add_argument('--targetMail', type=str, help='Email address of your target account')
	parser.add_argument('--sourceFolder', type=str, help='ID of your source folder')
	parser.add_argument('--targetFolder', type=str, help='ID of your target folder')
	parser.add_argument('--retries', type=int, default=3, help='Number of operation retries')	
	parser.add_argument('--refresh', action='store_true', help='Re-Fetches your files/folders from Google')
	parser.add_argument('--copy', action='store_true', help='Copy your files on target first')
	
	# initialize args
	args = sys.argv[1:]

	# parse arguments
	args, unknown = parser.parse_known_args(args)
	# print args, unknown
	# sys.exit(0)
	
	setupComplete = False
	
	# setup your accounts
	sourceMail = getattr(args, 'sourceMail', None)
	targetMail = getattr(args, 'targetMail', None)

	if not sourceMail:
		sourceMail = raw_input("Please enter the email address of your source account: ")
		
	if not targetMail:
		targetMail = raw_input("Please enter the email address of your target account: ")
	
	if validEmail(targetMail) and validEmail(sourceMail):
		
		source = gDrive(sourceMail)
		target = gDrive(targetMail)
		
		if source and target:
			setupComplete = True
	
	# proceed when setup complete
	if setupComplete:

		# initiliaze some variables
		doRefresh = getattr(args, 'refresh', False)
		copyFirst = getattr(args, 'copy', False)
		retryMaximum = getattr(args, 'retries', 3)
		sourceFolder = getattr(args, 'sourceFolder', None)
		targetFolder = getattr(args, 'targetFolder', None)
		
		# initialize gDriveMover-instance
		mover = gDriveMover(
			source = source,
			sourceFolder = sourceFolder,
			target = target,
			targetFolder = targetFolder
		)

		# # files / folders we already know
		files = target.fileHandler.files
		folders = target.fileHandler.folders

		# TODO: (jan.almeroth) Retain or remove existing items?

		if doRefresh or (len(files) == 0 and len(folders) == 0):

			if not copyFirst:
				items = mover.searchMode1()
			else:
				items = source.file.search()

			# print json.dumps(items)
			save(items, 'items.json')
			files, folders = source.processor.processFilesFolders(items)
			unlink('items.json')

		# new files / new folders that needs to be created
		newFiles, newFolders, newFoldersMove = target.processor.processNewFilesFolders()
		
		if len(newFolders): ########## createFolders

			raw_input("Press ENTER to create folders on target...")
			
			done = False
			retries = 0
			
			while not done and retries < retryMaximum:
				# create all new folders on target
				done = mover.createFolders()
				if not done:
					retries += 1
					print "Retrying..."
			
			target.fileHandler.writeFilesToDisk()

			if not done:
				print "Could not create all folders within", retryMaximum, "attempts."
				print "Giving up. Please run this script again."
				return


		if len(newFoldersMove): ########## moveFolders

			raw_input("Press ENTER to move folders on target...")

			done = False
			retries = 0
		
			while not done and retries < retryMaximum:
				# move folders into hierarchy on target
				done = mover.moveFolders()
				if not done:
					retries += 1
					print "Retrying..."
			
			target.fileHandler.writeFilesToDisk()

			if not done:
				print "Could not move all folders within", retryMaximum, "attempts."
				print "Giving up. Please run this script again."
				return
		
		if copyFirst: ########## copyFilesSource

			raw_input("Press ENTER to copy files on source...")
		
			done = False
			retries = 0
		
			while not done and retries < retryMaximum:

				# create a copy of all files on source
				done = mover.copyFilesSource()
				if not done:
					retries += 1
					print "Retrying..."
			
			target.fileHandler.writeFilesToDisk()

			if not done:
				print "Could not copy all files on source within", retryMaximum, "attempts."
				print "Giving up. Please run this script again."
				return
			
		raw_input("Press ENTER to copy files on target...")
		
		########## Start: copyFilesTarget
		
		done = False
		retries = 0
		
		while not done and retries < retryMaximum:
			# create a copy of all files on target
			done = mover.copyFilesTarget()
			if not done:
				retries += 1
				print "Retrying..."
		
		target.fileHandler.writeFilesToDisk()

		if not done:
			print "Could not copy all files on target within", retryMaximum, "attempts."
			print "Giving up. Please run this script again."
			return
			

if __name__ == '__main__':
	try:
		main()
	except (KeyboardInterrupt, SystemExit):
		print "Quitting."