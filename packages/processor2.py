#!/usr/bin/python
from helper import updateStatus

class processor(object):
    """docstring for processor"""
    def __init__(self, userObj):
        super(processor, self).__init__()

        # used for lookup of parents title
        self.user = userObj
        self.files = {}
        self.folders = {}

    def processFile(self, item):
        files = self.files
        fileId = item.get('id')
        
        if fileId in files: #exists
            # print "Update:", fileId, item
            files[fileId].update(item)
        else: # not exists
            files[fileId] = item
        
        self.files = files
        
    def processFolder(self, item):
        folders = self.folders
        folderId = item.get('id')
        
        if folderId in folders: #exists
            # print "Update:", folderId, item
            try:
                folders[folderId].update(item)
            except AttributeError:
                print "Could not update folder", folderId, "with", item
        else: # not exists
            folders[folderId] = item
        
        self.folders = folders
        
    def processParents(self, parent):
        """docstring for processParents"""
        folders = self.folders
        parentId = parent.get('id')
        
        if parentId in folders: # exists
            try:
                folders[parentId].update(parent)
            except AttributeError:
                print "Could not update folder", parentId, "with", parent
        else: # fetch info from API
            # print "Fetching info for", parentId
            item = self.user.file.fileGet(parentId)
            folders[parentId] = item
            
        self.folders = folders
        
    def processFilesFolders(self, items):
        print 10*"=", "processor.processFilesFolders",10*"="
        
        parentItems = []
        i = 0
        c = len(items)
        
        print "Crunching", c, "records."

        # merge new items into files/folders
        for item in items:
            
            i += 1
            updateStatus(i, c)
            
            typeFolder = 'application/vnd.google-apps.folder'
            mimeType = item.get('mimeType', typeFolder)

            # is some kind of file
            if mimeType != typeFolder:
                self.processFile(item)

            else: # is a folder
                self.processFolder(item)

            # item got parents
            parents = item.get('parents', [])

            for parent in parents:
                parentItems.append(parent)
        
        # print 'Found', len(parentItems), 'parents.'
        for parent in parentItems:
            self.processParents(parent)
        
        print "\nDone."
        # save all changes
        # self.fh.writeFilesToDisk()

        return (self.files, self.folders)

    def isNewFile(self, fileId):

        if fileId in self.newFiles: #exists
            return False
        else: # does not exist
            return True

    def isNewFolder(self, folderId):

        if folderId in self.newFolders: #exists
            return False
        else: # does not exist
            return True

    def isNewFolderMoved(self, folderId):

        if folderId in self.newFolders: #exists

            newFolder = self.newFolders.get(folderId)

            if newFolder.get('moved', False):
                return True
            else: # does not exist
                return False

    def setNewFolderMoved(self, folderId):
        newFolders = self.newFolders
        newFolders[folderId]['moved'] = True
        self.newFolders = newFolders

    def processNewFolders(self, folders):
        newFolders = {}
        newFoldersMove = {}

        for folderId in folders:
            # print folders[folder]
            if self.isNewFolder(folderId):
                newFolders[folderId] = folders[folderId]

            if not self.isNewFolderMoved(folderId):
                newFoldersMove[folderId] = folders[folderId]

        return (newFolders, newFoldersMove)

    def processNewFiles(self, files):
        newFiles = {}

        for fileId in files:
            # print files[aFile]
            if self.isNewFile(fileId):
                newFiles[fileId] = files[fileId]
        return newFiles


    def processNewFilesFolders(self, files = None, folders = None):
        print 10*"=", "processor.processNewFilesFolders",10*"="
        
        if not files:
            files = self.files

        if not folders:
            folders = self.folders

        newFiles = self.processNewFiles(files)
        newFolders, newFoldersMove = self.processNewFolders(folders)

        strFiles = "files: " + str(len(newFiles)).ljust(7, ' ')
        strFolders = "folders: " + str(len(newFolders)).ljust(7, ' ')
        strFoldersMove = "folders to move: " + str(len(newFoldersMove)).ljust(7, ' ')
        print strFiles, strFolders, strFoldersMove

        return (newFiles, newFolders, newFoldersMove)
