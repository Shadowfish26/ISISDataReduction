from Common import colour as colour
from Common import remove as remove
import curses
import sys
import os
import Globals as g
from pyraf import iraf
from collections import OrderedDict
import StringIO
from time import sleep
import subprocess


#stdout = sys.stdout

iraf.images()
iraf.imutil()

linesofheaders = int(0)
allfileinfo = {}

def blockPrint():
    sys.stdout = open(os.devnull,'w')

def endcursor(stdscr):
    #maxy,maxx = stdscr.getmaxyx()
   # stdscr.setsyx(maxy,0)
   pass
    

class column(object):
    
    def __init__(self,header,path,columnstart):
        self.row = int(1)
        self.toplimit = int(1)
        self.header = header
        self.path = path
        self.columnsize = int(8)
        self.columnstart = 2 + columnstart
        self.columnend = self.columnsize + self.columnstart
        self.datefolders = filelistfun(self.path)
        self.containsfiles = False
        self.scroll = 1
        self.maxlength = 8
    
    def action(self,key,stdscr):
        self.datefolders = filelistfun(self.path)
        if key == curses.KEY_UP: 
            self.row = self.row - 1
            if self.row < self.toplimit:
                self.row = int(self.toplimit)
            else:
                pass
            if self.row < self.scroll:
                self.scroll = self.scroll - 1
            else:
                pass

        elif key == curses.KEY_DOWN: 
            if self.row >= int(len(self.datefolders)): # bottom limit
                self.row = int(len(self.datefolders))
            else:
                self.row = self.row + 1
                if self.row > self.maxlength:
                    self.scroll = self.scroll + 1
                else:
                    pass
                
    def printit(self,stdscr,colhi,colno):
        if self.containsfiles == False:
            #self.datefolders = filelistfun(self.path)
            printcolumn(stdscr,self.datefolders,self.columnstart,self.row,self.columnsize,self.columnend,colhi,colno,self)
        else:
            # function to get files instead of folders (should be no sub folders)
            #self.datefolders = filelistfun(self.path)
            printcolumn(stdscr,self.datefolders,self.columnstart,self.row,self.columnsize,self.columnend,colhi,colno,self,xInfo=True,path=self.path)
            #infofun(stdscr,self.datefolders,self.columnstart,self.row,self.columnsize,self.columnend,colhi,colno,xInfo=True,path=self.path)

    def selectedrow(self):
        #self.datefolders = filelistfun(self.path)
        try:
            return self.datefolders[str(self.row)]
        except:
            return "None"
        
def RunLoop():
    curses.wrapper(MMLoop)
    
def MMLoop(stdscr):
    
    #blockPrint()
    #stdscr = curses.initscr()
    #stdscr = curses.newwin(1,28,20,13)
    curses.start_color()
    curses.init_pair(1,curses.COLOR_BLACK,curses.COLOR_WHITE)
    curses.init_pair(2,curses.COLOR_BLACK,curses.COLOR_CYAN)
    curses.cbreak()
    curses.noecho()
    curses.mousemask(1)
    
    
    
    #curses.setsyx(-1,-1)
    stdscr.keypad(1)
    
    
    stdscr.refresh()
    actualstdscr = stdscr
    
    maxy,maxx = stdscr.getmaxyx()
    
    infoboxsize = 9
    
    stdscr = curses.newwin(maxy-infoboxsize,maxx-2,0,1)
    stdscr.keypad(1)
    
    win = curses.newwin(infoboxsize,maxx-2,maxy-infoboxsize,1)
    win.refresh()
    win.addstr(1,1,"testttttttttttttttttttttttt")
    win.border()
    win.refresh()
    
    key = ''
    
    plottingparams = {}
    selwave = _wavelengthRanges()
    seltype = _fileTypetoPlot()
    mlines = _measurementlines()
    plottingparams["selwave"] = selwave
    plottingparams["seltype"] = seltype
    plottingparams["mlines"] = mlines
    
    # List of things
    reductiondir = g.homedir + "/Reductions/"
    
    columnlist = [0,0,0]
    columnpars = [0,0,0]
    columnpars[0] = ("Date",reductiondir)
    
    i = 0
    columnlist[0] = column(*columnpars[i] + (2,))

    
    datefolders = filelistfun(reductiondir)
    #printheaders(stdscr)
    #printcolumn(stdscr,datefolders,2,column1.row,6)
    
    columnhighlighted = int(0)
    dir = reductiondir
    
    while key != ord('q'):
        key = stdscr.getch()
        if key == ord('q'):
            break
        else:
            pass
        #stdscr.addch(20,25,key)
        redorder = [curses.KEY_RIGHT,curses.KEY_DOWN,curses.KEY_RIGHT,ord('n'),curses.KEY_LEFT,curses.KEY_LEFT,curses.KEY_DOWN]
        blueorder = [curses.KEY_RIGHT,curses.KEY_RIGHT,ord('n'),curses.KEY_LEFT,curses.KEY_LEFT,curses.KEY_DOWN]
        if key == ord('b') or key == ord('v'):
            if key == ord('b'):
                keyorder = blueorder
            else:
                keyorder = redorder
            while columnlist[0].row <  int(len(columnlist[0].datefolders)):
            #while columnlist[0].row <  6:
                for what in keyorder:
                    key = what
                    changeofrow = False
                    if key == curses.KEY_RIGHT:
                        columnhighlighted = columnhighlighted + 1
                        if columnhighlighted > 2:
                            columnhighlighted = 2
                        else:
                            pass
                    elif key == curses.KEY_LEFT:
                        columnhighlighted = columnhighlighted - 1
                        if columnhighlighted < 0:
                            columnhighlighted = 0
                        else:
                            pass
                    #elif key == curses.KEY_ENTER and columnlist[columnhighlighted].containsfiles == True:
                    elif key == ord('p') and columnlist[columnhighlighted].containsfiles == True:
                        #print columnlist[columnhighlighted].datefolders
                        splot(columnlist[columnhighlighted].datefolders[str(columnlist[columnhighlighted].row)],columnlist[columnhighlighted].path,plottingparams)
                    elif key == ord('m') and columnlist[columnhighlighted].containsfiles == True:
                        linemeasure(columnlist[columnhighlighted].datefolders,columnlist[columnhighlighted].path,plottingparams,win,columnlist[0].datefolders[str(columnlist[0].row)],highlighted = columnlist[columnhighlighted].datefolders[str(columnlist[columnhighlighted].row)])
                    elif key == ord('n') and columnlist[columnhighlighted].containsfiles == True:
                        linemeasure(columnlist[columnhighlighted].datefolders,columnlist[columnhighlighted].path,plottingparams,win,columnlist[0].datefolders[str(columnlist[0].row)],highlighted = "",all=True)
                    elif key == ord('w'):
                        plottingparams["selwave"].changeWave()
                    elif key == ord('r'):
                        plottingparams["selwave"].changeRange()
                    elif key == ord('e'):
                        plottingparams["seltype"].changeType()
                    elif key == ord('i'):
                        plottingparams["selwave"].setCust(win)
                    elif key == ord('o'):
                        plottingparams["selwave"].setCustrange(win)
                    elif key == ord('a'):
                        plottingparams["mlines"].addLine(win)
                    elif key == ord('z'):
                        plottingparams["mlines"].delLine()
                    elif key == curses.KEY_MOUSE:
                        plottingparams["mlines"].checkClick(stdscr,win)
                    else:
                        columnlist[columnhighlighted].action(key,stdscr)
                        changeofrow = True
                    
                    stdscr.clear()
                    stdscr.border()
                    stdscr.refresh()
                    printheaders(stdscr,plottingparams)
                    # Reload columns
                    
                    dir = columnpars[columnhighlighted][1]
                    #print dir
                    
                    if changeofrow == True:
                        for i in range(int(columnhighlighted+1),3):
                            #print "/home/nik/Reductions/" + columnlist[i-1].selectedrow()
                            dir = dir + columnlist[i-1].selectedrow() + "/"
                            columnpars[i] = ("Date2",dir)
                            columnlist[i] = column(*columnpars[i] + (columnlist[i-1].columnend,))
                            
                        if columnlist[i].selectedrow() != "None":
                            for file in os.listdir(dir + columnlist[i].selectedrow() + "/"):
                                if file.startswith("Extracted") and file.endswith("ABmagsquare.fits"):
                                    columnlist[i].containsfiles = True
                                else:
                                    pass
                        else:
                            pass
                        
                        #print columnlist[1].selectedrow()
                    
                    #Draw columns
                    #for i in range(0,3):  
                    #    columnlist[i].printit(stdscr,columnhighlighted,i)
                    #else:
                    #    pass
                    
                    # Print a frog
                    printfrog(stdscr)
        else:
            pass 
            
            
        # Do the movement action
        changeofrow = False
        if key == curses.KEY_RIGHT:
            columnhighlighted = columnhighlighted + 1
            if columnhighlighted > 2:
                columnhighlighted = 2
            else:
                pass
        elif key == curses.KEY_LEFT:
            columnhighlighted = columnhighlighted - 1
            if columnhighlighted < 0:
                columnhighlighted = 0
            else:
                pass
        #elif key == curses.KEY_ENTER and columnlist[columnhighlighted].containsfiles == True:
        elif key == ord('p') and columnlist[columnhighlighted].containsfiles == True:
            #print columnlist[columnhighlighted].datefolders
            splot(columnlist[columnhighlighted].datefolders[str(columnlist[columnhighlighted].row)],columnlist[columnhighlighted].path,plottingparams)
        elif key == ord('m') and columnlist[columnhighlighted].containsfiles == True:
            linemeasure(columnlist[columnhighlighted].datefolders,columnlist[columnhighlighted].path,plottingparams,win,columnlist[0].datefolders[str(columnlist[0].row)],columnlist[columnhighlighted].datefolders[str(columnlist[columnhighlighted].row)])
        elif key == ord('c') and columnlist[columnhighlighted].containsfiles == True:
            with open("/data/nik/Reductions/CHRIST","w") as christ:
                for i in columnlist[columnhighlighted].datefolders:
                    christ.write(columnlist[columnhighlighted].datefolders[i])
        elif key == ord('n') and columnlist[columnhighlighted].containsfiles == True:
            linemeasure(columnlist[columnhighlighted].datefolders,columnlist[columnhighlighted].path,plottingparams,win,columnlist[0].datefolders[str(columnlist[0].row)],columnlist[columnhighlighted].datefolders[str(columnlist[columnhighlighted].row)],all=True)
        elif key == ord('w'):
            plottingparams["selwave"].changeWave()
        elif key == ord('r'):
            plottingparams["selwave"].changeRange()
        elif key == ord('e'):
            plottingparams["seltype"].changeType()
        elif key == ord('i'):
            plottingparams["selwave"].setCust(win)
        elif key == ord('l'):
            getlog(columnlist[0].datefolders[str(columnlist[0].row)])
        elif key == ord('o'):
            plottingparams["selwave"].setCustrange(win)
        elif key == ord('a'):
            plottingparams["mlines"].addLine(win)
        elif key == ord('z'):
            plottingparams["mlines"].delLine()
        elif key == curses.KEY_MOUSE:
            plottingparams["mlines"].checkClick(stdscr,win)
        else:
            columnlist[columnhighlighted].action(key,stdscr)
            changeofrow = True
        
        stdscr.clear()
        stdscr.border()
        stdscr.refresh()
        printheaders(stdscr,plottingparams)
        # Reload columns
        
        dir = columnpars[columnhighlighted][1]
        #print dir
        
        if changeofrow == True:
            for i in range(int(columnhighlighted+1),3):
                #print "/home/nik/Reductions/" + columnlist[i-1].selectedrow()
                dir = dir + columnlist[i-1].selectedrow() + "/"
                columnpars[i] = ("Date2",dir)
                columnlist[i] = column(*columnpars[i] + (columnlist[i-1].columnend,))
                
            if columnlist[i].selectedrow() != "None":
                for file in os.listdir(dir + columnlist[i].selectedrow() + "/"):
                    if file.startswith("Extracted") and file.endswith("ABmagsquare.fits"):
                        columnlist[i].containsfiles = True
                    else:
                        pass
            else:
                pass
            
            #print columnlist[1].selectedrow()
        
        #Draw columns
        for i in range(0,3):  
            columnlist[i].printit(stdscr,columnhighlighted,i)
        else:
            pass
        
        # Print a frog
        printfrog(stdscr)

        

    columnlist = [0,0,0]
    columnpars = [0,0,0]
    curses.nocbreak()
    actualstdscr.keypad(0)
    curses.echo()
    curses.endwin()
    return
  
  
def printfrog(stdscr):
    maxy,maxx = stdscr.getmaxyx()
    #stdscr.addstr(maxy-3,maxx-3,"Test")
    froglist = []
    froglist.append('    _    _')
    froglist.append('   (o)--(o)')
    froglist.append("  /.______.\ ")
    froglist.append('  \________/')
    froglist.append(' ./        \.')
    froglist.append('( .        , )')
    froglist.append(' \ \_\\//_/ /')
    froglist.append('  ~~  ~~  ~~')
    
    row = maxy - (len(froglist) + 1)
    column = 2
    messagerow = row + 2
    for i in froglist:
        stdscr.addstr(row,column,i)
        row = row + 1
    
    message = []
    message.append("~~  w - cycle wavelength || i - input custom wavelength")
    message.append("  r - cycle range || o - input custom range")
    message.append("  e - cycle units plotted || l - load log for selected night")
    message.append("  v - automeasure all for red || b - automeasure all for blue")
    message.append("  m - measure highlighted line || p - splot highlighted spectrum")
    message.append("  z - remove a line || a - add a line")
    addline = 0
    for mess in message:
        if addline == 0:
            stdscr.addstr(messagerow + addline,15,mess)
        else:
            stdscr.addstr(messagerow + addline,17,mess)
        addline = addline + 1
    
def printheaders(stdscr,plottingparams):
    global linesofheaders
    stdscr.addstr(0,2,"Measuring Mode")
    stdscr.addstr(1,2,"-"*20)
    endcursor(stdscr)
    #stdscr.addstr(0,9,"||")
    selwave = plottingparams["selwave"]
    seltype = plottingparams["seltype"]
    mlines = plottingparams["mlines"]
        
    
    pos = 5
    for entry in selwave.wavelengths:
        if int(entry) == selwave.selwave:
            stdscr.addstr(3,pos,selwave.wavelengths[entry][0],curses.color_pair(2))
            endcursor(stdscr)
            #stdscr.addstr(3,10,"WHOLE")
        else:
            stdscr.addstr(3,pos,selwave.wavelengths[entry][0])
            endcursor(stdscr)
        pos = pos + 8
        
    stdscr.addstr(3,pos,"|")
    pos = pos + 8
    
    for entry in selwave.range:
        if int(entry) == selwave.selrange:
            stdscr.addstr(3,pos,selwave.range[entry][0],curses.color_pair(2))
            endcursor(stdscr)
            #stdscr.addstr(3,10,"WHOLE")
        else:
            stdscr.addstr(3,pos,selwave.range[entry][0])
            endcursor(stdscr)
        pos = pos + 8
    
    pos = 5
    for entry in seltype.filetypes:
        if int(entry) == seltype.seltype:
            stdscr.addstr(4,pos,seltype.filetypes[entry][0],curses.color_pair(2))
            endcursor(stdscr)
        else:
            stdscr.addstr(4,pos,seltype.filetypes[entry][0])
            endcursor(stdscr)
        pos = pos + 15
        
    for entry in mlines.lines:
        mline = mlines.lines[entry]
        if mline[1] == True:
            stdscr.addstr(mline[2],mline[3],"[X]" + mline[0])
        else:
            stdscr.addstr(mline[2],mline[3],"[ ]" + mline[0])
            
    for entry in mlines.fittype:
        mline = mlines.fittype[entry]
        if mline[1] == True:
            stdscr.addstr(mline[2],mline[3],"[X]" + mline[0])
        else:
            stdscr.addstr(mline[2],mline[3],"[ ]" + mline[0])
    
    linesofheaders = 5 # 3 + number of selectables

class _fileTypetoPlot():
    
    def __init__(self):
        self.filetypes = OrderedDict()
        self.filetypes["0"] = ("AB Mag per arc",True)
        self.filetypes["1"] = ("uJ per arc",False)
        self.filetypes["2"] = ("No flux calibration","noflux")
        self.seltype = 0

    def changeType(self):
        self.seltype = self.seltype + 1
        if self.seltype > 2:
            self.seltype = 0
        else:
            pass
        
class _wavelengthRanges():
    
    def __init__(self):
        self.wavelengths = OrderedDict()
        self.wavelengths["0"] = ["Whole"]
        self.wavelengths["1"] = ["5893"]
        self.wavelengths["2"] = ["4358"]
        self.wavelengths["3"] = ["5896"]
        self.wavelengths["4"] = ["5890"]
        self.wavelengths["5"] = ["Custom"]
        self.selwave = 0
        
        self.range = OrderedDict()
        self.range["0"] = ["70","70"]
        self.range["1"] = ["500","500"]
        self.selrange = 0
    
    def changeWave(self):
        self.selwave = self.selwave + 1
        if self.selwave > 5:
            self.selwave = 0
        else:
            pass
    
    def changeRange(self):
        self.selrange = self.selrange + 1
        if self.selrange > 1:
            self.selrange = 0
        else:
            pass
    
    def setCustrange(self,win):
        #maxy,maxx = stdscr.getmaxyx()
        curses.echo()
        win.addstr(1,1,"Enter bottom range: ")
        bottomlimit = win.getstr()
        win.addstr(1,1,"Enter top range: ")
        toplimit = win.getstr()
        
        self.range["1"][0] = str(bottomlimit)
        self.range["1"][1] = str(toplimit)

        #self.wavelengths["3"][0] = "Custom (%s - %s)" % (minwav,maxwav)
        curses.noecho()
               
    def setCust(self,win):
        #maxy,maxx = stdscr.getmaxyx()
        curses.echo()
        win.addstr(1,1,"Enter central wavelength: ")
        cenwav = win.getstr()
        
        self.wavelengths["3"][0] = str(cenwav)

        #self.wavelengths["3"][0] = "Custom (%s - %s)" % (minwav,maxwav)
        curses.noecho()
        

def getlog(date):
    yy = date[0] + date[1]
    mm = date[2] + date[3]
    dd = date[4] + date[5]
    subprocess.call('gedit /home/lplogs/logdata/20'+yy+'-'+mm+'/20'+yy+mm+dd+'.wht &', shell = True)
        
def linemeasure(files,path,plottingparams,win,date,highlighted,all=False,superall=False):
    

    
    for fileidentifier in files:
        if all == False:
            filename = highlighted
            kill = True
        else:
            filename = files[fileidentifier]
            with open("/data/nik/Reductions/CHRIST2","a") as christ:
                christ.write(path)
                christ.write(" ")
                christ.write(filename)
                christ.write("\n")
            kill = False
            
            
             
            
        import DatabasedOutputter
        
        selwave = plottingparams["selwave"]
        #seltype = plottingparams["seltype"]
        mlines = plottingparams["mlines"]
        measure = []
        measurecont = []
        measurecount = []
        measurecountcont = []
        FWHM = []
        AB = False
        thelines = []
    
        filefound = False
        
        for file in os.listdir(path + filename + "/"):
            if file.startswith("Extracted") and file.endswith("ABmagsquare.fits"):
                iraf.imgets(path + filename + "/" + file,"CAT-NAME")
                obj = iraf.imgets.value
                
                checkandconverttoUJARC(path,filename,file)
                
                try:
#                    iraf.imgets(path + filename + "/" + file,"ISIGRAT")
#                    grating = iraf.imgets.value
#                    wavelength1 = "5893"
#                    wavelength2 = "5893"
#                    wavelength3 = "5899"
#                    wavelength4 = "6138"
#                    wavelength5 = "4046"
#                    
#                    if "R316R" in grating or "R600R" in grating:
#                        mlines.lines["0"] = [wavelength1,True,21,90]
#                        mlines.lines["1"] = [wavelength2,False,20,90]
#                        mlines.lines["2"] = [wavelength3,True,19,90]
#                        mlines.lines["3"] = [wavelength4,False, 18,90]
#                        mlines.lines["4"] = [wavelength5,False, 17, 90]
#                    elif "R158R" in grating:
#                        mlines.lines["0"] = [wavelength1,False,21,90]
#                        mlines.lines["1"] = [wavelength2,True,20,90]
#                        mlines.lines["2"] = [wavelength3,False,19,90]
#                        mlines.lines["3"] = [wavelength4,False, 18,90]
#                        mlines.lines["4"] = [wavelength5,False, 17, 90]                       
#                    else:
#                        mlines.lines["0"] = [wavelength1,False,21,90]
#                        mlines.lines["1"] = [wavelength2,False,20,90]
#                        mlines.lines["2"] = [wavelength3,False,19,90]
#                        mlines.lines["3"] = [wavelength4,False,18,90]
#                        mlines.lines["4"] = [wavelength5,True,17,90]
                        
#                    if "R316R" in grating:
#                        mlines.lines["0"] = ["8027",False,21,90]
#                        mlines.lines["1"] = ["8140",True,20,90]
#                        mlines.lines["2"] = ["8150",True,19,90]
#                        mlines.lines["3"] = ["8186",True, 18,90]
#                        mlines.lines["4"] = ["8196", True, 17, 90]
                        
                    for file2 in os.listdir(path + filename + "/"):
                        if file2.startswith("wave") and file2.endswith(obj + ".fits"):
                            countsfile = file2
                        else:
                            pass

                except:
                    pass
                
                
                if AB == False:
                    file = "Extracted" + obj + "magsquare.fits"
                    with open("/data/nik/Reductions/CHRIST2","a") as christ:
                        christ.write(file)
                        christ.write(" -- ")
                        christ.write(path+filename+"/"+file)
                        christ.write("\n")
                else:
                    pass
                if os.path.isfile(path+filename+"/"+file):
                    filefound = True
                else:
                    filefound = False
                break
            else:
                pass
        
        if filefound == True:
            #if xmin != "":
            #    iraf.splot(path + filename + "/" + file,xmin=xmin,xmax=xmax)
            #else:
            #    iraf.splot(path + filename + "/" + file)
            cenwav = selwave.wavelengths[str(selwave.selwave)][0]
            xmin = str(int(cenwav) - int(selwave.range[str(selwave.selrange)][0]))
            xmax = str(int(cenwav) + int(selwave.range[str(selwave.selrange)][1]))

            with open("/data/nik/Reductions/CHRIST2","a") as christ:
                christ.write("Filefound\n")          
            
            numberoflines = 0
            
            fitlines = "/home/nik/Reductions/fitlines"    
            with open(fitlines,"w") as filething:
                for entry in mlines.fittype:
                    if mlines.fittype[entry][1] == True:
                        fittype = entry
                    else:
                        pass
                for entry in mlines.lines:
                    if mlines.lines[entry][1] == True:
                        filething.write("%s\t%s\n" % (mlines.lines[entry][0],fittype))
                        thelines.append(mlines.lines[entry][0])
                        numberoflines = numberoflines + 1
                    else:
                        pass
                    
                #filething.write("%s\tgaussian" % cenwav)
            
            range = xmin + " " + xmax
            
            remove(path+filename+"/log")
            try:
                with open("/data/nik/Reductions/CHRIST2","a") as christ:
                    christ.write("Doing fits prof ----")     
                iraf.fitprofs(path+filename+"/"+file,reg = range,pos=fitlines,log=path+filename+"/log", gfwhm="5")
                success = True
                with open("/data/nik/Reductions/CHRIST2","a") as christ:
                    christ.write("Done fits prof\n")     
            except:
                success = False
            if success == True:
                with open(path + filename + "/log","r") as logfile:
                    linepos = 1
                    for i,line in enumerate(logfile):
                        if i == 2:
                            win.addstr(linepos,1,line[:50])
                            win.refresh()
                            linepos = linepos + 1
                        if i > 2 and i <= 2 + numberoflines:
                            win.addstr(linepos,1,line[:50])
                            win.refresh()
                            
                            j=line.strip()
                            q = j.split()
                            try:
                                if float(thelines[3-i]) - float(q[0]) > 6:
                                    measure.append("")
                                    measurecont.append("")
                                else:
                                    measure.append(q[2])
                                    measurecont.append(q[1])
                            except:
                                measure.append(q[2])
                                measurecont.append(q[1])
                            linepos = linepos + 1
                        elif i > 2 + numberoflines:
                            break
            else:
                pass
            
            remove(path+filename+"/log2")
            try:
                iraf.fitprofs(path+filename+"/"+countsfile,reg = range,pos=fitlines,log=path+filename+"/log2", gfwhm="5")
                success = True
            except:
                success = False
            if success == True:
                with open(path + filename + "/log2","r") as logfile:
                    linepos = 1
                    for i,line in enumerate(logfile):
                        if i == 2:
                            win.addstr(linepos,1,line[:50])
                            win.refresh()
                            linepos = linepos + 1
                        if i > 2 and i <= 2 + numberoflines:
                            win.addstr(linepos,1,line[:50])
                            win.refresh()
                            
                            o=line.strip()
                            p = o.split()
                            try:
                                if float(thelines[3-i]) - float(p[0]) > 6:
                                    measurecount.append("")
                                    measurecountcont.append("")
                                    FWHM.append("")
                                else:
                                    measurecount.append(p[2])
                                    measurecountcont.append(p[1])
                                    FWHM.append(p[5])
                            except:
                                measurecount.append(p[2])
                                measurecountcont.append(p[1])
                                FWHM.append(p[5])
                            linepos = linepos + 1
                        elif i > 2 + numberoflines:
                            break
            else:
                pass           
            
            
            reload(DatabasedOutputter)
            headerlist = ["DATE","UTSTART","OBJECT","RUN","ISIARM","CENWAVE","ISIDEKKE","ISISLITW","ISIFILTA","ISIFILTB","ISIDICHR","RA","DEC","JD","AZSTART","ZDSTART","DAZSTART","AIRMASS","CCDXBIN","CCDYBIN","DATE-OBS","UTSTART","EXPTIME","CCDSPEED","GAIN","ISIGRAT","READNOIS"]
            headerinfo = []
            for i in headerlist:
                if i == "DATE":
                    headerinfo.append(date)
                else:
                    iraf.imgets(path + filename + "/" + file,i)
                    try:
                        headerinfo.append(iraf.imgets.value)
                    except:
                        headerinfo.append("Failed to get")
            i = 0
            for entry in mlines.lines:
                if mlines.lines[entry][1] == True:
                    try:     
                        DatabasedOutputter.writetoDB(headerinfo,mlines.lines[entry][0],measure[i],measurecont[i],measurecount[i],measurecountcont[i],headerlist,FWHM[i])
                    except:
                        DatabasedOutputter.writetoDB(headerinfo,mlines.lines[entry][0],"","","","",headerlist,"")
                    i = i + 1
                else:
                    pass
                
            if kill == True:
                return
            else:
                pass
        else:
            pass


class _measurementlines():
    
    def __init__(self):
        self.lines = OrderedDict()
        self.listoflines = ["4358","5890","5896","5893","9999"]
        i = 0
        startcolumn = 21
        while i < len(self.listoflines):
            column = startcolumn - i
            self.lines[str(i)] = [self.listoflines[i],False,column,90]
            i = i + 1
        #self.lines["0"] = ["4358",False,21,90]
        #self.lines["1"] = ["5890",False,20,90]
        #self.lines["2"] = ["5896",False,19,90]
        #self.lines["3"] = ["5893",False,18,90]
        #self.lines["4"] = ["9999",False,17,90]
        
        self.lastcolumn = column
        
        self.fittype = OrderedDict()
        self.fittype["gaussian"] = ["gaussian",True,self.lastcolumn - 1,85]
        self.fittype["lorentzian"] = ["lorentzian",False,self.lastcolumn - 2,85]
        
    def updatefittype(self):
        self.fittype["gaussian"][2] = self.lastcolumn - 1
        self.fittype["lorentzian"][2] = self.lastcolumn - 2
                
    def addLine(self,win):
        curses.echo()
        win.addstr(1,1,"Enter wavelength: ")
        wavelength = win.getstr()
        curses.noecho()
        noentries = len(self.lines)
        self.lastcolumn = self.lastcolumn - 1
        self.lines[str(noentries)] = [str(wavelength),False,self.lastcolumn,90]
        self.updatefittype()
    
    def delLine(self):
        noentries = len(self.lines)
        self.lastcolumn = self.lastcolumn + 1
        del self.lines[str(noentries - 1)]
        self.updatefittype()
        
        
    def switchState(self,variable):
        if self.lines[variable][1] == True:
            self.lines[variable][1] = False
        elif self.lines[variable][1] == False:
            self.lines[variable][1] = True
            
    def switchFittype(self,variable):
        if self.fittype["gaussian"][1] == True:
            self.fittype["gaussian"][1] = False
            self.fittype["lorentzian"][1] = True
        elif self.fittype["lorentzian"][1] == True:
            self.fittype["lorentzian"][1] = False
            self.fittype["gaussian"][1] = True
         
    def checkClick(self,stdscr,win):
        _,mx,my,_,_ = curses.getmouse()
        for entry in self.lines:
            if my == self.lines[entry][2] and self.lines[entry][3] - 2 < mx < self.lines[entry][3] + 4:
                self.switchState(entry)
            elif my == self.lines[entry][2] and self.lines[entry][3] + 3 < mx < self.lines[entry][3] + 10:
                self.setMeasure(win,entry)
            else:
                pass
        for entry in self.fittype:
            if my == self.fittype[entry][2] and self.fittype[entry][3] - 2 < mx < self.fittype[entry][3] + 10:
                self.switchFittype(entry)
            else:
                pass
    def setMeasure(self,win,entry):
        #maxy,maxx = stdscr.getmaxyx()
        curses.echo()
        win.addstr(1,1,"Enter wavelength: ")
        wavelength = win.getstr()

        
        self.lines[entry][0] = str(wavelength)

        #self.wavelengths["3"][0] = "Custom (%s - %s)" % (minwav,maxwav)
        curses.noecho()
def splot(filename,path,plottingparams):
    
    selwave = plottingparams["selwave"]
    seltype = plottingparams["seltype"]
    
    cenwav = selwave.wavelengths[str(selwave.selwave)][0]
    if cenwav == "Whole" or cenwav == "Custom":
        xmin = ""
        xmax = ""
    else:
        xmin = str(int(cenwav) - int(selwave.range[str(selwave.selrange)][0]))
        xmax = str(int(cenwav) + int(selwave.range[str(selwave.selrange)][1]))
    
    AB = seltype.filetypes[str(seltype.seltype)][1]
    # add a check for which file
    
    for file in os.listdir(path + filename + "/"):
        
        if file.startswith("Extracted") and file.endswith("ABmagsquare.fits"):
            iraf.imgets(path + filename + "/" + file,"CAT-NAME")
            obj = iraf.imgets.value
            if AB == False:
                file = "Extracted" + obj + "magsquare.fits"
                break
            elif AB == "noflux":
                file = "wave" + obj + ".fits"
                break
            else:
                pass
            break
        else:
            pass
    
    if xmin != "":
        iraf.splot(path + filename + "/" + file,band="1",line="1",xmin=xmin,xmax=xmax)
    else:
        iraf.splot(path + filename + "/" + file,band="1",line="1")
        
            
def printcolumn(stdscr,list,columnstart,rowselected,howmanycolumns,end,colhi,colno,everythingelse,xInfo=False,path='None'):
    # take in filelist and then just print it into a column
    # calculate how many columns it's going to take up
    global allfileinfo
    
    i = 1
    maxlength = 8
    # Print the folder
    
    while i < len(list) + 1:
        if i > maxlength:
            break
        else:
            pass
        
        j = (i + everythingelse.scroll) - 1
        
        if j > len(list):
            break
        else:
            pass
    
        
        if int(j) == int(rowselected):
            if colhi >= colno:
                stdscr.addstr(int(i) + linesofheaders,columnstart,list[str(j)][:howmanycolumns],curses.color_pair(2))
                endcursor(stdscr)
            else:
                stdscr.addstr(int(i) + linesofheaders,columnstart,list[str(j)][:howmanycolumns],curses.color_pair(1))
                endcursor(stdscr)
        else:
            stdscr.addstr(int(i) + linesofheaders,columnstart,list[str(j)][:howmanycolumns])
            endcursor(stdscr)
        stdscr.addstr(int(i) + linesofheaders,end,"|")
        endcursor(stdscr)
    # Potentially print EXTRA INFORMATION
    # Check here if the dict entry exists
    # It will return the list or NONE (NO FILES)
        if xInfo == True:
            fieldlist = ("EXPTIME","UTSTART","CENWAVE","ISIGRAT","AIRMASS")
            if "blue" in path.lower():
                arm = "blue"
            elif "red" in path.lower():
                arm = "red"
            else:
                arm = "NONE"
            
            try:
                # check it's there
                fileinfo = allfileinfo[list[str(j)]+arm] # this needs to be some sort of global list
            except:
                # init it
                allfileinfo[list[str(j)]+arm] = _extraInfo(list[str(j)],path)
                fileinfo = allfileinfo[list[str(j)]+arm]
            
            if fileinfo.infolist['FilePres'] == True:
                position = end + 2
                for info in fieldlist:
                    
                    length = 5
                    increment = 10
                    display = fileinfo.infolist[info][:length]
                    
                    if info == "CENWAVE":
                        
                        gratpm = int(g.GratingDict[fileinfo.infolist["ISIGRAT"]][0])
                        wavelength = int(float(fileinfo.infolist["CENWAVE"]))
                        display = str(wavelength) + "+-" + str(gratpm)
                        increment = 15
                    else:
                        pass
                        
                        
                        
                    
                    
                    stdscr.addstr(int(i) + linesofheaders,position,display)
                    endcursor(stdscr)
                    stdscr.addstr(0,position,info)
                    endcursor(stdscr)
                    position = position + increment
            else:
                pass
          
        i = i + 1


def checkandconverttoUJARC(path,objpath,file):
    
    #thefullnameofABmagperetc
    ABFile = file
    dir = path + objpath + "/" #driectory
    
    iraf.imgets(dir + ABFile,"CAT-NAME")
    object = iraf.imgets.value
    
    if os.path.isfile(dir + "Extracted" + object + "magsquare.fits") == True:
        remove(dir + "Extracted" + object + "magsquare.fits")
        #print "File exists, that's fine and this is working"
    else:
        pass
    if os.path.isfile(dir + "Extracted"+object+".fits") == True:
        #print "Would you like to convert the file?"
        
        red = "red"
        blue = "blue"
        if red in dir:
            arm = "red"
        elif blue in dir:
            arm = "blue"
        else:
            print dir
            print "BROKEN"
            exit()
            
        if arm == "blue":
            #print "Blue arm"
            pxscale = 0.2
        else:
            #print "Red arm"
            pxscale = 0.22
        
        slitwidth = 0
        binning = 0
        iraf.imgets(dir + ABFile,"ISISLITW")
        slitwidth = iraf.imgets.value
        iraf.imgets(dir + ABFile,"CCDXBIN")
        binning = iraf.imgets.value
        
        if slitwidth == 0:
            exit()
        elif binning == 0:
            exit()
        else:
            pass
        
        #slitarea = float(slitwidth)*float(pxscale)*float(binning)
        slitarea = float(slitwidth)*float(4*60)
        iraf.imarith(operand1=dir + "Extracted" + object + ".fits",op="/",operand2=slitarea,result=dir + "Extracted" + object + "magsquare.fits")
        
        
    else:
        pass
        #print "File not there is it"
    

        
def filelistfun(totaldir):
    foldernames={}
    i=1
    unsorteddir = ()
    for dir in os.listdir(totaldir):
        unsorteddir = unsorteddir + (dir,)
    for dir in sorted(unsorteddir):
        if os.path.isdir(totaldir + dir) == True:
            foldernames[str(i)] = dir
            i=i+1
        else:
            pass
    return foldernames



class _extraInfo():
    
    #info per folder
    
    def __init__(self,object,path):
        # fieldlist is all the possible fields that I can obs
        self.fieldlist = ("EXPTIME","UTSTART","UTOBS","CENWAVE","ISIGRAT","AIRMASS")
        self.path = path
        self.object = object
        self.filename = self.getFileName()
        self.infolist = self.extraInfo()
        
    def extraInfo(self):
        # We will do lots of imgets here
        infolist = {}
        #print path + filename
        if self.filename == "None":
            infolist['FilePres'] = False
        else:
            infolist['FilePres'] = True
            for field in self.fieldlist:
                #print self.path
                #print self.filename
                iraf.imgets(self.path + "/" + self.object + "/" + self.filename,field)
                #print iraf.imgets.value
                infolist[field] = iraf.imgets.value
        return infolist
                
            
    def getFileName(self):
        for file in os.listdir(self.path + "/" + self.object + "/"):
            if file.startswith("Extracted") and file.endswith("ABmagsquare.fits"):
                checkandconverttoUJARC(self.path,self.object,file)
                return file
            else:
                pass
        return "None"
    
