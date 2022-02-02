# ALMA Data Reduction Script, D. Petry (ESO), Aug 2020
# modified to include feathering step, M. Hoffman Aug 2020

# Imaging

thesteps = []
step_title = {0: 'Concat the MSs',
              1: 'Agg. bandwidth image config 6.4, 6.1, and ACA sim',
              2: 'Feathering combined agg. bandwidth image with TP image',
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

  thevis = ['gmc_2L.alma.cycle6.1.2018-10-02.ms',
            'gmc_2L.alma.cycle6.1.2018-10-03.ms',
            'gmc_2L.alma.cycle6.4.2018-10-02.ms',
            'gmc_2L.alma.cycle6.4.2018-10-03.ms',
            'gmc_2L.aca.cycle6.2018-10-06.ms',
            'gmc_2L.aca.cycle6.2018-10-07.ms']
  weightscale = [1., 1., 1., 1., 
                 0.193, 0.193]    

  concat(vis=thevis, 
         concatvis='gmc_2L.alma.all_int-weighted.ms',
         visweightscale = weightscale)

mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = 'gmc_2L.alma.all_int-weighted.ms'
  
  os.system('rm -rf gmc_2L.alma.all_int-mfs.I.manual-weighted*')
  tclean(vis = thevis,
         imagename = 'gmc_2L.alma.all_int-mfs.I.manual-weighted',
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
         mask = 'sdintimaging_gmc_2L.alma.all-sdgain5.joint.multiterm.mask',
         gridder = 'mosaic',
         pbcor = True,
         threshold = '0.021Jy',
         interactive = True
         )
## This is an interactive clean.  Begin with threshold=‘0.021Jy’.
## In interactive GUI, use:
## maxcycleniter (Components per major cycle) = 100 (later ~10000)
## iterations left = 1000000 (a large number)
## first cyclethreshold was ~1.9Jy.
## Lower the cycle threshold about 30-50% each time.
## End when cyclethreshold=threshold.
  
# Feather 
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  # Clean this section later
  #####################################
  #             USER INPUTS           #
  #####################################
  # Only user inputs required are the 
  # high res, low res, and pb name 

  highres='gmc_2L.alma.all_int-mfs.I.manual-weighted.image'
  lowres='gmc_2L.sd.image'
  #lowres='gmc_reorder.image'
  pb='gmc_2L.alma.all_int-mfs.I.manual-weighted.pb'

  #####################################
  #            PROCESS DATA           #
  #####################################
  # Reorder the axes of the low to match high/pb 

  myfiles=[highres,lowres]
  mykeys=['cdelt1','cdelt2','cdelt3','cdelt4']

  os.system('rm -rf lowres.* ')
  

  im_axes={}
  print('Making dictionary of axes information for high and lowres images')
  for f in myfiles:
       print(f)
       print('------------')
       axes = {}
       i=0
       for key in mykeys:
           q = imhead(f,mode='get',hdkey=key)
           axes[i]=q
           i=i+1
           print(str(key)+' : '+str(q))
       im_axes[f]=axes
       print(' ')

# Check if axes order is the same, if not run imtrans to fix, could be improved

  order=[]           

  for i in range(4):
       hi_ax = im_axes[highres][i]['unit']
       lo_ax = im_axes[lowres][i]['unit']
       if hi_ax == lo_ax:
           order.append(str(i))
       else:
           lo_m1 = im_axes[lowres][i-1]['unit']
           if hi_ax == lo_m1:
               order.append(str(i-1))
           else:
               lo_p1 = im_axes[lowres][i+1]['unit']
               if hi_ax == lo_p1:
                   order.append(str(i+1))
  order = ''.join(order)
  print('order is '+order)

  if order=='0123':
       print('No reordering necessary')
  else:
      imtrans(imagename=lowres,outfile='lowres.ro',order=order)
      lowres='lowres.ro'
      print('Had to reorder!')

  # Regrid low res Image to match high res image

  print('Regridding lowres image...')
  imregrid(imagename=lowres,
           template=highres,
           axes=[0,1,2,3],
           output='lowres.regrid')

  # Multiply the lowres image with the highres primary beam response

  print('Multiplying lowres by the highres pb...')
  immath(imagename=['lowres.regrid',
                    pb],
         expr='IM0*IM1',
         outfile='lowres.multiplied')


  # Feather together the low*pb and hi images

  print('Feathering...')
  feather(imagename='gmc_2L.Feather.image',
          highres=highres,
          lowres='lowres.multiplied')

  os.system('rm -rf gmc_2L.Feather.image.pbcor')
  immath(imagename=['gmc_2L.Feather.image',
                  'gmc_2L.alma.all_int-mfs.I.manual-weighted.pb'],
       expr='IM0/IM1',
       outfile='gmc_2L.Feather.image.pbcor')

  

# Export images to FITS format
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  myimages = ['gmc_2L.alma.all_int-mfs.I.manual-weighted']
  
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
  
  myimages = ['gmc_2L.sd']
  
  for myimagebase in myimages:
    exportfits(imagename = myimagebase+'.image',
               fitsimage = myimagebase+'.fits',
               overwrite = True
               )

  myimages = ['gmc_2L.Feather']
  
  for myimagebase in myimages:
     exportfits(imagename = myimagebase+'.image.pbcor',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )

     exportfits(imagename = myimagebase+'.image',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )
 

