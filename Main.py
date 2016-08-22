import Globals as g
g.init()
import curses.wrapper

import sys
if len(sys.argv) == 3:
	print "Executing in continuous mode"
	g.colour = sys.argv[1]
	g.date = sys.argv[2]
	g.cont = True
else:
	pass


import Navigation
if g.colour == "red":
	import ReductionMode as RM
else:
	import ReductionMode as RM
import MeasuringMode as MM
from Common import colour as colour
from Common import query_yes_no as query_yes_no

import os
sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=32, cols=100))
from time import sleep







# Although this is a hardcoded directory, I am only really using this program from two machines
# And realistically this can just be recoded into an input, but it is pointless for myself
if g.cont == True:
	g.homedir = "/data/nik"
else:
	if query_yes_no("Are you working from the laptop?: ",default="no") == True:
		g.homedir = "/media/ing_home"
	else:
		g.homedir = "/data/nik"
	
# I don't know why I had to do this sys.path.append, it might be something to do with opening the 
# 'history.dat' file
# cwd should be where the extraction program was opened
sys.path.append(g.cwd)
g.cwd = os.getcwd()

if g.cont == True:
	g.mode = "Reduce"
	g.reductdir = "/Reductions"
else:
	Navigation.chooseMode()
	Navigation.ChooseDirectory()



while True:
	if g.mode == "Reduce":
		RM.RMLoop()
	elif g.mode == "Measure":
		MM.RunLoop()
	sleep(0.5)
	print "You can type Q to exit"
	Navigation.chooseMode()
	