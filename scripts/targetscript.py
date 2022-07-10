#!/home/rts2obs/anaconda3/bin/python3 

#import rts2
import json
#from rts2 import scriptcomm
from rts2solib import scriptcomm

from rts2solib.big61filters import filter_set
from rts2solib import Config
#from rts2solib import to_dataserver
import requests
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from telescope import kuiper
import datetime
import math
import sys
import pytz
import requests

class scripter(scriptcomm.Rts2Comm):
    """
        Rts2Comm scripter class

        Description:
        Reads and executes the instructions
        in the json script file.
    """

    def __init__( self, faketarget=None  ):
        scriptcomm.Rts2Comm.__init__(self)
        self.cfg = Config()
        self.filters = filter_set()

        if faketarget is not None:
            self.log("W", "looking at fake target {}".format(faketarget))
            targetid=faketarget
        else:
            targetid = self.getValue("current_target", "SEL")

        self.targetid = targetid
        self.orpapitoken = 'xa3CNDyDYFojPUTDYMfnDtezzQmI37hl-7WA4Q'

        self.tel = kuiper()
        #TODO  this should be done via rts2 and not 
        # directly with the telescope class. 
        # to fix this may require updating rts2 telescope driver.
        self.tel.comBIAS("OFF")
        self.script = None
        self.log("W", "looking at target {}".format(targetid))
        name = self.getValue("current_name", "EXEC")

        # remove the first 4 bits that make the name
        # unique and write that to objectName.
        self.setValue( "objectName", name[4:] )

        #TODO
        # have the rts2_script be grabbed from the ORP API get method
        # shouldn't have to create the sql database connection like this...
        
        db_resp = None
        params = {
            'rts2id':int(self.targetid),
            'api_token':self.orpapitoken,
        }
        api_target = 'https://scopenet.as.arizona.edu/orp/api/v0/obsreq'
        try:
            self.log('W', 'Grabbing ORP observation doc')
            r = requests.get(url=api_target, json=params)
            result = json.loads(r.text)
            db_resp = result[0]
            self.script = db_resp['rts2_doc']
        except:
            self.log('E', 'ARTN ORP API ERROR QUERYING FOR TARGET: {}'.format(r.text))
        
        if db_resp:
            #self.setValue('ObservationID', db_resp[0].observation_id, "C0")
            self.setValue('ObservationID', db_resp['observation_id'], "C0")

            #binning = db_resp[0].binning
            binning = db_resp['binning']
            if binning in ("4x4", "3x3", "2x2", "1x1"):
                if binning == "1x1":
                    self.setValue("binning", 1)
                if binning == "2x2":
                    self.setValue("binning", 2)
                if binning == "3x3":
                    self.setValue("binning", 3)
                if binning == "4x4":
                    self.setValue("binning", 4)
            else:
                self.setValue("binning", 4) # 4x4 binning

            #if db_resp[0].non_sidereal:
            if db_resp['non_sidereal']:
                #self.rates = db_resp[0].non_sidereal_json
                self.rates = db_resp['non_sidereal_json']
                self.tel.comBIAS("ON")

                # The idea here is that the non sidereal
                # targets will have an RA and Dec, RA Bias rate, Dec bias rate,
                # position epoch, object time epoch, position angle, bias_percentage
                # and object rate. The telescope should go to the coordinates
                # RA+sin(position_angle)*object_rate, Dec+cos(position_angle)*object_rate
                # and set the bias rates to 
                # RA_bias_rate*bias_percentage, Dec_bias_rate*bias_percentage
                # Scott June 2019

                utc_at_position=self.rates["UTC_At_Position"]
                dt_epoch = pytz.utc.localize(datetime.datetime.strptime(utc_at_position, "%Y-%m-%dT%H:%M:%S"))
                now = pytz.utc.localize(datetime.datetime.utcnow())
                delta_time = now-dt_epoch
                
                biasra = float(self.rates['RA_BiasRate'])
                biasdec = float(self.rates['Dec_BiasRate'])
                ra_offset = biasra*delta_time.total_seconds()
                dec_offset = biasdec*delta_time.total_seconds()
                self.log("I", "Setting rates to {} {}".format(biasra, biasdec))
                self.tel.command("BIASRA {}".format(biasra))
                self.tel.command("BIASDEC {}".format(biasdec))

                self.log("I", "Setting offset to {}s {}s (UT {}, delta {})".format(ra_offset, dec_offset, utc_at_position, delta_time.total_seconds()))
                self.setValue( 'woffs', '{}s {}s'.format(ra_offset, dec_offset), 'BIG61')

            else:
                self.tel.command("BIASRA 0")
                self.tel.command("BIASDEC 0")

        self.has_exposed = False


    def run( self ):

        if self.script is not None:
            self.setValue("SHUTTER", 0, "C0")
            self.log("I", "running target {name} at {ra} {dec}".format( **self.script  ) )

            # move the object from the center of the chip
            #self.setValue( 'woffs', '1m 0', 'BIG61')
            total_exposures = 0
            for exp in self.script['obs_info']:
                total_exposures += int( exp["amount"] )
            
            exp_num = 0
            self.setValue("scriptPosition", total_exposures, 'C0')
            for exp in self.script['obs_info']:
                self.setValue("exposure", exp['exptime'] )
                try:
                    repeat = int( exp["amount"] )
                except ValueError:
                    repeat = 1
                self.log('W', "repeat is {}".format(repeat))
                self.setValue("scriptPosition", total_exposures, 'C0')
                for ii in range(repeat):
                    if exp['Filter'].lower() == 'clear':
                        filt = 'OPEN'
                    else:
                        filt = exp['Filter']

                    filtname = self.filters.check_alias(filt)

                    if filtname is None:
                        self.log("E", "filter {} not loaded on instrument".format(filt))
                    else:
                        self.setValue("filter",filtname, 'W0' )
                        self.setValue("scriptPosition", total_exposures, 'C0')
                        exp_num+=1
                        self.log("W", "Calling exp {} of {}".format(exp_num, total_exposures) )
                        imgdir = "/rts2data/Kuiper/Mont4k/%N/object/%f"
                        imgfile = self.exposure( self.before_exposure, imgdir)
                        self.log("W", "imgfile is {}".format(imgfile))
                        path = os.path.dirname(imgfile)
                        basename = os.path.basename(imgfile)

                        if exp_num == total_exposures:
                            status = 'completed'
                            percent_completed = 100.0
                        else:
                            status = 'inprogress'
                            percent_completed = float(exp_num)/float(total_exposures)*100.0

                        params = {
                            'rts2id':self.targetid,
                            'api_token':self.orpapitoken,
                            'status':status,
                            'percent_completed':percent_completed
                        }
                        api_target = 'https://scopenet.as.arizona.edu/orp/api/v0/obsreq'
                        try:
                            self.log('W', 'Updating ORP status')
                            r = requests.put(url=api_target, json=params)
                            self.log('W', r.text)
                        except:
                            self.log('E', 'ARTN ORP API ERROR UPDATING STATUS: {}'.format(r.text))

            if not self.has_exposed:
                self.log('E', 'DID NOT EXPOSE, taking 0 second exposure to get it to chug')
                self.setValue("exposure", 1)
                imgfile = self.exposure(self.before_exposure)

        else:
            self.log("E", "there doesn't seem to be script file! Skipping")


        if self.script is not None:
            if "requeue" in self.script:
                try:
                    self.requeue('requeue', int(self.script["requeue"] ) )
                except Exception as err:
                    self.log("E", "could not requeue b/c {}".format(err) )

        self.tel.comBIAS("OFF")       

    def before_exposure(self):
        self.has_exposed = True


faketarget=None
if len(sys.argv) == 2:
    faketarget = sys.argv[1]

sc=scripter(faketarget)
sc.run()
