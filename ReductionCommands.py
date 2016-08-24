########################################################################
# Standard Star Reduction Commands v 0.1                               #
# This file should contain all the commands to wavelength and flux     #
# calibrate a standard star with a given spectrum                      #
# All sky steps should be obtained in a different file                 # 
#                                                                      #
#                                                                      #
#                                                                      #
#                                                                      #
#                                                                      #
########################################################################


import os
from pyraf import iraf

from Common import remove,colour,query_yes_no

import Navigation

#This has to be done because for some reason PyRaf will not terminate
#the process when it's done. This should be a CLEAN EXIT. HOPEFULLY.
#Just type in `killIraf(iraf.MODULE)` e.g. `killIraf(iraf.display)`
#THIS HAS TAKEN ME MONTHS TO FIGURE OUT
from pyraf.irafexecute import processCache

#For spectra
iraf.noao()
#Apextract
iraf.twodspec()
#Identify/wave cal/splot
iraf.onedspec()

def killIraf(module = "None"):
	# done as a function just incase it fails
	try:
		#processCache.terminate(module)
		processCache.flush()
	except:
		pass

class fitsFile(object):
	
	def __init__(self,fileType,totalDir = "./"):
		self.newFile(fileType, totalDir = "./")
	
	def reset(self):
		self.fileName = None
		self.fileType = None
		self.arm = None
		self.totalDir = None
		self.exists = False
		
		# Has it been calibrated in any way WAVELENGTH + FLUX
		
	def newFile(self,fileType,totalDir):
		self.reset()
		self.totalDir = totalDir
		self.fileType = fileType
		self.fileName = self.getFile()
		if self.fileName is not None:
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
			fitsFile = Navigation.getFile()
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
			iraf.hedit(self.totalDir + self.fileName + "[1]",fields="EXTNAME",value="extension1",add="yes",update="yes",verify="no")
			killIraf(iraf.hedit)
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

	# Takes in standards name and does apall
	print "Extracting standard"
	try:
		iraf.apextract()
		iraf.apall(standard + "[1]", backgro="fit", out=outfile, interac="yes",trace="yes",fittrac="yes",extract="yes",extras="yes",review="yes")
	except:
		pass

	return outfile
	
def WavelengthCalibrate(standardC,arcC,name=False):
	if name==True:
		return "Identify the spectral lines?"
	else:
		pass
	
	arctoCal = WavelengthExtract(standardC,arcC)
	# This needs to be a function that will either do it automagically or ask for it to be done manually
	# i.e. use the WavelengthCalibrate function in TESTREDUCTION.PY but adapt it a bit
	WavelengthManual(standardC,arctoCal)
	
def WavelengthExtract(standardC,arcC,cuar = "cuar.fits"):	
	standard = standardC.fileName
	arc = arcC.fileName
	iraf.apextract()
	iraf.apall(arc + "[1]", out= cuar, ref=standard + "[1]", recen="no", trace="no", back="no", intera="no")
	print "cuar.fits file written\n"
	return cuar
	
def WavelengthManual(standardC,arctoCal,linelist = None):
	print "Identify the spectral lines in the next image (CuAr + CuNe). Do not resize the window, make it full screen or it will bug out. Trust me."
	print "You can find maps of the arclines at ~crb/ing/arcl/arclines"
	print "m - Write wavelength, f - fit, l - autodo lines, q - quit"
	standard = standardC.fileName
	iraf.imgets(standard + "[1]","CENWAVE")
	print ("The central wavelength is %s" % iraf.imgets.value)
	while True:
		if linelist is None:
			iraf.identify(arctoCal)
		else:
			print "Using custom linelist"
			iraf.identify(arctoCal, coordli=linelistdir + "cuarcune_IDS_hr.dat")
		if query_yes_no(colour.bold + 'Finish wavelength calibrations?: ' + colour.endc) is True:
			return
		else:
			pass
				
			
def ApplyWavelength(spectrumToCal,name=False,refimg="cuar.fits"):
    if name==True:
        return "Apply the wavelength calibration?"
    else:
        pass
	
	
	
	# Spectrum coming into this should be an EXTRACTED spectrum
	
	outputName = "wave" + spectrumToCal
	# Add a check to see if image exists?
	remove(outputName + ".fits")
	
    print "\nApplying wavelength calibration to image"
    iraf.hedit(spectrumToCal,fields="refspec1",value=refimg,add="yes",update="yes",verify="no")

    print "\nSaving new file '%s'" % outputName
    iraf.dispcor(spectrumToCal, out=outputName)    
    return outputName

