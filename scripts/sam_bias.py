#!/home/rts2obs/anaconda3/bin/python3

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

    def run(self): 
        for b in self.binnings:
            self.log('I','Starting darks for '+str(b)+'x'+str(b)+' binning')
            for i in range(0,15):
                self.setValue('SHUTTER', 'DARK')
                self.setValue('exposure', 0)
                self.setValue('binning',b)
                imgdir = "/rts2data/Kuiper/Mont4k/%N/dark/%f"
                filename = self.exposure(None, imgdir)


bs = bias_scripter()
bs.run()
