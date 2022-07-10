#!/home/rts2obs/anaconda3/bin/python3

import numpy
import os
from astropy.io import fits as pyfits

from rts2solib import scriptcomm
from rts2solib.big61filters import filter_set
from rts2solib import Config
from telescope import kuiper

#class BiasScript (scriptcomm.Rts2Comm):
#
#    """Class for taking a bunch of biases."""
#
#
#    def __init__(
#            self, numbias=2, binning=3 ):
#        scriptcomm.Rts2Comm.__init__(self)
#
#        self.numbias = numbias
#        self.binning = binning
#
#    def takeBias(self):
#        self.setValue('SHUTTER', 'DARK')
#        self.setValue('exposure', 0)
#        filename = self.exposure(None, "yo.fits")
#        
#        to_dataserver(filename, "yo.fits")
#        i = 0
##        while i < self.numbias:
##            i += 1
##            bias = self.exposure()
##            self.toDark(bias)
#
#
#    def run(self):
#        self.takeBias()


class bias_scripter(scriptcomm.Rts2Comm):
    '''
        Rts2Comm scripter class for biases

        Description:
        runs darks biases zeros etc
    '''
    def __init__(self):
        scriptcomm.Rts2Comm.__init__(self)
        self.cfg = Config()
        self.binnings = [3,4]
        self.bias_dictionary = {}

    def run(self): 
        for b in self.binnings:
            self.log('I','Starting darks for '+str(b)+'x'+str(b)+' binning')
            self.bias_dictionary[str(b)] = []
            for i in range(0,10):
                self.setValue('SHUTTER', 'DARK')
                self.setValue('exposure', 0)
                self.setValue('binning',b)
                imgdir = "/rts2data/Kuiper/Mont4k/%N/dark/%f"
                try:
                    filename = self.exposure(None, imgdir)
                    self.bias_dictionary[str(b)].append(filename)
                except:
                    self.log('E', 'Error in bias_artn.py when calling zero exposure to C0')

    def create_master_bias(self):
        for b in self.binnings:
            bias_files = self.bias_dictionary[str(b)]
            f = pyfits.open(bias_files[0])
            d = numpy.empty([len(bias_files), len(f[0].data), len(f[0].data[0])])
            d[0] = f[0].data / numpy.mean(f[0].data)
            for x in range(1, len(bias_files)):
                f = pyfits.open(bias_files[x])
                d[x] = f[0].data / numpy.mean(f[0].data)
            a = bias_files[0].split('/')
            of = ''
            for p in a[:len(a)-1]:
                of += p+'/'
            of += 'master_dark_b{}.fits'.format(b)
            f = pyfits.open(of, mode='append')
            m = numpy.median(d, axis=0)
            m = m / numpy.max(m)
            i = pyfits.PrimaryHDU(data=m)
            f.append(i)
            f.close()

def test_create_master():
    binnings = [3,4]
    pwd = '/rts2data/Kuiper/Mont4k/20220314/dark/stitched/'
    binning_dict = {}
    fits_files = [x for x in os.listdir(pwd) if 'fits' in x and 'master' not in x]
    for b in binnings:
        binning_dict[str(b)] = []
        print(b)
        for fi in fits_files:
            f = pyfits.open(pwd+fi)
            binn = f[0].header['ccdsum']
            if str(b) in binn:
                binning_dict[str(b)].append(pwd+fi)
        #print(binning_dict[b])

    bs = bias_scripter()
    bs.bias_dictionary = binning_dict
    bs.create_master_bias()

bs = bias_scripter()
bs.run()

