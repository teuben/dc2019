 
import combo_utils as combut

truth_image = 'ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel'
joint_vp = 'ngvlaSba_final.tab'
#"ngvla-and-sba-final.tab"

phase_center="J2000 08h37m27.2s 22d39m14.7s"
core_ms = 'ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc'
sd_ms='sd_30dor_new/sd_30dor_new.ngvla-sd_loc.sd'
sba_ms = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc'
sd_img_fixed = sd_ms+'.sf7.tp.fixed'

##############

# dec2020 new & correct VP table prescription for non-alma heterogeneous arrays-
rmtables(joint_vp)
vp.reset()
vp.setpbairy(telescope='NGVLA1',dishdiam=6.0,blockagediam=0.0,maxrad='8.5deg',reffreq='1.0GHz',dopb=True)
vp.setpbairy(telescope='NGVLA1',dishdiam=18.0,blockagediam=0.0,maxrad='8.5deg',reffreq='1.0GHz',dopb=True)
vp.saveastable(joint_vp)

# Empty list in which we'll build up a list of the image products
#  created along the way
#
# all images must have the same number of pixels
#  since they use one PB image in the fidelity calculation
#  the created_images will lack the TP maps so it's not a complete
#  manifest.

created_images = []
 
# core only imaging -- 

INT_imagename = core_ms + '.autoDev2.final'
#rmtables(INT_imagename+"*")
#delmod(vis=core_ms+'.ms')
"""
tclean(vis=core_ms+'.ms',imagename=INT_imagename,niter=10000,cycleniter=1000,pblimit=0.3,phasecenter=phase_center,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.05Jy',usemask='auto-multithresh',vptable=joint_vp,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.5,noisethreshold=5.0,minbeamfrac=0.3,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.65,verbose=True,startmodel='')
"""
for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

# make an SD image in Jy/pix on that grid-
sd_model = combut.make_clnMod_fromImg(sd_img_fixed,INT_imagename+'.image',pb_map=INT_imagename+'.pb',tag='coreGrid')

INT_imagename = core_ms + '.autoDev2.final.sdmod'
rmtables(INT_imagename+"*")
#delmod(vis=core_ms+'.ms')
tclean(vis=core_ms+'.ms',imagename=INT_imagename,niter=10000,cycleniter=1000,pblimit=0.3,phasecenter=phase_center,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.05Jy',usemask='auto-multithresh',vptable=joint_vp,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.5,noisethreshold=5.0,minbeamfrac=0.3,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.65,verbose=True,startmodel=sd_model)
for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)


INT_imagename = core_ms + '.simple.final'
rmtables(INT_imagename+"*")
#delmod(vis=core_ms+'.ms')
tclean(vis=core_ms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.3,phasecenter=phase_center,
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.05Jy',usemask='auto-multithresh',vptable=joint_vp,
       sidelobethreshold=3.5,noisethreshold=5.0,minbeamfrac=0.3,lownoisethreshold=2.5,negativethreshold=0.0,growiterations=50,smoothfactor=0.75,cyclefactor=0.65,verbose=True,startmodel='')
for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)


#sys.exit("you are here")

######## Joint imaging



#### CONCAT. in time order. get weights right.
infile=core_ms
infile2=sba_ms
#delmod(vis=infile2+'.ms')
#delmod(vis=infile+'.ms')
newms='joint_30dor.ngvla.revC_new'
# visweightscale = (6/18)**4
concat(vis=[infile+'.ms',infile2+'.ms'],concatvis=newms+'.ms',visweightscale=[1.0,0.0123])


# joint deconvolution

INT_imagename = newms+'.autoDev5b'
rmtables(INT_imagename+"*")
tclean(vis=newms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.3,phasecenter=phase_center,vptable=joint_vp,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=4.5,minbeamfrac=0.3,lownoisethreshold=3.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True)

tclean(vis=newms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.3,phasecenter=phase_center,vptable=joint_vp,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=3.0,minbeamfrac=0.3,lownoisethreshold=2.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True)


for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

[fthrd,fthrd_nopb] = combut.feather_one(sd_img_fixed,INT_imagename+'.image',INT_imagename+'.pb')
created_images.append(fthrd)
created_images.append(fthrd_nopb)

sd_model = combut.make_clnMod_fromImg(sd_img_fixed,INT_imagename+'.image',pb_map=INT_imagename+'.pb',tag='jointGrid')
#created_images.append(sd_model)

INT_imagename = newms+'.sdmod.autoDev5b'
rmtables(INT_imagename+"*")
tclean(vis=newms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.3,phasecenter=phase_center,vptable=joint_vp,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=4.5,minbeamfrac=0.3,lownoisethreshold=3.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True,startmodel=sd_model)

tclean(vis=newms+'.ms',imagename=INT_imagename,niter=20000,cycleniter=1000,pblimit=0.3,phasecenter=phase_center,vptable=joint_vp,deconvolver='multiscale',
       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1960,1960],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=3.0,minbeamfrac=0.3,lownoisethreshold=2.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True)

for mm in ['.image','.residual','.pb','.image.pbcor']:
    created_images.append(INT_imagename+mm)

[fthrd,fthrd_nopb] = combut.feather_one(sd_img_fixed,INT_imagename+'.image',INT_imagename+'.pb')
created_images.append(fthrd)
created_images.append(fthrd_nopb)

print(" **** Manifest of images created: ")
print(created_images)

# filter out '.pb' and '.residual' maps before calculating fidelity - 
best_images = []
for ii in created_images:
    if not(re.match(".*\.pb$",ii) or re.match(".*\.residual$",ii) or re.match(".*\.weight$",ii)):
        best_images.append(ii)

print(" **** Selected Images to calculate fidelity on: ")
print(best_images)

image_stats={}
# calculate fidelity - 
for mm in best_images:
    print("*********")
    print(mm)
    combut.calc_fidelity(mm,truth_image,INT_imagename+'.pb',outfile=mm+'.fiderr',pb_thresh=0.5)
    image_stats[mm]=imstat(imagename=mm,region='bigBox.reg')

######
# dec2020 results

"""

*************************************
image:  joint_30dor.ngvla.revC_new.autoDev5b.image.pbcor reference image: ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel
flux = 251 Jy
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.7257252947768178 -0.5102529731874439 0.3975533982624958 0.3969359756296168 0.8113437416241154
 ALMA:  1.1135284883833505 1.1137705402181433 1.1476313645633005 1.4328706817396908
*************************************


*************************************
image:  joint_30dor.ngvla.revC_new.sdmod.autoDev5b.image.pbcor reference image: ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel
flux = 1459 Jy
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.8286123961251899 0.8394931292509022 0.8155709237050999 0.8309822228491294 0.9692282626100348
 ALMA:  2.967037813136745 2.9679413771578593 3.215420984649042 4.628052506942166
*************************************

*************************************
image:  joint_30dor.ngvla.revC_new.autoDev5b.image.feather.pbcor reference image: ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel
flux=1214 Jy
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.8942536129765122 0.9010309715821835 0.9042620048800175 0.9022298548986262 0.9747270681962645
 ALMA:  4.178891924460086 4.181895751271701 4.980146385087764 10.75079515273022
*************************************

*************************************
image:  joint_30dor.ngvla.revC_new.sdmod.autoDev5b.image.feather.pbcor reference image: ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel
flux = 1259 Jy
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.8588630338374486 0.9201407798554713 0.9183649652028864 0.9188299176866213 0.9779053534119185
 ALMA:  4.408335523512674 4.410538301112445 5.356038055311191 12.581501794396852
*************************************


*************************************
image:  ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.simple.final.image.pbcor reference image: ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel
flux = 19 Jy
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.25146646658380667 -14.236070468873223 0.0615812329720925 0.061968964978787344 0.37381323472961975
 ALMA:  0.9935934976596343 0.9934942493730134 0.996639818990035 1.0146031001008615
*************************************

*************************************
image:  ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.autoDev2.final.image.pbcor reference image: ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel
flux = 46 Jy
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.31698428355403563 -7.959443636448599 0.10040321051078471 0.10110323170757196 0.5176073738610003
 ALMA:  0.9961594263951824 0.9960710822424068 1.0012757310403084 1.022470578629
*************************************

*************************************
image:  ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.autoDev2.final.sdmod.image.pbcor reference image: ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel
flux = 1276 
Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
0.6510601417435375 0.7626533645503266 0.7856442118233 0.7861394157609657 0.9377768336910302
 ALMA:  4.5494691228294375 4.549144149024705 4.3428119261421285 4.914217492376411
*************************************



"""
#############################################################

#tclean(vis=newms+'.ms',imagename=newms+'sdmod.autoDev5.short',niter=20000,cycleniter=200,pblimit=0.15,phasecenter=phase_center,vptable=vp_joint,deconvolver='multiscale', 
#       interactive=False,pbcor=True,cell='0.25arcsec',imsize=[1440,1440],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.02Jy',usemask='auto-multithresh',robust=2.0,
#       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=4.5,minbeamfrac=0.3,lownoisethreshold=3.0,negativethreshold=0.0,cyclefactor=0.85,verbose=True,
#       startmodel='sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image_plusTpFixed.pbcor.regrid.jyPix')
# this gives warnings like
# 2019-09-25 20:46:03     WARN    task_tclean::SDAlgorithmMSClean::takeOneStep (file ../../synthesis/ImagerObjects/SDAlgorithmMSClean.cc, line 182)       MSClean minor cycle stopped at large scale negative or diverging
#

#### ^^^^ these blow goats. 71%-ish fidelity. the old was better. make sure i can reproduce it- but, use the SBA model.

#tclean(vis=newms+'.ms',imagename=newms+'.sdmod.autoDev4',niter=10000,cycleniter=1000,pblimit=0.05,phasecenter=phase_center,vptable=vp_joint,deconvolver='multiscale',
#       interactive=True,pbcor=True,cell='0.25arcsec',imsize=[1440,1440],gridder='mosaic',uvtaper='2arcsec',weighting='natural',threshold='0.01Jy',usemask='auto-multithresh',robust=2.0,
#       scales=[0,7,35],smallscalebias=0.55,sidelobethreshold=3.0,noisethreshold=4.5,minbeamfrac=0.3,lownoisethreshold=2.5,negativethreshold=0.0,cyclefactor=0.65,verbose=True,
#       startmodel='sba_30dor_new.ngvla-sba-revC.autoDev5.sdmod.image_plusTpFixed.pbcor.regrid.jyPix')

#       startmodel='sd_30dor/sd_30dor.ngvla-sd.sdbetter.tp.fixed.regrid.jyPix')


###################################### OLD STUFF BELOW vvvvvvvvvvvvvvvvv

#sd_map = "sd_30dor.ngvla-sd.sdbetter.tp.fixed"
#int_map = "joint_30dor.ngvla.revC_newsdmod.autoDev5.image"
#int_pb = "joint_30dor.ngvla.revC_newsdmod.autoDev5.pb"

#outfile=int_map+'_plusTpFixed'
#rmtables(sd_map+".TMP.intGrid.intPb")
#imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
#immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
#feather(imagename=outfile+'.image',highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
#immath(imagename=[outfile+'.image',int_pb],expr='IM0/IM1',outfile=outfile+'.pbcor')

#int_map = "joint_30dor.ngvla.revC_newsdmod.autoDev5.short.image"
#int_pb = "joint_30dor.ngvla.revC_newsdmod.autoDev5.short.pb"

#outfile=int_map+'_plusTpFixed'
#rmtables(sd_map+".TMP.intGrid.intPb")
#imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
#immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
#feather(imagename=outfile+'.image',highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
#immath(imagename=[outfile+'.image',int_pb],expr='IM0/IM1',outfile=outfile+'.pbcor')

#int_map = "joint_30dor.ngvla.revC_new.sdmod.autoDev4.image"
#int_pb = "joint_30dor.ngvla.revC_new.sdmod.autoDev4.pb"

#outfile=int_map+'_plusTpFixed'
#rmtables(sd_map+".TMP.intGrid.intPb")
#imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
#immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
#feather(imagename=outfile+'.image',highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
#immath(imagename=[outfile+'.image',int_pb],expr='IM0/IM1',outfile=outfile+'.pbcor')


#
#************************************
#image:  joint_30dor.ngvla.revC_newsdmod.autoDev5.image_plusTpFixed.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.294794645125 0.71531413582 0.697083247397 0.712266399014 0.902447525773
# ALMA:  3.85476957918 3.86191486271 4.43266349343 5.2049278354
#*************************************
#

#
#*************************************
#image:  joint_30dor.ngvla.revC_newsdmod.autoDev5.image_plusTpFixed.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.266753647886 0.709584150426 0.680516392215 0.69867583429 0.890404703933
# ALMA:  3.2180902161 3.2215818793 3.59824287071 4.53735693492
#*************************************
#

#
#*************************************
#image:  joint_30dor.ngvla.revC_newsdmod.autoDev5.short.image_plusTpFixed.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.165329722998 0.732003958425 0.71550875123 0.717818424074 0.900543242697
# ALMA:  4.2766912723 4.28479812704 5.02046741896 6.69584605351
#*************************************

#
#*************************************
#image:  joint_30dor.ngvla.revC_newsdmod.autoDev5.short.image_plusTpFixed.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.134804558526 0.725638209242 0.698794369904 0.703615161782 0.888133051158
# ALMA:  3.550301165 3.55388272719 4.02737790075 5.61521261548
#*************************************
#

#
#*************************************
#image:  joint_30dor.ngvla.revC_new.sdmod.autoDev4.image_plusTpFixed.pbcor reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.465181595484 0.772668644522 0.75693406432 0.76392192083 0.922017497629
# ALMA:  3.84108703226 3.84788504273 4.38814869324 6.04903188411
#*************************************
#

#
#*************************************
#image:  joint_30dor.ngvla.revC_new.sdmod.autoDev4.image_plusTpFixed.image reference image: sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel
#Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff 
#0.487485191345 0.778213991512 0.770651731452 0.779354952019 0.934534614057
# ALMA:  4.19479603766 4.20480369445 4.91444700603 7.08593180965
#*************************************
#

