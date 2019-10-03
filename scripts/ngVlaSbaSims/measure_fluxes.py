
fluxRegions = ['bigBox.reg']

# these are in jy/pix so don't have a 'flux' key
# 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.skymodel','sd_30dor_new/sd_30dor_new.ngvla-sd_loc.sd.sf7.tp.fixedsbaGrid.regrid.jyPix '

image_list = ['sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.image.pbcor','sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.image.feather.pbcor','sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.sdmod.image.pbcor','sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.sdmod.image.feather.pbcor','ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.autoDev2.final.image.pbcor','ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.simple.final.image.pbcor','joint_30dor.ngvla.revC_new.autoDev5.image.pbcor','joint_30dor.ngvla.revC_new.autoDev5.image.feather.pbcor','joint_30dor.ngvla.revC_new.sdmod.autoDev5.image.pbcor','joint_30dor.ngvla.revC_new.sdmod.autoDev5.image.feather.pbcor']

# 
for ii in image_list:
  for rr in fluxRegions:
      print " ***** "+ii+"  ****  "+rr
      z=imstat(imagename=ii,region=rr)
      print z['flux'][0]

# new sum is 1224.8 vs 1328.2

***** sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.image.pbcor  ****  bigBox.reg
238.882714559
 ***** sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.image.feather.pbcor  ****  bigBox.reg
1214.19652058
 ***** sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.sdmod.image.pbcor  ****  bigBox.reg
1436.76561644
 ***** sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.sdmod.image.feather.pbcor  ****  bigBox.reg
1232.34425732
 ***** ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.autoDev2.final.image.pbcor  ****  bigBox.reg
70.9614828213
 ***** ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.simple.final.image.pbcor  ****  bigBox.reg
19.7578115375
 ***** joint_30dor.ngvla.revC_new.autoDev5.image.pbcor  ****  bigBox.reg
307.398163174
 ***** joint_30dor.ngvla.revC_new.autoDev5.image.feather.pbcor  ****  bigBox.reg
1213.46542283
 ***** joint_30dor.ngvla.revC_new.sdmod.autoDev5.image.pbcor  ****  bigBox.reg
1457.04472107
 ***** joint_30dor.ngvla.revC_new.sdmod.autoDev5.image.feather.pbcor  ****  bigBox.reg
1236.36306768
