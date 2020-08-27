
#################################
#
# Utilities to facilitate multi-array and single dish data combination
#  developed for ngVLA SBA design evaluation
#  Only used thus far with continuum images (no cubes)
#
# Brian Mason (NRAO)  
#  v1 - Sept 2019
#     - Jan 2020 - add peak finding, aperture flux comparison
#  v2 - Aug 2020 - improve and fix aperture flux routine
#               (circular regions; add an outer annulus option;
#                fix bug causing the master image to be overwritten at times)
#
# NOTE: do not do this:
# import combo_utils as cu
#  it will generate a global namespace conflict in CASA
#  call it something sillier and more distinctive.
#
#################################

# CASA stuff-
from taskinit import *
from imhead_cli import imhead_cli as imhead
from immath_cli import immath_cli as immath
from imregrid_cli import imregrid_cli as imregrid
from rmtables_cli import rmtables_cli as rmtables
from feather_cli import feather_cli as feather

# Python stuff-
import analysisUtils as au
import numpy as np
import pylab as pl
from scipy.ndimage.filters import maximum_filter

def fix_image_calib(sd_image,sd_img_fixed,cal_factor=1.0,beam_factor=1.0):
    """
    Rescale image brightness (cal_factor) and BMAJ,BMIN (beam_factor)
    in a CASA image sd_image (any CASA image). output file to 
    sd_img_fixed.
    """

    immath(imagename=[sd_image],expr='IM0*'+str(cal_factor),outfile=sd_img_fixed)
    hdr = imhead(imagename=sd_image,mode='summary')
    bmaj_str = str(hdr['restoringbeam']['major']['value'] * beam_factor)+hdr['restoringbeam']['major']['unit']
    bmin_str = str(hdr['restoringbeam']['minor']['value'] * beam_factor)+hdr['restoringbeam']['minor']['unit']
    # you have to do BMIN first
    imhead(sd_img_fixed,mode='put',hdkey='BMIN',hdvalue=bmin_str)
    imhead(sd_img_fixed,mode='put',hdkey='BMAJ',hdvalue=bmaj_str)

    return sd_img_fixed

def convert_angle(angle,to_unit='arcsec'):

    from_unit = angle['unit']

    # special case: no conversion
    if (from_unit == to_unit):
        new_angle = {'unit': angle['unit'], 'value': angle['value']}
        return new_angle

    # create variable from_angle which will be in radians
    #  if we can (or raise exception)
    if (from_unit == 'rad'):
        from_angle = angle['value']
    elif (from_unit == 'deg'):
        from_angle = angle['value'] / np.degrees(1)
    elif (from_unit == 'arcmin'):
        from_angle = angle['value'] / (np.degrees(1)*60.0)
    elif (from_unit == 'arcsec'):
        from_angle = angle['value'] / (np.degrees(1) * 3600.0)
    else:
        print " *** ERROR: Unrecognized unit in convert_angle "+angle['unit']
        raise Exception("Unknown unit.")
    if (to_unit == 'rad'):
        to_angle = from_angle
    elif (to_unit == 'deg'):
        to_angle = from_angle * np.degrees(1)
    elif (to_unit == 'arcsec'):
        to_angle = from_angle * np.degrees(1) * 3600.0
    elif (to_unit == 'arcmin'): 
        to_angle = from_angle * np.degrees(1) * 60.0
    else:
        print " *** ERROR: Unrecognized unit in convert_angle "+ to_unit
        raise Exception("Unknown unit.")

    new_angle = {'unit': to_unit, 'value': to_angle}
        
    return new_angle

def feather_one(sd_map,int_map,int_pb,tag=''):
    """ 
    Feather together a single dish map sd_map with an interferometric
    map int_map, with primary beams probably handled.

    returns the names of the pbcorrected and not pbcorrected images.
    """

    outfile=int_map+tag+'.feather'
    outfile_pbcord=outfile+'.pbcor'
    outfile_uncorr=outfile
    #rmtables(outfile_uncorr)
    #rmtables(outfile_pbcord)
    rmtables(sd_map+".TMP.intGrid.intPb")
    imregrid(imagename=sd_map,template=int_map,output=sd_map+".TMP.intGrid",overwrite=True)
    immath(imagename=[sd_map+".TMP.intGrid",int_pb],expr='IM0*IM1',outfile=sd_map+".TMP.intGrid.intPb")
    feather(imagename=outfile_uncorr,highres=int_map,lowres=sd_map+".TMP.intGrid.intPb")
    immath(imagename=[outfile_uncorr,int_pb],expr='IM0/IM1',outfile=outfile_pbcord)

    # clean up after self
    rmtables(sd_map+".TMP.intGrid.intPb")
    rmtables(sd_map+".TMP.intGrid")

    return [outfile_pbcord,outfile_uncorr]


def make_clnMod_fromImg(sd_map,int_map,tag='',clean_up=True):
    """ 

    Take sd_map and regrid it into pixel coordinates of int_map, converting from
      Jy/bm into Jy/pix.

    Both input images are CASA images presumed to have surface brightess
     units of Jy/bm

    tag is an optional string that will be included in the outpu file name

    Returns the name of the output file.

    Note: sd_map and int_map can be of any provenance as long as the SB units
    are Jy/bm. Results have only been validated for the case that the sd_map
    pixels are larger than the int_map pixels however.

    """

    regridded_sd_map = sd_map +'.TMP.regrid'
    out_sd_map = sd_map +tag+'.regrid.jyPix'

    imregrid(imagename=sd_map,template=int_map,output=regridded_sd_map,overwrite=True)
    sd_header = imhead(regridded_sd_map)
    int_header = imhead(int_map)

    rad_to_arcsec = 206264.81
    twopi_over_eightLnTwo = 1.133

    flux_conversion = (rad_to_arcsec*np.abs(sd_header['incr'][0]))*(rad_to_arcsec*np.abs(sd_header['incr'][1])) / (twopi_over_eightLnTwo * sd_header['restoringbeam']['major']['value'] * sd_header['restoringbeam']['minor']['value'])

    print "===================="
    print "THESE SHOULD BE ARCSEC:"+sd_header['restoringbeam']['major']['unit']+" "+sd_header['restoringbeam']['minor']['unit']
    print "THESE SHOULD BE RADIANS: "+sd_header['axisunits'][0]+" "+sd_header['axisunits'][1]
    print "if not the unit conversions were wrong...."
    print "===================="

    flux_string = "(IM0 * %f)" % flux_conversion

    rmtables(out_sd_map)
    immath(imagename=regridded_sd_map,expr=flux_string,outfile=out_sd_map,mode='evalexpr')
    new_unit = 'Jy/pixel'
    imhead(imagename=out_sd_map,mode='put',hdkey='BUNIT',hdvalue=new_unit)

    # clean up after self-
    rmtables(regridded_sd_map)

    return out_sd_map

def calc_fidelity(inimg,refimg,pbimg='',psfimg='',fudge_factor=1.0,scale_factor=1.0,pb_thresh=0.25,clean_up=True,outfile=''):
    """Calculate fidelity of inimg with reference to refimg. 

    Use Gaussian PSF with parameters described in inimg header, unless
    an explicit psfimg is provided.

    If a primary beam image (pbimg) is provided, use it to restrict
    the area over which the fidelity is calculated, using pb_thresh as
    the lower limit (relative to max(pbimg)).

    clean_up controls whether intermediate files created in the
    process are removed or not (all contain the string TMP). These can
    be useful for sanity checking, but proper behavior is not
    guaranteed if any are present already when the routine is called.

    outfile specifies the file-name root for a fidelity image and a fractional error
    image that will be created.
       --- ****a pbimg is required to creat the outfile
       
    inimg, refimg, [psfimg], and [pbimg] should be CASA images. outfile is a CASA image.
    All input images should have the same axes and axis order.

    ***pbimg, if provided, should furthermore have the same pixel coordinates as inimg
       (Cell size, npix, coordinate reference pixel, etc)***

    ***all input images should have the same number and ordering of axes!!!

    fudge_factor multiples the beamwidth obtained from the input image, before 
      convolving refimg for comparison
    scale_factor multiplies the inimg pixel values (i.e. it recalibrates them)
      --> use these reluctantly and only if you know what you are doing

    OUTPUTS:  a dictionary containing

      f1 = 1 - max(abs(inimg-refimg)) / max(refimg) - 'classic' definition

      f2 = 1 - sum( refimg .* abs(inimg-refimg) ) / sum( refimg .* inimg)
         --> this is a somewhat poorly behaved fidelity definition that was evaluated for ngVLA
              (appearing in the draft ngVLA science requirements, May 2019)
         --> it is equivalent to a weighted sum of fractional errors, with the fraction taken with
               respect to the formed image inimg and the weight being inimg*refimg

      f2b = 1 - sum( refimg .* abs(inimg-refimg) ) / sum( refimg .* refimg)
         --> this is the original (ngVLA science requirememts, Nov. 2017) and better-behaved 
               ngVLA fidelity definition, with the fraction taken with respect to the model (refimg),
               and the weight being refimg^2

      f3 = 1 - sum( beta .* abs(inimg-refimg) ) / sum( beta.^2 )
         --> this is the current ngVLA fidelity definition that has been adopted, where
                beta_i = max(abs(inimg_i,),abs(refimg_i))

      In all of the above "i" is a pixel index, .* and .^ are element- (pixel-) wise operations,
       and sums are over pixels

      Various ALMA-adopted fidelity measures are also reported, and the correlation coefficient


    HISTORY: 
      August/September 2019 - B. Mason (nrao) - original version

    """

    ia=iatool()

    ia.open(inimg)
    # average over the stokes axis to get it down to 3 axes which is what our other one has
    imvals=np.squeeze(ia.getchunk()) * scale_factor
    img_cs = ia.coordsys()
    # how to trim the freq axis--
    #img_shape = (ia.shape())[0:3]
    img_shape = ia.shape()
    ia.close()
    # get beam info
    hdr = imhead(imagename=inimg,mode='summary')
    bmaj_str = str(hdr['restoringbeam']['major']['value'] * fudge_factor)+hdr['restoringbeam']['major']['unit']
    bmin_str = str(hdr['restoringbeam']['minor']['value'] * fudge_factor)+hdr['restoringbeam']['minor']['unit']
    bpa_str =  str(hdr['restoringbeam']['positionangle']['value'])+hdr['restoringbeam']['positionangle']['unit']

    # i should probably also be setting the beam * fudge_factor in the *header* of the input image

    if len(pbimg) > 0:
        ia.open(pbimg)
        pbvals=np.squeeze(ia.getchunk())
        pbvals /= np.max(pbvals)
        pbvals = np.where( pbvals < pb_thresh, 0.0, pbvals)
        #good_pb_ind=np.where( pbvals >= pb_thresh)
        #bad_pb_ind=np.where( pbvals < pb_thresh)
        #pbvals[good_pb_ind] = 1.0
        #if bad_pb_ind[0]:
        #    pbvals[bad_pb_ind] = 0.0
    else:
        pbvals = imvals*0.0 + 1.0
        #good_pb_ind = np.where(pbvals)
        #bad_pb_ind = [np.array([])]

    ##

    ##############
    # open, smooth, and regrid reference image
    #

    smo_ref_img = refimg+'.TMP.smo'

    # if given a psf image, use that for the convolution. need to regrid onto input
    #   model coordinate system first. this is mostly relevant for the single dish
    #   if the beam isn't very gaussian (as is the case for alma sim tp)
    if len(psfimg) > 0:
        # consider testing and fixing the case the reference image isn't jy/pix
        ia.open(refimg)
        ref_cs=ia.coordsys()
        ref_shape=ia.shape()
        ia.close()
        ia.open(psfimg)
        psf_reg_im=ia.regrid(csys=ref_cs.torecord(),shape=ref_shape,outfile=psfimg+'.TMP.regrid',overwrite=True,axes=[0,1])
        psf_reg_im.done()
        ia.close()
        ia.open(refimg)
        # default of scale= -1.0 autoscales the PSF to have unit area, which preserves "flux" in units of the input map
        #  scale=1.0 sets the PSF to have unit *peak*, which results in flux per beam in the output 
        ref_convd_im=ia.convolve(outfile=smo_ref_img,kernel=psfimg+'.TMP.regrid',overwrite=True,scale=1.0)
        ref_convd_im.setbrightnessunit('Jy/beam')
        ref_convd_im.done()
        ia.close()
        if clean_up:
            rmtables(psfimg+'.TMP.regrid')
    else:
        # consider testing and fixing the case the reference image isn't jy/pix
        ia.open(refimg)    
        im2=ia.convolve2d(outfile=smo_ref_img,axes=[0,1],major=bmaj_str,minor=bmin_str,pa=bpa_str,overwrite=True)
        im2.done()
        ia.close()

    smo_ref_img_regridded = smo_ref_img+'.TMP.regrid'
    ia.open(smo_ref_img)
    im2=ia.regrid(csys=img_cs.torecord(),shape=img_shape,outfile=smo_ref_img_regridded,overwrite=True,axes=[0,1])
    refvals=np.squeeze(im2.getchunk())
    im2.done()
    ia.close()

    ia.open(smo_ref_img_regridded)
    refvals=np.squeeze(ia.getchunk())
    ia.close()

    # set all pixels to zero where the PB is low - to avoid NaN's
    imvals = np.where(pbvals,imvals,0.0)
    refvals = np.where(pbvals,refvals,0.0)
    #if len(bad_pb_ind) > 0:
        #imvals[bad_pb_ind] = 0.0
        #refvals[bad_pb_ind] = 0.0

    deltas=(imvals-refvals).flatten()
    # put both image and model values in one array to calculate Beta for F_3- 
    allvals = np.array( [np.abs(imvals.flatten()),np.abs(refvals.flatten())])
    # the max of (image_pix_i,model_pix_i), in one flat array of length nixels
    maxvals = allvals.max(axis=0)

    # carilli definition. rosero eq1
    f_eq1 = 1.0 - np.max(np.abs(deltas))/np.max(refvals)
    f_eq2 = 1.0 - (refvals.flatten() * np.abs(deltas)).sum() / (refvals * imvals).sum()
    f_eq2b = 1.0 - (refvals.flatten() * np.abs(deltas)).sum() / (refvals * refvals).sum()
    #f_eq3 = 1.0 - (maxvals[gi] * np.abs(deltas[gi])).sum() / (maxvals[gi] * maxvals[gi]).sum()
    f_eq3 = 1.0 - (pbvals.flatten() * maxvals * np.abs(deltas)).sum() / (pbvals.flatten() * maxvals * maxvals).sum()

    # if an output image was requested, and a pbimg was given; make one.
    if ((len(outfile)>0) & (len(pbimg)>0)):
        weightfile= 'mypbweight.TMP.im'
        rmtables(weightfile)
        immath(imagename=[pbimg],mode='evalexpr',expr='ceil(IM0/max(IM0) - '+str(pb_thresh)+')',outfile=weightfile)
        betafile = 'mybeta.TMP.im'
        rmtables(betafile)
        immath(imagename=[inimg,smo_ref_img_regridded],mode='evalexpr',expr='iif(abs(IM0) > abs(IM1),abs(IM0),abs(IM1))',outfile=betafile)
        # 19sep19 - change to the actual F_3 contrib ie put abs() back in
        rmtables(outfile)
        print " Writing fidelity error image: "+outfile
        immath(imagename=[inimg,smo_ref_img_regridded,weightfile,betafile],expr='IM3*IM2*abs(IM0-IM1)/sum(IM3*IM3*IM2)',outfile=outfile)
        # 19sep19 - add fractional error (rel to beta) to output
        rmtables(outfile+'.frac')
        print " Writing fractional error image: "+outfile+'.frac'
        immath(imagename=[inimg,smo_ref_img_regridded,weightfile,betafile],expr='IM2*(IM0-IM1)/IM3',outfile=outfile+'.frac')
        if clean_up:
            rmtables(weightfile)
            rmtables(betafile)

    # pearson correlation coefficient evaluated above beta = 1% peak reference image
    gi=np.where( np.abs(maxvals) > 0.01 * np.abs(refvals.max()) )
    ii = imvals.flatten()
    mm = refvals.flatten()
    mm -= mm.min()
    # (x-mean(x)) * (y-mean(y)) / sigma_x / sigma_y
    cc = (ii[gi] - ii[gi].mean()) * (mm[gi] - mm[gi].mean()) / (np.std(ii[gi]) * np.std(mm[gi]))
    #cc = (ii[gi] - ii[gi].mean()) * (mm[gi] - mm[gi].mean()) / (np.std(mm[gi]))**2
    corco = cc.sum() / cc.shape[0]

    fa = np.abs(mm) / np.abs(mm - ii)
    fa_0p1 = np.median( fa[ (np.abs(ii) > 1e-3 * mm.max()) | (np.abs(mm) > 1e-3 * mm.max())  ])
    fa_1 = np.median( fa[ (np.abs(ii) > 1e-2 * mm.max()) | (np.abs(mm) > 1e-2 * mm.max())  ])
    fa_3 = np.median( fa[ (np.abs(ii) > 3e-2 * mm.max()) | (np.abs(mm) > 3e-2 * mm.max())  ])
    fa_10 = np.median( fa[ (np.abs(ii) > 1e-1 * mm.max()) | (np.abs(mm) > 1e-1 * mm.max()) ] )

    #gi2 = (np.abs(ii) > 1e-3 * mm.max()) | (np.abs(mm) > 1e-3 * mm.max())  

    print "*************************************"
    print 'image: ',inimg,'reference image:',refimg
    print "Eq1  / Eq2  / Eq2b  / Eq3 / corrCoeff "
    print f_eq1, f_eq2, f_eq2b, f_eq3,corco
    print ' ALMA: ',fa_0p1,fa_1,fa_3,fa_10
    print "*************************************"

    fidelity_results = {'f1': f_eq1, 'f2': f_eq2, 'f2b': f_eq2b, 'f3': f_eq3, 'falma': [fa_0p1, fa_1, fa_3, fa_10]}

    if clean_up:
        rmtables(smo_ref_img)
        rmtables(smo_ref_img_regridded)

    return fidelity_results

def jyBm2jyPix(in_image,out_image):
    """ 
    Blindly convert pixel values of in_image to Jy/pix, assuming they are Jy/bm.
    we check nothing and overwrite out_image so you best watch yourself.
    """

    rad_to_arcsec = 206264.81
    twopi_over_eightLnTwo = 1.133

    hdr=imhead(in_image)

    flux_conversion = (rad_to_arcsec*np.abs(hdr['incr'][0]))*(rad_to_arcsec*np.abs(hdr['incr'][1])) / (twopi_over_eightLnTwo * hdr['restoringbeam']['major']['value'] * hdr['restoringbeam']['minor']['value'])
    flux_string = "(IM0 * %f)" % flux_conversion

    rmtables(out_image)
    immath(imagename=in_image,expr=flux_string,outfile=out_image,mode='evalexpr')
    new_unit = 'Jy/pixel'
    imhead(imagename=out_image,mode='put',hdkey='BUNIT',hdvalue=new_unit)

    return 0

def sum_region_fluxes(imvals,peak_indices,radius=4.0):
    """
    sum pixels in regions around peak_indices
    regions are specified with a radius in pixels
    """
    fluxes = np.zeros(peak_indices.shape[0])
    x_flux = np.zeros(peak_indices.shape[0])
    y_flux = np.zeros(peak_indices.shape[0])
    pixcount = np.zeros(peak_indices.shape[0])
    # radius to extract in pixels - 
    rr = radius
    for k in range(fluxes.size):
        i_low = peak_indices[k][0] - np.round(rr)
        i_high = peak_indices[k][0] + np.round(rr)
        j_low = peak_indices[k][1] - np.round(rr)
        j_high = peak_indices[k][1] + np.round(rr)
        x_flux[k] = peak_indices[k][0]
        y_flux[k] = peak_indices[k][1]
        if i_low < 0:
            i_low = 0
        if i_high >= imvals.shape[0]:
            i_high = imvals.shape[0]-1
        if j_low < 0:
            j_low = 0
        if j_high >= imvals.shape[1]:
            j_high = imvals.shape[1]-1
        # bsm aug2020 - important bug fix ... declare this->
        subimage = np.array(imvals[i_low:i_high,j_low:j_high])
        ii = np.arange(0,i_high-i_low)
        jj = np.arange(0,j_high-j_low)
        ii.size
        jj.size
        subimage.size
        mask = ((ii[:,np.newaxis] - rr+1)**2 + (jj[np.newaxis,:] - rr+1)**2) > rr**2
        mask.size
        subimage[mask] = 0.0
        fluxes[k] = subimage.sum()
        pixcount[k] = np.sum(mask)
        #print k,fluxes[k]
    
    return fluxes,x_flux,y_flux,pixcount

def compare_fluxes(img1="./ngvla_30dor/ngvla_30dor.ngvla-core-revC.autoDev2.image",img2="./ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat",mask1="",mask2="",search_size = 2.0, thresh = 4.5, search_img=1,maxrad=50.0,minrad=1.0,radstep=1.0,doAnnuli=False,flipMask=False,dumbTest=False):
    """
    img1,img2: casa images to compare
    search_size: width of search region in beams (beam is takem from chosen search image)
    thresh: threshold for peak detection (robust sigma above median, default = 4.5)
    search_img: which image (1 or 2) to search for peaks (must have a beam)
    minrad,maxrad,radstep: start, stop, and delta radii for flux sums (in beams, again taken from search image)
    
    images are presumed to be on the same grid to start with (shape, pixel size) -- use imgregrid task
    and presumed to be in Jy/pixel (or otherwise same brightness unit per pixel) -- use combut.jyBm2jyPix()

    returns: flux(search), flux(other), peak_locations

    22jan2020 currently uses a square aperture (needs updating to circular) and hard wires the range of radii. return radii are in 
      pixels not arcsec.

    """

    #print "THRESH ", thresh
    if (search_img == 1):
        main_img = img1
        aux_img = img2
    else:
        main_img = img2
        aux_img = img1

    print " main image = ",main_img
        
    ia=iatool()

    # main image characteristics
    ia.open(main_img)
    # average over the stokes axis to get it down to 3 axes which is what our other one has
    main_img_cs = ia.coordsys()
    # how to trim the freq axis--
    #img_shape = (ia.shape())[0:3]
    main_img_shape = ia.shape()
    print main_img_shape
    imvals=np.squeeze(ia.getchunk())
    immask=np.squeeze(ia.getchunk(getmask=True))
    ia.close()
    # get beam info
    hdr = imhead(imagename=main_img,mode='summary')
    cd1 = imhead(imagename=main_img,mode='get',hdkey='cdelt1')
    cd1 = convert_angle(cd1,'arcsec')
    cd2 = imhead(imagename=main_img,mode='get',hdkey='cdelt2')
    cd2 = convert_angle(cd2,'arcsec')
    mean_cell = (np.abs(cd1['value']*cd2['value']))**0.5
    bmaj_str = str(hdr['restoringbeam']['major']['value'] )+hdr['restoringbeam']['major']['unit']
    bmin_str = str(hdr['restoringbeam']['minor']['value'] )+hdr['restoringbeam']['minor']['unit']
    bpa_str =  str(hdr['restoringbeam']['positionangle']['value'])+hdr['restoringbeam']['positionangle']['unit']
    bmaj =  convert_angle(hdr['restoringbeam']['major'],'arcsec')
    bmin =  convert_angle(hdr['restoringbeam']['minor'],'arcsec')
    beam_fwhm = ( bmaj['value'] * bmin['value'] )**0.5
    print "beam: "+ str(beam_fwhm) + " " + bmaj['unit']
    print "mean pix: "+ str(mean_cell) + " " + cd1['unit']

    # secondary image characteristics
    ia.open(aux_img)
    # average over the stokes axis to get it down to 3 axes which is what our other one has
    aux_img_cs = ia.coordsys()
    # how to trim the freq axis--
    #img_shape = (ia.shape())[0:3]
    aux_img_shape = ia.shape()
    print aux_img_shape
    auxvals=np.squeeze(ia.getchunk())
    auxmask=np.squeeze(ia.getchunk(getmask=True))
    ia.close()
    # get beam info
    aux_hdr = imhead(imagename=aux_img,mode='summary')
    #aux_bmaj_str = str(aux_hdr['restoringbeam']['major']['value'] * fudge_factor)+aux_hdr['restoringbeam']['major']['unit']
    #aux_bmin_str = str(aux_hdr['restoringbeam']['minor']['value'] * fudge_factor)+aux_hdr['restoringbeam']['minor']['unit']
    #aux_bpa_str =  str(aux_hdr['restoringbeam']['positionangle']['value'])+aux_hdr['restoringbeam']['positionangle']['unit']
    #aux_beam_fwhm = ( aux_hdr['restoringbeam']['major']['value'] * aux_hdr['restoringbeam']['minor']['value'] )**0.5
    #print beam_fwhm

    # create joint mask and zero out fluxes in either
    #  that are not in the joint mask
    totmask = immask & auxmask
    if flipMask:
        totmask = ~totmask
    imvals[~totmask] = 0.0
    auxvals[~totmask]=0.0

    if dumbTest:
        return imvals, auxvals, immask, auxmask

    # size of peak search region in pixels - 
    pix_search_size = search_size * (beam_fwhm / mean_cell)
    print "PIX SEARCH SIZE"
    print pix_search_size
    peak_indices = find_peaks(inimg=main_img,search_size = pix_search_size, thresh = thresh)    
    print "PIX INDICES"
    print peak_indices
    # radii in pixels
    radii = np.arange(minrad,maxrad,radstep)*beam_fwhm / mean_cell
    flux_vs_rad = np.array([])
    rms_vs_rad = np.array([])
    for i in radii:
        # these return an array of fluxes of individual regions
        mainInner,xx,yy,main_inner_count = sum_region_fluxes(imvals,peak_indices,radius=i)
        auxInner, dumx,dumy,aux_inner_count = sum_region_fluxes(auxvals,peak_indices,radius=i)
        if (doAnnuli):
            mainOuter,xx,yy,main_outer_count = sum_region_fluxes(imvals,peak_indices,radius= i+np.round(beam_fwhm/mean_cell))
            auxOuter, dumx,dumy,aux_outer_count = sum_region_fluxes(auxvals,peak_indices,radius=i+np.round(beam_fwhm/mean_cell))
            main_flux = 2.0* mainInner - mainOuter * main_inner_count / (2*main_inner_count - main_outer_count)
            aux_flux = 2.0* auxInner - auxOuter * aux_inner_count / (2*aux_inner_count - aux_outer_count)
        else:
            main_flux = mainInner
            aux_flux = auxInner
        # take the median and MAD of these
        flux_vs_rad = np.append(flux_vs_rad,np.median(main_flux/aux_flux))
        rms_vs_rad = np.append(rms_vs_rad,au.MAD(main_flux/aux_flux))

    return radii * mean_cell,flux_vs_rad,rms_vs_rad,xx,yy,imvals

def find_peaks(inimg="./ngvla_30dor/ngvla_30dor.ngvla-core-revC.skymodel.flat",search_size = 55, thresh = 4.5):
  """

   Find peaks in a CASA image. respects image mask. Heuristic: do a local max filter over a
   neighborhood of size search_size, and select those which are > 4.5 sigma (with sigma estimated
   as MAD of the image as a whole)

  """
  print "THRESH ", thresh
  ia=iatool()
  ia.open(inimg)
  imvals=np.squeeze(ia.getchunk())
  # somewhat confusingly, the mask is True where pixels are good, and False where bad.
  immask=np.squeeze(ia.getchunk(getmask=True))
  ia.close()
  print imvals.shape

  # compute some stats excluding NaN's - 
  #imvals2 = imvals[~np.isnan(imvals)]
  imvals2 = imvals[np.isfinite(imvals) & immask]
  pix_mean = imvals2.mean()
  #pix_sd = np.std(imvals2)
  print "MEDIAN"
  pix_median = np.median(imvals2)
  # note: by default this is normalized so that the std dev of
  #  a gaussian is 1.0
  pix_mad = au.MAD(imvals2)

  neighborhood = np.ones([np.round(search_size),np.round(search_size)],dtype=np.bool)
  print neighborhood.shape

  print "MAX Filter"
  is_local_max = maximum_filter(imvals,footprint=neighborhood)==imvals

  # this is a boolean array, same dims as imvals. True where you have a local max
  #  that's over the threshold specified here - 
  #highest_peaks = is_local_max & np.asarray(np.asarray(imvals > pix_median + 5.0*pix_mad))
  # so is this - 
  print is_local_max.shape
  highest_peaks = is_local_max & (imvals > (pix_median + thresh*pix_mad))
  print highest_peaks.shape,pix_median,thresh,pix_mad
  # this gives the indices where the value is TRUE - 
  peak_indices = np.argwhere(highest_peaks)
  print peak_indices.shape

  return peak_indices


def random_line(npoints = 100.0, slopeVarFrac = 0.5):
    """
    return a line with a random mean and slope, each normally distributed.
    the mean square of the lines is one ("unit variance" if you fix the mean at zero)
    variance by default is equally apportioned between the mean and the slope terms;
    tweak slopeVarFrac to change this. (the variance fraction actually goes as the square of that
    variable sorry)
    the mean of the lines is zero.
    """

    ivals = np.arange(npoints)
    this_traj = ( np.random.normal()*np.ones(npoints) + (2.0*slopeVarFrac) * 3**0.5 * np.random.normal() * (ivals - 0.5*(npoints-1.0)) / (0.5*(npoints-1.0)) ) / (1.0 + 4.0*slopeVarFrac**2)**0.5
    return this_traj

def corrupt_sd_ptg(inms,outms,rmsx=1.0,rmsy=1.0):
    """
    Randomly corrupt pointing data in MS
     corruptions are random normal in each dimension and
     uncorrelated between pointing locations. RMS is in arcseconds.

    This works on simulated total power data. not tested on other data.
    """

    tb.open(inms,nomodify=True)
    tb.copy(outms)
    tb.close()
    tb.done()

    tb.open(outms+'/POINTING',nomodify=False)
    direction = tb.getcol("DIRECTION")
    d0=direction[0,0,:]
    d1=direction[1,0,:]
    dd0 = np.random.normal(size=d0.shape)/206264.8*rmsx
    dd1 = np.random.normal(size=d0.shape)/206264.8*rmsy
    direction[0,0,:] = d0 + dd0
    direction[1,0,:] = d1 + dd1
    tb.putcol("DIRECTION",direction)
    tb.close()
    tb.done()

    return 0

def plotOneScan(myms,rms=5.6):
    """
    Select scans one by one and corrupt their pointing.

    works for simulated TP data. not tested for other types of data.
    
    RMS is in arcseconds
    """
    tb.open(myms+'/POINTING')
    direction = tb.getcol("DIRECTION")
    d0=direction[0,0,:] 
    d1=direction[1,0,:]
    dd0 = d0 - np.roll(d0,1)
    dd1 = d1 - np.roll(d1,1)
    tb.close()
    tb.done()
    xstep = np.abs(np.median(d0-np.roll(d0,1)))
    ystep = np.abs(np.median(d1-np.roll(d1,1)))
    if xstep > ystep:
        scans_in_x = True
        scan_bound_ind = np.argwhere(np.abs(dd0) > 4.0 * np.median(np.abs(dd0)))
    else:
        scans_in_x = False
        scan_bound_ind = np.argwhere(np.abs(dd1) > 4.0 * np.median(np.abs(dd1)))    
    # we're missing the end element -- 
    highind = d0.size-1
    if scan_bound_ind[-1] != highind:
        scan_bound_ind = np.append(scan_bound_ind,d0.size-1)
    if scan_bound_ind[0] != 0:
        scan_bound_ind = np.append([0],scan_bound_ind)
    for i in range(scan_bound_ind.size - 1):
        gi = np.arange(scan_bound_ind[i+1]-scan_bound_ind[i])+scan_bound_ind[i]
        npts = gi.size
        delta0 = random_line(npts)*rms/206264.8
        delta1 = random_line(npts)*rms/206265.8
        pl.plot(d0[gi]+delta0,d1[gi]+delta1)

    #pl.plot(d0*57.2958,d1*57.2958,'.')

    return d0,d1


def plotPointing(myms):
    """
    Plot pointing locations in MS
     plot is in degrees. return values are radians like the table.
    """
    tb.open(myms+'/POINTING')
    direction = tb.getcol("DIRECTION")
    tb.close()
    d0=direction[0,0,:] 
    d1=direction[1,0,:]
    pl.plot(d0*57.2958,d1*57.2958,'.')
    tb.close()
    tb.done()
    return d0,d1

# run as
#  casa -c comb_utils.py 
#   to run in standalone script mode
#
if __name__ == "__main__":

    image_list = ['joint_30dor.ngvla.revC_new.sdmod.autoDev4.image_plusTpFixed.pbcor']

    for inimg in image_list:
        calc_fidelity(inimg,'sba_30dor_new/sba_30dor_new.ngvla-sba-revC.skymodel',
                      pbimg='joint_30dor.ngvla.revC_newsdmod.autoDev5.pb',fudge_factor=1.0,scale_factor=1.0,
                      pb_thresh=0.25,clean_up=True)
        #,outfile=inimg+'.fiderr')

