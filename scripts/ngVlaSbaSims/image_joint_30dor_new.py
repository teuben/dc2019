 
import combo_utils as combut

truth_image = 'ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel'
joint_vp = "ngvla-and-sba-final.tab"

phase_center="J2000 08h37m27.2s 22d39m14.7s"
core_ms = 'ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc'
sd_ms='sd_30dor_new/sd_30dor_new.ngvla-sd_loc.sd'
sba_ms = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc'
sd_img_fixed = sd_ms+'.sf7.tp.fixed'

##############

# Empty list in which we'll build up a list of the image products
#  created along the way
#
# all images must have the same number of pixels
#  since they use one PB image in the fidelity calculation
#  the created_images will lack the TP maps so it's not a complete
#  manifest.

created_images = []
 
# set VPs carefully in all scripts. rmtable them first.
# reset VP for core only imaging
vp.reset()

# core only imaging -- 

INT_imagename = core_ms + '.autoDev2.final'
delmod(vis=core_ms+'.ms')
tclean(vis=core_ms+'.ms',imagename=INT_imagename,niter=10000,cycleniter=1000,pblimit=0.15,phasecenter=phase_center,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.05Jy',usemask='auto-multithresh',
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.5,noisethreshold=5.0,minbeamfrac=0.3,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.65,verbose=True,startmodel='')
for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

INT_imagename = core_ms + '.simple.final'
delmod(vis=core_ms+'.ms')
tclean(vis=core_ms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.15,phasecenter=phase_center,
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.05Jy',usemask='auto-multithresh',
       sidelobethreshold=3.5,noisethreshold=5.0,minbeamfrac=0.3,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.65,verbose=True,startmodel='')
for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)


#sys.exit("you are here")

######## Joint imaging

# create the VP table explicitly - even though i know this doesn't work....
vp.reset()
rmtables(joint_vp)
vp.setpbairy(telescope='NGVLA',dishdiam=6.0,blockagediam=0.0,maxrad='3.5deg',reffreq='1.0GHz',dopb=True)
sba_table = vp.getuserdefault('NGVLA')
vp.setpbairy(telescope='NGVLA',dishdiam=18.0,blockagediam=0.0,maxrad='1.78deg',reffreq='1.0GHz',dopb=True)
ngvla_table = vp.getuserdefault('NGVLA')
vp.setuserdefault(sba_table,'NGVLA','sbaNgvla')
vp.setuserdefault(ngvla_table,'NGVLA','ngvla')
vp.saveastable(joint_vp)
#### or - 
#vp.reset()
#vp.loadfromtable(joint_vp)


#### CONCAT. in time order. get weights right.
infile=core_ms
infile2=sba_ms
delmod(vis=infile2+'.ms')
delmod(vis=infile+'.ms')
newms='joint_30dor.ngvla.revC_new'
# visweightscale = (6/18)**4
concat(vis=[infile+'.ms',infile2+'.ms'],concatvis=newms+'.ms',visweightscale=[1.0,0.0123])


# joint deconvolution

INT_imagename = newms+'.autoDev5'
tclean(vis=newms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.15,phasecenter=phase_center,vptable=joint_vp,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=4.5,minbeamfrac=0.3,lownoisethreshold=3.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True)

for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

[fthrd,fthrd_nopb] = combut.feather_one(sd_img_fixed,INT_imagename+'.image',INT_imagename+'.pb')
created_images.append(fthrd)
created_images.append(fthrd_nopb)


sd_model = combut.make_clnMod_fromImg(sd_img_fixed,INT_imagename+'.image',tag='jointGrid')
#created_images.append(sd_model)

INT_imagename = newms+'.sdmod.autoDev5'
tclean(vis=newms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.15,phasecenter=phase_center,vptable=joint_vp,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=4.5,minbeamfrac=0.3,lownoisethreshold=3.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True,startmodel=sd_model)

for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

[fthrd,fthrd_nopb] = combut.feather_one(sd_img_fixed,INT_imagename+'.image',INT_imagename+'.pb')
created_images.append(fthrd)
created_images.append(fthrd_nopb)

###
# other version: sdmodle = 6msdmodFeathered-


sd_model = combut.make_clnMod_fromImg("sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.sdmod.image.feather.pbcor",INT_imagename+'.image',tag='jointGrid') 
#created_images.append(sd_model)

INT_imagename = newms+'.sdmod6m.autoDev5'

tclean(vis=newms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.15,phasecenter=phase_center,vptable=joint_vp,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=4.5,minbeamfrac=0.3,lownoisethreshold=3.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True,startmodel=sd_model)

for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

###

[fthrd,fthrd_nopb] = combut.feather_one(sd_img_fixed,INT_imagename+'.image',INT_imagename+'.pb')
created_images.append(fthrd)
created_images.append(fthrd_nopb)

print " **** Manifest of images created: "
print created_images

# filter out '.pb' and '.residual' maps before calculating fidelity - 
best_images = []
for ii in created_images:
    if not(re.match(".*\.pb$",ii) or re.match(".*\.residual$",ii) or re.match(".*\.weight$",ii)):
        best_images.append(ii)

print " **** Selected Images to calculate fidelity on: "
print best_images

# calculate fidelity - 
for mm in best_images:
    combut.calc_fidelity(mm,truth_image,INT_imagename+'.pb',outfile=mm+'.fiderr',pb_thresh=0.5)


