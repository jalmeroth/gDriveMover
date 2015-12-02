#!/usr/bin/python
import json
import requests
import urllib
import Queue

from urlRequest import URLRequestThread
from helper import output

class files(object):
    """docstring for files"""
    def __init__(self, userObj):
        super(files, self).__init__()
        self.fields = "id,mimeType,parents(id,isRoot),title"
        self.user = userObj
    
    def hello(self):
        """docstring for hello"""
        print "Hello " + self.user.user_Id
    
    def listChildren(self, folderId, token = None, q = None, fields = None):
        """docstring for listChildren"""
        maxResults = 1000
        
        if q == None:
            q = "mimeType != 'application/vnd.google-apps.folder' AND trashed != true"
        
        if fields == None:
            fields = "items/id,nextPageToken"
        
        params = {
            'folderId': folderId,
            'maxResults': maxResults,
            'pageToken': token,
            'q': q,
            'fields': fields
        }
        
        url = 'https://www.googleapis.com/drive/v2/files/' + folderId + '/children'
        
        r = requests.get(url, headers=self.user.headers(), params=params)
        
        return r.json()
    
    def _search(self, q, token, fields, maxResults):
        """This is where the actual search is happening"""
        
        if token:
            # print "Fetching next", maxResults, "items with token", str(token[0:15]) + "..."
            msg = "Fetching next " + str(maxResults) + " items with token " + str(token)
            output(msg)
        
        url = 'https://www.googleapis.com/drive/v2/files'
        
        params = {
            "pageToken": token,
            "q": q,
            "maxResults": maxResults,
            "fields": fields
        }
        
        r = requests.get(url, headers=self.user.headers(), params=params)
        
        data = r.json()
        return data

    def search(self, q = None, fields = None, maxResults = 100):
        
        token = None
        
        if q == None:
            q = "trashed != true"

        print 10*"=", "file.search"
        print "Query:", q
        
        if fields == None:
            fields = "items("+ self.fields + "),nextPageToken"

        result = []
        
        while True:
            
            data = self._search(q, token, fields, maxResults)
            
            token = data.get('nextPageToken')
            # print "Token", token
            
            items = data.get('items', [])
            # print "Found", len(items), "items"
            
            result.extend(items)
            
            if not token:
                break
        
        print "\nDone."
        return result

    def fileGet(self, fileId, fields = None):
        """docstring for fileGet"""
        
        if not fields:
            fields = self.fields
            
        url = 'https://www.googleapis.com/drive/v2/files/' + fileId
        
        params = {
            "fileId": fileId,
            "fields": fields
        }

        r = requests.get(url, headers=self.user.headers(), params=params)
        
        if r.status_code == requests.codes.ok:
            data = r.json()
            return data
            
    def getName(self, fileId):
        """docstring for getName"""
        title = self.fileGet(fileId, 'title')
        if title:
            return title.get('title')

    def makeCopy(self, items, fields = None):
        """docstring for makeCopy"""
        
        if fields == None:
            fields = self.fields
        
        params = {
            "fields": fields
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        headers.update(self.user.headers())
        # print headers
        
        threads = []
        q = Queue.Queue()
        
        for item in items:
            # print item
            fileId = item.get('id')
            newFileId = item.get('newFileId')
            
            if newFileId:
                copyId = newFileId
            else:
                copyId = fileId
            
            title = item.get('title')
            parents = item.get('parents', [])
            
            payload = {
                "title": title,
                "parents": parents
            }
            # print payload
            
            url = "https://www.googleapis.com/drive/v2/files/" + copyId + "/copy?" + urllib.urlencode(params)
            # print url
        
            new_thread = URLRequestThread(
                q,
                "POST",
                url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            new_thread.setName(fileId)
            threads.append(new_thread)
            new_thread.start()

        for t in threads:
            t.join()
        
        result = {}
        
        while not q.empty():
            
            index, data = q.get()
            result[index] = data
                
        return result

    def update(self, fileId, **kwargs):
        """docstring for insertFile"""
        
        params = {
            'addParents': ",".join(kwargs.get('addParents', [])),
            'removeParents': ",".join(kwargs.get('removeParents', [])),
            'fields': kwargs.get('fields', self.fields)
        }
        
        url = 'https://www.googleapis.com/drive/v2/files/' + fileId
        
        r = requests.put(url, headers=self.user.headers(), params=params)
        
        return r.json()

    def updateFiles(self, items, fields = None):
        """docstring for updateFiles"""
        if fields == None:
            fields = self.fields
        
        threads = []
        q = Queue.Queue()
        headers = self.user.headers()
        
        for item in items:
            # print item
            folderId = item.get('folderId')
            newFolderId = item.get('newFolderId')
            addParents = item.get('addParents', [])
            removeParents = item.get('removeParents', [])
            
            params = {
                "addParents": ",".join(addParents),
                "removeParents": ",".join(removeParents),
                "fields": fields
            }
            # print newFolderId
            url = 'https://www.googleapis.com/drive/v2/files/' + newFolderId
            
            new_thread = URLRequestThread(
                q,
                "PUT",
                url,
                headers=headers,
                params=params
            )
            
            new_thread.setName(folderId)
            threads.append(new_thread)
            new_thread.start()

        for t in threads:
            t.join()
        
        result = {}
        
        while not q.empty():
            
            index, data = q.get()
            result[index] = data
                
        return result

    def insert(self, **kwargs):
        """docstring for insertFile"""
        params = {
            'fields': kwargs.get('fields', self.fields)
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            'title': kwargs.get('title', 'Untitled'),
            'parents': kwargs.get('parents', []),
            'mimeType': kwargs.get('mimeType', 'application/vnd.google-apps.folder')
        }
        
        headers.update(self.user.headers())
        
        url = 'https://www.googleapis.com/drive/v2/files?' + urllib.urlencode(params)
        
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        
        return r.json()

    def insertFiles(self, items, fields = None):
        """docstring for insertFiles"""
        
        if fields == None:
            fields = self.fields
        
        params = {
            "fields": fields
        }

        url = "https://www.googleapis.com/drive/v2/files?" + urllib.urlencode(params)
        # print url

        headers = {
            "Content-Type": "application/json",
        }
        
        headers.update(self.user.headers())

        threads = []
        q = Queue.Queue()
        
        for item in items:
            itemId = item.get('id')
            title = item.get('title', 'Untitled')
            parents = item.get('parents', [])
            mimeType = item.get('mimeType', 'application/vnd.google-apps.folder')
    
            payload = {
                "title": title,
                "parents": parents,
                "mimeType": mimeType
            }
            # print payload
    
            new_thread = URLRequestThread(
                q,
                "POST",
                url,
                headers=headers,
                data=json.dumps(payload)
            )

            new_thread.setName(itemId)
            threads.append(new_thread)
            new_thread.start()

        for t in threads:
            t.join()
        
        result = {}
        
        while not q.empty():
            
            index, data = q.get()
            result[index] = data
                
        return result

def main():
    """docstring for main"""
    pass

if __name__ == '__main__':
    main()