############
# Simulation parameters 
############

## Simanalyze script 
anaScript = 'ACAanalyze.py'   # ARC's recommendation 
#anaScript = 'ACAanalyze2.py' # CASA Guide method 

fitsFile = 'skymodel-b.fits'


### Simulation settings 
#project = "gmc_1" # 10s int pwv=5mm
#project = "gmc_10" # 10s int pwv=5mm
#project = "gmc_1_noise" # with noisy MS
project = "gmc_1b" # 10s int pwv=5mm for skymodel-b.fits

indirection = "J2000 12h00m00.0s -35d00m0.0s"
incell = "0.05arcsec"
incenter = "115 GHz"
inwidth = "2GHz" 
inbright = '0.0001' #[Jy/pix] blank for auto scaling using SN in model image
config = ["alma.cycle6.4","alma.cycle6.1"] # Must be string array 
acaconfig = "aca.cycle6"
hourangle = '' # blank for 'transit'

# Mosaic setting 
mapsize = "160 arcsec" 
mapsizeTP = str( float(mapsize.split("arcsec")[0])*1.3 )+" arcsec"

# Sensitivity setting 
integration = '10s'  
pwv = 5

# Check the help page of simobserve() for time setting. 
#timeRatio = [120, 360, 480] #  12m : 7m : TP
totaltime12 = '1' # Number of visit per field 
totaltime7 =  '3' # 
totaltimeTP = '4' # 

# Output image setting
outcell = '0.2 arcsec'
outImgSize = [1250,1250]

## Use noisy visibility for image
noisy = False
