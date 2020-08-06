############
# Simulation parameters 
############

## PATH to configuration files
configPATH = '/home/takagits/work/alma/simmos/'

## Simanalyze script 
anaScript = 'ACAanalyzeL.py'   # ARC's recommendation 

## Sky model
fitsFile = 'skymodel.fits'


### Simulation settings 
#project = "gmc_1" # 10s int pwv=5mm
#project = "gmc_1_noise" # with noisy MS
#project = "gmc_10" # 10sx10 int pwv=5mm
project = "gmc_2L" # 10sx2 int pwv=5mm in 2days

indirection = "J2000 12h00m00.0s -35d00m0.0s"
incell = "0.05arcsec"
incenter = "115 GHz"
inwidth = "2GHz" 
inbright = '0.0001' #[Jy/pix] 
config = ["alma.cycle6.4","alma.cycle6.1"] # Must be string array with 'alma.*'
acaconfig = "aca.cycle6" 
hourangle = '' # blank for 'transit'

# Mosaic setting 
mapsize = "160 arcsec" 
mapsizeTP = str( float(mapsize.split("arcsec")[0])*1.3 )+" arcsec"

# Sensitivity setting 
integration = '10s'  
pwv = 5.

# Check the help page of simobserve() for time setting. 
#timeRatio = [120, 360, 480] #  12m : 7m : TP
nVisit12 = '2' # Number of visit per field 
nVisit7 =  '6' # 
nVisitTP = '8' # 
days = 2  # number of days for observation

# Output image setting
outcell = '0.2 arcsec'
outImgSize = [1250,1250]

## Use noisy visibility for image
noisy = False
