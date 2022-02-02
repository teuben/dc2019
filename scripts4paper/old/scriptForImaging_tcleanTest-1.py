# ALMA Data Reduction Script, D. Petry (ESO), Aug 2020
# modified by Adele Plunkett (NRAO) , Aug 2020
# Goal: to test different TCLEAN methods

########
## SETUP FILES, BY Adele

DataDir = '/lustre/cv/users/aplunket/Combo/DC2020/Data/SimObs/gmcSkymodel_120L/gmc_120L/' # --> Directory where the data are located, used only in mystep=0

########

# Imaging

thesteps = [10]
step_title = {0: 'Concat the MSs',
              1: 'Make dirty image',
              2: 'Non-interactive simple TCLEAN',
              3: 'Interactive TCLEAN',
              4: 'Auto-masking TCLEAN',
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

######################
## Dirty image
######################

mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = 'gmc_120L.alma.all_int-weighted.ms'

  os.system('rm -rf gmc_120L.inter.dirt*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.inter.dirt',
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
         niter = 0,
         weighting = 'briggs',
         robust = 0.5,
         mask = 'pb',pbmask=0.2,
         gridder = 'mosaic',
         pbcor = True,
         interactive = False
         )

######################
## Simple 
######################

mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = 'gmc_120L.alma.all_int-weighted.ms'
  peakflux = '3.8Jy'
  threshold = '0.011Jy' ## peak / 1000*3
  os.system('rm -rf gmc_120L.inter.simple*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.inter.simple',
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
         niter = 1000000,
         cycleniter = 100000,
         cyclefactor=2.0,
         weighting = 'briggs',
         robust = 0.5,
         usemask = 'pb',pbmask=0.3,
         gridder = 'mosaic',
         pbcor = True,
         threshold = threshold,
         interactive = False
         )



######################
## Interactive
######################
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = 'gmc_120L.alma.all_int-weighted.ms'
  
  os.system('rm -rf gmc_120L.inter.interactive*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.inter.interactive',
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
         #mask = 'sdintimaging_gmc_120L.alma.all-sdgain5.joint.multiterm.mask',
         usemask = 'pb',pbmask=0.3,
         gridder = 'mosaic',
         pbcor = True,
         threshold = '0.011Jy',
         interactive = True
         )
## This is an interactive clean.  Begin with threshold='0.011Jy'.
## In interactive GUI, use:
## maxcycleniter (Components per major cycle) = 100 (later ~10000)
## iterations left = 1000000 (a large number)
## first cyclethreshold was ~1.9Jy.
## used cyclethreshold: 1.9Jy, 1.0Jy, 0.6Jy, 0.4Jy, 0.2Jy, 0.1Jy, 0.06Jy, 0.04Jy, 0.02 Jy, 0.011Jy
## Lower the cycle threshold about 30-50% each time.
## End when cyclethreshold=threshold


######################
## Auto-masking
######################
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = 'gmc_120L.alma.all_int-weighted.ms'
  threshold = '0.011Jy' ## peak / 1000*3
  #threshold = '0.038Jy' ## peak / 1000
  
  os.system('rm -rf gmc_120L.inter.auto*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.inter.auto',
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
         niter = 1000000,
         cycleniter = 100000,
         cyclefactor=2.0,
         weighting = 'briggs',
         robust = 0.5,
         gridder = 'mosaic',
         pbcor = True,
         threshold = threshold,
         interactive = True,
         # Automasking Parameters below this line
         usemask='auto-multithresh',
         sidelobethreshold=2.0,
         noisethreshold=4.25,
         lownoisethreshold=1.5, 
         minbeamfrac=0.3,
         growiterations=75,
         negativethreshold=0.0,
         verbose=True)
######################
## Export to fits
######################

mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  ## This still requires user intervention to hardcode the filenames
  os.chdir('inter_interact_thresh38mJy')
  ## inter_interact_thresh11mJy/ inter_interact_thresh38mJy/
  myimages = ['gmc_120L.inter.interactive'] 
  ## inter_auto_thresh11mJy/ inter_auto_thresh38mJy/
  #myimages = ['gmc_120L.inter.auto']
  ## inter_simple_thresh11mJy/ inter_simple_thresh38mJy/
  #myimages = ['gmc_120L.inter.simple']
  
  for myimagebase in myimages:
    exportfits(imagename = myimagebase+'.image.pbcor',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )

    exportfits(imagename = myimagebase+'.image',
               fitsimage = myimagebase+'.image.fits',
               overwrite = True
               )
 
    exportfits(imagename = myimagebase+'.pb',
               fitsimage = myimagebase+'.pb.fits',
               overwrite = True
               )
  
 

