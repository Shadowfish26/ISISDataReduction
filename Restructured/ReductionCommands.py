import os
from pyraf import iraf

class fitsFile(object):
	
	def __init__(self,totalDir,fileType):
		self.newFile(totalDir,fileType)
	
	def reset(self):
		self.fileName = None
		self.fileType = None
		self.arm = None
		self.totalDir = None
		self.exists = False
		
		# Has it been calibrated in any way WAVELENGTH + FLUX
		
	def newFile(self,totalDir,fileType):
		self.reset()
		self.totalDir = totalDir
		self.fileType = fileType
		self.fileName = self.getFile()
		if self.fileName:
			self.exists = True
		self.extFix()

	def getFile(self):
		fitsFile = None
		for file in os.listdir("./"):
			if file.startswith(self.fileType) == True:
				if file.endswith(".fit") == True or file.endswith(".fits") == True:
					fitsFile = file
				else:
					pass
			else:
				pass
		if fitsFile == None:
			print "%s not found, please enter the name of the file" % self.fileType
			# TO BE WRITTEN
		return fitsFile
		
	def getArm(self):
		try:
			iraf.imgets(self.fileName + "[1]","ISIARM")
			self.arm = iraf.imgets.value
		except:
			self.arm = "red" 
		
	def extFix(self):
		# Some files from database have wrong extension names, needs to be altered before you can use the file
		try:
			iraf.display()
			iraf.hedit(self.totalDir + self.fileName + "[1]",fields="EXTNAME",value="extension1",add="yes",update="yes",verify="no")
		except:
			print "Extension fix failed"
			pass
	
	
def loadFiles(totaldir):
	#standard = getFile(totaldir,standard)
	#arc = getFile(totaldir,arc)
	pass

def ExtractStand(standardC, name=False, outfile="apallStd"):
	if name==True:
		return "Extract the spectrum for the standard star"
	else:
		pass
	
	standard = standardC.fileName
	print standard
	
	outfile = totaldir + outfile
	#remove(outfile + ".fits")

	# Takes in standards name and does apall
	print "Extracting standard"
	iraf.apextract()
	iraf.apall(standard + "[1]", backgro="fit", out=outfile, interac="yes",trace="yes",fittrac="yes",extract="yes",extras="yes",review="yes")
	print "The above seems to be buggy \n\n\n\n\n"

	return outfile
	
def WavelengthCalibrate(standardC,arcC,name=False):
	if name==True:
		return "Identify the spectral lines?"
	else:
		pass
	
	WavelengthExtract(standardC,arcC)
	WavelengthManual(standardC)
	
def WavelengthExtract(standardC):	
	standard = standardC.fileName
	iraf.apall(arc + "[1]", out= cuar, ref=standard + "[1]", recen="no", trace="no", back="no", intera="no")
	print "cuar.fits file written\n"
	return True
	
def WavelengthManual(standardC,arcC):
	standard = standardC.fileName
	arc = arcC.fileName
	print "Identify the spectral lines in the next image (CuAr + CuNe). Do not resize the window, make it full screen or it will bug out. Trust me."
	print "You can find maps of the arclines at ~crb/ing/arcl/arclines"
	print "m - Write wavelength, f - fit, l - autodo lines, q - quit"
	iraf.imgets(standard + "[1]","CENWAVE")
	print ("The central wavelength is %s" % iraf.imgets.value)
	while True:
		highorlow = raw_input(colour.bold + '(H)igh resolution or (L)ow Resolution: ' + colour.endc)
		linelistdir = g.homedir+g.reductdir+"/linelists/"
		if highorlow == "H":
			print "High resolution linelist will be used"
			iraf.identify(cuar, coordli=linelistdir + "cuarcune_IDS_hr.dat")
			return True
		elif highorlow == "L":
			print "Low resolution linelist will be used"
			iraf.identify(cuar, coordli=linelistdir + "cuarcune_IDS_lr.dat")
			return True
		elif highorlow == "Q":
			return False
		else:
			pass
			

