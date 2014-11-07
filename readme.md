#gDriveMover
gDriveMover helps you to move your Google Drive-Data from one Google account to an other.

Imagine you started using Google Drive, before your company even knew what the Google Apps Platform means for their business.
Now it is the time to move on and make the switch to your company Google account, taking all your existing documents with you.

##Process
* _source_: check domain sharing settings (make outside sharing possible)
* _source/target_: make sure enough free space is available
* [Register a Google Drive API Client in Developer Console](https://github.com/jalmeroth/gDriveMover/wiki/API_Client)
* run ./gDriveMover
	* authorize accounts (source, target)
	* create config file (gDrive.json)
	* create a folder on source
		* share this folder with your target-account (Can edit)
	* create a folder on target
	* listFilesFolders
	* createFolders
	* moveFolders
	* copyFilesSource
	* copyFilesTarget
* _source_: delete source-folder including all files

##Prerequisites
* [Python Requests: HTTP for Humans](http://docs.python-requests.org/en/latest/user/install/#install)

##FAQ

####Shut up and take my money!
We are not accepting donations at this time.

####Will my documents versions be preserved?
No. Google does not copy the documents version history.

####Which editions of Google Drive are supported?
All flavours of [Google Apps](https://support.google.com/a/answer/175121) are supported:

* Google Apps Unlimited (includes Google Apps for Education)
* Google Apps for Work (includes special editions for nonprofits and government agencies)
* Legacy free edition of Google Apps (no longer available to new customers)

###Questions or need some help?
Send me an e-mail to: <gDriveMover@almeroth.com>.
