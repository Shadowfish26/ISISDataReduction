import os
import ReductionCommands as RC

def ReloadModules():
	global RC
	# Kind of hacky, but has to be done otherwise PyRaf will think
	# you're in the same directory forever... which is bad.
	reload(RC.iraf)
	RC.iraf.images()
	
os.chdir("/home/nik/Reductions/TestingFluxCalibrations")
standard = RC.fitsFile("standard")
arc = RC.fitsFile("arc")

extractedFile = RC.ExtractStand(standard)
RC.WavelengthCalibrate(standard,arc)
RC.ApplyWavelength(extractedFile)
