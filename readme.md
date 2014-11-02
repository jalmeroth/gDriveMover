#gDriveMover
The purpose of gDriveMover is to help you move your Google Drive-Data from one Google account to an other.

Imagine you started using Google Drive, before your company even knew what the Google Apps Platform means for their business.
Now it is the time to move on and make the switch to your company Google account, taking all your existing documents with you.

###Source
This is your old account. Let us name it <checker86@gmail.com>.

###Target
This is your shiny new corporate account. Let us name it <firstname.lastname@cool-company.com>.

##Process
* _source_: check domain sharing settings (make outside sharing possible)
* _source/target_: make sure enough free space is available
* _target_: create two folders (e.g. _Source, _Target)
	* share source-folder with your source account (Can edit)
* Register API Client in Developer Console
	* create config file (gDrive.json)
* run ./gDriveMover
	* authorize accounts (source, target)
	* listFilesFolders
	* createFolders
* _target_: unshare folder

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
