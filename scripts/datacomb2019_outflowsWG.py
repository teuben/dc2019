################################
## LUPUS 3 Outflow Working Group
## Developed at Data Combination 2019 workshop at Lorentz Center, August, 2019
## Report can be found here: https://github.com/teuben/dc2019/tree/master/report 
## Script started by Adele Plunkett, 14 August 2019
## Updated 17 August 2019; 20 November 2019; January 2020
################################

## Some important details:
## ************
## SCRIPT:
## These are commands to be run in CASA. It has been tested with: CASA 5.6.0-60   -- Common Astronomy Software Applications
## This script is intended to be run line-by-line (i.e. copy-paste), 
## it has not been tested from start to finish in script mode (i.e. execfile('datacomb2019_outflowsWG.py')).
## ************
## DATA: 
## The data are from ALMA#2015.1.00306.S (PI: Plunkett).  Contact aplunket@nrao.edu for more details.
## The dataset can be obtained following: https://github.com/teuben/dc2019/blob/master/data/README_DC2019_data


'''
NOTE: The original interferometry data were cut down to 10 channels of 1 km/s each by the following commands:
line = {“restfreq”   : ‘115.27120GHz’,
 ‘start’      : ‘-1.0km/s’,
 ‘width’      : ‘1.0km/s’,
 ‘nchan’      : 10,}
mstransform(sharedir+vis7m,‘mst_07_nchan10_start0kms.ms’,
 datacolumn=‘DATA’,outframe=‘LSRK’,mode=‘velocity’,regridms=True,keepflags=False,
 **line)
mstransform(sharedir+vis12m,‘mst_12_nchan10_start0kms.ms’,
 datacolumn=‘DATA’,outframe=‘LSRK’,mode=‘velocity’,regridms=True,keepflags=False,
 **line)
'''

#################################
# (0) Setup the data
#################################

datadir = '/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Lup3mms_Share/' #the directory where your test data are held
workingdir ='/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Post-workshop2/' #the directory where you want to work
vis7m = datadir+'mst_07_nchan10_start0kms.ms' #7m-array interferometry (uv) data
vis12m = datadir+'mst_12_nchan10_start0kms.ms' #12m-array interferometry (uv) data
TPfits = datadir+'TP_12CO.fits'  #Single dish/ Total power image in fits format (as delivered by ALMA)
TPim = 'TP.image' #Total power image, in CASA image format (you will need to convert from the Fits format, see following line)
#importfits(fitsimage=TPfits,imagename=TPim)  ## You just need to do this the first time, in order to get your TP Fits file into the CASA format (*.image)
vis12m7m = 'int12m7m.ms' #The name you will give to the concatenated 12m+7m uv data (or the name of the previously-concatenated 12m+7m data)


##############
## (1) FEATHER 
## Generally, follow the CasaGuide https://casaguides.nrao.edu/index.php/M100_Band3_Combine_5.4
##############

# We will create a Diagnostics directory, because many of these plots/files will actually be useful for other methods.
os.system('mkdir -p Diagnostics')
os.chdir('Diagnostics')

# In CASA, look at mosaic map pointings
os.system('rm -rf *m_mosaic.png')
iminfo12m = au.plotmosaic(vis12m,sourceid='0',figfile='12m_mosaic.png')
iminfo7m = au.plotmosaic(vis7m,sourceid='0',figfile='7m_mosaic.png')
## I also save the output in the variables iminfo, because they hold the size of the image we will want to create, in arcsec. 
imsize_x = iminfo7m[1]-iminfo7m[2]
imsize_y = iminfo7m[3]-iminfo7m[4]
print('#***** Image size should be approximately: {0:.0f} x {1:.0f} arcsec'.format(imsize_x,imsize_y))
#***** Image size should be approximately: 392 x 267 arcsec

# Look at how many spectral windows you have in each *.ms 
listobs(vis=vis7m,listfile='7m.listobs')
listobs(vis=vis12m,listfile='12m.listobs')
# In this case, 9 spws with 7m; 3 spws with 12m

# Look at weights 
# (note: Plotms can take a long time for large datasets. You may want to average.)
# In CASA 
os.system('rm -rf 7m_WT.png 12m_WT.png')
plotms(vis=vis12m,yaxis='wt',xaxis='uvdist',spw='0~2:200',
       coloraxis='spw',plotfile='12m_WT.png')
#
plotms(vis=vis7m,yaxis='wt',xaxis='uvdist',spw='0~8:200',
       coloraxis='spw',plotfile='7m_WT.png')

# We found that the SPW 7 has lower amplitudes, therefore we choose to remove that in this case
split(vis=vis7m,outputvis='int7m.ms.spl',spw='0,1,2,3,4,5,6,8',datacolumn='data')
vis7m = 'int7m.ms.spl'

# Concat, you could also scale weights, but the weights here look good already
# (note: Concat can take a long time for large datasets. Cut out what you don't need before concat.)
os.system('rm -rf *12m7m.ms')
concat(vis=[vis12m,vis7m],concatvis=vis12m7m)
listobs(vis=vis12m7m,listfile='12m7m.listobs')

#Test: concat(vis=[vis12m,vis7m],concatvis=vis12m7m+'.cpfalse', copypointing=False)

## Concat may give a warning like this, and I ignored it:
#2019-08-17 14:26:05 WARN  MSConcat::copySysCal  /Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Post-workshop/12m7m.ms does not have a valid syscal table,
#2019-08-17 14:26:05 WARN  MSConcat::copySysCal+   the MS to be appended, however, has one. Result won't have one.
#2019-08-17 14:26:05 WARN  MSConcat::concatenate (file ../../ms/MSOper/MSConcat.cc, line 825)  Could not merge SysCal subtables

## You may need this combined *.ms later
os.system('mv *12m7m.ms ../NewData/.')
vis12m7m = workingdir+'NewData/'+vis12m7m

os.chdir(workingdir)


####################################
## CLEAN the interferometry data
## NOTE: You are currently in the Feather directory, but maybe better to move to 'NewData'
###################################

os.system('mkdir -p NewImages')
os.chdir('NewImages')

'''
Use these *.ms:
datadir = '/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Lup3mms_Share/' #the directory where your test data are held
vis12m = datadir+'mst_12_nchan10_start0kms.ms'
vis12m7m = workingdir+'NewData/int12m7m.ms' #You chose the name of your combined interferometry image
vis7m = workingdir+'Diagnostics/7m.ms.spl' ## You had to create this in the previous step
'''

field='Lupus_3_MMS*' # Look in the log to find the name of your source; * is wild-card.
phasecenter='J2000 16h09m18.1 -39d04m44.0' # Look in the listobs, or use the known source coordinates

## I have not confirmed this, but I'm told that for efficiency purposes, tclean likes image size numbers factorizable by 2,3,5,7. These are:
'''for i in range(20,5001,5):
     if i%2.==0 and i%3.==0 and i%7.==0:
         print i
'''

iminfo12m = au.plotmosaic(vis12m,sourceid='0')
iminfo7m = au.plotmosaic(vis7m,sourceid='0')
## I also save the output in the variables iminfo, because they hold the size of the image we will want to create, in arcsec. 
imsize_x = iminfo7m[1]-iminfo7m[2]
imsize_y = iminfo7m[3]-iminfo7m[4]
print('#***** Image size should be approximately: {0:.0f} x {1:.0f} arcsec'.format(imsize_x,imsize_y))

## Find the beamsizes.  You will need AnalysisUtils (au), found here: https://casaguides.nrao.edu/index.php/Analysis_Utilities
expected_hpbw12m = au.estimateSynthesizedBeam(vis12m)
expected_hpbw7m = au.estimateSynthesizedBeam(vis7m)
print('#**** Expected beamsize for 12m: {0:.2f}; {1:.2f}'.format(expected_hpbw12m,expected_hpbw7m))
print('#**** Suggest cell for 12m: {0:.1f}; {1:.1f}'.format(expected_hpbw12m/4,expected_hpbw7m/4))
#**** Expected beamsize for 12m: 1.49; 8.96
#**** Suggest cell for 12m: 0.4; 2.2
cell12m = 0.4
cell7m = 2.0
##Then calculate image size
imsize12_x_px = imsize_x/cell12m
imsize12_y_px = imsize_y/cell12m
imsize7_x_px = imsize_x/cell7m
imsize7_y_px = imsize_y/cell7m
print('#**** Suggest imsize (in px) for 12m: [{0:.0f}, {1:.0f}]'.format(imsize12_x_px,imsize12_y_px))
print('#**** Suggest imsize (in px) for 7m: [{0:.0f}, {1:.0f}]'.format(imsize7_x_px,imsize7_y_px))
#**** Suggest imsize (in px) for 12m: [981; 668]
#**** Suggest imsize (in px) for 7m: [196; 134]
## Note, these are likely too big, so you may round down some.

## 7m parameters
lineimage7m = {"restfreq"   : '115.27120GHz',
  'start'      : '0.0km/s', 
  'width'      : '1.0km/s',
  'nchan'      : 8,
  'imsize'     : [196,160], 
  'cell'       : '2arcsec',
  'gridder'    : 'mosaic',
  'weighting'  : 'briggs',
  'robust'     : 0.5,
}

## 12m parameters
lineimage12m = {"restfreq"   : '115.27120GHz',
  'start'      : '0.0km/s', #you can set this in km/s
  'width'      : '1.0km/s', #you can set this in km/s
  'nchan'      : 8, #you can choose fewer channels to save time; I'm choosing not to image first and last channels
  'imsize'     : [896,630], #also tried [896,540]; [900,600]
  'cell'       : '0.4arcsec',
  'gridder'    : 'mosaic',
  'weighting'  : 'briggs',
  'robust'     : 0.5,
}

#First we make a "dirty" image of each (niter=0, or no iterations) just to see that the image parameters are OK.  
#This test case should not take too long (less than a few minutes)
tclean(vis=vis7m,imagename='int7m_niter0',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=0,interpolation='nearest',**lineimage7m)

tclean(vis=vis12m,imagename='int12m_niter0',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=0,interpolation='nearest',**lineimage12m)

tclean(vis=vis12m7m,imagename='int12m7m_niter0',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=0,interpolation='nearest',**lineimage12m) ##use the parameters for the higher-resolution interferometer when making the combined 12m+7m map

## Compare maps, and make sure they they are covering the same region; that cell size is OK; that frequencies/velocities make sense, etc.
## Use CASAviewer: viewer(infile='int7m_niter0.image')

#Next, RUN a deeper TCLEAN of each map
niter=20000 ## You can increase this when things are going well.  I usually begin with 10000-20000, and then repeat as needed.
cniter=500 ## It was recommended to me to use a smaller (<1000) cniter, but this takes longer
gain=0.05 ## It was recommended to me to use a smaller (<0.1 default) gain, but this takes longer
threshold='0mJy' ## You can clean based on iterations or threshold 

## YOUR 12m+7m map
tclean(vis=vis12m7m,imagename='int7m12m_clean',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=niter,cycleniter=cniter,gain=gain,threshold=threshold,usemask='pb',pbmask=0.3,restoringbeam='common',**lineimage12m)
## Save the intermediate product
'''
os.system('mkdir 7m12m_iter100000')
os.system('cp -rf int7m12m_clean.* 7m12m_iter100000/.')
'''

## YOUR 12m-only map 
tclean(vis=vis12m,imagename='int12m_clean',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=niter,cycleniter=cniter,gain=gain,threshold=threshold,usemask='pb',pbmask=0.3,restoringbeam='common',**lineimage12m)
## Save the intermediate product
'''
os.system('mkdir 12m_iter100000')
os.system('cp -rf int12m_clean.* 12m_iter100000/.')
'''

## YOUR 7m-only map 
tclean(vis=vis7m,imagename='int7m_clean',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=niter,cycleniter=cniter,gain=gain,threshold=threshold,usemask='pb',pbmask=0.3,restoringbeam='common',**lineimage7m)
## Save the intermediate product
'''
os.system('mkdir 7m_iter80000')
os.system('cp -rf int7m_clean.* 7m_iter80000/.')
'''

## I tweaked pbmask to be slightly higher than the default (which is 0.2?) because the edges in this map may be particularly noisy, with bright emission.
## YOU can do more iterations of TCLEAN, until you are happy with the "CLEAN" image
## v1:
## NOTE: I have run 12m for 20000 iterations; I could run more.
## NOTE: I have run 7m for 80000 iterations; I could run more.
## NOTE: I have run 7m12m for 150000 iterations; Between 100000-150000 iterations, a more sophisticated clean might be needed.
## v2:
## We chose to run the same iterations for each method.  Also, we want to test outputs at different iterations.
## Let's run: 40000, 60000, 80000, 100000 for each map.

## This next step will be needed (kernel='commonbeam') if restoringbeam='common' is not included in TCLEAN.  
## In other words, you want a single beam, NOT a beam per channel.  
## This should be used in the case of relatively narrow spectral coverage, so the beam does not change much.
'''
imsmooth(imagename='int7m12m_clean.image',outfile='int7m12m.imsmooth',kernel='commonbeam')
imsmooth(imagename='int7m_clean.image',outfile='int7m.imsmooth',kernel='commonbeam')
imsmooth(imagename='int12m_clean.image',outfile='int12m.imsmooth',kernel='commonbeam') #this is a trick when you need a single beam, rather than a beam per channel.  It will be necessary for the feather with TP image.  Be careful if you have many channels, as you may be using the incorrect beam.
'''

## You may get some warnings like this, but I ignore it for now: 2019-08-14 07:45:07	WARN	imsmooth::Image2DConvolver::_dealWithRestoringBeam	Convolving kernel has minor axis 0.0736102 arcsec which is less than the pixel diagonal length of 0.565685 arcsec. Thus, the kernel is poorly sampled, and so the output of this application may not be what you expect. You should consider increasing the kernel size or regridding the image to a smaller pixel size

os.chdir(workingdir)


########################
## Prepare to FEATHER
########################

os.system('mkdir -p Feather')
os.chdir('Feather')

intimagename = '../NewImages/int7m12m_clean' #prefix from the TCLEAN command above 
#Drop the Stokes axis in both images
#Remember to use the *.smooth image, if you had to smooth after clean
imsubimage(imagename=intimagename+'.image',dropdeg=True,outfile='IntForComb.imsmooth.dropdeg') 
#importfits(fitsimage=TPfits,imagename=TPim)  ## You just need to do this the first time, in order to get your TP Fits file into the CASA format (*.image)
imsubimage(imagename=TPim,dropdeg=True,outfile='TPForComb.dropdeg')

Intim =  'IntForComb.imsmooth.dropdeg' #12m+7m image from TCLEAN, after imsubimage
Intpb =  intimagename+'.pb' #primary beam response, this was created in your previous 12m+7m TCLEAN
Intmask = intimagename+'.mask' #mask from TCLEAN (cutting below a certain pb value), this was created in your previous 12m+7m TCLEAN
TPim = 'TPForComb.dropdeg'

#Regrid the Inter. mask to have 1 channel (note, this may be based on the PB, but user may choose/draw other masks.)
imsubimage(imagename=Intmask,
           chans='0',outfile=Intmask+'.cut',dropdeg=True)
#Regrid the Inter. PB mask to have 1 channel
imsubimage(imagename=Intpb,
           chans='0',outfile=Intpb+'.cut',dropdeg=True)

#check that rest frequencies match - Initially different. You have to use "imreframe" to set the rest frequency of the TP image to match that of 12m
tp_restfreq=imhead(TPim,mode='get',hdkey='restfreq')
int_restfreq=imhead(Intim,mode='get',hdkey='restfreq')
if tp_restfreq == int_restfreq: print('## Frequencies match')
else: print('##**** Need to align frequencies: TP: {0}; Interf.: {1}'.format(tp_restfreq,int_restfreq))
## IF YOU SEE ##**** Need to align frequencies:
imreframe(imagename=TPim,output=TPim+'.ref',outframe='lsrk',restfreq='115271199999.99998Hz') ## You would need to indicate the rest frequency for your dataset.
tp_restfreq=imhead(TPim+'.ref',mode='get',hdkey='restfreq') #check again
if tp_restfreq == int_restfreq: print('## Frequencies match!!')
else: print('##**** Need to align frequencies: TP: {0}; Interf.: {1}'.format(tp_restfreq,int_restfreq))
## In case you want to use this version elsewhere:
## exportfits(imagename=TPim+'.ref/',fitsimage='TP.image.ref.fits',velocity=True)

#Regrid TP image to match Interferometry image (note that the 'Freq' and 'Stokes' axes are flipped)
imregrid(imagename=TPim+'.ref',
         template=Intim,
         axes=[0,1,2],
         output='TP.image.regrid')

'''
#Regrid TP image to match Interferometry in spectral axis only
imregrid(imagename=TPim+'.ref',
		template=Intim,
		axes = [2],
		output = 'TP.image.regrid.spec')
'''

#Trim the 7m+12m and (regridded) TP images
#Do this with the mask that was created in TCLEAN based on the PB (can also do with a box, as in CASAGuides)
os.system('rm -rf TP.regrid.subim')
os.system('ln -s ../NewImages/int7m12m_clean.mask.cut .')

imsubimage(imagename='TP.image.regrid',
           outfile='TP.regrid.subim',
           mask='int7m12m_clean.mask.cut',stretch=True)

os.system('rm -rf Int.image.subim')
imsubimage(imagename=Intim,
           outfile='Int.image.subim',
           mask='int7m12m_clean.mask.cut',stretch=True)

#CONTINUE WITH TP.regrid.subim and Int.image.subim

#Mask the PB image to match the Int/TP images
imsubimage(imagename=Intpb+'.cut',
           outfile='Int.pb.subim',
           mask='int7m12m_clean.mask.cut')

#Multiply the TP image by the 7m+12m primary beam response 
os.system('rm -rf TP.subim.depb')
immath(imagename=['TP.regrid.subim',
                  'Int.pb.subim'],
       expr='IM0*IM1',stretch=True,
       outfile='TP.subim.depb')

#I see this warning, but ignore it: 2019-08-14 07:42:02	WARN	ImageExprCalculator::compute	image units are not the same: 'Jy/beam' vs ''. Proceed with caution. Output image metadata will be copied from one of the input images since imagemd was not specified



########################
## Ready to FEATHER
########################

os.system('rm -rf Feather.image')
feather(imagename='Feather.image',
        highres='Int.image.subim',
        lowres='TP.subim.depb')

exportfits(imagename='Feather.image',fitsimage='final_feather.fits',velocity=True)
exportfits(imagename='TP.subim.depb',fitsimage='TP.subim.depb.fits',velocity=True)
exportfits(imagename='int7m12m_clean.image',fitsimage='final_int7m12m_clean.fits',velocity=True)
exportfits(imagename='int7m12m_clean.residual',fitsimage='final_int7m12m_clean.res.fits',velocity=True)

os.chdir(workingdir)

######################
# HYBRID -- IN PROGRESS!!!
######################

os.system('mkdir -p Hybrid1')
os.chdir('Hybrid1')

TPforComb = workingdir+'Feather/TP.image.regrid.spec'
vis12m7m = workingdir+'NewData/int12m7m.ms' #You chose the name of your combined interferometry image

'''
# May need again:
field='Lupus_3_MMS*' # Look in the log to find the name of your source; * is wild-card.
phasecenter='J2000 16h09m18.1 -39d04m44.0' # Look in the listobs, or use the known source coordinates
'''

## May need to mask pixels in TP
os.system('rm -rf TP_unmasked.image')
os.system('cp -r ../Feather/TP.image.regrid.spec ' +
          'TP_unmasked.image')
ia.open('TP_unmasked.image')
ia.replacemaskedpixels(0., update=True)
ia.close()

## May also need to downsample the TP to make a smaller image?

## HYBRID 1
## use TP as model for cleaning 7m+12m; feather TP with this image

## 12m parameters
lineimage12m = {"restfreq"   : '115.27120GHz',
  'start'      : '0.0km/s', #you can set this in km/s
  'width'      : '1.0km/s', #you can set this in km/s
  'nchan'      : 8, #you can choose fewer channels to save time; I'm choosing not to image first and last channels
  'imsize'     : [896,630], #also tried [896,540]; [900,600]
  'cell'       : '0.4arcsec',
  'gridder'    : 'mosaic',
  'weighting'  : 'briggs',
  'robust'     : 0.5,
}

#RUN TCLEAN as above
niter=20000 ## You can increase this when things are going well.  I usually begin with 10000-20000, and then repeat as needed.
cniter=500 ## It was recommended to me to use a smaller (<1000) cniter, but this takes longer
gain=0.05 ## It was recommended to me to use a smaller (<0.1 default) gain, but this takes longer
threshold='0mJy' ## You can clean based on iterations or threshold 

## YOUR 12m+7m map -- HERE...
tclean(vis=vis12m7m,imagename='int7m12m_TPmodel',startmodel='TP_unmasked.image',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=niter,cycleniter=cniter,gain=gain,threshold=threshold,usemask='pb',pbmask=0.3,restoringbeam='common',**lineimage12m)
## Save the intermediate product
'''
os.system('mkdir 7m12m_TPmodel_iter40000')
os.system('cp -rf int7m12m_TPmodel.* 7m12m_TPmodel_iter40000/.')
'''




## HYBRID 2
## use TP as model for cleaning 7m; feather TP with 7m image; this as model for cleaning 12m; feather 
my7mimage = workingdir+'Feather/7m_iter80000/int7m_clean.image/'

######################
## Day 2: TP2VIS
## Documentation here: https://github.com/tp2vis/distribute
########################

os.system('mkdir -p Tp2vis')
os.chdir('Tp2vis')

'''
#1.0 Collect the files
#You might need this, in case you started again at this section.
datadir = '/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Lup3mms_Share/' #the directory where your test data are held
workingdir ='/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Post-workshop/'
vis7m = workingdir+'Diagnostics/int7m.ms.spl' #We discovered in the "diagnostics" step that one SPW needed to be removed.
vis12m = datadir+'mst_12_nchan10_start0kms.ms'
TPim = workingdir+'TP.image.ref' 
vis12m7m = workingdir+'Diagnostics/int12m7m.ms'
'''

#1.1: Make a pointing (ptg) file
listobs(vis12m,listfile='calibrated_12m.log')
!cat calibrated_12m.log | grep "none" | awk '{print $4,$5}' | sed 's/\([0-9]*\)\:\([0-9]*\):\([0-9.]*\) /\1h\2m\3 /' | sed 's/\([0-9][0-9]\)\.\([0-9][0-9]\)\.\([0-9][0-9]\)\./\1d\2m\3\./' | awk '{printf("J2000 %ss %ss\n",$1,$2)}' > 12.ptg
#Note: the exclamation point (!) indicates a bash command you can run within CASA

#1.2: Find a reasonable RMS
TPrms=imstat(TPim,axes=[0,1])['rms'][20:30].mean() #remember, these are the channels of the SD image (which has more than 10 channels)
print('#TP rms: {}'.format(TPrms))
#TP rms: 0.188200941992

#2. Run TP2VIS:
#You may need to: execfile('distribute/tp2vis.py')                                          # load tp2vis 
tp2vis(TPim,'tp.ms','12.ptg',rms=TPrms)                     # Basic usage to make visibilities, mostly standard settings
tp2vis(TPim,'tp_winpix9.ms','12.ptg',rms=TPrms, winpix=9)            # Again, make visibilities, winpix is important if emission around edges
## Note: For this dataset, winpix=9 appears to be an ok option.  Not fully tested.

#2.1 Check the tclean of the TP *.ms file, with niter=0
lineimagename =  'tp2vis'
field='Lupus_3_MMS*' # science field(s). 
phasecenter='J2000 16h09m18.1 -39d04m44.0'

## 12m parameters from above, this is just a test to make sure the combination will be correct
lineimage12m = {"restfreq"   : '115.27120GHz',
  'start'      : '0.0km/s', #you can set this in km/s
  'width'      : '1.0km/s', #you can set this in km/s
  'nchan'      : 8, #you can choose fewer channels to save time; I'm choosing not to image first and last channels
  'imsize'     : [896,630], #Note, this can be found with analysisutils (see above)
  'cell'       : '0.4arcsec',
  'gridder'    : 'mosaic',
  'weighting'  : 'briggs',
  'robust'     : 0.5,
}

## Notice the difference when using winpix=9
tclean(vis=['tp.ms'],imagename=lineimagename+'_wp0_niter0',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=0,interpolation='nearest',**lineimage12m)
tclean(vis=['tp_winpix9.ms'],imagename=lineimagename+'_wp9_niter0',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=0,interpolation='nearest',**lineimage12m)
## We will use the winpix=9 version.

## IF OK, the, you should add the 12m and 7m visibilities as input to TCLEAN.
## First assess the weights, using a plotting function in TP2VIS
## If you only have the 12m+7m ms already concatenated:
#tp2vispl([vis12m7m,'tp_winpix9.ms'],outfig='tp2vispl.png') 
## Otherwise, separate 7m and 12m for visualization: 
tp2vispl([vis12m,vis7m,'tp_winpix9.ms'],outfig='tp2vispl_v2.png') 

##Next, RUN a TCLEAN with niter=0
##First you can concat all the UV data
concat(vis=[vis12m,vis7m,'tp_winpix9.ms'],concatvis='all.ms.cpfalse', copypointing=False)
tclean(vis='all.ms.cpfalse',imagename=lineimagename+'_niter0',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=0,interpolation='nearest',**lineimage12m)
##If you prefer not to concat first, then another option:
#tclean(vis=[vis12m7m,'tp_winpix9.ms'],imagename=lineimagename+'_niter0',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=0,interpolation='nearest',**lineimage12m)


#Finally, RUN a deeper TCLEAN of each map
niter=10000 ## You can increase this when things are going well.
cniter=500 ## It was recommended to me to use a smaller (<1000) cniter, but this takes longer
gain=0.05 ## It was recommended to me to use a smaller (<0.1 default) gain, but this takes longer
threshold='0mJy' ## You can clean based on iterations or threshold 

## Image deeper:
niter=50000 ## You can increase this when things are going well.
tclean(vis='all.ms.cpfalse',imagename=lineimagename+'_clean',field=field,spw='',phasecenter=phasecenter,mosweight=True,specmode='cube',niter=niter,cycleniter=cniter,gain=gain,threshold=threshold,usemask='pb',pbmask=0.3,**lineimage12m)

exportfits(imagename=lineimagename+'_clean.image',fitsimage='final_tp2vis.fits',velocity=True)
exportfits(imagename=lineimagename+'_clean.residual',fitsimage='final_tp2vis.res.fits',velocity=True)

os.chdir(workingdir)

######################
## Day 3: SDInt
## Documentation here: https://github.com/urvashirau/WidebandSDINT
########################

os.system('mkdir -p Sdint')
os.chdir('Sdint')

## You should be able to make a gaussian beam for the PSF with a script.
## I could not get this working yet: execfile('/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/dc2019/scripts/make_gauss_beam_cube.py')
## Instead I use the PSF from TP2VIS+Tclean

## FILE List:
## Parameter names chosen to work with runsdint.py
## vis == vis12m7m; sdimage = TPim from before
workingdir ='/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Post-workshop/'
vis = workingdir+'Diagnostics/int12m7m.ms' #your combined interferometry image
sdimage = workingdir+'TP.image' #your TP image; Has the axes: ra,dec,freq,stokes
sdpsf = workingdir+'Tp2vis/tp2vis_niter0_cpfalse2.psf/' ## PSF that comes from TP2VIS (or another cleaning method)

#check that rest frequencies match - Initially different. 
#PSF should carry the information of the interferometry rest frequency.
#You have to use "imreframe" to set the rest frequency of the TP image to match that of 12m
tp_restfreq=imhead(sdimage,mode='get',hdkey='restfreq')
psf_restfreq=imhead(sdpsf,mode='get',hdkey='restfreq')
if tp_restfreq == psf_restfreq: print('## Frequencies match')
else: print('##**** Need to align frequencies: TP: {0}; Interf.: {1}'.format(tp_restfreq,psf_restfreq))
imreframe(imagename=sdimage,output=sdimage+'.ref',outframe='lsrk',restfreq='115271199999.99998Hz')
tp_restfreq=imhead(sdimage+'.ref',mode='get',hdkey='restfreq') #check again
if tp_restfreq == psf_restfreq: print('## Frequencies match!!')
else: print('##**** Need to align frequencies: TP: {0}; Interf.: {1}'.format(tp_restfreq,psf_restfreq))
sdimage=sdimage+'.ref'

## CHECK HEADER DIMENSIONS
axim = imhead(sdimage)['axisnames']
axpsf = imhead(sdpsf)['axisnames']
print('#*****Image axes; PSF axes: {} {}'.format(axim,axpsf))

## Switch Stokes and Freq axis so that dimensions = [ra,dec,stokes,freq], apparently required by CASA in the later steps
## You can do this for the image...
imtrans(imagename=sdimage,outfile='TP.image.trans',order='0132')   # switch stokes (3) and freq (2) axes
sdimage = 'TP.image.trans' ## Drop the degenerate axis??
## Check again...
axim = imhead(sdimage)['axisnames']
axpsf = imhead(sdpsf)['axisnames']
print('#*****NEW Image axes; PSF axes: {} {}'.format(axim,axpsf))


## Cut the SD image to have the same number of frequency channels as the PSF 
shapeim = imhead(sdimage)['shape']
shapepsf = imhead(sdpsf)['shape']
print('#*****Image shape; PSF Shape: {} {}'.format(shapeim,shapepsf))
imregrid(imagename=sdimage,
         template=sdpsf,
         axes=[3],
         output='TP.regrid')
## Check again:
shapeim = imhead('TP.regrid')['shape']
shapepsf = imhead(sdpsf)['shape']
print('#*****Image shape; PSF Shape: {} {}'.format(shapeim,shapepsf))

## FINALLY...
## To actually run:
## You'll need SDInt from: https://github.com/urvashirau/WidebandSDINT
## Then, you need the *.py scripts from WidebandSDINT/ScriptForRealData/
## I copy those into my workingdir
## You can run with: execfile('runsdint.py')
## Note, I had to make a few changes to runsdint.py.
## (1) copy and paste the files and parameters listed below, in the first section of runsdint.py
## (2) in jointim = SDINT_imager, you'll need to update: width=width, nchan=nchan,

workingdir ='/Users/aplunket/ResearchNRAO/Meetings/DataComb2019/Lup3mms/Post-workshop/'
vis = workingdir+'Diagnostics/int12m7m.ms' #your combined interferometry image
sdimage = workingdir+'SDInt/TP.regrid' #your TP image; Has the axes: ra,dec,freq,stokes
sdpsf = workingdir+'Tp2vis/tp2vis_niter0_cpfalse2.psf/' ## PSF that comes from TP2VIS (or another cleaning method); Will need to drop the degenerate axis

deconvolver='hogbom'
specmode='cube'
gridder='mosaic'

phasecenter='J2000 16h09m18.1 -39d04m44.0'
imsize=[896,630]
cell='0.4arcsec'
reffreq='115.27120GHz'
dishdia=12.0 # in meters
niter=10000
cycleniter= 500
scales=[0,12,20,40,60,80,100]
pblimit=0.2
mythresh='5mJy'
mask=''
nchan=8 ## ensure that runsdint.py uses nchan=nchan
start='0.0km/s'
width='1.0km/s'  ## ensure that runsdint.py uses width=width


exportfits(imagename='tryit.joint.cube.image',fitsimage='final_sdint.fits',velocity=True)
exportfits(imagename='tryit.joint.cube.residual',fitsimage='final_sdint.res.fits',velocity=True)



