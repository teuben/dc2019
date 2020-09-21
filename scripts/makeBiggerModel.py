
# make a bigger version of skymodel-scaled to evaluate
#  flux loss from the reference box
#  and compare smoothed with simulated TP obs

inimage='skymodel-scaled.image'


# make a bigger image with the image in the  middle
image_header_dict = imregrid(inimage,template='get')
rmtables('testbig.im')
newdict=imregrid(imagename=inimage,output='testbig.im',replicate=True)
newdict['shap'][0]=8192
newdict['shap'][1]=8192
newdict['csys']['direction0']['crpix'][0]=4096.
newdict['csys']['direction0']['crpix'][1]=4096.
imregrid(imagename=inimage,output='testbig.im',template=newdict)

# zero out the mask (probably there's a better way)
makemask(mode='copy',inpimage='testbig.im',inpmask='testbig.im:mask0',output='testbig.im:bakmask')
ia.open('testbig.im')
ia.calcmask(mask="testbig.im > -1e14",name='mask0')
ia.done()

# smooth it
ia.open('testbig.im')    
im2=ia.convolve2d(outfile='testbig.smo57p06arcsec.im',axes=[0,1],major='57.06arcsec',minor='57.06arcsec',pa='0deg',overwrite=True)
im2.done()
ia.close()

#
# results (from viewer)
#  map   "whole map"    fluxbox.reg peak
# original    8659        6647      n/a
# large       8662        6647      n/a
# largeSmo    8662        6391     1864
#  SD         7191        6040     1860
#  SD 'fixed'             5711     1537
#
# take-aways
#
#  *the simulated TP map is in fact pretty good compared to
#     a simply constructed, should-be equivalent 
#    it is low by 5.5% in total flux. peak flux is good to < 1%
#
#  *the "fix" that worked on the ngVLA use case is deleterious here
#
#  *we lose about 3.9% of integrated flux to bleeding off the edge in the TP map
#    the appropriate point of comparison for our maps total flux is therefore
#    0.961 x (original map sum) = 6040 Jy
#
