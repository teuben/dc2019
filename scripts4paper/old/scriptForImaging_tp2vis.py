# ALMA Data Reduction Script, D. Petry (ESO), Aug 2020
# Modified for tp2vis, A. Plunkett Aug 2020

########
## SETUP FILES, BY Adele
'''
I'll skip mystep = 0
ln -s ../TestHybrid/gmc_120L.alma.all_int-weighted.ms .
ln -s ../Data/Tclean/sdintimaging_gmc_120L.alma.all-sdgain5.joint.multiterm.mask
ln -s ../Data/SimObs/gmcSkymodel_120L/gmc_120L/gmc_120L.sd.image .
'''
########

# Imaging

thesteps = [3]
step_title = {0: 'Concat the (interferometry) MSs',
              1: 'Generate pseudo-visibilities with tp2vis',
              2: 'Agg. bandwidth image config 6.4, 6.1, and ACA, and TP visibilities',
              3: 'Export images to FITS format'}

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

  thevis = ['gmc_120L.alma.cycle6.4.2018-10-02.ms',
            'gmc_120L.alma.cycle6.1.2018-10-02.ms',
            'gmc_120L.alma.cycle6.4.2018-10-03.ms',
            'gmc_120L.alma.cycle6.1.2018-10-03.ms',
            'gmc_120L.alma.cycle6.4.2018-10-04.ms',
            'gmc_120L.alma.cycle6.1.2018-10-04.ms',
            'gmc_120L.alma.cycle6.4.2018-10-05.ms',
            'gmc_120L.alma.cycle6.1.2018-10-05.ms',
            'gmc_120L.aca.cycle6.2018-10-20.ms',
            'gmc_120L.aca.cycle6.2018-10-21.ms',
            'gmc_120L.aca.cycle6.2018-10-22.ms',
            'gmc_120L.aca.cycle6.2018-10-23.ms']

  weightscale = [1., 1., 1., 1., 1., 1., 1., 1.,
                 0.193, 0.193, 0.193, 0.193]

  concat(vis=thevis, 
         concatvis='gmc_120L.alma.all_int-weighted.ms',
         visweightscale = weightscale)

mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])
  
  # Generate pointing file: (this didn't work for me with the simulated dataset.
  #listobs('gmc_120L.alma.all_int-weighted.ms',listfile='inter.log')
  #!cat inter.log | grep "none" | awk '{print $4,$5}' | sed 's/\([0-9]*\)\:\([0-9]*\):\([0-9.]*\) /\1h\2m\3 /' | sed 's/\([0-9][0-9]\)\.\([0-9][0-9]\)\.\([0-9][0-9]\)\./\1d\2m\3\./' | awk '{printf("J2000 %ss %ss\n",$1,$2)}' > int.ptg
  
  ## Optional: To get RMS, use blank channels, or a signal-free box.
  #imstat('gmc_120L.sd.image',axes=[0,1],box='260,310,280,330')['rms'][:6].mean() #-->440.86, seems too high.
  #tp2vis('gmc_120L.sd.image','tp.ms','12m.ptg',nvgrp=5,rms=440.86)

  wfactor=0.01
  tp2vis('gmc_120L.sd.image','tp_withwt.ms','12m.ptg',deconv=True,maxuv=10,nvgrp=4)
  tp2viswt('tp_withwt.ms',wfactor,'multiply')


mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = ['gmc_120L.alma.all_int-weighted.ms','tp_withwt.ms']
  
  os.system('rm -rf gmc_120L.tp2vis*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.tp2vis',
         field = '',
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
         mask = 'sdintimaging_gmc_120L.alma.all-sdgain5.joint.multiterm.mask',
         gridder = 'mosaic',
         pbcor = True,
         threshold = '0.021Jy',
         interactive = True
         )
## This is an interactive clean.  Begin with threshold='0.021Jy'.  Cleaned down to ~0.03Jy.
## In interactive GUI, use:
## maxcycleniter (Components per major cycle) = 100 (later ~10000)
## iterations left = 1000000 (a large number)
## first cyclethreshold was ~1.9Jy.
## Lower the cycle threshold about 30-50% each time.
## End when cyclethreshold=threshold.


 
# Export images to FITS format
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  myimages = ['gmc_120L.tp2vis']
  
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
  
