import math
import os
import glob 
import analysisUtils as aU

############
# Simulation parameters 
############

## Read parameter file 
execfile('paramL.py')


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
    os.system('mkdir '+project)
              
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
intTime = str( float(integration.split("s")[0])*float(nVisit12))+'s'
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
print "# 12m Number of visits = ", nVisit12
print "# 12m Array sensitivity [mJy] = ", rms12m*1000
print "# 7m HPBW [arcsec] = ", hpbw[1]
print "# 7m Number of pointing = ", npoint7 # simple guess 
print "# 7m Number of visits = ", nVisit7
print "# TP Number of visits = ", nVisitTP
print "# 12m time per day [h]= ", float(nVisit12)*npoint12*float(integration.split("s")[0])/3600/days
print "#  7m time per day [h]= ", float(nVisit7)*npoint7*float(integration.split("s")[0])/3600/days
print "#  TP time per day [h]= ", float(nVisitTP)*npoint12*float(integration.split("s")[0])/3600/days
print "###########################################"

input_line = raw_input("Check the simulation params [RETURN/n] :")
if input_line: 
    sys.exit()

import datetime
day = datetime.date(2018, 10, 1)
oneDay = datetime.timedelta(days=1)
totaltime12 = str(math.ceil((float(nVisit12)/days)))
totaltime7 = str(math.ceil((float(nVisit7)/days)))
totaltimeTP = str(math.ceil((float(nVisitTP)/days)))


# 12m Observation

time12mPerDay=float(nVisit12)*npoint12*float(integration.split("s")[0])
for iday in range(days): 
    day = day + oneDay
    
    date = str(day).replace('-','/')
    print '### Observation in '+date

    # Prepare config list for each observing date
    cfglist = []
    for cf in config:
        cfgname = project+'/'+cf+'.'+str(day)+'.cfg'
        cfglist.append(cfgname)
        os.system('cp '+configPATH+cf+'.cfg '+cfgname)
        
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
            refdate            = date, #"2012/12/01",
            hourangle          = hourangle, 
            user_pwv           = pwv, 
            totaltime          =  totaltime12,
            graphics           =  "both"
        )
    d = str(day)
    os.system('mkdir %s/%s' %(project,d))
    os.system('mv %s/%s* %s/%s' %(project,project,project, d))
        
for iday in range(days):
    day = day + oneDay   
    date = str(day).replace('-','/')
    print '### Observation in '+date

    # Prepare config list for each observing date
    cfg = "aca.tp"
    cfgname = project+'/'+cfg+'.'+str(day)+'.cfg'
    os.system('cp '+configPATH+cfg+'.cfg '+cfgname)

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
        antennalist        =  cfgname,
        sdant              = 0,
        refdate            = date, #"2012/12/02",
        hourangle          = hourangle,     
        user_pwv           = pwv, 
        totaltime          =  totaltimeTP ,
        graphics           =  "both"
    )

    d = str(day)
    os.system('mkdir %s/%s' %(project,d))
    os.system('mv %s/%s* %s/%s' %(project,project,project, d))

    
for iday in range(days): 
    day = day + oneDay   
    date = str(day).replace('-','/')
    print '### Observation in '+date

    # Prepare config list for each observing date
    cfg = acaconfig 
    cfgname = project+'/'+cfg+'.'+str(day)+'.cfg'
    os.system('cp '+configPATH+cfg+'.cfg '+cfgname)
    
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
        antennalist        =  cfgname,
        refdate            = date, #"2012/12/02" ,
        hourangle          = hourangle,     
        user_pwv           = pwv, 
        totaltime          =  totaltime7,
        graphics           =  "both"
    )

    d = str(day)
    os.system('mkdir %s/%s' %(project,d))
    os.system('mv %s/%s* %s/%s' %(project,project,project, d))

    

############################################

# Make symbolic links of MS and skymodel 
os.chdir(project)
cfgList = glob.glob('*.cfg')
for cfg in cfgList:
    dt = cfg.split('.')[-2]
    if 'tp' in cfg: # product of TP does not have date in name 
        # MS files
        msname = glob.glob(dt+'/*.ms')        
        for vis in msname:
            if 'noisy' in vis:
                visOut = vis.replace('tp.noisy', 'tp.'+dt+'.noisy.sd.ms')
            else:
                visOut = vis.replace('tp.sd.ms', 'tp.'+dt+'.sd.ms')        
            os.system('ln -s %s %s' %(vis, visOut.split('/')[1]))
        # Skymodel 
        skymodel = glob.glob(dt+'/*.skymodel')[0]
        skymodelOut = skymodel.replace('tp.skymodel','tp.'+dt+'.skymodel')
        os.system('ln -s %s %s' %(skymodel, skymodelOut.split('/')[1]))        
    else:
        os.system('ln -s %s/*ms .'% dt)
        os.system('ln -s %s/*skymodel .'% dt)        
os.chdir('../')

############################################ 


print "############################################"
print "# Start simanalyze script : "+anaScript 
print "############################################"

execfile(anaScript)


