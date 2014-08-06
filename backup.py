import os
import sys
import json
import time
import string
import shutil
import zipfile

#To do:
# - Add support for encryption

def check_config(data):

	''' check for validity of config file '''

#	missing = filter(lambda x: not x in data, ["Drive", "Dirs", "Interval", "Encrypt", "Key"])
	missing = filter(lambda x: not x in data, ["Drive", "Dirs", "Interval", "Zip"])
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

#	val = data["Encrypt"]
#	if not isinstance(val, bool):
#		print "Error: Encrypt must be a boolean"
#		sys.exit(-1)
#	if val:
#		val = data["Key"]
#		if not isinstance(val, str):
#			print "Error: Key must be a string"
#			sys.exit(-1)
#		if not val:
#			print "Error: Key cannot be empty"
#			sys.exit(-1)



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
	print "Backup started"
	start = time.time()

	dirs = config["Dirs"]
	drv  = config["Drive"].upper()
	zip_ = config["Zip"]

	if not os.path.exists("%s:\\" % drv):
		print "Error: Drive not found"
		sys.exit(-1)

	path = "%s:\\Backups" % (drv)
	if not os.path.exists(path):
		os.mkdir(path)

	dpath = time.strftime("%H.%M.%S %d.%m.%Y", time.localtime())
	path = os.path.join(path, dpath)
	if zip_:
		path += ".zip"
		zfile = zipfile.ZipFile(path, "w")
	else:
		if not os.path.exists(path):
			os.mkdir(path)

	for dir_ in dirs:
		for p, dnames, fnames in os.walk(dir_):

			op = p
			p = p.split("\\")
			p[0] = p[0].replace(":", "")
			ps = ["\\".join(p[:i]) for i in range(1,len(p)+1)]
			if not zip_:
				for d_path in ps:
					jp = os.path.join(path, d_path)
					if not os.path.exists(jp):
						os.mkdir(jp)

			p = os.path.join(path, ps[-1])
			for file_ in fnames:
				if zip_:
					zfile.write(os.path.join(op, file_), os.path.join(op, file_))
				else:
					try:
						shutil.copy(os.path.join(op, file_), p)
					except:
						print "Error: Couldn't copy file %s" % os.path.join(op, file_)
	if zip_:
		zfile.close()
	print "Backup completed in %d seconds" % int(time.time() - start)

def main():
	load_config()
	while True:
		backup_files()
		time.sleep(config["Interval"])

if __name__ == "__main__":
	main()
