import numpy as np
from math import log10
from math import ceil
import sys
from pyraf import iraf
import os
import subprocess

from pyraf import irafexecute

from time import sleep

from collections import OrderedDict

import pickle

from Common import colour as colour

from Common import query_yes_no as query_yes_no

from Navigation import chooseArm as chooseArm
from Navigation import ChooseDirectory as ChooseDirectory
from Navigation import chooseDate as chooseDate

#import Globals as g

print "Loading required packages"

cache = irafexecute._ProcessCache()

iraf.noao()
iraf.onedspec()
iraf.twodspec()
iraf.apextract()
iraf.imred()
iraf.crutil()
iraf.images()
iraf.imgeom()
iraf.stsdas()
iraf.imred()
iraf.ccdred()
iraf.task(lacos_spec = "./lacos_spec.cl")

import ReductionCommands


standard = "None"
arc = "None"
cenwave = "None"
stdname = "None"
obsdate = "None"
standardarm = ""
arcarm = ""
grating = ""
rawSky = ""
arm = ""
totaldir = ""

#Sometimes if I process the image, then it only has one extension
#standardextension = ""
standardextension = "[1]"
skyextension = ""
#skyextension = "[1]"

#saveFiles()

def RMLoop():
    global totaldir
    global standard
    global arc
    global rawSky
    GratingDict = g.GratingDict
    if g.cont == True:
        g.arm = g.colour
        g.datedir = "/" + g.date

    else:
        chooseDate()
        chooseArm()
    totaldir = g.homedir+g.reductdir+g.datedir+"/"+g.arm+"/"
    print "The complete working directory is %s" % totaldir
    getFiles()
    
    
    # Run the commands in this order to do a complete run.

    
    commandlist = OrderedDict()
    #commandlist['DownloadStand']=[GetStandard,standard]
    commandlist['Extract']=[ExtractStand,standard]
    commandlist['WaveCal']=[WavelengthCalibrate,standard,arc]
    commandlist['ApplyWave']=[ApplyWavelength,standard,"apallStd.fits"]
    commandlist['Sens']=[SensFunc,stdname]
    commandlist['ApplyFlux']=[ApplyFlux,"waveapallStd"]
    commandlist['ABConv']=[ABConversion]
    
    skylist = OrderedDict()
    skylist['Extract'] = [extractSky]
    #skylist['Cosmic'] = []
    skylist['Block'] = [blkAvg]
    skylist['Wavecal'] = [otherskyCal,standard,"blkavgSky.fits","waveblkavgSky"]
    skylist['Fitlines'] = [testFitLines,standard,"blkavgSky.fits","waveblkavgSky"]
    skylist['ApplyAB'] = [ApplyAB]
    
    refdic = {"2":commandlist['Extract'],"3":commandlist['WaveCal'],"4":commandlist['ApplyWave'],"5":commandlist['Sens'],"6":commandlist['ApplyFlux'],"7":commandlist['ABConv'],"P":[splot],"D":[GetStandard,standard],
    "K":[saveFiles],"L":[getFiles],"S1":[extractSky],"S2":[removeCosmics],"S3":[blkAvg],"S4":[skyCalib,standard,"blkavgSky.fits","waveblkavgSky"],"C1":[chooseDate],"C2":[chooseArm],"A":[ApplyAllToObj],"S5":[ApplyAB],"T1":[BiasLevel],
    "MMM":[testFitLines,standard,"blkavgSky.fits","waveblkavgSky"]}
    
    DoWhat = "None"
    
    while True:
        cache.flush()
        os.chdir(totaldir)        
        reload(iraf)

        try:
            GetStdName()
        except:
            print "The error"
            pass
        # This first bit is to set the colour of the word arm,
        # Probs a bit unecessary 
        print colour.endc
        #if arm == "blue":
        #    print colour.blue
        #else:
        #    print colour.red
        if standardarm == "Blue arm":
            standc = colour.blue
        else:
            standc = colour.red
        if arcarm == "Blue arm":
            arcc = colour.blue
        else:
            arcc = colour.red
        if g.arm == "blue":
            armc = colour.blue
        else:
            armc = colour.red

        
        if g.cont == True:
            while True:
                try:
                    DoIt(*refdic["L"])
                    print "Done all the steps for getting the file"
                    if rawSky == "None":
                        # print that it's done
                        compfile = open("/data/nik/Reductions/completedblue", "a")
                        compfile.write(g.date + "\n")
                        exit()
                    else:
                        for f in skylist:
                            DoItQ(*skylist[f])
                except:
                    # write to a file here
                    failfile = open("/data/nik/Reductions/failedblue","a")
                    failfile.write(g.date + "\n")
                    exit()
            
            
            
            
            
            
            
            # GUI
        else:

                
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            print "Welcome to my assisted reduction program!"
            print "First I would recommend you download the standard (D) if you have not already!!!\n"
            print "The files you are currently using:"
            print "\tStandard - %s (%s, %s%s%s)" % (standard.replace(totaldir,""),stdname,standc,standardarm,colour.endc)
            print "\tArc - %s (%s%s%s)" % (arc.replace(totaldir,""),arcc,arcarm,colour.endc)
            print "\tCenwave of std - %dA (%d-%d)" % (float(cenwave), float(cenwave)+-int(GratingDict[grating][0]/2),float(cenwave)+int(GratingDict[grating][0]/2))
            print "\tDate - %s and arm - %s%s%s" % (obsdate,armc, g.arm,colour.endc)
            print "\tGrating - %s" % grating
        #    try:
        #        print GratingDict[grating]
        #    except:
        #        print "Couldn't get grating information"
            try:
                print  ("\nWhat would you like to do?\n"
                    "--------------------------------\n"
                    "   Flux and wavelength calibrations\n"
                    "--------------------------------\n"
                    + colour.purple + "1 - Do a complete runthrough\n"
                    "2 - Extract the standard star\n"
                    "3 - Identify spectral lines\n"
                    "4 - Apply the wavelength calibrations\n"
                    "5 - Calculate a sensitivity function\n"
                    "6 - Apply the flux calibrations\n"
                    "7 - Convert the standard into AB Magnitudes\n"
                    "A - Apply calibrations to another standard to check them\n"
                    "--------------------------------\n"
                    + colour.teal + "S1 - Extract Sky (Including auto debiasing)\n"
                    "S2 - Cosmic ray removal (OBSOLETE)\n"
                    "S3 - Shrink to one dimensional image\n"
                    "S4 - Calibrations (Including wavelength correction)\n"
                    "S5 - AB Conversion\n"
                    # "S4 - Wavelength calibration (1st)\n"
                    # "S5 - Flux calibration (2nd)\n"
                    + colour.endc +
                    "--------------------------------\n"
                    "   Loading files etc.\n"
                    "--------------------------------\n"
                    "D - Download the standard (automatically - not always possible)\n"
                    "P - Show files and splot one of them\n"
                    "K - Input file names\n"
                    "L - Try and reload files\n"
                    "C1/2 - Change directory/arm (Doesn't actually work due to IRAF bug) (Might work now)\n"
                    "0 - Quit\n"
                    "--------------------------------\n"
                    "Last issued command was - %s") % (DoWhat)
                if standardarm != arcarm or standardarm.lower() != g.arm + " arm":
                    print colour.red + colour.bold + "WARNING. ARMS / INSTRUMENTS ARE NOT CONSISTENT"
                    print "DO NOT TRY AND RUN ANY COMMANDS BECAUSE THEY WON'T CALIBRATE CORRECTLY"
                    print "I won't stop you from running the commands, just please change the files"
                    print "Try running 'L' to load files from the new arm?" + colour.endc
                    match = 0
                else:
                    match = 1
                print armc
                DoWhat=raw_input("> ")
            except:
                DoWhat = "0"
            
            DoWhat = DoWhat.upper()
        
            
            if str(DoWhat) == "0" or str(DoWhat) == '':
                if query_yes_no('Are you sure you want to quit?',default="yes") == True:  
                    RemoveEverything()        
                    print "Quitting..."
                    print "\033[0m"
                    sleep(1)
                    break
                else:
                    pass
            elif str(DoWhat) == "R":
                RemoveEverything()
                
            elif str(DoWhat) == "TEST":
                while True:
                    DoIt(*refdic["L"])
                    if rawSky == "None":
                        break
                    else:
                        for f in skylist:
                            DoItQ(*skylist[f])
                    
            elif str(DoWhat) == "1":
                if standard == "None" or arc == "None":
                    print "Please enter the files first!"
                else:
                    if query_yes_no("Are you sure you want to do this?") == True:
                        for f in commandlist:
                            DoItQ(*commandlist[f])
                    else:
                        pass
                Continue()
            elif str(DoWhat).startswith('C') == True:
                DoIt(*refdic["C1"])
                DoIt(*refdic["C2"])
                try:
                    totaldir = g.homedir+g.reductdir+g.datedir+"/"+g.arm+"/"
                    print "Should've changed to %s" % totaldir
                    print "Make sure you run 'L' or your files won't be reloaded"
                except:
                    print "No arm selected / folder doesn't exist, select it now"
                    print "Don't know how you've managed this tbh"
                    Continue()
                os.chdir(totaldir)
                reload(iraf)
                DoIt(*refdic["L"])
                # HAVE TO RELOAD EVERYTHING, COULD'VE DONE THIS AGES AGO AND FIXED A LOT OF PROBLEMS ...........
                # WAS NEVER A BUG IN IRAF AFTER ALL HAHAHAHAHAHAHAHAHA///
                # NOT CHANGING IT AGAIN FUCK THAT
                commandlist['Extract']=[ExtractStand,standard]
                commandlist['WaveCal']=[WavelengthCalibrate,standard,arc]
                commandlist['ApplyWave']=[ApplyWavelength,standard,"apallStd.fits"]
                commandlist['Sens']=[SensFunc,stdname]
                commandlist['ApplyFlux']=[ApplyFlux,"waveapallStd"]
                commandlist['ABConv']=[ABConversion]
                
                refdic = {"2":commandlist['Extract'],"3":commandlist['WaveCal'],"4":commandlist['ApplyWave'],"5":commandlist['Sens'],"6":commandlist['ApplyFlux'],"7":commandlist['ABConv'],"P":[splot],"D":[GetStandard,standard],
            "K":[saveFiles],"L":[getFiles],"S1":[extractSky],"S2":[removeCosmics],"S3":[blkAvg],"S4":[skyCalib,standard,"blkavgSky.fits","waveblkavgSky"],"C1":[chooseDate],"C2":[chooseArm],"A":[ApplyAllToObj],"S5":[ApplyAB],"T1":[BiasLevel]}
        
                    
                
                
                
            else:
                try:
                    sleep(1)
                    DoIt(*refdic[str(DoWhat)])
                    Continue()
                except:
                    print "Command not recognised / process died"
                    print "LOVE TRYING TO DEBUG WHEN THIS HAPPENS"
                    Continue()
                    pass
