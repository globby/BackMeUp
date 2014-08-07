import os
import sys
import json
import time
import string
import shutil
import zipfile

#	BackMeUp - Python local backup script
#	Copyright (C) 2014 globby
#
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License along
#	with this program; if not, write to the Free Software Foundation, Inc.,
#	51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

def check_config(data):

	''' check for validity of config file '''

	missing = filter(lambda x: not x in data, ["Drive", "Dirs", "Interval", "Zip", "FollowSym", "RetryDrive", "RetryIntv", "RetryTimes"])
	if missing:
		print "Error: Field%s: %s missing from config.json" % ("s"*(len(missing) < 1), missing[0] if len(missing) == 1 else str(missing))
		sys.exit(-1)

	val = data["Drive"]
	if not val.upper() in list(string.ascii_uppercase):
		print "Error: Invalid Drive letter"
		sys.exit(-1)

	val = data["Dirs"]
	if not isinstance(val, list):
		print "Error: Dirs must be a list of directories"
		sys.exit(-1)
	failed = []
	for directory in val:
		if not os.path.exists(directory):
			failed.append(directory)
	if failed:
		print "Error: Director%s do%sn't exist: %s" % ("ies" if len(failed) > 1 else "y", "es"*(len(failed) > 1), failed[0] if len(failed) == 1 else str(failed))
		sys.exit(-1)

	val = data["Interval"]
	if not isinstance(val, int):
		print "Error: Interval must be an integer"
		sys.exit(-1)
	if not val > 0:
		print "Error: Interval must be > 0"
		sys.exit(-1)

	val = data["Zip"]
	if not isinstance(val, bool):
		print "Error: Zip must be a boolean"
		sys.exit(-1)

	val = data["FollowSym"]
	if not isinstance(val, bool):
		print "Error: FollowSym must be a boolean"
		sys.exit(-1)

	val = data["RetryDrive"]
	if not isinstance(val, bool):
		print "Error: RetryDrive must be a boolean"
		sys.exit(-1)
	if val:
		val = data["RetryIntv"]
		if not isinstance(val, int):
			print "Error: RetryIntv must be an integer"
			sys.exit(-1)
		if not val > 0:
			print "Error: Interval must be > 0"
			sys.exit(-1)

		val = data["RetryTimes"]
		if not isinstance(val, int):
			print "Error: RetryTimes must be an integer"
			sys.exit(-1)
		if not val > 0 and not val == -1:
			print "Error: RetryTimes must be > 0"
			sys.exit(-1)

def load_config():
	global config
	
	''' load the config.json file '''

	if os.path.isfile("config.json"):
		try:
			with open("config.json", "rb") as f:
				data = f.read()
		except IOError:
			print "Error: Failed to open config.json"
			sys.exit(-1)
		try:
			data = json.loads(data)
		except:
			print "Error: Failed to parse config.json"
			sys.exit(-1)

		check_config(data)
		config = data
		print "Successfully loaded config.json!"
	else:
		print "Error: Couldn't find config.json"

def backup_files():

	''' backup files '''

	start = time.time()

	dirs = config["Dirs"]
	drv  = config["Drive"].upper()
	zip_ = config["Zip"]

	if not os.path.exists("%s:\\" % drv):
		print "Error: Drive not found"
		return False

	print "Backup started"

	path = "%s:\\Backups" % (drv)
	if not os.path.exists(path):
		os.mkdir(path)

	dpath = time.strftime("%H.%M.%S %d.%m.%Y", time.localtime())
	path = os.path.join(path, dpath)

	if zip_:
		path += ".zip"
		zfile = zipfile.ZipFile(path, "w")

	for dir_ in dirs:
		if zip_:
			for path, dirs, files in os.walk(dir_):
				for f in files:
					zfile.write(os.path.join(path, f))
			zfile.close()
		else:
			try:
				shutil.copytree(dir_, path, symlinks=config["FollowSym"])
			except:
				print "Error: Failed to copy files"
				sys.exit(-1)

	print "Backup completed in %d seconds" % int(time.time() - start)
	return True

def main():
	load_config()
	retries = 0
	while True:
		_ = backup_files()
		if _:
			time.sleep(config["Interval"])
		else:
			retries += 1
			if retries <= config["RetryTimes"] or config["RetryTimes"] == -1:
				print "Retrying in %d seconds ..." % config["RetryIntv"]
				time.sleep(config["RetryIntv"])
			else:
				print "RetryTimes exhausted. Giving up."
				break

if __name__ == "__main__":
	main()
