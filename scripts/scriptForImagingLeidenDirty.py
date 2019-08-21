# ALMA Data Reduction Script

# Imaging

thesteps = []
step_title = {0: 'Cube for target NGC_346, spw 22, 7 bins for Leiden',
              1: 'Export images to FITS format'}

try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]
# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.


thevis = ['region3by3-7M-leiden-avg.ms']


# Cube for target NGC_346, spw 22
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf NGC_346_sci.spw22.cube.I.manual-region3by3-7m-7bins-leiden*')
  tclean(vis = thevis,
         imagename = 'NGC_346_sci.spw22.cube.I.manual-region3by3-7m-7bins-leidenDirty',
         field = 'NGC_346', 
         intent = 'OBSERVE_TARGET#ON_SOURCE',
         phasecenter = 3, #00:59:05.089680 -72.10.33.24000 ICRS
         stokes = 'I',
         spw = '0',
         outframe = 'LSRK',
         restfreq = '230.538GHz', # CO 2-1 lab rest freq
         specmode = 'cube',
         imsize = [640, 640], # 3500 arcsec x 2000 arcsec
         cell = '1.4arcsec',
         deconvolver = 'hogbom',
         niter = 100,
         weighting = 'briggs',
         robust = 0.5,
         mask = '',
         gridder = 'mosaic',
         pbcor = True,
         threshold = '0.02Jy',
         width = '3.333MHz',
         start = '230.405GHz', 
         nchan = 7, 
         interactive = True
         )
  
  

  
  

# Export images to FITS format
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  myimages = ['NGC_346_sci.spw16.cube.I.manual',
              'NGC_346_sci.spw16_18_20_22_24.mfs.I.manual',
              'NGC_346_sci.spw18.cube.I.manual',
              'NGC_346_sci.spw20.cube.I.manual',
              'NGC_346_sci.spw22.cube.I.manual',
              'NGC_346_sci.spw24.cube.I.manual']
  
  for myimagebase in myimages:
    exportfits(imagename = myimagebase+'.image.pbcor',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )
    exportfits(imagename = myimagebase+'.pb',
               fitsimage = myimagebase+'.pb.fits',
               overwrite = True
               )
  

