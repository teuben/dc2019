############
# Simulation parameters 
############

## Simanalyze script 
anaScript = 'ACAanalyze.py'   # ARC's recommendation 
#anaScript = 'ACAanalyze2.py' # CASA Guide method 

fitsFile = 'M51ha.fits'
#fitsFile = 'ngc3627/psfmatched_sdssSwarp-g.fits'

### Simulation settings 
project = "m51c"


indirection = "J2000 23h59m59.96s -34d59m59.50s"
incell = "0.1arcsec"
incenter = "330.076 GHz"
inwidth = "50MHz" 
inbright = '0.004' # blank for auto scaling using SN in model image
config = ["alma.cycle6.3"] #,"alma.cycle6.1"] # Must be string array 
acaconfig = "aca.cycle6"
hourangle = '' # blank for 'transit'

# Mosaic setting 
mapsize = "80 arcsec" 
mapsizeTP = str( float(mapsize.split("arcsec")[0])*1.3 )+" arcsec"

# Sensitivity setting 
integration = '10s'  
pwv = 0.9
# Check the help page of simobserve() for time setting. 
timeRatio = [1, 3, 4] #  12m : 7m : TP
totaltime12 = '30min'  # blank for 1 integ. per field
totaltime7 =  '72min'  #str(timeRatio[1]) #'' # '3'  #  
totaltimeTP = '123min' # str(timeRatio[2]) #'' # '2h' #


