
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
inimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.autoDev2.final.image.pbcor"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
##combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
##imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rcore,fcore,efcore,xx,yy,imv =combut.compare_fluxes(inimg_jypix_regrid,refimg)


# JOINT SDMOD+Feather
inimg="joint_30dor.ngvla.revC_new.sdmod.autoDev5b.image.feather.pbcor"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
##combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
##imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rjoint,fjoint,efjoint,xx,yy,imv =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA only
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5b.final.image.pbcor"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba,fsba,efsba,xx,yy,imv =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA SDMOD
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5b.final.sdmod.image.pbcor"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba2,fsba2,efsba2,xx,yy,imv =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA Feather
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5b.final.image.feather.pbcor"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba3,fsba3,efsba3,xx,yy,imv =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# SBA SDMOD Feather
inimg="sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5b.final.sdmod.image.feather.pbcor"
refimg="ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel.flat"
inimg_jypix=inimg+'.TMP.jyPix'
combut.jyBm2jyPix(inimg,inimg_jypix)
inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
rsba4,fsba4,efsba4,xx,yy,imv =combut.compare_fluxes(inimg_jypix_regrid,refimg)

# code to sanity check aperture locations.
#   still needs to be  flipped after plotting
myFig,myAx = pl.subplots(1)

myAx.imshow(imv,origin='lower')
myAx.set_xticklabels([])
myAx.set_yticklabels([])
myAx.plot(yy,xx,"+")
pl.show()


# IF YOU EDIT THIS be sure to put the factor of two (r to D) in-
pl.close()
pl.plot(rjoint*2.0,fjoint,label='JointSdmodFeather',color='k')
#pl.plot(rjoint,fjoint+efjoint,color='k',linestyle=':')
#pl.plot(rjoint,fjoint-efjoint,color='k',linestyle=':')
#pl.plot([53,53],[0,1.1],color='k',linestyle='--')
#pl.text(55,0.92,'JointSdmodFeather Bmin & Fidelity',color='k')
#pl.plot([0,7*0.5*60],[0.71,0.71],color='k',linestyle=':')
pl.plot(rsba*2.0,fsba,label='SBA',color='r')
#pl.plot(rsba,fsba+efsba,color='r',linestyle=':')
#pl.plot(rsba,fsba-efsba,color='r',linestyle=':')
pl.plot([60.4,60.4],[0,0.4],color='r',linestyle='--')
pl.text(57,0.4,'SBA Bmin',color='r')
pl.plot([35.3,35.3],[0,0.5],color='r',linestyle='-.')
pl.text(21,0.42,'SBA LAS',color='r')

pl.plot([0,6*0.5*60],[0.32,0.32],color='r',linestyle=':')
pl.plot(rcore*2.0,fcore,label='Core Only',color='b')
#pl.plot(rcore,fcore+efcore,color='k',linestyle=':')
#pl.plot(rcore,fcore-efcore,color='k',linestyle=':')
pl.plot([21.8,21.8],[0,0.12],color='b',linestyle='--')
pl.text(20,0.1,'Core Bmin ',color='b')
pl.plot([18.6,18.6],[0,0.19],color='b',linestyle='-.')
pl.text(18,0.21,'Core LAS ',color='b')

#pl.plot([0,5*0.5*60],[0.14,0.14],color='b',linestyle=':')
pl.xlabel('Aperture Diameter [arcsec]')
pl.ylabel('Fraction of Flux Recovered')
pl.title('ngVLA Simulated Obs+Imaging Compared to Input (Truth)')
pl.legend(loc='center right')
pl.xlim([0,90])
pl.savefig("ngvlaFluxFracsV2b.png")
#pl.savefig("ngvlaFluxFracs.png")


pl.plot(rsba2,fsba2,label='SBA SDmod',color='c')
pl.plot([56,56],[0,0.86],color='c',linestyle='--')
pl.text(57,0.8,'SBA SDmod Bmin & Fidelity',color='c')
pl.plot([0,6*0.5*60],[0.86,0.86],color='c',linestyle=':')

pl.plot(rsba3,fsba3,label='SBA Feather',color='m')
pl.plot([53,53],[0,0.93],color='m',linestyle='--')
pl.text(57,0.9,'SBA Feather Fidelity',color='m')
pl.plot([0,6*0.5*60],[0.93,0.93],color='m',linestyle=':')

pl.plot(rsba4,fsba4,label='SBA SDmod+Feather',color='g')
pl.plot([54,54],[0,0.95],color='g',linestyle='--')
pl.text(59,0.93,'SBA SDmod+Feather  Fidelity',color='g')
pl.plot([0,6*0.5*60],[0.95,0.95],color='g',linestyle=':')

pl.legend()

pl.savefig("ngvlaFluxFracsVtruth.png")

###############################################################
"""
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

"""
