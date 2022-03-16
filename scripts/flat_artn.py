#!/home/rts2obs/anaconda3/bin/python3 

# Example configuation of flats.
# (C) 2010 Petr Kubanek
#
# Please see flats.py file for details about needed files.
#
# You most probably would like to modify this file to suit your needs.
# Please see comments in flats.py for details of the parameters.

import json
import numpy
import sys

from rts2solib import flats 
from rts2solib.big61filters import filter_set
from telescope import kuiper

k = kuiper()
Filters = filter_set()
Flat, FlatScript = flats.Flat, flats.FlatScript

Flat_list = []
binnings = [3, 4]

for f in Filters:
    if str(f).lower() != 'open':# and str(f).lower() != 'bessell-u':
        for b in binnings:
            Flat_list.append(Flat((f,), binning=b, window='100 100 500 500'))

# You would at least like to specify filter order, if not binning and
# other thingsa

# binning[0]==3x3 and binning[1]=1x1
expt = numpy.arange(1, 5, 0.2)
expt = numpy.append(expt, numpy.arange(5, 10, 0.5))
expt = numpy.append(expt, numpy.arange(10, 41))

f = FlatScript(
    eveningFlats=Flat_list,maxBias=0, maxDarks=0, expTimes=expt
)


f.log('I', 'Sammy boys flat script start')
# Change deafult number of images
f.flatLevels(optimalFlat=20000, defaultNumberFlats=5, biasLevel=1000, allowedOptimalDeviation=0.3)

# Run it..
# Configure domeDevice,tmpDirectory and mountDevice if your device names differ
f.run()
	#raise Exception("test error")
#except Exception as err:
#	f.log("E", "there was an erro in creating the master flats {}".format(err) )



