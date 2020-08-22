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
TP_mask = '/lustre/cv/users/aplunket/Combo/DC2020/Data/Tclean/sdintimaging_gmc_120L.alma.all-sdgain5.joint.multiterm.mask' # --> Mask you can use for TCLEAN

##----------------------------------------------------------
## (1) Image each array

os.chdir(WorkingDir)

## a,b,c = aU.pickCellSize('gmc_120L.alma.cycle6.1.2018-10-03.ms', spw='0', imsize=True, cellstring=True)

# Imaging interferometry-data only
thesteps = [10]
step_title = {0: 'Concat the MSs',
              1: 'Agg. bandwidth image config 6.4, 6.1, and ACA sim',
              1.1: 'Restart: Agg. bandwidth image config 6.4, 6.1, and ACA sim (Step 1)',
              2: 'Setup TP as startmodel',
              3: 'Agg. bandwidth image using TP as startmodel',
              3.1: 'Restart: Agg. bandwidth image (Step 3)',
              4: 'Additional steps from Kauffman',
              5: 'Feather image from step 3',
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
## maxcycleniter (Components per major cycle) = 10000 (later ~200000)
## iterations left = 1000000 (a large number)
## Max value in dirty image is ~3.8 Jy.
## First cyclethreshold was 0.57Jy in GUI.  Set this to 1.9Jy, ofr50% of peakres.
## Lower the cycle threshold about 30-50% each time.
## Used: 1.9Jy; 1.3Jy; 1.0Jy; 0.5Jy; 0.3Jy; 0.2 Jy; 0.12Jy; 0.08Jy; 0.04Jy; 0.03Jy; 0.02Jy 
## Adjust threshold to be 11mJy, which is <peak of dirty image>/1000.*3 (assuming dyn. range of 1000)
## End when cyclethreshol=threshold.
 
mystep = 1.1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = 'gmc_120L.alma.all_int-weighted.ms'
  
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
         mask = TP_mask,
         gridder = 'mosaic',
         pbcor = True,
         threshold = '0.021Jy',
         interactive = True
         )   

## Emulate  interactive clean above.  Begin with threshold='0.021Jy'.
## In interactive GUI, use: 
## maxcycleniter (Components per major cycle) = 10000 (later ~200000)
## iterations left = 1000000 (a large number)
## Max value in dirty image is ~3.8 Jy.
## First cyclethreshold was 0.57Jy in GUI.  Set this to 1.9Jy, or 50% of peakres.
## Lower the cycle threshold about 30-50% each time.
## Used: 1.9Jy; 1.3Jy; 1.0Jy; 0.5Jy; 0.3Jy; 0.2 Jy; 0.12Jy; 0.08Jy; 0.04Jy; 0.03Jy; 0.021Jy
## Going deeper: 0.011Jy, 0.008Jy ,0.005Jy. Model flux no longer increasing for cyclethreshold<0.04Jy.
## Adjust threshold to be 11mJy, which is <peak of dirty image>/1000.*3 (assuming dyn. range of 1000)
## End when cyclethreshol=threshold.

# Continue Imaging as needed
mystep = 3.1
if (mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  thevis = [Int_vis] # --> Interferometer visibility file
 
  #os.system('rm -rf gmc_120L.hybrid*')
  tclean(vis = thevis,
         imagename = 'gmc_120L.hybrid',
         #startmodel = scaled_name,
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
         #mask = TP_mask,
         gridder = 'mosaic',
         pbcor = True,
         threshold = '0.008Jy',
         interactive = True
         )   

# Additional steps from Kauffman method
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

'''
# get the positive interferometer-only clean components
os.system('rm -rf deconvolved-sdinput.intmodel')
immath(outfile='deconvolved-sdinput.intmodel',
   imagename=['deconvolved-sdinput.model',
              'apex_trans_regrid_scaled_unmasked_noneg.image'],
   mode='evalexpr',
   expr='iif((IM0-IM1) >= 0.00, IM0-IM1, 0.0)')


# remove those components if they are at the map edge
os.system('rm -rf deconvolved-sdinput-masked.intmodel')
immath(outfile='deconvolved-sdinput-masked.intmodel',
   imagename=['deconvolved-sdinput.intmodel',
              'deconvolved-sdinput.flux.pbcoverage'],
   mode='evalexpr',
   expr='iif((IM1) >= 0.25, IM0, 0.0)')

imhead('deconvolved-sdinput-masked.intmodel',
       mode='put',
       hdkey='bunit', hdvalue='Jy/pixel')


# smooth the interferometer-only components to the synthesized beam
SynthBeamMaj = imhead('deconvolved-sdinput.image', mode='get', hdkey='bmaj')['value']
SynthBeamMin = imhead('deconvolved-sdinput.image', mode='get', hdkey='bmin')['value']
SynthBeamPA = imhead('deconvolved-sdinput.image', mode='get', hdkey='bpa')['value']

os.system('rm -rf deconvolved-sdinput.intimage')
imsmooth(imagename='deconvolved-sdinput-masked.intmodel',
         outfile='deconvolved-sdinput.intimage',
         kernel='gauss',
         major=str(SynthBeamMaj)+'arcsec',
         minor=str(SynthBeamMin)+'arcsec',
         pa=str(SynthBeamPA)+'deg')


# produce a non-negative single-dish map in Jy/beam
os.system('rm -rf apex_trans_regrid_scaled_unmasked_noneg_perbeam.image')
immath(outfile='apex_trans_regrid_scaled_unmasked_noneg_perbeam.image',
   imagename=['apex_trans_regrid_scaled_unmasked_noneg.image'],
   mode='evalexpr', expr='IM0/'+str(FactorJyperPixel))

imhead('apex_trans_regrid_scaled_unmasked_noneg_perbeam.image',
       mode='put',
       hdkey='bunit', hdvalue='Jy/beam')
imhead('apex_trans_regrid_scaled_unmasked_noneg_perbeam.image',
       mode='put',
       hdkey='bmaj', hdvalue=str(SingleDishResolutionArcsec)+'arcsec')
imhead('apex_trans_regrid_scaled_unmasked_noneg_perbeam.image',
       mode='put',
       hdkey='bmin', hdvalue=str(SingleDishResolutionArcsec)+'arcsec')
imhead('apex_trans_regrid_scaled_unmasked_noneg_perbeam.image',
       mode='put',
       hdkey='bpa', hdvalue='0deg')
'''
# Feather 
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  #####################################
  #             USER INPUTS           #
  #####################################
  # Only user inputs required are the 
  # high res, low res, and pb name 

  highres = 'gmc_120L.hybrid.image'
  lowres = TP_image
  pb='gmc_120L.hybrid.pb'

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

  if order=='0,1,2,3':
       print('No reordering necessary')
  else:
      imtrans(imagename=lowres,outfile='lowres.ro',order=order)
      lowres='lowres.ro'
      print('Had to reorder!')

  # Regrid low res Image to match high res image

  print('Regridding lowres image...')
  imregrid(imagename=lowres,
           template=highres,
           axes=[0,1,2],
           output='lowres.regrid')

  # Multiply the lowres image with the highres primary beam response

  print('Multiplying lowres by the highres pb...')
  immath(imagename=['lowres.regrid',
                    pb],
         expr='IM0*IM1',
         outfile='lowres.multiplied')


  # Feather together the low*pb and hi images

  print('Feathering...')
  feather(imagename='gmc_120L.hybrid.Feather.image',
          highres=highres,
          lowres='lowres.multiplied')

  os.system('rm -rf gmc_120L.hybrid.Feather.image.pbcor')
  immath(imagename=['gmc_120L.hybrid.Feather.image',
                  'gmc_120L.alma.all_int-mfs.I.manual-weighted.pb'],
       expr='IM0/IM1',
       outfile='gmc_120L.hybrid.Feather.image.pbcor')



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
    exportfits(imagename = myimagebase+'.image',
               fitsimage = myimagebase+'.fits',
               overwrite = True
               )
    exportfits(imagename = myimagebase+'.pb',
               fitsimage = myimagebase+'.pb.fits',
               overwrite = True
               )
  
  myimages = [TP_image]

  for myimagebase in myimages:
    exportfits(imagename = myimagebase,
               fitsimage = myimagebase.split('/')[-1]+'.fits',
               overwrite = True
               )

  myimages = ['gmc_120L.hybrid.Feather']
  
  for myimagebase in myimages:
     exportfits(imagename = myimagebase+'.image.pbcor',
               fitsimage = myimagebase+'.pbcor.fits',
               overwrite = True
               )

     exportfits(imagename = myimagebase+'.image',
               fitsimage = myimagebase+'.fits',
               overwrite = True
               )
 
  myimages = [scaled_name]
  
  for myimagebase in myimages:
     exportfits(imagename = myimagebase,
               fitsimage = myimagebase+'.fits',
               overwrite = True
               )

