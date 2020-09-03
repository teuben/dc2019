# ALMA Data Reduction Script, D. Petry (ESO), Aug 2020

# Imaging

thesteps = []
step_title = {0: 'Concat the MSs',
              1: 'Agg. bandwidth image config 6.4, 6.1, and ACA sim',
              2: 'Export images to FITS format'}

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
         usemask='pb',
         pbmask=0.3
         )
  
  

  

# Export images to FITS format
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  myimages = ['gmc_120L.alma.all_int-mfs.I.manual-weighted']
  
  for myimagebase in myimages:
    exportfits(imagename = myimagebase+'.image.pbcor',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )
    exportfits(imagename = myimagebase+'.pb',
               fitsimage = myimagebase+'.pb.fits',
               overwrite = True
               )
  

