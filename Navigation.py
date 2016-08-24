from Common import query_yes_no,colour
import os

def listFiles(directory = "./",include = None, exclude = None):
	# takes directory and returns all fit/fits files
	filelist = {}
	i = 1
	
	if include is not None:
		for file in os.listdir(directory):
			if file.endswith(".fit") or file.endswith(".fits"):
				for name in include:
					if name in file:
						print "%d - %s\t\t\t" % (i,file)
						filelist[str(i)] = file
						i = i + 1
						#break
					else:
						pass

	elif exclude is not None:
		for file in os.listdir(directory):
			printq = True
			if file.endswith(".fit") or file.endswith(".fits"):
				for name in include:
					if name in file:
						printq = False
					else:
						pass
				if printq == True:
					filelist[str(i)] = file
					i = i + 1
				else:
					pass
				
	else:
		for file in os.listdir(directory):
			if file.endswith(".fit") or file.endswith(".fits"):
				print "%d - %s\t\t\t" % (i,file)
				filelist[str(i)] = file
				i = i + 1
				
	return filelist

def getFile():
	filelist = listFiles()    
	fileSelec=str(raw_input(colour.bold + "File no.: " + colour.endc))
	return filelist[fileSelec]
