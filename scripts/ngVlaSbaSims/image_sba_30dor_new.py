
import combo_utils as combut

## 27DEC20 BSM COMMENTED OUT WITH "##" SD IMAGING TO JUST RERUN THE C.01 SBA

# all images must have the same number of pixels
#  since they use one PB image in the fidelity calculation
#  the created_images will lack the TP maps so it's not a complete
#  manifest.
created_images = []

# set this-
truth_image = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.skymodel' 
myvp='ngvlaSba_final.tab'

# simulated MS's, without the '.ms'
phase_center="J2000 08h37m27.2s 22d39m14.7s"
sd_ms='sd_30dor_new/sd_30dor_new.ngvla-sd_loc.sd'
#sba_ms = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc'
sba_ms='sba_30dor_new/sba_30dor_new.ngvla-revC.01.sba'
sd_image = sd_ms+'.sf7.tp'

# create VP
rmtables(myvp)
vp.reset()
vp.setpbairy(telescope='NGVLA1',dishdiam=6.0,blockagediam=0.0,maxrad='8.5deg',reffreq='1.0GHz',dopb=True)
vp.setpbairy(telescope='NGVLA1',dishdiam=18.0,blockagediam=0.0,maxrad='8.5deg',reffreq='1.0GHz',dopb=True)
vp.saveastable(myvp)


# grid the single dish map
cellsize=au.primaryBeamArcsec(frequency=93,fwhmfactor=1.05,diameter=18)/9.0
sdimaging(infiles=sd_ms+'.ms',outfile=sd_image,cell=['4.3arcsec','4.3arcsec'],gridfunction='sf',convsupport=7,imsize=[114,114])

#created_images.append(sd_image)

sd_img_fixed = combut.fix_image_calib(sd_image,sd_image+'.fixed',cal_factor = 1.28, beam_factor = 0.85)
sd_img_fixed = sd_image+'.fixed'
created_images.append(sd_img_fixed)

# SBA image 
INT_imagename = sba_ms+'.autoDev5b.final'
delmod(vis=sba_ms+'.ms')
tclean(vis=sba_ms+'.ms',imagename=INT_imagename,niter=100000,cycleniter=1000,threshold='0.14Jy',pblimit=0.10,phasecenter=phase_center,vptable=myvp,
       interactive=False,pbcor=True,cell='1.25arcsec',imsize=[392,392],gridder='mosaic',weighting='natural',usemask='auto-multithresh',
       sidelobethreshold=1.5,noisethreshold=5.0,minbeamfrac=0.1,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.75,verbose=True)

tclean(vis=sba_ms+'.ms',imagename=INT_imagename,niter=100000,cycleniter=1000,threshold='0.14Jy',pblimit=0.10,phasecenter=phase_center,vptable=myvp,
       interactive=False,pbcor=True,cell='1.25arcsec',imsize=[392,392],gridder='mosaic',weighting='natural',usemask='auto-multithresh',
       sidelobethreshold=1.5,noisethreshold=2.5,minbeamfrac=0.1,lownoisethreshold=1.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.75,verbose=True)

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
INT_imagename = sba_ms+'.autoDev5b.final.sdmod'
tclean(vis=sba_ms+'.ms',imagename=INT_imagename,niter=100000,cycleniter=1000,threshold='0.14Jy',pblimit=0.10,phasecenter=phase_center,vptable=myvp,
       interactive=False,pbcor=True,cell='1.25arcsec',imsize=[392,392],gridder='mosaic',weighting='natural',usemask='auto-multithresh',startmodel=sd_model,
       sidelobethreshold=1.5,noisethreshold=5.0,minbeamfrac=0.1,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.75,verbose=True)

tclean(vis=sba_ms+'.ms',imagename=INT_imagename,niter=100000,cycleniter=1000,threshold='0.14Jy',pblimit=0.10,phasecenter=phase_center,vptable=myvp,
       interactive=False,pbcor=True,cell='1.25arcsec',imsize=[392,392],gridder='mosaic',weighting='natural',usemask='auto-multithresh',
       sidelobethreshold=1.5,noisethreshold=2.5,minbeamfrac=0.1,lownoisethreshold=1.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.75,verbose=True)

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


##########
#inimg,refimg,pbimg='',psfimg='',fudge_factor=1.0,scale_factor=1.0,pb_thresh=0.25,clean_up=True,outfile=''):

# run shell script do_sba_jvm here - it's a 1% effect on peak brightness,
#   total flux, and flux of the brightest "object"

#sd_img_fixed = "sd_30dor_zeroTau/sd_30dor_zeroTau.ngvla-sd.sdbetter.tp.fix2"
#int_map = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image'
#int_pb = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.pb'

#outfile=int_map+'_plusTpFixed'
#rmtables(sd_map+".TMP.intGrid.intPb")
#imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
#immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
#feather(imagename=outfile+'.image',highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
#immath(imagename=[outfile+'.image',int_pb],expr='IM0/IM1',outfile=outfile+'.pbcor')

#int_map = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image'
#int_pb = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.pb'
#outfile=int_map+'_plusTpFixed'
#rmtables(sd_map+".TMP.intGrid.intPb")
#imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
#immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
#feather(imagename=outfile+'.image',highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
#immath(imagename=[outfile+'.image',int_pb],expr='IM0/IM1',outfile=outfile+'.pbcor')

#int_map = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image.JvM'
#int_pb = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.pb'
#outfile=int_map+'_plusTpFixed'
#rmtables(sd_map+".TMP.intGrid.intPb")
#imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
#immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
#feather(imagename=outfile+'.image',highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
#immath(imagename=[outfile+'.image',int_pb],expr='IM0/IM1',outfile=outfile+'.pbcor')

#int_map = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image.JvM'
#int_pb = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.pb'
#outfile=int_map+'_plusTpFixed'
#rmtables(sd_map+".TMP.intGrid.intPb")
#imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
#immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
#feather(imagename=outfile+'.image',highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
#immath(imagename=[outfile+'.image',int_pb],expr='IM0/IM1',outfile=outfile+'.pbcor')


##### FIDELITY RESULTS
# 29dec20 new c.01 results
#  these are equivalent to results previously obtained
"""
*************************************
image:  sba_30dor_new/sba_30dor_new.ngvla-revC.01.sba.autoDev5b.final.sdmod.image.feather.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.skymodel
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.933486121611 0.948268737776 0.947403029944 0.950477245611 0.994727136839
 ALMA:  9.44457249634 9.44457249634 10.9985481583 20.4999826495
*************************************
*************************************
image:  sba_30dor_new/sba_30dor_new.ngvla-revC.01.sba.autoDev5b.final.sdmod.image.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.skymodel
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.823840123343 0.857823722461 0.834721770784 0.849089127595 0.983901114905
 ALMA:  3.46299423899 3.46299423899 3.37577567323 4.61027207577
*************************************
*************************************
image:  sba_30dor_new/sba_30dor_new.ngvla-revC.01.sba.autoDev5b.final.image.feather.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.skymodel
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.922274159827 0.925945301744 0.928626205351 0.929232441025 0.991190956403
 ALMA:  7.74344082499 7.74344082499 8.30508247864 13.3890719299
*************************************
"""

######################
# 29dec20 - not sure exactly where the final results in the memo are captured 
#   these below don't appear to be them

# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.597834017293 -1.33861569248 0.2995042199 0.299513085042 0.831007450116
#  ALMA:  1.02175095806 1.02175095806 1.03219515629 1.16833090531
# *************************************


#************************************
#image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image.JvM reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.598394843374 -1.3167879181 0.301424795928 0.301453620541 0.823399030669
# ALMA:  1.02534308091 1.02534308091 1.0377758294 1.19206880819
#*************************************

# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.597978757391 -1.32342821523 0.300514042678 0.300675614089 0.816169182529
#  ALMA:  1.02592020643 1.02592020643 1.03844077043 1.18528191227
# *************************************

# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.617707447517 -0.98874119061 0.334559640859 0.334579527148 0.85883555414
#  ALMA:  1.06272473777 1.06272473777 1.0744770796 1.22563354996
# *************************************

#*************************************
#image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image.JvM reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.618246975428 -0.972359424307 0.336350310367 0.336397257881 0.852406198868
# ALMA:  1.06621530206 1.06621530206 1.08130647821 1.25110243134
#*************************************

# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.617861730636 -0.961806145923 0.337224641582 0.337433625381 0.845151713553
#  ALMA:  1.08040335555 1.08040335555 1.09463081133 1.24895008654
# *************************************

# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image_plusTpFixed.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.800094886819 0.893804169263 0.90212374137 0.902244142598 0.981438727441
#  ALMA:  4.38321430386 4.38321430386 5.44214534766 11.5694274424
# *************************************

#*************************************
#image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image.JvM_plusTpFixed.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.802824441476 0.894183835532 0.902310462318 0.902308410984 0.980666920919
# ALMA:  4.09042024224 4.09042024224 5.12920808451 11.7845923481
#*************************************

# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image_plusTpFixed.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.809478293229 0.909852036048 0.914467856307 0.913177303012 0.976506158112
#  ALMA:  6.37630126049 6.37630126049 7.38963098642 14.6967453638
# *************************************

#*************************************
#image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image.JvM_plusTpFixed.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.812884116221 0.907212871077 0.91180729549 0.909757955119 0.973917665798
# ALMA:  5.61978046867 5.61978046867 6.45433687902 13.6515715982
#*************************************

# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image_plusTpFixed.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.801080374901 0.890534665272 0.899358737753 0.899385913103 0.980682377326
#  ALMA:  4.32194295037 4.32194295037 5.28196459846 11.171963816
# *************************************


# *************************************
# image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image_plusTpFixed.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
# Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
# 0.810747445827 0.906366222395 0.911364265327 0.909790967955 0.975338931901
#  ALMA:  6.0720189369 6.0720189369 6.99382500632 14.3811935709
# *************************************

#*************************************
#image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image.JvM_plusTpFixed.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.813758437599 0.903341284633 0.908327031574 0.905886583449 0.972235361002
# ALMA:  5.294661809 5.294661809 6.07455888808 13.3081708172
#*************************************

#*************************************
#image:  sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.image.JvM_plusTpFixed.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.803552024445 0.890835947949 0.899455777472 0.899341019137 0.979707074803
# ALMA:  4.02557335844 4.02557335844 4.99388452581 11.4782381644
#*************************************





