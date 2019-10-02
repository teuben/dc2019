
import combo_utils as combut

# all images must have the same number of pixels
#  since they use one PB image in the fidelity calculation
#  the created_images will lack the TP maps so it's not a complete
#  manifest.
created_images = []

# set this-
truth_image = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.skymodel' 
myvp='sba_final.tab'

# simulated MS's, without the '.ms'
phase_center="J2000 08h37m27.2s 22d39m14.7s"
sd_ms='sd_30dor_new/sd_30dor_new.ngvla-sd_loc.sd'
sba_ms = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc'
sd_image = sd_ms+'.sf7.tp'

# grid the single dish map
#cellsize=au.primaryBeamArcsec(frequency=93,fwhmfactor=1.05,diameter=18)/9.0
sdimaging(infiles=sd_ms+'.ms',outfile=sd_image,cell=['4.3arcsec','4.3arcsec'],gridfunction='sf',convsupport=7,imsize=[114,114])

#created_images.append(sd_image)

sd_img_fixed = combut.fix_image_calib(sd_image,sd_image+'.fixed',cal_factor = 1.28, beam_factor = 0.85)
#created_images.append(sd_img_fixed)

# SBA image 
INT_imagename = sba_ms+'.autoDev5.final'
delmod(vis=sba_ms+'.ms')
tclean(vis=sba_ms+'.ms',imagename=INT_imagename,niter=100000,cycleniter=1000,threshold='0.14Jy',pblimit=0.10,phasecenter=phase_center,vptable=myvp,
       interactive=False,pbcor=True,cell='1.25arcsec',imsize=[392,392],gridder='mosaic',weighting='natural',usemask='auto-multithresh',
       sidelobethreshold=1.5,noisethreshold=5.0,minbeamfrac=0.1,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.75,verbose=True)
for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

# do JvM here if so inclined

[fthrd,fthrd_nopb] = combut.feather_one(sd_img_fixed,INT_imagename+'.image',INT_imagename+'.pb')
created_images.append(fthrd)
created_images.append(fthrd_nopb)

# img, refimg, pb, outfile
#first_result = combut.calc_fidelity(fthrd,)

# make Jy/pix version of TP map on the pixellization of the map we just made
sd_model = combut.make_clnMod_fromImg(sd_img_fixed,INT_imagename+'.image',tag='sbaGrid')
created_images.append(sd_model)

delmod(vis=sba_ms+'.ms')
INT_imagename = sba_ms+'.autoDev5.final.sdmod'
tclean(vis=sba_ms+'.ms',imagename=INT_imagename,niter=100000,cycleniter=1000,threshold='0.14Jy',pblimit=0.10,phasecenter=phase_center,vptable=myvp,
       interactive=False,pbcor=True,cell='1.25arcsec',imsize=[392,392],gridder='mosaic',weighting='natural',usemask='auto-multithresh',startmodel=sd_model,
       sidelobethreshold=1.5,noisethreshold=5.0,minbeamfrac=0.1,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.75,verbose=True)
# rms off source ~0.15 Jy/bm
for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

[fthrd,fthrd_nopb] = combut.feather_one(sd_img_fixed,INT_imagename+'.image',INT_imagename+'.pb')
created_images.append(fthrd)
created_images.append(fthrd_nopb)

#my_image ='sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.sdmod.image.feather.pbcor'
#combut.calc_fidelity(my_image,truth_image,'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.sdmod.pb', 
#                     outfile=my_image+'.fiderr')

print " *************** CREATED_IMAGES: "
print created_images

best_images = []
for ii in created_images:
    if not(re.match(".*\.pb$",ii) or re.match(".*\.residual$",ii) or re.match(".*\.weight$",ii)):
        best_images.append(ii)

print " **** Selected images to calculate fidelity on: "
print best_images

for mm in best_images:
    combut.calc_fidelity(mm,truth_image,INT_imagename+'.pb',outfile=mm+'.fiderr',pb_thresh=0.5)


