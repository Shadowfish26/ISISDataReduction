from Common import colour as colour

import Globals as g
import os
from Common import query_yes_no as query_yes_no
            
def chooseMode():
    while True:
        modein = str(raw_input(colour.bold + "Choose a mode - (R)eduction or (M)easure (Default is %s): " % (g.mode) + colour.endc ))
        if modein.upper() == "R":
            g.mode = "Reduce"
            return
        elif modein.upper() == "M":
            g.mode = "Measure"
            return
        elif modein.upper() == "Q":
            exit()
        elif modein == "":
            return
        else:
            print "Please choose R or M\n"
            
def ChooseDirectory():
    # Initialise these, only need cwd to get history.dir
    # workingdir should ed up being the completed dir I reckon
    # Load the last worked in dir if there is one (should be) as lastdir
    print "Current dir is %s" % g.cwd
    # This should always be no, for my purposes at least
    if query_yes_no("Do you want to use the directory you opened the file in?",default="no") == True:
        return
    # Now we need to get the reductdir which is just going to be ~/Reductions, and should always be that
    elif query_yes_no("Do you want to use the '~/Reductions' directory?", default="yes") == True:
        if os.path.exists(g.homedir + "/Reductions") == True:
            g.reductdir = "/Reductions"
            # reductdir has been set, now have to pick a date given as 'datedir'
            # in this context, lastdir is the DATE obtained from HISTORY.DAT
            return g.reductdir
        else:
            print "Directory doesn't exist"
            print "Please create it"
            print "Exiting the whole program for some reason!"
            exit()
    else:
        print "nvm then"
        exit()
        
def chooseArm():
    while True:
        armchoice = str(raw_input(colour.bold + "Are you going to use the" + colour.blue + "(B)lue" + colour.black + " or " + colour.red + "(R)ed" + colour.black + " arm?: " + colour.endc))
        if str(armchoice).upper() == "R":
            print "Red arm selected"
            g.arm = "red"
            break
        elif str(armchoice).upper() == "B":
            print "Blue arm selected"
            g.arm = "blue"
            break
        elif str(armchoice).upper() == "Q":
            exit()
        else:
            print "Please select (R)ed or (B)lue or (Q)uit"    
    if os.path.exists(g.homedir+g.reductdir+g.datedir+"/"+g.arm) == True:
        print "Seems to exist JUST FINE"
    else:
        print "Going to make the directory for the arm with colour %s" % g.arm
        print "This might fail if you don't have permissions, but in this case, the program isn't going to work at all is it?"
        os.mkdir(g.homedir+g.reductdir+g.datedir+"/"+g.arm)
        print "Should've made the directory for you"
    return

def chooseDate():
    try:
        f = open(g.cwd + "/history.dat","r")
        lastdir = f.readline()
        f.close()
    except:
        lastdir = "None"
        
    while True:
                    direc = str(raw_input(colour.bold + "Choose a directory (YYMMDD), L returns a list, leave blank to use last directory (%s): " % (lastdir) + colour.endc ))
                    if direc == "" and lastdir != "None":
                        g.datedir = "/" + lastdir
                        return
                    elif direc == "" and lastdir == "None":
                        print "No last dir, please enter one"
                        pass
                    elif direc == "L":
                        print "Listing directories"
                        # I actually want to make this into a more advanced function, but it fits the bill for now
                        # In numerical order and also list some parameters about what is contained in the folder
                        # Actually possible to do this by extracting information from a standard, but can also do it
                        # by saving the data into a .dat file
                        print os.listdir(g.homedir + g.reductdir)
                    elif direc == "Q":
                        # Quit whole program, why not?
                        print "Quitting EVERYTHING"
                        Continue()
                        exit()
                    else:
                        g.datedir = "/"+direc
                        print (g.cwd + "/history.dat")
                        f = open(g.cwd + "/history.dat","w")
                        f.write(direc)
                        f.close()                
                        print os.getcwd()
                        return
                
    