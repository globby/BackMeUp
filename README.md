BackMeUp
========

#### Description
A simple but functional python backup script


#### Config.json explained
* Drive - Letter of the drive to back up to
* Dirs - A list of directories to back up
* Interval - Number of seconds between each backup
* Zip - Compile into a zip file
* FollowSym - Follow symlinks
* RetryDrive - Retry the drive if not found
* RetryIntv - Number of seconds before retrying drive
* RetryTimes - Number of times to retry drive before quitting (-1 for infinite)
* DelOldBkps - Delete old backups
* DelAfter - Only keep the x newest backups


#### To do:
* Add encryption capabilities
