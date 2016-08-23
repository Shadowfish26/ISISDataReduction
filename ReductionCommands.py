def print_table(table):
    # Shamelessly took this from a stackoverflow answer, works really well
    col_width = [max(len(str(x)) for x in col) for col in zip(*table)]
    for line in table:
        print "| " + " | ".join("{:{}}".format(x, col_width[i])
                            for i, x in enumerate(line)) + " |"
    
    
def Continue():
    raw_input(colour.bold + 'Press enter to continue...' + colour.endc)

def ABConversion(name=False,outfile="FluxwaveapallStd",apallStd="waveapallStd",sky="no"):
    if name==True:
        return "Make a copy of the standard flux in ABMagnitudes?"
    else:
        pass
    
    outfile = totaldir + outfile
    apallStd = totaldir + apallStd

    if os.path.isfile(apallStd+".fits") == False:
        print "You need to run the extraction steps first"
        return None
    else:
        pass    

    removethese = ["temp.dat",
    "temp.0001.fits",
    "temp.1001.fits",
    "alteredtemp",
    "testalteration.fits"]
    
    for i in removethese:
        remove(totaldir + i)
    remove(outfile+"StdAB.fits")
    remove(outfile+"ABtemp.fits")
    
    # Ask for the slit width so the sky background value are given as mag per square arcsecond
    
    if arm == "blue":
        print "Blue arm"
        pxscale = 0.2
    else:
        print "Red arm"
        pxscale = 0.22
    
    #if query_yes_no("Is this a sky background image (will ask for slit width)", default = "no") == True:
    if sky == "yes":
        while True:
            
            iraf.imgets(rawSky+skyextension,"ISISLITW")
            SlitFactor = iraf.imgets.value
            while 2 < 1:
                slitwidth = raw_input(colour.bold + 'Enter the slitwidth in arcsecond (Leave empty to use %s): '% SlitFactor + colour.endc )
                if slitwidth == '':
                    slitwidth = SlitFactor
                    break
                else:
                    print "Using your own value of slitwidth - %s" % slitwidth
                    if query_yes_no('Are you really sure you want to use this?', default="no") == True:
                        break
                    else:
                        print "Good choice captain."
            
            iraf.imgets(rawSky+skyextension,"CCDXBIN")
            BinFactor = iraf.imgets.value
            #print "Spacial binning is %s" % iraf.imgets.value
            while 2 < 1:
                binning = raw_input(colour.bold + 'Binning (Leave empty to use %s): ' % BinFactor + colour.endc )
                if binning == '':
                    binning = BinFactor
                    break
                else:
                    print "Using your own value of binning - %s" % binning
                    if query_yes_no('Are you really sure you want to use this?', default="no") == True:
                        break
                    else:
                        print "Good choice captain."
            slitwidth = SlitFactor
            binning = BinFactor          
            #ccdheight = 20 * pxscale # height of the ccd in arcsecond apparently (since taking 20 px)
            ccdheight = pxscale
            slitname = "magsquare"
            try:
                slitarea = float(slitwidth)*float(ccdheight)*float(binning)
                break
            except:
                print "You didn't enter a number"
    else:
        slitarea = 1
        slitname = ""

    filename = outfile + ".fits"

    iraf.noao()
    iraf.onedspec()

    iraf.scopy(filename, output=totaldir + "temp", format="onedspec")
    iraf.wspectext(input = totaldir + "temp.0001.fits", output = totaldir + "temp.dat", header="no")

    pa=np.loadtxt(totaldir + "temp.dat")

    x = pa[:,0]
    y = pa[:,1]
    
    print "Performing the conversion"

    f = open(totaldir + 'alteredtemp', 'w')
    i = 0
    while i<len(x):
        try:
            #y[i] = -2.5*log10(((10E10*((x[i]*1E-10)**2))*y[i])/(3E08))-48.60
            #y[i] = -2.5*log10(((10E10*((x[i]*1E-10)**2))*y[i])/(3E08))-48.60

            if y[i] < 0:
                y[i] = 0
            else:
                pass
            
            y[i] = -2.5*log10(3.34E4*((x[i])**2)*(y[i]/slitarea)) + 8.90        # 193.2 is the square arcseconds conversion, come back later DONT FORGET ABOUT IT nvm lol

            f.write("%f  %f\n" % (x[i],y[i]))
            i = i + 1
        except:
            f.write("%f  %f\n" % (x[i],y[i-1]))
            i = i + 1
            #print i
    print "Converted"
    f.close()

    print "Writing to a new fits file"
    iraf.rspectext(input=totaldir + "alteredtemp", output=outfile+"ABtemp"+slitname+".fits")
    
    print "Making a copy of the waveapallStd to steal its headers and overwriting it"
    iraf.imcopy(input=apallStd+".fits",output=outfile+"AB"+slitname+".fits")
    iraf.imarith(operand1=outfile+"AB"+slitname+".fits",op="*",operand2="0",title=outfile+"AB"+slitname+".fits",result=outfile+"AB"+slitname+".fits")
    iraf.imarith(operand1=outfile+"AB"+slitname+".fits",op="+",operand2=outfile+"ABtemp"+slitname+".fits",title=outfile+"AB"+slitname+".fits",result=outfile+"AB"+slitname+".fits")
    try:
        print "\nMake sure you check this file against the standard %s" % stdname
    except:
        print "This bit didn't work but who cares? :)"

    print "Remove temp files"
    for i in removethese:
        remove(i)
    remove(outfile+"ABtemp.fits")

    return outfile+"AB"+slitname+".fits"


def DoItQ(function,*args):
    # Ask whether or not the person wants to run the function (will delete files)
    #question = "Do you want to run '%s'" % function(*args,name=True)
    #if query_yes_no(question) == True:
    function(*args)
    #else:
    #    pass

def DoIt(function,*args):
    function(*args)

def remove(filename):
    # This will attempt to remove whatever filename is passed.
    # Requires os
    try:
        os.remove(filename)
        print ("Removed file called %s" % filename)
    except:
        print ("Didn't remove %s" % filename)

def RemoveEverything():

    if query_yes_no("Do you want to remove all 'temporary' files?", default="no") == True:
        pass
    else:
        return
    # Useful for removing files when starting a new run, or if you have to break out
    print "Removing old temporary files"
    print "Shouldn't really run this, it hasn't been updated"
    print "DARE I SARE - LEGACY FUNCTION"

    remove("apallStd.fits")
    remove("cuar.fits")
    remove("std")
    remove("sensfunc.0001.fits")
    #remove("FluxwaveapallStd.fits")
    #remove("FluxwaveapallStdAB.fits")
    remove("waveapallStd.fits")
    remove("alteredtemp")
    remove("FluxwaveapallStdABtemp.fits")
    remove("temp.0001.fits")
    remove("temp.1001.fits")
    remove("temp.dat")

def ExtractStand(standard, name=False, outfile="apallStd"):
    if name==True:
        return "Extract the spectrum for the standard star"
    else:
        pass
    
    print standard
    print totaldir
    print os.getcwd()
    
    standard = standard.replace(totaldir,"")
    print standard
    
    outfile = totaldir + outfile
    remove(outfile + ".fits")

    # Takes in standards name and does apall
    print "Defining the standard and extracting it"
    reload(iraf)
    iraf.apextract()
    iraf.apall(standard + standardextension, backgro="fit", out=outfile, interac="yes",trace="yes",fittrac="yes",extract="yes",extras="yes",review="yes")
    #iraf.splot(outfile +".fits",band=1)
    print "The above seems to be buggy \n\n\n\n\n"

    return outfile

def WavelengthCalibrate(standard,arc,name=False):
    if name==True:
        return "Identify the spectral lines?"
    else:
        pass
    #cuar = totaldir + "cuar"
    cuar = "cuar"
    standardt = standard.replace(totaldir,"")
    arc = arc.replace(totaldir,"")
    print standard
    print os.getcwd()
    print totaldir
    remove(cuar +".fits")
    remove(totaldir + "waveapallStd.fits")
        
    
    # Takes in standard and arc then asks you to identify the spectral features
    iraf.apall(arc + "[1]", out= cuar, ref=standardt + "[1]", recen="no", trace="no", back="no", intera="no")
    print "cuar.fits file written\n"
    print "Identify the spectral lines in the next image (CuAr + CuNe). Do not resize the window, make it full screen or it will bug out. Trust me."
    print "You can find maps of the arclines at ~crb/ing/arcl/arclines"
    print "m - Write wavelength, f - fit, l - autodo lines, q - quit"
    iraf.imgets(standard + "[1]","CENWAVE")
    print ("The central wavelength is %s" % iraf.imgets.value)
    #hr = high res, lr = low res
    while True:
        highorlow = raw_input(colour.bold + '(H)igh resolution or (L)ow Resolution: ' + colour.endc)
        linelistdir = g.homedir+g.reductdir+"/linelists/"
        if highorlow == "H":
            print "High resolution linelist will be used"
            iraf.identify(cuar, coordli=linelistdir + "cuarcune_IDS_hr.dat")
            break
        elif highorlow == "L":
            print "Low resolution linelist will be used"
            iraf.identify(cuar, coordli=linelistdir + "cuarcune_IDS_lr.dat")
            break
        elif highorlow == "Q":
            break
        else:
            pass
    #iraf.identify("cuar", coordli=cwd+"/spectrallines.dat")
    
def WavelengthRecalibration(arcfile,object):
    # legacy function
    print "LEGACY FUNCTION"
    iraf.apall(arcfile + "[1]", out=object+"cuar", ref=standard + standardextension, recen="no", trace="no", back="no", intera="no")
    print "Apalled"
    iraf.reidentify(referenc = "cuar.fits",images=object+"cuar.fits", coordli="linelists$cuarcune_IDS_lr.dat",match="10",interac="yes",answer="yes")
    #iraf.identify(object+"cuar", coordli="linelists$cuarcune_IDS_lr.dat")
    return object +"cuar"
    

def ApplyWavelength(standard,spectrum,name=False,refimg="cuar.fits"):
    if name==True:
        return "Apply the wavelength calibration?"
    else:
        pass
    
    spectrum = spectrum
    if spectrum == "apallStd.fits":
        spectrum = totaldir + spectrum
    else:
        pass

    # Applies the wavelenght calibration to the standard star
    refimg = refimg
    # Could modify this so that it works for a sky background image as well
    remove("wave"+spectrum)
    print "\nApplying calibration to standard star"
    print "Say 'yes' to update\n"
    iraf.hedit(spectrum,fields="refspec1",value=refimg,add="yes",update="yes",verify="no")

    print "\nSaving new file 'wave%s'" % spectrum
    iraf.dispcor(spectrum, out=totaldir + "wave" + spectrum.replace(totaldir,""))
    
    return totaldir + "wave"+spectrum.replace(totaldir,"")

def ApplyFlux(spectrum,name=False):
    if name==True:
        return "Apply the flux calibration?"
    else:
        pass
    
    remove(totaldir + "Flux"+spectrum+".fits")
    remove(totaldir + "Flux"+spectrum+"f.fits")

    # Apply the flux calibration based on the sensfunc to the standard
    # The file structure is different if you are using the sky, so has to be different
    print "\nApplying flux calib to spectrum"
    print "\nSaving new file 'Flux%s'" % spectrum
    Fluxout = totaldir + "Flux" + spectrum
    spectrum = totaldir + spectrum
    print Fluxout
    print spectrum
    print totaldir
    print g.cwd
    extinctionfile = g.cwd + "/extinctionwithwave.dat"
    print extinctionfile
    try:
        iraf.calibrate(input=spectrum,output=Fluxout,sensiti=totaldir + "sensfunc",extinction=extinctionfile)
        #iraf.calibrate(input=spectrum,output="Flux"+spectrum,sensiti="sensfunc")
        outputfile=Fluxout
    except:
        #try:
        iraf.calibrate(input=spectrum,output=Fluxout + "f",sensiti=totaldir + "sensfunc.0001", extinction=extinctionfile)
        outputfile=Fluxout+"f"
        #except:
        #    print "No sensfunc file is here oh no!"
    print "Applied"
    return outputfile 

def GetStandard(standard,name=False): #Download Standard
    if name==True:
        return "Determine and download the standard star?"
    else:
        pass

    # Check the name of the standard used for flux calibration and then attempt to donwload it
    # Uses the ING database which all follow similar naming patterns
    # There shouldn't be any that it can't recognise, but who knows~
    print "\nGetting standard data for flux calibration"
    print "The name of the standard and its datafile must be in ./standards"
    print "Will now try to automatically download it"
    standardsdir = totaldir + "standards"
    print "Standards directory should be %s" % standardsdir

    iraf.imgets(standard + standardextension,"CAT-NAME")
    stdname = iraf.imgets.value

    print "Adding %s to the database" % stdname

    # IRAF demands that the names follow this format
    stdname = stdname.replace("+","_")
    stdname = stdname.replace("-","_")
    stdname = stdname.replace("SP","sp")
    
    # Make a directory if it doesn't already exist and then attempt to download the file
    subprocess.call(["mkdir",standardsdir])
    if os.path.isfile(standardsdir + stdname+".dat") == False:
        subprocess.call(["wget","-O",standardsdir+"/"+stdname+".dat","http://catserver.ing.iac.es/landscape/tn065-100/"+stdname+".dat"])
    else:
        print "File already exists"

    # Check if the file is 0kb and then try the _1a extension
    fsize = os.path.getsize(standardsdir+"/"+stdname+".dat")
    if fsize == 0:
        print "There is more than one file perhaps"
        print "The file has not downloaded correctly. Will try and download another one."
        subprocess.call(["wget","-O",standardsdir+"/"+stdname+".dat","http://catserver.ing.iac.es/landscape/tn065-100/"+stdname+"_1a.dat"])
    else:
        print "File seems to be okay!"
        pass
    
    if fsize == 0:
        print "You are going to have to get the data manually, soz"
        print "Google the name of standard and try to find data for it, I wrote a little sequence to convert \n"
        print "AB mag format to IRAF format"
        return
    else:
        pass

    # Add the standard name to the required data file
    f = open(standardsdir + "/standards.men", "w")
    f.write("%s.dat" % stdname)
    f.close()

    print "\nThe file should now have been downloaded and added to the database"

def SensFunc(stdname,name=False):
    if name==True:
        return "Determine the sensfunc?"
    else:
        pass
    
    if checkforFileSKY(totaldir + "std") == True or checkforFileSKY(totaldir + "sensfunc.0001.fits") == True:
        if query_yes_no('A sensfunc already exists, are you really sure you want to overwrite it?: ', default="no") == True:
            pass
        else:
            print "Perhaps make a backup first, exiting this function now."
            return
    else:
        pass
    
    if os.path.isfile(totaldir + "waveapallStd.fits") == False:
        print "Please run 2-4 to extract and wavelength calibrate the standard"
        return
    else:
        pass

    remove(totaldir + "std")
    remove(totaldir + "sensfunc.0001.fits")
    # Calculate the sensfunc based on the bandpasses in the downloaded datafile vs.
    # the data that is in our observed standard
    print "Next step is to calculate the sensfunction"
    print "Just press enter when it asks you too and then do your sensfunc\n"

    #remove("sensfunc.0001.fits")
    #remove("std")

    #iraf.standard(totaldir + "waveapallStd.fits", output=totaldir + "std", extinction=g.cwd + "/extinctionwithwave.dat", star_name=stdname, caldir=totaldir + "standards/")
    
    # Make it ask for standard name just in case
    standardname = str(raw_input('Input name of standard (leave blank to auto get it): '))
    if standardname == '':
        stdname = stdname.lower()
    else:
        stdname = standardname.lower()
    
    print stdname
    
    
    print "Load it up and choose a range to remove, don't do any calculating this time round"
    print "Enter both values as blank if you've already done this or don't want to change anything"
    
    iraf.standard(totaldir + "waveapallStd.fits", output=totaldir + "std", extinction=g.cwd + "/extinctionwithwave.dat", star_name=stdname, caldir=totaldir + "standards/")

    #print "\nd->p to remove a point (there are two for each) then f or g to fit\n"

    iraf.sensfunc(standards=totaldir + "std",sens=totaldir + "sensfunc", extinction = g.cwd + "/extinctionwithwave.dat")
    
    remove(totaldir + "std")
    remove(totaldir + "sensfunc.0001.fits")
    
    bottomval = raw_input("Choose bottom wavelength: ")
    topval = raw_input("Choose top wavelength: ")
    if bottomval == "" or topval == "":
        pass
    else:
        bottomval = int(bottomval)
        topval = int(topval)
        f = open(totaldir + "standards/" + stdname + ".dat","r+")
        d = f.readlines()
        f.seek(0)
        for i in d:
            j=i.strip()
            q = j.split(" ")
            try:
                #print q[2]
                if q[0] == "#":
                    f.write(i)
                elif int(q[0]) > bottomval and int(q[0]) < topval:
                    f.write(i)
                else:
                    pass
            except:
                pass
        f.truncate()
        f.close()
    
    iraf.standard(totaldir + "waveapallStd.fits", output=totaldir + "std", extinction=g.cwd + "/extinctionwithwave.dat", star_name=stdname, caldir=totaldir + "standards/")

    print "\nd->p to remove a point (there are two for each) then f or g to fit\n"
    print "If you're working on my laptop, thne you can press F1 to do d->p \n"

    iraf.sensfunc(standards=totaldir + "std",sens=totaldir + "sensfunc", extinction = g.cwd + "/extinctionwithwave.dat")

# Applying the calibrations to another file

def ApplyAllToObj(): #legacy
    # Check if the calibrations have been performed before trying to apply them or else the program will just quit out
    
    #LEGACY FUNCTION, NOT PROPERLY CODED TO DO totaldir + totaldir + totaldir + totaldir + totaldir + 

    if os.path.isfile(totaldir + "database/idcuar") == False:
        print "Please perform a wavelength calibration on the standard first (using 3)"
        return
    else:
        print "Wavelength calibration file found"
        pass

    if os.path.isfile(totaldir + "sensfunc.0001.fits") == False:
        print "Please perform a flux calibration on the standard first (using 5)"
        return
    else:
        print "Extinction (sensfunc) calibration found"
        pass
    
    # Need the inputs as well (i.e. what is the standard that you are going to be applying the things to)

    for file in os.listdir(totaldir):
            if file.startswith("standard") == True and file.endswith(".fit"):
                try:                
                    filename = file
                    iraf.imgets(totaldir + filename + standardextension,"CAT-NAME")
                    standardname = iraf.imgets.value
                    if query_yes_no("Use file %s (%s)?" % (filename,standardname)) == True:
                        break
                    else:
                        pass
                except:
                    print "Error with %s" % file
            else:
                pass    
    # Extract and apply
    standard = "Dummy" # Required for some reason, I could just remove it from the function tho
    # This should be an input (below)
    # filename = "standard2.fit"
    filename = totaldir + filename
    extfile = ExtractStand(filename, outfile="tempextractfile")
    wavefile = ApplyWavelength(standard,extfile)
    fluxfile = ApplyFlux(wavefile)
    
    # standardName = 
    # Conversion of the file to AB mag
    ABfile = ABConversion(name=False,outfile=fluxfile,apallStd=wavefile)

    os.rename(ABfile,standardname+"AB.fits")
    
    # Clean up files, keep the converted file only
    print "Cleaning up files"

    remove(extfile)
    remove(wavefile)
    remove(fluxfile)
    remove(ABfile)
    remove("Fluxwavetempextractfile.fits")
    remove("FluxwavetempextractfileABtemp.fits")
    remove("wavetempextractfile.fits")
    remove("tempextractfile.fits")

    print "File saved as %s" % (standardname+"AB.fits")

    """ Need to make this remove all the other temporary files if possible, might have to return some name 
        values from the other functions (take a look at all the files that are created).
        Otherwise you can only do this once. Also it would make sense to make the filenames an input, perhaps
        read out some data from them like I usually do and also check to see if the actual calibration files
        exist, otherwise it's probably just going to crash and not create/remove files causing problems in
        the future.
    """




# Getting the sky

def SkyPresent():
    # Check if the sky file is present and then offer to load it
    global rawSky
    if os.path.isfile(rawSky) == True:
        print "Sky exists"
        return True
    else:
        if query_yes_no('Do you want to load a sky file?', default="yes") == True:
            for file in os.listdir(totaldir):
                if file.startswith("sky") == True:
                    if query_yes_no("Use %s for the sky?" % file) == True:
                        #rawSky = reductdir + "/Reductions/" + workingdir+ "/" + arm + "/" + file
                        rawSky = totaldir + file
                        CheckEXTNAME(rawSky,"[1]")    
                        return True
                    else:
                        pass
                else:
                    pass
        else:
            print "THIS GON FAIL THEN"
            return False

def extractSky():
    if SkyPresent() == False:
        print "SKY NOT PRESENT"
        return
    else:
        pass
    
    print "Going to get and subtract the BIAS first"
    BiasLevel()
    
    LACosmicRemoval()
    
    # Once debiased, remove cosmics (and add a tag like BiasLevel()
        
    remove(totaldir + "narrowedSky.fits")
    #print "\n\nLook at the sky and make sure it's okay. Select a region where they are few cosmic rays (the area chosen will include the 10 pixels to the right of the one you enter"
    #print "Also check to make sure the BIAS level has been removed, CTRL-C if it hasn't"
    #iraf.display(rawSky + skyextension,frame="1")
    #print "If the image is no good, enter Q"
    #while True:
    #    x = raw_input(colour.bold + 'Enter the left most chosen pixel: ' + colour.endc)
    #    if str(x) == "q" or str(x) == "Q":
    #        print "Stopping sky extraction..."
    #        Continue()        
    #        return
    #    else:
    #        try:
    #            x = int(x)
    #            iraf.imcopy(rawSky+skyextension+"["+str(x)+":"+str(x+20)+",*]", output = totaldir + "narrowedSky.fits")
    #            break
    #        except:
    #            print "You didn't enter an integer or q, try again"
    
    input = rawSky
    input2 = rawSky.replace(totaldir,"")
    input2 = input2.replace(".fits","")
    
    
    #convert to onedspec
    #combine as median
    #delete old files ....
    
    
    #iraf.imcopy(rawSky+skyextension+"["+str(int(ceil(coord)-regionsize))+":"+str(int(ceil(coord)+regionsize))+",*]", output = totaldir + "narrowedSky.fits")

def checkforFileSKY(filename):
    if os.path.isfile(totaldir + filename) == True:
        return True
    else:
        return False
    

def removeCosmics():
    if SkyPresent() == False:
        return
    else:
        pass
    
    if checkforFileSKY("narrowedSky.fits") == False:
        print "File - %s doesn't exist yet, run previous step"
        return
    else:
        pass
    
    remove(totaldir + "nocosmicSky.fits")
    remove(totaldir + "nocosmicSky2.fits")
    print "Automatically removing cosmic rays hopefully"
    #try:
        # This is in a try because of some stupid bug
    #    iraf.cosmicrays(totaldir + "narrowedSky.fits", output=totaldir + "nocosmicSky.fits",interactive = "no")
    #except:
    #    pass
    
    #try:
        # This is in a try because of some stupid bug
    #    iraf.display(totaldir + "narrowedSky.fits" + skyextension,frame="1")
    #    iraf.cosmicrays(totaldir + "nocosmicSky.fits", output=totaldir + "nocosmicSky2.fits",interactive = "yes",npasses="15",window="7",train="yes")
    #except:
    #    pass
    
    print "You can now remove any leftovers yourself (DS9 window)"
    print "Create a rectangle around the ray by pressing 'a' at corners, 'u' will undo your last move"
    #iraf.imedit(input=totaldir + "nocosmicSky.fits", output=totaldir + "nocosmicSkyt.fits")
    #if os.path.isfile(totaldir + "nocosmicSkyt.fits") == True:
#        remove("nocosmicSky.fits")
    #    os.rename(totaldir + "nocosmicSkyt.fits",totaldir +  "nocosmicSky.fits")
    #else:
    #    pass
    remove(totaldir + "narrowedSky.fits")

def blkAvg():
    if SkyPresent() == False:
        return
    else:
        pass
    
    #if checkforFileSKY("nocosmicSky.fits") == False:
    #    print "File - %s doesn't exist yet, run previous step"
    #    return
    #else:
    #    pass
    
    #remove(totaldir + "blkavgSky.fits")
    #print "Shrinking image to one dimensional"
    #iraf.blkavg(input=totaldir+"narrowedSky.fits",output=totaldir + "blkavgSky.fits",b1=41,b2=1)
    #print "blkavg'd"
    
#    file = rawSky
#    try:
#        iraf.imgets(rawSky + "[1]","TRIMSEC")
#    except:
#        try:
#            iraf.imgets(rawSky, "TRIMSEC")
#        except:
#            pass
#    trimsec = iraf.imgets.value
#    trimsec = trimsec.replace("[","")
#    trimsec = trimsec.replace("]","")
#    trimsec = trimsec.split(",")
#    trimsec = trimsec[0].split(":")
#    print trimsec[1]
    
    iraf.scopy(input = rawSky,output = totaldir + "allthesefiles",format="onedspec")
    iraf.combine(input = "allthesefiles.*.fits", output = "blkavgSky.fits", combine = "median")
    for files in os.listdir(totaldir):
        if "allthesefiles" in files:
            remove(files)
        else:
            pass
    print "median'd"
    
    
    
    
    
    
    
    
    # can I do something better .....
    
    
    #remove(totaldir + "nocosmicSky.fits")

def otherskyCal(standard,blkavg,waveblkavg):
    refimg = "cuar.fits"
    ApplyWavelength(standard,totaldir + blkavg,refimg=refimg)

def testFitLines(standard,blkavg,waveblkavg):
    
    #if grating == "R158R" or grating == "R316R":
    #    fitlines = "/home/nik/Reductions/fitlineslr"
    #    line = 5893.0
    #    print line
    #else:
    #    fitlines = "/home/nik/Reductions/fitlineshr" 
    #    line = 5890.0
    #    print line
   


    if grating == "R158R" or grating == "R316R":
        fitlines = "/home/nik/Reductions/fitlineslr"
        line = 5577.0
        print line
    elif grating == "R600R":
        fitlines = "/home/nik/Reductions/fitlineshr"
        line = 5890.0
        print line
    else:
        fitlines = "/home/nik/Reductions/fitlinesblue"   
        line = 4358
        print line        
    # fitlines = "/home/nik/Reductions/fitlines2"
    
    
    
    
    
    attempts = 0
    while attempts < 10:
        remove(totaldir + "/log")
        iraf.fitprofs(totaldir + waveblkavg,reg = str(int(line)-30) + " " + str(int(line)+50),pos=fitlines,log=totaldir + "/log", gfwhm="5")
        f = open(totaldir + "/log","r")
        d = f.readlines()
        f.seek(0)
        measval = 0.00
        for i in d:
            j=i.strip()
            q = j.split(" ")
            try:
                #print q[2]
                if q[0] == "#":
                    pass
                else:
                    print q[0]
                    measval = q[0]
                    break
            except:
                pass
        f.close()
        measval = float(measval)
        
        
        diff = line - measval
        
        
        if abs(diff) < 0.2:
            break
        #elif abs(diff) > 10:
        #    raise
        else:
            attempts = attempts + 1
        print diff
        
        iraf.specshift(spectra=waveblkavg,shift=diff)
        
    print waveblkavg
    filename = ApplyFlux(waveblkavg.replace(totaldir,""))
    #remove(blkavg)
    #remove(waveblkavg+".fits")
    iraf.imgets(rawSky+skyextension,"CAT-NAME")
    object = iraf.imgets.value
    
    os.rename(filename+".fits",totaldir + "Extracted"+object+".fits")
    os.rename(waveblkavg+".fits",totaldir + "wave"+object+".fits")



def skyCalib(standard,blkavg,waveblkavg):
    if SkyPresent() == False:
        return
    else:
        pass

    if checkforFileSKY("blkavgSky.fits") == False:
        print "File - %s doesn't exist yet, run previous step"
        return
    else:
        pass
    
    #blkavg = totaldir + blkavg
    waveblkavg = totaldir + waveblkavg
    
    iraf.imgets(totaldir + blkavg,"CAT-NAME")
    object = iraf.imgets.value
    print "Object is %s" % object
    
    arcfile = totaldir + object+"arc.fit"
    
    if os.path.isfile(arcfile) == True:
        os.rename(totaldir + "arc2.fit",arcfile)
        
        refimg = WavelengthRecalibration(arcfile,totaldir + object)
    else:
        refimg = "cuar.fits"
    
    ApplyWavelength(standard,totaldir + blkavg,refimg=refimg)
    linelist=['4358','5199','5577','5890','6157','6300','6364','6563.3','6863.95','7340.88','7913.71','8190','8344.60','8430.17','8827.10']
    # make sure it fits
    print "Need to make sure the wavelengths are correct before applying the flux (wavelength dep) calibration"
    print "Image will splot, check against these lines"
    print "Check for lines"
    print linelist
    iraf.splot(waveblkavg)
    while True:
        while True:
            try:
                shift2 = raw_input(colour.bold + "Shift by how many Angstroms?: " + colour.endc)
                if shift2 == '':
                    shift = 0
                else:
                    shift = float(shift2) 
                break
            except:
                print "Please enter a number"
        iraf.specshift(spectra=waveblkavg,shift=shift)
        print "Shifted by %s" % shift
        print "Check for lines"
        print linelist
        iraf.splot(waveblkavg)
        if query_yes_no("Finished changing it?", default="no") == True:
            break
        else:
            pass
        
        
    
    filename = ApplyFlux(waveblkavg.replace(totaldir,""))
    #remove(blkavg)
    #remove(waveblkavg+".fits")

    
    os.rename(filename+".fits",totaldir + "Extracted"+object+".fits")
    os.rename(waveblkavg+".fits",totaldir + "wave"+object+".fits")

""" General commands for listing files etc """

def listFiles():
    if query_yes_no("List just sky files?: ", default="no") == False:
        filelist = {}
        i = 1
        for file in os.listdir(totaldir):
            if file.endswith(".fit") or file.endswith(".fits"):
                if file == standard:
                    print "%d - %s\t\t\tstandard" % (i,file)
                elif file == arc:
                    print "%d - %s\t\t\tarc" % (i,file)
                elif file == "FluxwaveapallStdAB.fits":
                    print "%d - %s\t\t\tConverted to AB mag" % (i,file)
                else:
                    print "%d - %s" % (i, file)
                filelist[str(i)] = file
                i = i + 1
    else:
        print "\n"
        filelist = {}
        foldernames={}
        i=1
        unsorteddir = ()
        for dir in os.listdir(totaldir):
            unsorteddir = unsorteddir + (dir,)
        for dir in sorted(unsorteddir):
            if os.path.isdir(totaldir + dir) == True and dir != "database" and dir != "standards":
                #print dir
                for file in os.listdir(totaldir + dir):
                    if file.startswith("Extracted") and file.endswith("ABmagsquare.fits"):
                        filelist[str(i)] = totaldir + dir + "/" + file
                        foldernames[str(i)] = dir
                        i=i+1
                    else:
                        pass
            else:
                pass
        # this is the list of parameters we want to get
        # possible to make it interactive, but for another year
        fieldlist = ("EXPTIME","UTSTART","UTOBS")
        table = [("File no.","Name") + fieldlist]
        table = table + [extraInfo(x,foldernames[x],filelist[x],fieldlist) for x in sorted(filelist)]
        print_table(table)


    return filelist

def extraInfo(x,foldername,filename,fieldlist):
    # We will do lots of imgets here
    list = (str(x),foldername)
    for field in fieldlist:
        iraf.imgets(totaldir + filename,field)
        #print iraf.imgets.value
        list = list + (iraf.imgets.value,)    
    return list

def listFilesMoreInfo(): # LEGACYYYYYYY
    filelist = {}
    i=1
    for dir in os.listdir(totaldir):
        if os.path.isdir(dir) == True and dir != "database" and dir != "standards":
            #print dir
            for file in os.listdir(totaldir + dir):
                if file.startswith("Extracted"):
                    filelist[str(i)] = "./" + dir + "/" + file
                    #print "%d - %s" % (i,file)
                    i=i+1
                else:
                    pass
        else:
            pass
    table = [(str(x), str(filelist(x))) for x in filelist]
    print_table()

def splot():
    filelist = listFiles()    
    splotting=str(raw_input(colour.bold + "File no.: " + colour.endc))
    xmini=str(raw_input(colour.bold + 'Min wavelength (leave black for whole spec): ' + colour.endc))
    xmaxi=str(raw_input(colour.bold + 'Max wavelength (leave blank for whole spec): ' + colour.endc))
    if xmini != "" and xmaxi != "":
        try:
            iraf.splot(totaldir + filelist[splotting],xmin=xmini,xmax=xmaxi)
        except:
            print "Error splotting"
    else:
        try:
            iraf.splot(totaldir + filelist[splotting])
        except:
            print "Not splottable"

def GetStdName():
    
    global stdname
    global cenwave
    global standard
    global obsdate
    global grating

    #print "Defining the name of the standard star"

    iraf.imgets(standard + standardextension,"CAT-NAME")
    stdname = iraf.imgets.value

    # IRAF demands that the names follow this format
    stdname = stdname.replace("+","_")
    stdname = stdname.replace("-","_")
    stdname = stdname.replace("SP","sp")

    iraf.imgets(standard + standardextension,"CENWAVE")
    cenwave = iraf.imgets.value

    iraf.imgets(standard + standardextension,"DATE-OBS")
    obsdate = iraf.imgets.value

    iraf.imgets(standard + standardextension,"ISIGRAT")
    grating = iraf.imgets.value
    print "getstdname works"
    return stdname,cenwave

def getFiles():
    global standard
    global arc
    global cenwave
    global standardarm
    global arcarm
    global rawSky
    standard = "None"
    arc = "None"
    rawSky = "None"
    picklefile = totaldir + "fits_files.p"
    if os.path.isfile(picklefile) == False or os.path.getsize(picklefile) == 0:
        print "No 'fits_files.p' file found - creating one"
        fits_files = {"standard":"placeholder.fits","arc":"placeholder.fits","sky":"placeholder.fits"}
        pickle.dump(fits_files,open(picklefile,"w"))
    else:
        pass
    fits_files = pickle.load(open(picklefile,"r"))
    if os.path.isfile(totaldir + fits_files['standard']) == True:
        print "Standard found"
        print totaldir + fits_files['standard']
        print totaldir
        standard = totaldir + fits_files['standard']
        print standard
        CheckEXTNAME(standard,standardextension)    
        iraf.imgets(standard + standardextension,"ISIARM")
        standardarm = iraf.imgets.value
    else:
        for file in os.listdir(totaldir):
            if file.startswith("standard") == True:
                if file.endswith(".fit") == True or file.endswith(".fits") == True:
                    #if query_yes_no("Use %s for the standard?" % file) == True:
                        #standard = reductdir + "/Reductions/" + workingdir+ "/" + arm + "/" + file
                    standard = totaldir + file
                    CheckEXTNAME(standard,standardextension)                    
                    iraf.imgets(standard + standardextension,"ISIARM")
                    standardarm = iraf.imgets.value
                   # else:
                       # pass
                else:
                    pass
            else:
                pass    
    if os.path.isfile(totaldir + fits_files['arc']) == True:
        print "Arc found"
        arc = totaldir + fits_files['arc']
        CheckEXTNAME(arc,"[1]")    
        iraf.imgets(arc + "[1]","ISIARM")            
        arcarm = iraf.imgets.value
    else:
        for file in os.listdir(totaldir):
            if file.startswith("arc") == True:
                #if query_yes_no("Use %s for the arc?" % file) == True:
                    #arc = reductdir + "/Reductions/" + workingdir+ "/" + arm + "/" + file
                arc = totaldir + file
                CheckEXTNAME(arc,"[1]")    
                iraf.imgets(arc + "[1]","ISIARM")            
                arcarm = iraf.imgets.value
               # else:
                #    pass
            else:
                pass        
    if os.path.isfile(totaldir + fits_files['sky']) == True:
        print "Sky found"
        print "From pickle"
        rawSky = totaldir + fits_files['sky']
        try:
            CheckEXTNAME(rawSky,"[1]")
        except:
            CheckEXTNAME(rawSky,"")
    else:
        tempsky = getsky()
        if tempsky == "None":
            rawSky = "None"
        else:
            rawSky = totaldir + tempsky
            #Continue()
            CheckEXTNAME(rawSky,"[1]")
        #for file in os.listdir(totaldir):
        #    if file.startswith("sky") == True:
        #        if query_yes_no("Use %s for the sky?" % file) == True:
        #            #rawSky = reductdir + "/Reductions/" + workingdir+ "/" + arm + "/" + file
        #            rawSky = totaldir + file
        #            CheckEXTNAME(rawSky,"[1]")    
        #        else:
        #            pass
        #    else:
        #        pass    
    if standard == "None" and arc == "None":
        print "No arc or standard, exiting the program, please put 'em in"
        exit()
    else:
        pass
    
    try:
        print "Writing file names to file (if any updated)"
        fits_files = {"standard":standard.replace(totaldir,""),"arc":arc.replace(totaldir,""),"sky":rawSky.replace(totaldir,"")}
        pickle.dump(fits_files,open(picklefile,"w"))
        GetStdName()
    except:
        print "err0r pickling"
        print "Probs a totaldir error"
    return        
#        else:
    #    print "These files do not exist, make sure they're entered correctly"
    #    print "Standard - %s, Arc - %s" % (fits_files['standard'],fits_files['arc'])
    #    Continue()
    #    return

def getsky():
    print "\n"
    filelist = {}
    filelistext = {}
    #foldernames={}
    i=1
    
    found = False
    for folder in os.listdir(totaldir):
        if os.path.isdir(totaldir + folder) == True:
            print totaldir + folder
            for file in os.listdir(totaldir + folder):
                if file.startswith("wht"):
                    for file2 in os.listdir(totaldir+folder):
                        os.rename(totaldir + folder + "/" + file2, totaldir + file2)
                    os.rmdir(totaldir + folder)
                    found = True
                    break
                else:
                    pass
        else:
            pass
        if found == True:
            break
        else:
            pass
    
    for otherfiles in os.listdir(totaldir):
        if otherfiles.startswith("Extracted"):
            remove(totaldir + otherfiles)
        elif otherfiles.startswith("wave") and otherfiles.endswith(".fits"):
            remove(totaldir + otherfiles)
        elif otherfiles.startswith("narrowedSky"):
            remove(totaldir + otherfiles)
        elif otherfiles.startswith("blkavg"):
            remove(totaldir+otherfiles)
        elif otherfiles.startswith("Fluxwaveblkavg"):
            remove(totaldir+otherfiles)
        elif otherfiles.startswith("wht"):
            skyfile = otherfiles
        else:
            pass
        
    
    print skyfile
    print "DONE getting sky file"
    
    return skyfile





def CheckEXTNAME(file,extension):
    # On some of the old files, it has this "compression" thing which needs to be changed to "extension1"
    # I think this will be present on all old archived files, so it makes sense to check for it and change it
    try:
        iraf.imgets(file + extension, "EXTNAME")
    except:
        print "Passed extension hasn't worked I don't think"
        print "Fix your code Nik"
        return
    if iraf.imgets.value.upper() == "COMPRESSED_IMAGE":
        iraf.hedit(file + extension,fields="EXTNAME",value="extension1",add="yes",update="yes",verify="no")
    else:
        print "Think I have to add it anyway"
        # Actually do, I checked. Don't know why but there you go. Shouldn't this automatically be in files ????
        iraf.hedit(file + extension,fields="EXTNAME",value="extension1",add="yes",update="yes",verify="no")
        

def saveFiles():
    # I can change this later, it is not particularly useful at the moment
    # Don't use!!!!!!
    global standard
    global arc
    global rawSky
    print "Enter the names of all files when prompted, leave the field blank to keep it as before"
    
    picklefile="fits_files.p"
    
    tsta = str(raw_input(colour.bold + "Enter file name of the standard rxxxxxxx.fit (%s): "  % standard + colour.endc))
    if tsta == "":
        tsta = standard
    elif os.path.isfile(tsta) == False:
        print "%s does not exist!" % tsta
    else:
        standard = tsta
        print "New standard is %s" % tsta

    tarc = str(raw_input(colour.bold + "Enter file name of the arc rxxxxxxx.fit (%s): " % arc + colour.endc ))
    if tarc == "":
        tarc = arc
    elif os.path.isfile(tarc) == False:
        print "%s does not exist" % tarc
    else:
        arc = tarc
        print "New arc is %s" % tarc
    
    trawSky = str(raw_input(colour.bold + "Enter file name of the sky file rxxxxxxx.fit (%s): "  % rawSky + colour.endc))
    if trawSky == "":
        trawSky = rawSky
    elif os.path.isfile(trawSky) == False:
        print "%s does not exist" % trawSky
    else:
        rawSky = trawSky
        print "New arc is %s" % trawSky
        
    print "Writing file names to file (if any updated)"
    fits_files = {"standard":standard,"arc":arc,"sky":rawSky}
    pickle.dump(fits_files,open(picklefile,"w"))
    
    
    global stdname
    global cenwave

    try:
        GetStdName()
    except:
        pass

def ListDirectories():
    print "Nothing to see here just yet"
            



def ApplyAB():
    if SkyPresent() == False:
        return
    else:
        pass
    #def ABConversion(name=False,outfile="FluxwaveapallStd",apallStd="waveapallStd"):
    
    #currently only configured to do one file, but I can easily change this to inputs if it needed to be, for now it don't matter
    
    #wavefile="waveblkavgSky"
    #object = str(raw_input('Enter object name (case sensitive): '))
    #object = "GAIA15AFI"
    iraf.imgets(rawSky+skyextension,"CAT-NAME")
    object = iraf.imgets.value
    
    wavefile = "wave"+object+".fits"
    
    if checkforFileSKY(wavefile) == False:
        print "File - %s doesn't exist yet, run previous step"
        return
    else:
        pass
    
    #iraf.imgets(wavefile,"CAT-NAME")
    #object = iraf.imgets.value
    
    iraf.scopy(input=totaldir + wavefile,output=totaldir + wavefile,format="onedspec")
    
    # print tell them what the binning is
    iraf.imgets(rawSky+skyextension,"CCDXBIN")
    print "Spacial binning is %s" % iraf.imgets.value
    
    ABConversion(outfile="Extracted"+object,apallStd=wavefile+".0001",sky="yes")
    ABConversion(outfile="Extracted"+object,apallStd=wavefile+".0001",sky="no")
    
    print "And now we put all the files into a directory woo."
    if os.path.isdir(totaldir + object) == True:
        print "Already reduced this object, this might be from another time in the night, putting in a new directory"
        i = 2
        while True:
            objectdir = object + "-" + str(i)
            if os.path.isdir(objectdir) == True:
                i = i + 1
                print "%s exists" % objectdir
            else:
                break
    else:
        objectdir = object
        
    os.mkdir(totaldir + objectdir)
    
    filestomove=["unbiasedsky.fits","blkavgSky.fits","Extracted"+object+".fits","Extracted"+object+"AB.fits","Extracted"+object+"ABmagsquare.fits","Extracted"+object+"ABtempmagsquare.fits","sky.fit","wave"+object+".fits","wave"+object+".fits.0001.fits",object+"arc.fit","sky.fits",rawSky,"narrowedSky.fits","uncosmiced.fits"]
    for i in filestomove:
        try:
            if os.path.isfile(totaldir + i) == True:
                os.rename(totaldir + i,totaldir + objectdir+"/"+i)
                print "Moved %s" % i
            else:
                print "File wasn't made in the first place mate"
        except:
            print "Couldn't move %s" % i
    
    print "got this far"        
    tomove = rawSky.replace(totaldir,"")
    #tomove = tomove.replace("wht","vht")
    os.rename(totaldir + tomove, totaldir + objectdir + "/" + tomove.replace("wht","vht"))
    
    for file in os.listdir(totaldir):
        if file.startswith("wave"+object) and file.endswith(".fits"):
            remove(file)
        elif file.startswith("temp") and file.endswith(".fits"):
            remove(file)
        else:
            pass
    #remove("blkavgSky.fits") # The most important file ......
        
        
def BiasLevel():
    
    # Make it so you can choose the start / end or make it dependent on binning
    # Think that is all I need to add to this
    
    iraf.imgets(rawSky+"[0]","EXTEND")
    if iraf.imgets.value == "T":
        TEMPSKYEXTENSION = "[1]"
    else:
        TEMPSKYEXTENSION = ""
    
    
    iraf.imgets(rawSky+TEMPSKYEXTENSION,"BIASED")
    print iraf.imgets.value
    if iraf.imgets.value.lower() == "yes":
        print "Already debiased"
        return
    else:
        print "Commence debiasing"
    
    # Some images don't have the [1] for some reason?
    # Here is a "temporary" bit of code that will adapt to it
    print "If you get an error here, you need to go and change 'normalextension' in your code"
    normalextension = "[1]"
    #normalextension = "" # Uncomment this if it's a "weird one"
        
    iraf.imgets(rawSky+normalextension,"CCDYBIN")
    YBIN = int(iraf.imgets.value)
    iraf.imgets(rawSky+normalextension,"CCDXBIN")
    XBIN = int(iraf.imgets.value)
    
    # These are the DEFAULT POSITIONS
    x_start = 200 / XBIN
    x_end = (200 + 44) / XBIN
    y_start = (4190 - 11) / YBIN
    y_end = 4190 / YBIN
    # Default values
    print "Default Values:"
    print x_start
    print y_start
    
    iraf.display(rawSky+normalextension,frame="1")
    
    
    # This is where it should check for a file to use for the bias values
    
    # Check if file exists
    if checkforFileSKY("biasposition.dat") == True:
        # If exists, load values from it
        # Load file
        print "Loading bias position from file (should be same across all sky files)"
        biascoords = pickle.load(open(totaldir + "biasposition.dat","r"))
        # Load values
        x_start = biascoords['x_start']
        x_end = int(x_start) + (44/XBIN)
        
        y_end = biascoords['y_end']
        y_start = int(y_end) - (11/YBIN)
    # If doesn't exist, run next step and create file afterwards
    
    # Just incase some dodgy windowing is going on...
    # It has happened and it WILL happen in the future.
    else:
        if g.cont == True:
            iraf.imgets(rawSky+normalextension,"BIASSEC")
            biassec = iraf.imgets.value
            biassec = biassec.replace("[","")
            biassec = biassec.replace("]","")
            biassec = biassec.split(",")
            biassecy = biassec[1].split(":")
            biassecx = biassec[0].split(":")
            print biassec
            
            biassecx[0]=int(biassecx[0])
            biassecx[1]=int(biassecx[1])
            biassecy[0]=int(biassecy[0])
            biassecy[1]=int(biassecy[1])
            
            NEWX = int((biassecx[0]+biassecx[1])/2)
            NEWY = int((biassecy[0]+biassecy[1])/2)
            
            print NEWX
            print NEWY
            
            
        else:
            print "Make sure you check these, just incase the observer has used a stupid window (silly observers)"
            NEWX = raw_input(colour.bold + "x-coordinate for BIAS (Blank to use default (%d), should do this normally): " % x_start + colour.endc )                        
            NEWY = raw_input(colour.bold + "y-coordinate for BIAS (Blank to use default (%d), should do this normally): "  % y_end + colour.endc)
        
        if NEWX == "":
            x_start = x_start
        else:
            x_start = int(NEWX) - int(((biassecx[1]-biassecx[0])/2)/10)
            x_end = int(NEWX) + int(((biassecx[1]-biassecx[0])/2)/10)

        if NEWY == "":
            y_end = y_end
        else:
            y_end = int(NEWY) + int((int(biassecy[1]-biassecy[0])/2)/10) + 1
            y_start = int(NEWY) - int((int(biassecy[1]-biassecy[0])/2)/10) - 1
            
        biascoords = {"x_start":x_start,"y_end":y_end}
        pickle.dump(biascoords,open(totaldir + "biasposition.dat","w"))
    
    print "Values being used:"
    print x_start
    print y_start
    
    
    RANGEX = (x_end - x_start)
    RANGEY = (y_end - y_start)
    iraf.imcopy(rawSky+normalextension+"["+str(x_start)+":"+str(x_end)+","+str(y_start)+":"+str(y_end)+"]", output = totaldir + "tempSkyforBias.fits")
    
    iraf.blkavg(input=totaldir + "tempSkyforBias.fits",output=totaldir + "tempSkyforBiasBLKAVG.fits",b1=RANGEX,b2=RANGEY,option="average")

    iraf.scopy(totaldir + "tempSkyforBiasBLKAVG.fits", output=totaldir + "tempSkyforBiasBLKAVGoned.fits", format="onedspec")
    iraf.wspectext(input = totaldir + "tempSkyforBiasBLKAVGoned.fits.0001.fits", output = totaldir + "BIASLEVEL.dat", header="no")
    
    biasfile=np.loadtxt(totaldir +  "BIASLEVEL.dat")

    dontcare = biasfile[:,0]
    biasvalues = biasfile[:,1]
    
    #print biasvalues
    #BIASVALUE = np.mean(biasvalues)
    BIASVALUE = np.median(biasvalues)
    print BIASVALUE
    
    remove(totaldir + "tempSkyforBias.fits")
    remove(totaldir + "tempSkyforBiasBLKAVG.fits")
    remove(totaldir + "tempSkyforBiasBLKAVGoned.fits.0001.fits")
    remove(totaldir + "tempSkyforBiasBLKAVGoned.fits.0002.fits")
    remove(totaldir + "BIASLEVEL.dat")
    
    print "Fin"
    
    SubtractBias(BIASVALUE)

def SubtractBias(BIASVALUE):
    # This function is to subtract the BIAS from the SKY only
    print BIASVALUE
    BIASVALUE = int(BIASVALUE)
    print BIASVALUE
    iraf.imarith(operand1=rawSky+"[1]",op="-",operand2=str(BIASVALUE),result=totaldir + "biassky.fits")
    iraf.hedit(totaldir + "biassky.fits",fields="BIASED",value="YES",add="yes",update="yes",verify="no")
    os.rename(rawSky,totaldir + "unbiasedsky.fits")
    os.rename(totaldir + "biassky.fits",rawSky)


def LACosmicRemoval():
    
    for file in os.listdir(totaldir):
        if file.startswith("lacos"):
            remove(file)
        else:
            pass
    print rawSky
    try:
        iraf.imgets(rawSky + "[1]","NOCOSMIC")
    except:
        iraf.imgets(rawSky,"NOCOSMIC")
    print iraf.imgets.value
    if iraf.imgets.value.lower() == "yes":
        print "Already cosmic"
        return
    else:
        print "Commence cosmic"
        
    inputimage = rawSky
    outputimage = totaldir + "nocosmics.fits"
    maskimage = totaldir + "mask.fits"
    #have to run this twice ????
    try:
        iraf.lacos_spec(input=inputimage,output=outputimage,outmask=maskimage,gain="0.98",readn="4",xorder="9",yorder="2",objlim="5")
    except:
        remove(maskimage)
    try:
        iraf.lacos_spec(input=inputimage,output=outputimage,outmask=maskimage,gain="0.98",readn="4",xorder="9",yorder="2",objlim="5")
    except:
        pass
    remove(maskimage)      
    iraf.hedit(totaldir + "nocosmics.fits",fields="NOCOSMIC",value="YES",add="yes",update="yes",verify="no")
    os.rename(rawSky,totaldir + "uncosmiced.fits")
    os.rename(totaldir + "nocosmics.fits",rawSky)
