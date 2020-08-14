# ALMA Data Reduction Script
# ScriptForImaging.py by Dirk Petry, Aug 2020
# Adapted for Hybrid combination, by Adele Plunkett, Aug 2020

##---------------------------------------------------------
## Additional libraries and imports

import os
from astropy import units as u
import numpy as np

##----------------------------------------------------------
## (0) Set up files

DataDir = '/lustre/cv/users/aplunket/Combo/DC2020/Data/SimObs/gmcSkymodel_120L/gmc_120L/' # --> Directory where the data are located
WorkingDir = '/lustre/cv/users/aplunket/Combo/DC2020/TestHybrid/'# --> Directory where you want to work
Int_vis = DataDir + 'gmc_120L.concat.ms' # --> Interferometer visibility file
TP_image = DataDir + 'gmc_120L.sd.image' # --> Total power image, should be in *.image format
TP_image0 = DataDir + 'gmc_120L.sd.image0' # --> Total power image, should be in *.image format

##----------------------------------------------------------
## (1) Image each array

os.chdir(WorkingDir)

## a,b,c = aU.pickCellSize('gmc_120L.alma.cycle6.1.2018-10-03.ms', spw='0', imsize=True, cellstring=True)

# Imaging interferometry-data only
thesteps = [1]
step_title = {0: 'Concat the MSs',
              1: 'Agg. bandwidth image config 6.4, 6.1, and ACA sim',
              2: 'Setup TP as startmodel',
              3: 'Agg. bandwidth image using TP as startmodel',
              4: 'Feather image from step 3',
              10: 'Export images to FITS format'}
try:
  print('List of steps to be executed ...', mysteps)
  thesteps = mysteps
except:
  print('global variable mysteps not set.')
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print('Executing all steps: ', thesteps)

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]
# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.


# put restfreqs in this dictionary,
# one for each SPW ID, e.g. {17: '350GHz', 19: '356GHz'}
therestfreqs = {0: '115.GHz'}
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = [DataDir+'gmc_120L.alma.cycle6.4.2018-10-02.ms',
            DataDir+'gmc_120L.alma.cycle6.1.2018-10-02.ms',
            DataDir+'gmc_120L.alma.cycle6.4.2018-10-03.ms',
            DataDir+'gmc_120L.alma.cycle6.1.2018-10-03.ms',
            DataDir+'gmc_120L.alma.cycle6.4.2018-10-04.ms',
            DataDir+'gmc_120L.alma.cycle6.1.2018-10-04.ms',
            DataDir+'gmc_120L.alma.cycle6.4.2018-10-05.ms',
            DataDir+'gmc_120L.alma.cycle6.1.2018-10-05.ms',
            DataDir+'gmc_120L.aca.cycle6.2018-10-20.ms',
            DataDir+'gmc_120L.aca.cycle6.2018-10-21.ms',
            DataDir+'gmc_120L.aca.cycle6.2018-10-22.ms',
            DataDir+'gmc_120L.aca.cycle6.2018-10-23.ms']

  weightscale = [1., 1., 1., 1., 1., 1., 1., 1.,
                 0.193, 0.193, 0.193, 0.193]

  concat(vis=thevis, 
         concatvis='gmc_120L.alma.all_int-weighted.ms',
         visweightscale = weightscale)


mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = 'gmc_120L.alma.all_int-weighted.ms'
  
  os.system('rm -rf gmc_120L.alma.all_int-mfs.I.manual-weighted*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.alma.all_int-mfs.I.manual-weighted',
         field = '0~68',
         intent = 'OBSERVE_TARGET#ON_SOURCE',
         phasecenter = 'J2000 12:00:00 -35.00.00.0000',
         stokes = 'I',
         spw = '0',
         outframe = 'LSRK',
         specmode = 'mfs',
         nterms = 1,
         imsize = [1120, 1120],
         cell = '0.21arcsec',
         deconvolver = 'hogbom',
         niter = 100,
         weighting = 'briggs',
         robust = 0.5,
         mask = '',
         gridder = 'mosaic',
         pbcor = True,
         threshold = '0.021Jy',
         interactive = True
         )

## This is an interactive clean.  Begin with threshold='0.021Jy'.
## In interactive GUI, use: 
## maxcycleniter (Components per major cycle) = 100 (later ~10000)
## iterations left = 1000000 (a large number)
## first cyclethreshold was 0.57Jy.
## Lower the cycle threshold about 30-50% each time.
## End when cyclethreshol=threshold.
  
##----------------------------------------------------------
## (2) Hybrid imaging

# Setup total power model
mystep = 2

# For real data, you may need to regrid the single dish here
if(mystep in thesteps):
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    if imhead(TP_image)['unit']=='Jy/beam': print('SD units {}. OK, will convert to Jy/pixel.'.format(imhead(TP_image)['unit']))
    elif imhead(TP_image)['unit']=='Jy/pixel': print('SD units {}. SKIP conversion. '.format(imhead(TP_image)['unit']))
    else: print('SD units {}. NOT OK, needs conversion. '.format(imhead(TP_image)['unit']))

    SingleDishResolutionArcsec = imhead(TP_image)['restoringbeam']['major']['value'] #in Arcsec
    CellSizeArcsec = np.abs(imhead(TP_image)['incr'][0])*u.rad.to(u.arcsec) #in Arcsec
    toJyPerPix = CellSizeArcsec**2/(1.1331*SingleDishResolutionArcsec**2)
    #toJyPerPix = 1./(1.1331*SingleDishResolutionArcsec**2)
    SDEfficiency = 1.0 #--> Scaling factor
    fluxExpression = "(IM0 * {0:f} / {1:f})".format(toJyPerPix,SDEfficiency)
    scaled_name = TP_image.split('/')[-1]+'.Jyperpix'

    os.system('rm -rf '+scaled_name)
    immath(imagename=TP_image,
           outfile=scaled_name,
           mode='evalexpr',
           expr=fluxExpression)
    hdval = 'Jy/pixel'
    dummy = imhead(imagename=scaled_name,
                   mode='put',
                   hdkey='BUNIT',
                   hdvalue=hdval)


# Image with TP as startmodel
mystep = 3
if (mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = [Int_vis] # --> Interferometer visibility file
 
  os.system('rm -rf gmc_120L.hybrid*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.hybrid',
         startmodel = scaled_name,
         field = '0~68',
         intent = 'OBSERVE_TARGET#ON_SOURCE',
         phasecenter = 'J2000 12:00:00 -35.00.00.0000',
         stokes = 'I',
         spw = '0',
         outframe = 'LSRK',
         specmode = 'mfs',
         nterms = 1,
         imsize = [1120, 1120],
         cell = '0.21arcsec',
         deconvolver = 'hogbom',
         niter = 100,
         weighting = 'briggs',
         robust = 0.5,
         mask = '',
         gridder = 'mosaic',
         pbcor = True,
         threshold = '1mJy',
         interactive = True
         )   

# Feather 
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

#################
#################

## Enter Feather steps here


#################
#################
  

# Export images to FITS format
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  myimages = ['gmc_120L.alma.all_int-mfs.I.manual-weighted',
                       'gmc_120L.hybrid' ]
  
  for myimagebase in myimages:
    exportfits(imagename = myimagebase+'.image.pbcor',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )
    exportfits(imagename = myimagebase+'.pb',
               fitsimage = myimagebase+'.pb.fits',
               overwrite = True
               )
  

