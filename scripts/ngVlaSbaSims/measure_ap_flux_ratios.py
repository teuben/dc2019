
#
# script to quantitatively measure flux in two integrated apertures as a function of
#   aperture radius.  very much a work in progress.
#
# TO DO: circular aperture. more programmatic validation. plot regions programmatically.
#   refactor previous code to use new bits. understand few % deviation from expectation
#   (as regards total fluxes). extract specific numbers and compare. don't hardwire radii,
#   plus return them in arcseconds.
# Check axes (0,1,2,3) and ensure all these bits play nicely with a frequency axis.
#  run on other datasets.
#

#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as plt

import combo_utils as combut

#############################################

# core
inimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.autoDev2.image"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rcore,fcore,efcore =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA only
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.image"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba,fsba,efsba =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA SDMOD
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.sdmod.image"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba2,fsba2,efsba2 =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA Feather
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.image.feather.image"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba3,fsba3,efsba3 =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA SDMOD Feather
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.sdmod.image.feather.image"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba4,fsba4,efsba4 =combut.compare_fluxes(inimg_jypix_regrid,refimg)

inimg="joint_30dor.ngvla.revC_new.sdmod.autoDev4.image_plusTpFixed.image"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rjoint,fjoint,efjoint =combut.compare_fluxes(inimg_jypix_regrid,refimg)

pl.close()
gi=range(500)
pl.plot(rjoint[gi]*0.21,fjoint[gi],label='JointSdmodFeather',color='k')
pl.plot([53,53],[0,0.71],color='k',linestyle='--')
pl.text(55,0.69,'JointSdmodFeather Bmin & Fidelity',color='k')
pl.plot([0,7*0.5*60],[0.71,0.71],color='k',linestyle=':')
pl.plot(rsba[gi]*0.21,fsba[gi],label='SBA',color='r')
pl.plot([55,55],[0,0.4],color='r',linestyle='--')
pl.text(57,0.3,'SBA Bmin & Fidelity',color='r')
pl.plot([0,6*0.5*60],[0.32,0.32],color='r',linestyle=':')
pl.plot(rcore[gi]*0.21,fcore[gi],label='Core Only',color='b')
pl.plot([19,19],[0,0.2],color='b',linestyle='--')
pl.text(20,0.1,'Core Bmin & Fidelity',color='b')
pl.plot([0,5*0.5*60],[0.14,0.14],color='b',linestyle=':')
pl.xlabel('Aperture Size [arcsec]')
pl.ylabel('Fraction of Flux; Fidelity')
pl.title('ngVLA Simulated Obs+Imaging Compared to Input (Truth)')
#pl.legend()
#pl.savefig("ngvlaFluxFracs.png")


pl.plot(rsba2[gi]*0.21,fsba2[gi],label='SBA SDmod',color='c')
pl.plot([56,56],[0,0.86],color='c',linestyle='--')
pl.text(57,0.8,'SBA SDmod Bmin & Fidelity',color='c')
pl.plot([0,6*0.5*60],[0.86,0.86],color='c',linestyle=':')

pl.plot(rsba3[gi]*0.21,fsba3[gi],label='SBA Feather',color='m')
pl.plot([53,53],[0,0.93],color='m',linestyle='--')
pl.text(57,0.9,'SBA Feather Fidelity',color='m')
pl.plot([0,6*0.5*60],[0.93,0.93],color='m',linestyle=':')

pl.plot(rsba4[gi]*0.21,fsba4[gi],label='SBA SDmod+Feather',color='g')
pl.plot([54,54],[0,0.95],color='g',linestyle='--')
pl.text(59,0.93,'SBA SDmod+Feather  Fidelity',color='g')
pl.plot([0,6*0.5*60],[0.95,0.95],color='g',linestyle=':')

pl.legend()

pl.savefig("ngvlaFluxFracsVtruth.png")

###############################################################

# pixel size in arcsec-
pxsz=0.25

# regrid TP
tpimg="sd_30dor/sd_30dor.ngvla-sd.sd.sf7.tp.fixed"
refimg="joint_30dor.ngvla.revC_new.sdmod.autoDev4.image_plusTpFixed.image"
tpimg_jypix=tpimg+'.TMP.jyPix'
combut.jyBm2jyPix(tpimg,tpimg_jypix)
tpimg_jypix_regrid=tpimg_jypix+'.TMP.regrid'
imregrid(imagename=tpimg_jypix,template=refimg,output=tpimg_jypix_regrid,overwrite=True)

# core
inimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC.autoDev2.image"
refimg=tpimg_jypix_regrid
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rcore,fcore,efcore =combut.compare_fluxes(inimg_jypix_regrid,refimg)

pl.plot(rcore*pxsz,fcore)

# SBA only
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.image"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba,fsba,efsba =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA SDMOD
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.sdmod.image"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba2,fsba2,efsba2 =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA Feather
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.image.feather.image"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba3,fsba3,efsba3 =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA SDMOD Feather
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC.autoDev5.final.sdmod.image.feather.image"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
#rsba4,fsba4,efsba4 =combut.compare_fluxes(inimg_jypix_regrid,refimg)

inimg="joint_30dor.ngvla.revC_new.sdmod.autoDev4.image_plusTpFixed.image"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rjoint,fjoint,efjoint =combut.compare_fluxes(inimg_jypix_regrid,refimg)

pl.close()
pl.plot(rjoint*pxsz,fjoint,label='JointSdmodFeather',color='k')
pl.plot([53,53],[0,0.71],color='k',linestyle='--')
pl.text(55,0.69,'JointSdmodFeather Bmin & Fidelity',color='k')
pl.plot([0,7*0.5*60],[0.71,0.71],color='k',linestyle=':')
pl.plot(rsba*pxsz,fsba,label='SBA',color='r')
pl.plot([55,55],[0,0.4],color='r',linestyle='--')
pl.text(57,0.3,'SBA Bmin & Fidelity',color='r')
pl.plot([0,6*0.5*60],[0.32,0.32],color='r',linestyle=':')
pl.plot(rcore*pxsz,fcore,label='Core Only',color='b')
pl.plot([19,19],[0,0.2],color='b',linestyle='--')
pl.text(20,0.1,'Core Bmin & Fidelity',color='b')
pl.plot([0,5*0.5*60],[0.14,0.14],color='b',linestyle=':')
pl.xlabel('Aperture Size [arcsec]')
pl.ylabel('Fraction of Flux; Fidelity')
pl.title('ngVLA Simulated Obs+Imaging Compared to TP')
#pl.legend()
#pl.savefig("ngvlaFluxFracs.png")


pl.plot(rsba2*pxsz,fsba2,label='SBA SDmod',color='c')
pl.plot([56,56],[0,0.86],color='c',linestyle='--')
pl.text(57,0.8,'SBA SDmod Bmin & Fidelity',color='c')
pl.plot([0,6*0.5*60],[0.86,0.86],color='c',linestyle=':')

pl.plot(rsba3*pxsz,fsba3,label='SBA Feather',color='m')
pl.plot([53,53],[0,0.93],color='m',linestyle='--')
pl.text(57,0.9,'SBA Feather Fidelity',color='m')
pl.plot([0,6*0.5*60],[0.93,0.93],color='m',linestyle=':')

pl.plot(rsba4*pxsz,fsba4,label='SBA SDMod+Feather',color='g')
pl.plot([54,54],[0,0.95],color='g',linestyle='--')
pl.text(59,0.93,'SBA SDmod+Feather  Fidelity',color='g')
pl.plot([0,6*0.5*60],[0.95,0.95],color='g',linestyle=':')

pl.legend()

pl.savefig("ngvlaFluxFracsVsTp.png")

