import os
import glob 
import analysisUtils as aU

############
# Simulation parameters 
############

## Read parameter file 
execfile('param.py')


############

print "###################################################"
print "###  Project directory: "+project
print "###################################################"

isThere = glob.glob(project)
if isThere:
    print " "
    print "###  Deleting existing project directory: "+project
    print " "
    os.system('rm -rf %s' %project)

print "# Saving parameter files to %s.param.py" %project
os.system('rm -rf %s.param.py'%project)
os.system('cp param.py %s.param.py'%project)

print "# Using image file "+fitsFile 
skymodel = fitsFile 

## Use following command to get FITS file of M51. 
isThere = glob.glob('M51ha.fits')
if not isThere and fitsFile == 'M51ha.fits': 
    os.system('curl https://casaguides.nrao.edu/images/3/3f/M51ha.fits.txt -f -o M51ha.fits')

hd = imhead(imagename= fitsFile)
pixSize = abs(hd['incr'][0]*180/3.141592*3600) # arcsec 

"""
# RMS estimate with simple sigma clipping
imsize = hd['shape']
box = '0,0,%s,%s'%(str(imsize[0]-1),str(imsize[1]-1))
imgData = imval( fitsFile, box=box)['data']
niter = 5
data = imgData
rms = 0
data[np.isnan(data)] = -1
med = np.max(data)
for i in range(niter):
    nonzero = data > 1e-33
    noise = data < (med+3*rms)
    med = np.median( data[nonzero*noise] )
    rms = np.std( data[nonzero*noise])

snr = np.max(imgData)/rms 
"""

print " "
print "### Original FITS specification : ", fitsFile 
print "# pixel scale [arcsec] = ", pixSize
print "# image shape = ", hd['shape']
print "# image size [arcsec] = ", pixSize*hd['shape'][0]
#print "# SNR of image max = ", snr 
print "###########################################"

input_line = raw_input("Check the image spec [RETURN/n] :")
if input_line: 
    sys.exit()



# [12m 7m] primary beam size 
diam = np.array([12., 7.])
wave = 2.99792e8/ (float(incenter.split("GHz")[0])*1.e9)
hpbw = 1.02 * wave / diam *180/3.141592 *3600 # arcsec


# number of pointing with 0.5PB spacing
npoint12 = int((float(mapsize.split("arcsec")[0]) / hpbw[0] *2))**2
npoint7 = int((float(mapsize.split("arcsec")[0]) / hpbw[1] *2))**2
"""
if not totaltime12:
    totaltime12 = str(npoint12 * float(integration.split("s")[0]))+'s'
if not totaltime7:
    totaltime7 = str(npoint7 * float(integration.split("s")[0])*timeRatio[1])+'s'
if not totaltimeTP: 
    totaltimeTP = str(npoint12 * float(integration.split("s")[0])*timeRatio[2])+'s'
"""

## Sensitivity setting 
#

beam = []
mrs = [] # Maximum Recoverable Scale 
for i in range(len(config)):
    beam.append(aU.estimateSynthesizedBeamForConfig(config[i], incenter))
    mrs.append(aU.estimateMRSForConfig(config[i], incenter))


# Number of pixel per beam (estimated)
pixScale  = (float(incell.split("arcsec")[0])) # arcsec 
beamSize = beam[0]
npix_per_beam = (beamSize/pixScale)**2



print " "
print "# Sensitivity calculation .... "
print " "
intTime = str( float(integration.split("s")[0])*float(totaltime12))+'s'
rms12m = aU.sensitivity(incenter, inwidth, intTime, pwv=pwv, antennalist = config[0])



print " "
print "### Sky Model specification : "
print "# Project name = ", project
print "# pixel scale [arcsec] = ", incell 
print "# Peak intensity [Jy/pix] = ", inbright
print "# Estimated peak [Jy/beam] = ", float(inbright)*npix_per_beam
print "# image shape = ", hd['shape']
print "# image size [arcsec] = ", hd['shape'][0]*float(incell.split("arcsec")[0])
print " "
print "### Mapping specification (estimated): "
print "# ALAM configuration = ", config
print "# Estimated beamsize = ", beam
print "# Maximum recoverable scale = ", mrs
print "# ACA configuration = ", acaconfig
print "# Map size (INT) = ", mapsize
print "# Map size (TP) = ", mapsizeTP
print "# Integration time = ", integration 
print "# 12m HPBW [arcsec] = ", hpbw[0]
print "# 12m Number of pointing = ", npoint12 # simple guess 
print "# 12m Total time = ", totaltime12
print "# 12m Array sensitivity [mJy] = ", rms12m*1000
print "# 7m HPBW [arcsec] = ", hpbw[1]
print "# 7m Number of pointing = ", npoint7 # simple guess 
print "# 7m Total time = ", totaltime7
print "# TP Total time = ", totaltimeTP
print "###########################################"

input_line = raw_input("Check the simulation params [RETURN/n] :")
if input_line: 
    sys.exit()



# 12m Observation 
cfglist = [item + ".cfg" for item in config] 
for cfg in cfglist: 
  simobserve(
    project = project,
    skymodel =  skymodel,
    indirection = indirection, 
    incell = incell, 
    inbright = inbright, 
    incenter = incenter,    
    inwidth = inwidth, 
    setpointings       =  True,
    integration        =  integration,
    mapsize            =  mapsize,
    maptype            =  "ALMA-OT",
    pointingspacing    =  "0.5PB",    
    obsmode            =  "int",
    antennalist        =  cfg, 
    refdate            = "2012/12/01",
    hourangle          = hourangle, 
    user_pwv           = pwv, 
    totaltime          =  totaltime12,
    graphics           =  "both"
  )


# TP Observation 
simobserve(
    project = project,
    skymodel =  skymodel,
    indirection = indirection, 
    incell = incell, 
    inbright = inbright, 
    incenter = incenter,    
    inwidth = inwidth, 
    integration        =  integration,
    mapsize            =  mapsizeTP,
    maptype            =  "square",
    obsmode            =  "sd",
    antennalist        =  "aca.tp.cfg",
    sdant              = 0,
    refdate            = "2012/12/02",
    hourangle          = hourangle,     
    user_pwv           = pwv, 
    totaltime          =  totaltimeTP ,
    graphics           =  "both"
)


# 7m Observation 
simobserve(
    project = project,
    skymodel =  skymodel,
    indirection = indirection, 
    incell = incell, 
    inbright = inbright, 
    incenter = incenter,    
    inwidth = inwidth, 
    setpointings       =  True,
    integration        =  integration,
    mapsize            =  mapsize,
    maptype            =  "ALMA-OT",
    pointingspacing    =  "0.5PB",    
    obsmode            =  "int",
    antennalist        =  acaconfig+'.cfg',
    refdate            = "2012/12/02" ,
    hourangle          = hourangle,     
    user_pwv           = pwv, 
    totaltime          =  totaltime7,
    graphics           =  "both"
)


############################################ 


print "############################################"
print "# Start simanalyze script : "+anaScript 
print "############################################"

execfile(anaScript)


