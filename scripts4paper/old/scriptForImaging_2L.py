# ALMA Data Reduction Script

## a,b,c = aU.pickCellSize('gmc_120L.alma.cycle6.1.2018-10-03.ms', spw='0', imsize=True, cellstring=True)

# Imaging

thesteps = []
step_title = {0: 'Agg. bandwidth image config 6.1 sim',
              1: 'Agg. bandwidth image config 6.4 sim',
              2: 'Agg. bandwidth image ACA sim',
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

# Images
im1 = 'gmc_2L.alma.cycle6.1-mfs.I.manual'   # 12m 
im2 = 'gmc_2L.alma.cycle6.4-mfs.I.manual'   # 12m
im3 = 'gmc_2L.aca.cycle6-mfs.I.manual'      #  7m


# put restfreqs in this dictionary,
# one for each SPW ID, e.g. {17: '350GHz', 19: '356GHz'}
therestfreqs = {0: '115.GHz'}

mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = ['gmc_2L.alma.cycle6.1.2018-10-02.ms',
            'gmc_2L.alma.cycle6.1.2018-10-03.ms']
  
  os.system('rm -rf %s*' % im1)
  tclean(vis = thevis,
         imagename = im1,
         field = '0~51',
         intent = 'OBSERVE_TARGET#ON_SOURCE',
         phasecenter = 'J2000 12:00:00 -35.00.00.0000',
         stokes = 'I',
         spw = '0',
         outframe = 'LSRK',
         specmode = 'mfs',
         nterms = 1,
         imsize = [288, 288],
         cell = '0.81arcsec',
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
  
  
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = ['gmc_2L.alma.cycle6.4.2018-10-02.ms',
            'gmc_2L.alma.cycle6.4.2018-10-03.ms']
  
  os.system('rm -rf %s*' % im2)
  tclean(vis = thevis,
         imagename = im2,
         field = '0~51',
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
  
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = ['gmc_2L.aca.cycle6.2018-10-06.ms',
            'gmc_2L.aca.cycle6.2018-10-07.ms']
  
  os.system('rm -rf %s*' % im3)
  tclean(vis = thevis,
         imagename = im3,
         field = '0~16',
         intent = 'OBSERVE_TARGET#ON_SOURCE',
         phasecenter = 'J2000 12:00:00 -35.00.00.0000',
         stokes = 'I',
         spw = '0',
         outframe = 'LSRK',
         specmode = 'mfs',
         nterms = 1,
         imsize = [108, 108],
         cell = '2.7arcsec',
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
  

  

# Export images to FITS format
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  myimages = [im1, im2, im3]
  
  for myimagebase in myimages:
    exportfits(imagename = myimagebase+'.image.pbcor',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )
    exportfits(imagename = myimagebase+'.pb',
               fitsimage = myimagebase+'.pb.fits',
               overwrite = True
               )
  

