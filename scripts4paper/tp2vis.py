# Taken from the Quick Array Combinations (QAC)
# https://github.com/teuben/QAC/blob/master/contrib/tp2vis.py
#
#
#
# A collection of TP2VIS functions to aid in combining ALMA
# Total Power and Visibilities in a Joint Deconvolution
#
# Authors: Peter Teuben & Jin Koda (hacked version)
#
# Public functions:
#    tp2vis_version()
#    tp2vis(imagename, msname, ptg, maxuv=10.0, rms=None, nvgrp=4, deconv=True)
#    tp2visbl(imagename, ptg, maxuv=10.0, nvgrp=4, deconv=True)
#    tp2viswt(mslist,mode='stat',value=0.5)
#    tp2vistweak(dirtyname,cleanname,pbcut=0.8)
#    tp2vispl(mslist,ampPlot=True,show=False)
#
# Helper functions:
#    tp2vis_version()
#    getptg()
#    axinorder()
#    arangeax()
#    guessarray()
#

import os, sys, shutil, re, time, datetime
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt

__version__ = "14-apr-2021 PJT/LMF"

try:
    # casa5
    from tasks import imhead, immath
    from taskinit import msmdtool, casalog, qatool, tbtool, mstool, iatool, vptool, smtool
    vp = vptool()
    msmd = msmdtool()
    ms = mstool()
    qa = qatool()
    tb = tbtool()
    ia = iatool()
    sm = smtool()
    print("tp2vis for CASA5 [%s]" % __version__)
except:
    try:
        # casa6
        from casatasks import imhead
        from casatasks import immath
        from casatasks import imstat

        from casatools import msmetadata as msmdtool
        from casatools import ms as mstool
        from casatools import vpmanager as vptool
        from casatools import quanta as qatool
        from casatools import table as tbtool
        from casatools import image as iatool
        from casatools import simulator as smtool
        from casatools import measures as metool

        vp = vptool()
        msmd = msmdtool()
        ms = mstool()
        qa = qatool()
        tb = tbtool()
        ia = iatool()
        sm = smtool()
        me = metool()
        print("tp2vis for CASA6 [%s]" % __version__)        
    except:
        print("WARNING: tp2vis will not function")


## ===========================================
## Global parameters: observatory & telescopes
## ===========================================

# Following assumes uniform, non-heterogeneous, dish size
t2v_arrays = {}

# ALMA 12m array parameters
apara = {'observatory':'ALMA',                  # observatory name
         'antList':    ['DA','DV','A00'],       # list of ant names (DA##, DV##, A##)    PM## also possible
         'dish':        12.0,                   # dish diam [meters]
         'fwhm100':     65.2,                   # fwhm@100GHz [56.5"@115.2GHz]
         'maxRad':     999.0}                   # cutoff rad of FoV [arcsec]
t2v_arrays['ALMA12'] = apara.copy()

# ALMA 7m
apara = {'observatory':'ALMA',
         'antList':    ['CM','A00'],            # CM##  (A## are from simobserve)
         'dish':         7.0,
         'fwhm100':    105.0,                   # fwhm@100GHz [35"@300GHz]
         'maxRad':     999.0}
t2v_arrays['ALMA07'] = apara.copy()

# ALMA TP [to deal with single-dish TP cube]
apara = {'observatory':'ALMA',
         'antList':    ['TP'],
         'dish':        12.0,
#        'fwhm100':     65.2,                   # fwhm@100GHz [56.5"@115.2GHz]
         'fwhm100':     58.3,                   # fwhm@100GHz [before SF conv]
         'maxRad':     999.0}
t2v_arrays['ALMATP'] = apara.copy()

# VIRTUAL TP2VIS array [for TP visibilities]
# see also qac_vp()
use_vp = False
if use_vp:
    apara = {'observatory':'VIRTUAL',           # a primary beam of 
             'antList':    ['VIRTUAL'],         # virtual interferometer
             'dish':        12.0,               # should be defined here.
             'fwhm100':     65.2,
#             'fwhm100':     58.3,
             'maxRad':     150.0}
    vp.reset()                                  # reset vpmanager
    vp.setpbgauss(telescope='OTHER',
                  othertelescope=apara['antList'][0],# set PB of VI in vpmanager
                  halfwidth=str(apara['fwhm100'])+'arcsec',
                  maxrad=str(apara['maxRad'])+'arcsec',
                  reffreq='100.0GHz',
                  dopb=True)
    # antnames='DV00' etc.
    vp.summarizevps()
else:                                           # without vpmanager working,
    apara = {'observatory':'ALMA',              # use ALMA for now
             'antList':    ['ALMA'],            # experiment with 'DV01' (an Airy function)
             'dish':        12.0,
#             'fwhm100':     65.2,
             'fwhm100':     58.3,
             'maxRad':     999.0}
t2v_arrays['VIRTUAL']    = apara.copy()

# softer dish sampling instead of the VIRTUAL dish size
dish3 = None

# see also qac_vp()
use_schwab = False


## =================
## Support functions
## =================
    
def tp2vis_version():
    print("tp2vis: %s" % __version__)

   
def axinorder(image):
    """
        Ensure we have the image in RA-DEC-POL-FREQ axes order.
        Helper function for tp2vis()
    """
    ia.open(image)
    h0 = ia.summary()
    ia.done()
    axname = h0['axisnames']
    print("AXIS NAMES:",axname)
    print("AXIS SHAPES:",list(h0['shape']))

    order = ''
    for ax in ['Right Ascension','Declination','Stokes','Frequency']:
        if not ax in axname:
            raise Exception("ERROR: No %s axis in %s" % (ax,image))
        else:
            iax   = list(axname).index(ax)
            order = order + '%1d' % (iax)

    if order == '0123':
        return True
    else:
        return False

def arangeax(image):
    """
        Re-arrange axes and make a RA-DEC-POL-FREQ cube. assume
        axinorder() is already run and 4 axes exist in order.
        Helper function for tp2vis()
        input:   image
        output:  temporary image name
    """

    dd = ''.join(re.findall('[0-9]',str(datetime.datetime.now())))
    imageout = 'tmp_arangeax_' + dd + '.im'
    os.system('rm -rf %s' % imageout)
    ia.open(image)
    h0 = ia.summary()
    axname = h0['axisnames']

    order = ''
    for ax in ['Right Ascension','Declination','Stokes','Frequency']:
        if ax in axname:
            iax   = list(axname).index(ax)
            order = order + '%1d' % (iax)
    if len(order) == 4:                         # all axes exist
        # on older CASA before 5.0 you will loose beam and
        # object name (bugs.txt #017)
        print("transpose order=%s" % order)
        ia2 = ia.transpose(outfile=imageout,order=order)
        ia2.done()
        ia.done()
        print("Written transposed ",imageout)
    else:
        print("bad transpose order=%d" % order)
        return None

    return imageout


def getptg(pfile):
    """ get the ptg's (CASA pointings) from a ptg file into a list                                                            
    'J2000 19h00m00.00000 -030d00m00.000000',...
            Helper function for tp2vis()
    """
    fp = open(pfile)
    lines = fp.readlines()
    fp.close()
    ptg = []
    for line in lines:
        if line[0] == '#': continue
        w = line.strip().split()
        ptg.append("%s %s %s" % (w[0],w[1],w[2]))
    return ptg

def guessarray(msfile):
    """ guess array name from MS
    this function uses the definitions of known arrays at the beginning
    of this code. See t2v_arrays[]
    msfile:    measurement set name
    Helper function for tp2vis()
    CAVEAT: analysis of the ANTENNA table is no guarentee that a dish
    is used in the correlations.
    """

    # Read antenna names in MS
    if not os.path.exists(msfile):              # make sure MS exists
        print("GUESSARRAY ERROR: no %s exists" % (msfile))
        return None
    tb.open(msfile+'/ANTENNA')                  # open MS
    antnames = tb.getcol('NAME')                # read ant names
    sizes = tb.getcol('DISH_DIAMETER')          # and dish sizes
    tb.close()                                  # close MS

    # Calculate likelihood of each array type
    probs = {}
    for iarray in list(t2v_arrays.keys()):      # loop over known arrays
        nant = 0                                # reset counter
        for iant in t2v_arrays[iarray]['antList']:  # how many ants of each
            nant += sum([(iant in x) for x in antnames]) # known array in MS
        frac = float(nant) / len(antnames)      # frac of ants of known array
        probs[iarray] = frac

    # Pick array and return
    mostlikelyarray = max(probs,key=probs.get)  # most likely array

    if antnames[0] == 'A00':                    # special case for simobserve()
        if sizes[0] ==  7.0: mostlikelyarray = 'ALMA07'
        if sizes[0] == 12.0: mostlikelyarray = 'ALMA12'
        print("guessarray %s %g -> %s" % (antnames[0],sizes[0],mostlikelyarray))

    return mostlikelyarray

def schwab_spheroidal(alpha,m,rscale,dist2d):
    """ return 2d kernel image of schwab's spheroidal function (Schwab 1984)
    
    CASA's sdimaging() uses the tabulated approx. of spheroidal function
    in Schwab 1984. Schwab's definition is different from the common
    definition as used in scipy. Within Schwab, the definition of
    key parameters (e.g., alpha, m) are not consistent in text and in table.
    Using the definition in the Schwab's table, the Schwab's spheroidal
    function is related to the scipy's as:
    
    Schwab(alpha,m,eta) =
      (1-eta^2)^((2-alpha)/2) *  scipy.special.pro_ang1(0, 0, m*pi/2, eta)[0]
    This means in the scipy's notation, n=0, alpha=m=0, and gamma=m*pi/2.
    In our definition, dist2d is eta, and the new parameter rscale to 
    Note again that this alpha and m are different from Schwab's.
    
    Required:
    ---------
    alpha       Schwab's parameter alpha
    m           Schwab's parameter m
    rscale      size of kernel - it becomes zero at pixel=rscale
    dist2d      2d image that contains distances from center
    """
    gamma        = m * np.pi / 2.0
    schwab       = (1.0-(dist2d/rscale)**2)**((2.0-alpha)/2.0) * \
                       sp.special.pro_ang1(0,0,gamma,(dist2d/rscale))[0]
    bad          = np.isnan(schwab)
    schwab[bad]  = 0.0
    schwab       = schwab / np.sum(schwab)
    return schwab


## ==========================================================
## TP2VIS: main function to convert TP cube into visibilities
## ==========================================================

def tp2vis(infile, outfile, ptg, maxuv=10.0, rms=None, nvgrp=4, deconv=True, winpix=0):
    """
    Required:
    ---------
    infile    Input IM filename,  in Jy/beam.  Must exist
    outfile   Output MS filename. Must not exist
    ptg       this can be one of:
              None:     NOT ALLOWED ANYMORE UNTIL RE-IMPLEMENTED TO AUTO_FILL
              string:   ptg file  (or list of strings?) - see also qtp_ms_ptg() [OK]
              list:     list of strings (from e.g. qtp_ms_ptg())   [OK]
              ms:       MS containing the pointings [not implemented]
    Optional:
    ---------
    maxuv     maximum uv distance of TP vis distribution (in m)
              default=10m for 12m ALMA dish
    rms       set the RMS (by default this will be ignored) in the infile
              in order to compute an initial guess for the weights
              Should be Jy/beam
              See also tp2viswt(mode=3)
    nvgrp     Number of visibility group (nvis = 1035*nvgrp)
              The number of antenna is hardcoded as 46
    deconv    Use deconvolution as input model? (True)
              When you have a Jy/pixel map, you want to set deconv=False
    winpix    Width of the Tukey window to reduce aliasing [=0 for no window],
              Number of pixels from each edge
    Some Technical Background:
    --------------------------
    There are 46 virtual antennas, each pointing will be visited 'nvgrp' times before
    going to the next field. Within each there are gaussian distributed 1035 visibilities
    as we don't store auto-correlations. Antenna positions are arbitrary, we only randomize
    the distribution in UV, and force a (0,0) for total flux. Thus UV is not derived from
    the antpos.
    """

    # CASA bug fixes
    # ==============

    bug001_Fixed = False
    bug028_Fixed = True

    # Parameters
    # ==========

    seed  = 123                                 # for random number
    seed  = 987                                 # for random number
    seed  = 1
    seed  = 2
    seed  = 3
    seed  = 123

    # Query the input image
    # =====================

    # Check if exists - do we really mean this? file and directory or os.path.isdir
    # if os.path.isfile(outfile) or os.path.isdir(outfile):
    if os.path.isfile(outfile):
        print("Cannot overwrite",outfile)
        return

    # Ensure RA-DEC-POL-FREQ axis order (CASA simulator needs it)
    if axinorder(infile):                       # if 4 axes in order
        imagename = infile                      # use original file
        delimage  = False
    else:                                       # if not, rearrange
        imagename = arangeax(infile)            # and use re-aranged data
        delimage  = True        

    # Parameters from TP cube header
    # ==============================

    cms    = qa.constants('c')['value']         # speed of light in m/s

    h0         = imhead(imagename,mode='list')
    cb_shape   = h0['shape']                    # cube shape
    cb_nx      = h0['shape'][0]                 # num of pixels, RA
    cb_ny      = h0['shape'][1]                 #              , DEC
    cb_dx      = np.abs(h0['cdelt1'])           # pixel size [radian]!
    cb_dy      = np.abs(h0['cdelt2'])
    cb_objname = h0['object']                   # object name
    cb_nchan   = h0['shape'][3]                 # num of channels
    cb_fstart  = h0['crval4']-h0['crpix4']*h0['cdelt4'] # start freq [Hz]
    cb_fwidth  = h0['cdelt4']                   # chan width [Hz]
    cb_reffreq = cb_fstart + 0.5*cb_fwidth      # chan central freq [Hz]
    cb_refwave = cms / (cb_reffreq)             # wavelength [m]
    cb_refcode = h0['reffreqtype']              # e.g. 'LSRK'
    cb_bunit   = h0['bunit'].upper()            # JY/BEAM or JY/PIXEL

    cb_fstart  = cb_fstart /1.0e9               # Hz -> GHz
    cb_fwidth  = cb_fwidth /1.0e9
    cb_reffreq = cb_reffreq/1.0e9

    # Parameters for TP and virtual interferometer (VI) primary beams
    # ===============================================================

    twopi  = 2.0*np.pi
    apr    = qa.convert('1.0rad','arcsec')['value'] # arcsec per radian
    stof   = 2.0*np.sqrt(2.0*np.log(2.0))           # FWHM=stof*sigma

    # TP beam
    fwhm100   = t2v_arrays['ALMATP']['fwhm100'] # FWHM at 100GHz [arcsec]
    tp_beamFWHM  = fwhm100*(100.0/cb_reffreq)   # at obs freq [arcsec]
    tp_beamSigma = tp_beamFWHM/stof/apr         # sigma of TP beam [rad]
    tp_beamSigFT = 1.0/(twopi*tp_beamSigma)     # sigma in fourier [lambda]
    print("tp_sigma [rad], tp_sigmaFT [lambda]: ",tp_beamSigma,tp_beamSigFT)

    # VI beam
    vi_antname   = t2v_arrays['VIRTUAL']['observatory'] # VI observatory
    vi_dish      = t2v_arrays['VIRTUAL']['dish']# VI dish size [m]

    fwhm100  = t2v_arrays['VIRTUAL']['fwhm100'] # FWHM at 100GHz [arcsec]
    vi_beamFWHM  = fwhm100*(100.0/cb_reffreq)   # at reffreq [arcsec]
    vi_beamSigma = vi_beamFWHM/stof/apr         # sigma of VI beam [rad]
    vi_beamSigFT = 1.0/(twopi*vi_beamSigma)     # sigma in fourier [lambda]
    print("vi_sigma [rad], vi_sigmaFT [lambda]: ",vi_beamSigma,vi_beamSigFT)

    # Obtain pointing coordinates
    # ===========================

    print("Using ptg = ",ptg)
    if type(ptg) == type([]):
        pointings = ptg                         # list of J2000/RA/DEC strings
    else:
        pointings = getptg(ptg)                 # convert file to list

    # Deconvolution of TP cube (images) by TP beam
    #   (if deconv=False the input image will be used instead)
    # ========================================================
    
    # Check unit of TP cube
    if deconv:
        if cb_bunit != 'JY/BEAM':
            print("ERROR: unit should be 'Jy/beam' when deconv=True",cb_bunit)
            return
    else:
        if cb_bunit != 'JY/PIXEL':
            print("ERROR: unit should be 'Jy/pixel' when deconv=False",cb_bunit)
            return

    # Constants
    apr    = qa.convert('1.0rad','arcsec')['value'] # arcsec per radian
    cbm    = np.pi/(4.0*np.log(2.0))                # beamarea=cbm*bmaj*bmin

    # Number of pixels per TP beam
    apixel = np.abs((cb_dx*apr)*(cb_dy*apr))    # area in pixel [arcsec2]
    abeam  = cbm*tp_beamFWHM**2                 # area of TP beam [arcsec2]
    nppb   = abeam/apixel                       # To convert Jy/bm to Jy/pix
    print("Number of pixels per beam:",nppb)

    # Cutoff length of TP's gaussian beam tail
    eps    = 0.01                               # cutoff amp of gauss tail
    uvcut  = np.sqrt(-2.0*tp_beamSigFT**2*np.log(eps)) # uvdist there
    uvcut  = np.minimum(maxuv/cb_refwave,uvcut) # compare with maxuv
    print("UVCUT:", uvcut/1000.0,"kLambda")

    # Generate uvdist^2 image [notice: x-axis runs vertically] 
    frqx      = np.fft.fftfreq(cb_nx,cb_dx)     # frequency in x
    frqy      = np.fft.fftfreq(cb_ny,cb_dy)     # frequency in y
    vgrd,ugrd = np.meshgrid(frqy,frqx)          # make grids
    uvgrd2    = ugrd**2+vgrd**2                 # uvdist^2 image

    del frqx,frqy,vgrd,ugrd


    # Open TP cube (@todo:  this can go inside the if deconv)
    ia.open(imagename)

    # Output deconvolved cube
    if deconv:
        dd = ''.join(re.findall('[0-9]',str(datetime.datetime.now())))
        imagedecname = 'tmp_imagedec_' + dd + '.im'
        ia2 = ia.newimagefromimage(imagename,imagedecname,overwrite=True)

        if use_schwab:
            print("Using Schwab's spheroidal function in TP deconvolution")
            # Schwab's spheroidal function [pixel unit]
            # @todo  make sure we can use /, or do we need // in python3
            #        make sure odd numbers work
            x0        = np.arange(-cb_nx//2,-cb_nx//2+cb_nx)  # get cb_nx pix
            y0        = np.arange(-cb_ny//2,-cb_ny//2+cb_ny)  # get cb_ny pix
            xx,yy     = np.meshgrid(x0,y0)
            xygrid    = np.sqrt(xx*xx + yy*yy)
            schwab    = schwab_spheroidal(1.0,6.0,3.0,xygrid) # alpha=1, m=6
            schwab_ft = np.fft.fft2(np.fft.ifftshift(schwab))

            del x0,y0,xx,yy,xygrid,schwab

        # Loop over channels
        print("Deconvolution loop starts")
        for iz in range(cb_nchan):

            # Beam in Fourier domain
            freq      = cb_fstart+cb_fwidth*(0.5+iz)      # chan cen freq [GHz]
            beamSigFT = tp_beamSigFT * freq/cb_reffreq
            beamFT    = np.exp(-uvgrd2/(2.0*beamSigFT**2))
            if use_schwab:
                beamFT    = beamFT * schwab_ft            # Gauss * Schwab

            # Channel image to be deconvolved
            image     = ia.getchunk([-1,-1,-1,iz],[-1,-1,-1,iz])
            image     = image[:,:,0,0]                    # image[ix][iy][0][0]
            image     = image / nppb                      # scale to Jy/pixel

            # Apply Tukey window
            if winpix > 0:
                nwin      = winpix
                mask      = ia.getchunk([-1,-1,-1,iz],[-1,-1,-1,iz],getmask=True)
                mask      = mask[:,:,0,0]                 # mask[ix][iy][0,0]
                nnx       = mask.shape[0]
                nny       = mask.shape[1]
                maskexp   = np.zeros([nnx+2,nny+2])       # add 1pix each edge
                maskexp[1:nnx+1,1:nny+1] = mask           # edge = 0 (blank)
                dist = distance_transform_edt(maskexp)-1. # dist. from blanks
                dist[dist<0]     = 0                      # outside/blanks=0
                dist[dist>nwin]  = nwin                   # deep inside=nwin
                dist      = dist/nwin                     # normalize to [0,1]
                dist      = dist[1:nnx+1,1:nny+1]         # trim the expansion
                mask      = 0.5*(1.0-np.cos(np.pi*dist))  # Tukey window
                image     = image * mask                  # apply

                del dist,mask

            # Deconvolution 
            imageFT          = np.fft.fft2(image,axes=(0,1))
            imageFTdec       = imageFT.copy()
            idx0             = (uvgrd2   > (uvcut**2))    # idx of outer uv
            idx1             = np.logical_not(idx0)       # idx of inner uv
            imageFTdec[idx1] = imageFT[idx1]/beamFT[idx1] # just for inner uv
            imageFTdec[idx0] = 0.0                        # set outer uv zero
            imagedec         = np.fft.ifft2(imageFTdec)
            ia2.putchunk(np.real(imagedec), blc=[0,0,0,iz])

        ia2.close()
        imhead(imagedecname,mode='put',hdkey='bunit',hdvalue='Jy/pixel')
                                                          # unit=Jy/pixel
    ia.close()


    # List parameters for virtual interferometric obs
    # ===============================================

    # Due to CASA construction, we cannot set some params directly
    # and have to define many indirect params. E.g., Nvis cannot be set,
    # but is calculated as Nvis=npair*(ttot/tint), where npair=num of ant
    # pairs, ttot=total integ time, and tint=integ time per vis.

    nant            = 46                        # # of fake antennas
    npair           = (nant*(nant-1))//2        # # of baselines
    nvis            = npair * nvgrp             # # of vis per point
    source          = cb_objname                # object name
    npnt            = len(pointings)

    # Spectral windows
    spw_nchan       = cb_nchan                  # # of channels
    spw_fstart      = cb_fstart                 # start freq [GHz]
    spw_fwidth      = cb_fwidth                 # freq width [GHz]
    spw_fresolution = cb_fwidth
   
    spw_fband       = 'bandtp'                  # fake name
    spw_stokes      = 'I'                       # 1 pol axis (or e.g. 'XX YY')
    spw_refcode     = cb_refcode                # e.g. 'LSRK'

    # Feed
    fed_mode        = 'perfect X Y'    
    fed_pol         = ['']
  
    # Fields
    fld_calcode     = 'OBJ'
    fld_distance    = '0m'                      # infinite distance

    # Observatory
    if use_vp:
        obs_obsname     = 'WSRT'      # picking this results in no data in pure tp2vis even
        obs_obsname     = 'ALMA'
        obs_obspos      = me.observatory(obs_obsname)          # coordinate
        obs_obsname     = t2v_arrays['VIRTUAL']['observatory'] # observatory        
    else:
        obs_obsname     = t2v_arrays['VIRTUAL']['observatory'] # observatory
        obs_obspos      = me.observatory(obs_obsname)          # coordinate

    # Telescopes
    tel_pbFWHM      = t2v_arrays['VIRTUAL']['fwhm100']*(100./spw_fstart) # asec
    tel_mounttype   = 'alt-az'
    tel_coordsystem = 'local'                   # coordinate of antpos
    tel_antname     = t2v_arrays['VIRTUAL']['antList'][0]
    tel_dish        = t2v_arrays['VIRTUAL']['dish']
    if dish3 != None:
        print("WARNING: using non-standard tel_dish = %g for antname = %s" % (dish3,tel_antname))
        tel_dish = dish3

    # Fake antenna parms
    tel_antposx     = np.arange(nant)*1000.0    # fake ant positions
    tel_antposy     = np.arange(nant)*1000.0    # the UV's will be random
    tel_antposz     = np.arange(nant)*1000.0    # later one
    tel_antdiam     = [tel_dish] * nant         # all dish sizes the same

    # Numbers of vis per pointing and for all pointings
    tvis            = 1.0                       # integ time per vis
    tpnt            = tvis * nvgrp              # integ time per ptgs
    ttot            = tpnt * npnt               # tot int time for all pnt
    tstart          = -ttot/2                   # set start/end time of obs,
    tend            = +ttot/2                   # so that (tend-tstart)/tvis
                                                # = num of vis per point

    # Print parameters
    # ================

    print( "TP2VIS Parameters")
    print( "   input image name:                    %s" % (imagename))
    print( "   image shape:                         %s" % (repr(cb_shape)))
    print( "   output measurement set name:         %s" % (outfile))
    print( "   number of pointings:                 %d" % (npnt))
    print( "   number of visibilities per pointing: %d" % (tpnt*npair))
    print( "   start frequency [GHz]:               %f" % (spw_fstart))
    print( "   frequency width [GHz]:               %f" % (spw_fwidth))
    print( "   frequency resolution [GHz]:          %f" % (spw_fresolution))
    print( "   freq channels:                       %d" % (spw_nchan))
    print( "   polarizations:                       %s" % (spw_stokes))
    print( "   antenna name:                        %s" % (tel_antname))
    print( "   VI primary beam fwhm [arcsec]:       %f" % (tel_pbFWHM))
    print( "   VI primary beam sigmaFT [m]:         %f" % (vi_beamSigFT*cb_refwave))
    print( "   ttot                                 %f" % (ttot))
    print( "   frame:                               %s" % (spw_refcode))
    print( "   seed:                                %d" % (seed))
    print( "   use_vp:                              %s" % (repr(use_vp)))
    print( "   use_schwab:                          %s" % (repr(use_schwab)))

    # Set parameters in CASA
    # ======================

    spw_fstart        = str(spw_fstart)      + 'GHz'
    spw_fwidth        = str(spw_fwidth)      + 'GHz'
    spw_fresolution   = str(spw_fresolution) + 'GHz'

    if seed >= 0:
        np.random.seed(seed)
  
    sm.open(outfile)
    
    if use_vp:
        vptable = outfile + '/TP2VISVP'
        vp.saveastable(vptable)
    else:
        vptable = None

    print("OBS/TEL:",obs_obsname, obs_obspos, tel_antname, tel_mounttype, tel_coordsystem, tel_antdiam)

    sm.setconfig(telescopename=obs_obsname,
                referencelocation=obs_obspos,
                antname=tel_antname,
                mount=tel_mounttype,
                coordsystem=tel_coordsystem,
                x=tel_antposx,y=tel_antposy,z=tel_antposz,
                dishdiameter=tel_antdiam)

    sm.setspwindow(spwname=spw_fband,
                freq=spw_fstart,
                deltafreq=spw_fwidth,
                freqresolution=spw_fresolution,
                nchannels=spw_nchan,
                refcode=spw_refcode,
                stokes=spw_stokes)

    sm.setfeed(mode=fed_mode,
                pol=fed_pol)

    for k in range(0,npnt):
        this_pointing = pointings[k]
        src = source + '_%d' % (k)
        # src = source                                     # uniq field ID's are not neeed (Petry 2019)        
        sm.setfield(sourcename=src,
                sourcedirection=this_pointing,
                calcode=fld_calcode,
                distance=fld_distance)

    sm.setlimits(shadowlimit=0.001,
                elevationlimit='10deg')

    sm.setauto(autocorrwt=0.0)

    sm.settimes(integrationtime=str(tvis)+'s',
                usehourangle=True,
                referencetime=me.epoch('utc', 'today'))

    # Generate (empty) visibilities
    # =============================

    # This step generates (u,v,w), based on target coord and antpos
    # following current CASA implementation, but (u,v,w) will be
    # replaced in the next step.
    
    print("Running sm.observemany")
    sources    = []
    starttimes = []
    stoptimes  = []

    tstart_src = tstart
    tend_src   = tstart_src + tpnt
    
    for k in range(npnt):
        src = source + '_%d' % (k)
        sources.append(src)
        starttimes.append(str(tstart_src)+'s')
        stoptimes.append(str(tend_src)+'s')
        tstart_src = tstart_src + tpnt
        tend_src   = tstart_src + tpnt

    sm.observemany(sourcenames=sources,
            spwname=spw_fband,
            starttimes=starttimes,
            stoptimes=stoptimes)

    # Genarate (replace) (u,v,w) to follow Gaussian
    # =============================================

    # Beam size in uv [m]
    beamSigFT = vi_beamSigFT*cb_refwave         # sigmaF=D/lambda -> D [m]

    # Include (u,v) = (0,0)
    uu = np.array([0.0])
    vv = np.array([0.0])

    # Rest follows Gaussian distribution with < uvcut^2
    nuv = 1                                     # (0,0) exists already
    uvcut2 = (uvcut*cb_refwave)**2              # 1/lambda -> meter
    while (nuv<nvis):                           # loop until enough
        nrest = nvis-nuv
        utmp,vtmp = np.random.normal(scale=beamSigFT,size=(2,nrest))
        ok    = utmp**2+vtmp**2 < uvcut2        # generate gauss and
        uu    = np.append(uu,utmp[ok])          # ok for uvdist<uvcut
        vv    = np.append(vv,vtmp[ok])
        nuv   = uu.size

    uu = uu[:nvis]
    vv = vv[:nvis]
    ww = np.zeros(nvis)

    del utmp,vtmp, ok

    # Replicate the same uv set for all pointings
    if npnt > 1:
        uu = np.ravel([uu,]*npnt)
        vv = np.ravel([vv,]*npnt)
        ww = np.ravel([ww,]*npnt)

    nuvw = uu.shape[0]
    tb.open(outfile,nomodify=False)
    uvw  = tb.getcol('UVW')
    print("UVW shape",uvw.shape,nuvw,uvw[:,1])     # IndexError: too many indices for array
    if len(np.ravel(uvw)) > 0:
        nrow = uvw.shape[1]
        if nrow == nuvw:
            uvw = np.array([uu,vv,ww])
            tb.putcol('UVW',uvw)
            print("UVW0",uu[1],vv[1],ww[1])
        else:
            print("Bad UVW",nrow,nuvw)
    else:
        print("WARNING: no uvw?")


    # Set WEIGHT and SIGMA columns temporarily
    # ========================================

    # Adjust weights
    #   weight of individual vis = sqrt(nvis)*rmsJy
    #   after natural wtg --> sqrt(nvis)*rmsJy / sqrt(nvis) = rmsJy

    if rms != None:
        print("Adjusting the weights using rms = %g  nvis=%d" % (rms,nvis))
        weight = tb.getcol('WEIGHT')
        w = rms * np.sqrt(nvis)
        w = 1.0/(w*w)
        print("WEIGHT: Old=%s New=%g Nvis=%d" % (weight[0,0],w,nvis))
        weight[:,:] = w                         # weight[npol,nvis*npnt]
        tb.putcol('WEIGHT',weight)              # set WEIGHT
        sigma = 1/np.sqrt(weight)               # SIGMA
        tb.putcol('SIGMA',sigma)                # set SIGMA
    else:
        print("The WEIGHT column is not filled, all 1.0")
    tb.close()

    del uvw

    # Fill vis amp/phase based on deconvolved TP image
    # ================================================

    sm.setdata(fieldid=list(range(0,npnt)))     # set all fields
    if use_vp:                                  # set primary beam
        # according to Kumar
        sm.setvp(dovp=True,usedefaultvp=False, vptable=vptable)
    else:
        sm.setvp(dovp=True,usedefaultvp=False)

    print("Running sm.predict")                 # Replace amp/pha - key task
    if deconv:
        sm.predict(imagename=imagedecname)      # deconvolved cube
        os.system('rm -rf %s' % imagedecname)   # remove the temp file
    else:
        sm.predict(imagename=imagename)         # input TP cube

    # Print Summary
    sm.summary()

    # Save PB info
    # ============

    f = open(outfile + '/TP2VIS.ascii','w')            # save VP/PB info
    f.write('TP2VIS definition of VIRTUAL interferometer\n')
    for key in list(t2v_arrays['VIRTUAL'].keys()):
        f.write('%s:%s\n' % (key, str(t2v_arrays['VIRTUAL'][key])))
    f.close()

    # Close measurement set
    # =====================
    sm.done()


    # Corrections on CASA header
    #   Most of following should not be necessary if CASA has no bug
    # ==============================================================

    if not bug001_Fixed:
        print("Correcting CASA header inconsistencies [bug001]")
        # REST_FREQUENCY in /SOURCE
        #    Having REST_FREQUENCY in header does not make sense (since
        #    multiple lines, but CASA MS does have it. So, put it in.
        h0       = imhead(imagename,mode='list')

        if 'restfreq' in list(h0.keys()):
            restfreq = h0['restfreq'][0]        # restfreq from image header
        else:
            if h0['cunit4'] == 'Hz':            # set it to ref freq [Hz]
                restfreq = h0['crval4']
            elif h0['cunit4'] == 'MHz':
                restfreq = h0['crval4'] * 1.0e6
            elif h0['cunit4'] == 'GHz':
                restfreq = h0['crval4'] * 1.0e9

        print("SET RESTFREQ:::",restfreq/1e9," GHz")
        print("   Set restfreq= in (t)clean manually if this restfreq is incorrect")

        tb.open(outfile + '/SOURCE',nomodify=False)
        rf = tb.getcol('REST_FREQUENCY')
        rf = rf * 0 + restfreq
        tb.putcol('REST_FREQUENCY',rf)
        tb.close()

        # REF_FREQUENCY in /SPECTRAL_WINDOW
        #    Not clear what should be in this data column, but all ALMA data
        #    seem to have REF_FREQUENCY = REST_FREQUENCY, so we follow.
        tb.open(outfile + '/SPECTRAL_WINDOW',nomodify=False)
        rf = tb.getcol('REF_FREQUENCY')
        rf = rf * 0 + restfreq
        tb.putcol('REF_FREQUENCY',rf)
        tb.close()

    if not bug028_Fixed:
        print("Set offset time stamps between fields [bug028]")
        # clean task requires different time stamps for different fields
        tb.open(outfile,nomodify=False)
        time0 = tb.getcol("TIME")
        time1 = tb.getcol("TIME_CENTROID")
        t0    = time0[0]
        time0 = [t0 + 1.*ii for ii in range(len(time0))]
        time1 = time0
        tb.putcol('TIME',time0)
        tb.putcol('TIME_CENTROID',time1)
        tb.close()

    if delimage:
        os.system('rm -rf %s' % imagename)

    #-end of tp2vis()

## =======================================================
## TP2VISBL: Return baselines (a primitive of tp2vis)
## =======================================================
           
def tp2visbl(infile, ptg=None, dish=12.0, maxuv=10.0, nvgrp=4, seed=123):
    """
    Return just a set of baselines from a single pointing TP2VIS, a hacked version of tp2vis()
    
    Required:
    ---------
    infile    Input IM filename. The WCS of this file is used to set the RA,DEC and spectral
              axis of the MS.
    
    Optional:
    ---------
    ptg       string:   the RA,DEC of the source to be observed, if to override from infile
    dish      Dish size (12m for ALMA)
    
    maxuv     maximum uv distance of TP vis distribution (in m)
              default=10m for 12m ALMA dish
    
    nvgrp     Number of visibility group (nvis = 1035*nvgrp)
              The number of antenna is hardcoded as 46
    
    """

    def qac_tpdish(name, size=None):
        """
        A patch to work with dishes that are not 12m (currently hardcoded in tp2vis.py)
        
        @todo   explain relationship to qac_vp()
        E.g. for GBT (a 100m dish) you would need to do:
        
        qac_tpdish('ALMATP',100.0)
        qac_tpdish('VIRTUAL',100.0)
        
        Note that ALMATP and VIRTUAL need to already exist.
        """
        if size == None:
            if name in t2v_arrays.keys():
                print(t2v_arrays[name])
            else:
                print("'%s' not a valid dish name, valid are : %s" % (name,str(t2v_arrays.keys())))
                return
        old_size = t2v_arrays[name]['dish']
        old_fwhm = t2v_arrays[name]['fwhm100']
        r = size/old_size
        t2v_arrays[name]['dish']   = size
        t2v_arrays[name]['fwhm100']= old_fwhm / r
        print("QAC_DISH: %s %g %g -> %g %g" % (name,old_size, old_fwhm, size, old_fwhm/r))

    
    # Parameters
    # ==========

    seed  = 123                                 # for random number

    # Dish cheat
    # ==========
    qac_tpdish('ALMATP',dish)
    qac_tpdish('VIRTUAL',dish)

    # Query the input image
    # =====================

    # Ensure RA-DEC-POL-FREQ axis order (CASA simulator needs it)
    if axinorder(infile):                       # if 4 axes in order
        imagename = infile                      # use original file
        delimage  = False
    else:                                       # if not, rearrange
        imagename = arangeax(infile)            # and use re-aranged data
        delimage  = True        

    # Parameters from TP cube header
    # ==============================

    cms    = qa.constants('c')['value']         # speed of light in m/s

    h0         = imhead(imagename,mode='list')
    cb_shape   = h0['shape']                    # cube shape
    cb_nx      = h0['shape'][0]                 # num of pixels, RA
    cb_ny      = h0['shape'][1]                 #              , DEC
    cb_dx      = np.abs(h0['cdelt1'])           # pixel size [radian]!
    cb_dy      = np.abs(h0['cdelt2'])
    cb_objname = h0['object']                   # object name
    cb_nchan   = h0['shape'][3]                 # num of channels
    cb_fstart  = h0['crval4']-h0['crpix4']*h0['cdelt4'] # start freq [Hz]
    cb_fwidth  = h0['cdelt4']                   # chan width [Hz]
    cb_reffreq = cb_fstart + 0.5*cb_fwidth      # chan central freq [Hz]
    cb_refwave = cms / (cb_reffreq)             # wavelength [m]
    cb_refcode = h0['reffreqtype']              # e.g. 'LSRK'
    cb_bunit   = h0['bunit'].upper()            # JY/BEAM or JY/PIXEL

    cb_fstart  = cb_fstart /1.0e9               # Hz -> GHz
    cb_fwidth  = cb_fwidth /1.0e9
    cb_reffreq = cb_reffreq/1.0e9

    # Parameters for TP and virtual interferometer (VI) primary beams
    # ===============================================================

    twopi  = 2.0*np.pi
    apr    = qa.convert('1.0rad','arcsec')['value'] # arcsec per radian
    stof   = 2.0*np.sqrt(2.0*np.log(2.0))           # FWHM=stof*sigma

    # TP beam
    fwhm100   = t2v_arrays['ALMATP']['fwhm100'] # FWHM at 100GHz [arcsec]
    tp_beamFWHM  = fwhm100*(100.0/cb_reffreq)   # at obs freq [arcsec]
    tp_beamSigma = tp_beamFWHM/stof/apr         # sigma of TP beam [rad]
    tp_beamSigFT = 1.0/(twopi*tp_beamSigma)     # sigma in fourier [lambda]
    print("tp_sigma [rad], tp_sigmaFT [lambda]: ",tp_beamSigma,tp_beamSigFT)

    # VI beam
    vi_antname   = t2v_arrays['VIRTUAL']['observatory'] # VI observatory
    vi_dish      = t2v_arrays['VIRTUAL']['dish']# VI dish size [m]

    fwhm100  = t2v_arrays['VIRTUAL']['fwhm100'] # FWHM at 100GHz [arcsec]
    vi_beamFWHM  = fwhm100*(100.0/cb_reffreq)   # at reffreq [arcsec]
    vi_beamSigma = vi_beamFWHM/stof/apr         # sigma of VI beam [rad]
    vi_beamSigFT = 1.0/(twopi*vi_beamSigma)     # sigma in fourier [lambda]
    print("vi_sigma [rad], vi_sigmaFT [lambda]: ",vi_beamSigma,vi_beamSigFT)

    # Obtain pointing coordinates    (@todo fix this so it uses crval1,crval2)
    # ===========================

    if ptg == None:
        ptg = '%gdeg %gdeg' % (h0['crval1']*360/twopi,h0['crval2']*360/twopi)
    print("Using ptg = ",ptg)

    # Deconvolution of TP cube (images) by TP beam
    #   (if deconv=False the input image will be used instead)
    # ========================================================
    
    # Constants
    apr    = qa.convert('1.0rad','arcsec')['value'] # arcsec per radian
    cbm    = np.pi/(4.0*np.log(2.0))                # beamarea=cbm*bmaj*bmin

    # Number of pixels per TP beam
    apixel = np.abs((cb_dx*apr)*(cb_dy*apr))    # area in pixel [arcsec2]
    abeam  = cbm*tp_beamFWHM**2                 # area of TP beam [arcsec2]
    nppb   = abeam/apixel                       # To convert Jy/bm to Jy/pix
    print("Number of pixels per beam:",nppb)

    # Cutoff length of TP's gaussian beam tail
    eps    = 0.01                               # cutoff amp of gauss tail
    uvcut  = np.sqrt(-2.0*tp_beamSigFT**2*np.log(eps)) # uvdist there
    uvcut  = np.minimum(maxuv/cb_refwave,uvcut) # compare with maxuv
    print("UVCUT:", uvcut/1000.0,"kLambda")

    # Generate uvdist^2 image [notice: x-axis runs vertically] 
    frqx      = np.fft.fftfreq(cb_nx,cb_dx)     # frequency in x
    frqy      = np.fft.fftfreq(cb_ny,cb_dy)     # frequency in y
    vgrd,ugrd = np.meshgrid(frqy,frqx)          # make grids
    uvgrd2    = ugrd**2+vgrd**2                 # uvdist^2 image

    del frqx,frqy,vgrd,ugrd

    # List parameters for virtual interferometric obs
    # ===============================================

    # Due to CASA construction, we cannot set some params directly
    # and have to define many indirect params. E.g., Nvis cannot be set,
    # but is calculated as Nvis=npair*(ttot/tint), where npair=num of ant
    # pairs, ttot=total integ time, and tint=integ time per vis.

    nant            = 46                        # # of fake antennas
    npair           = (nant*(nant-1))//2        # # of baselines
    nvis            = npair * nvgrp             # # of vis per point
    source          = cb_objname                # object name
    npnt            = 1

    # Spectral windows
    spw_nchan       = cb_nchan                  # # of channels
    spw_fstart      = cb_fstart                 # start freq [GHz]
    spw_fwidth      = cb_fwidth                 # freq width [GHz]
    spw_fresolution = cb_fwidth
   
    spw_fband       = 'bandtp'                  # fake name
    spw_stokes      = 'I'                       # 1 pol axis (or e.g. 'XX YY')
    spw_refcode     = cb_refcode                # e.g. 'LSRK'

    # Feed
    fed_mode        = 'perfect X Y'    
    fed_pol         = ['']
  
    # Fields
    fld_calcode     = 'OBJ'
    fld_distance    = '0m'                      # infinite distance

    # Observatory
    if use_vp:
        obs_obsname     = 'WSRT'      # picking this results in no data in pure tp2vis even
        obs_obsname     = 'ALMA'
        obs_obspos      = me.observatory(obs_obsname)          # coordinate
        obs_obsname     = t2v_arrays['VIRTUAL']['observatory'] # observatory        
    else:
        obs_obsname     = t2v_arrays['VIRTUAL']['observatory'] # observatory
        obs_obspos      = me.observatory(obs_obsname)          # coordinate

    # Telescopes
    tel_pbFWHM      = t2v_arrays['VIRTUAL']['fwhm100']*(100./spw_fstart) # asec
    tel_mounttype   = 'alt-az'
    tel_coordsystem = 'local'                   # coordinate of antpos
    tel_antname     = t2v_arrays['VIRTUAL']['antList'][0]
    tel_dish        = t2v_arrays['VIRTUAL']['dish']
    if dish3 != None:
        print("WARNING: using non-standard tel_dish = %g for antname = %s" % (dish3,tel_antname))
        tel_dish = dish3

    # Fake antenna parms
    tel_antposx     = np.arange(nant)*1000.0    # fake ant positions
    tel_antposy     = np.arange(nant)*1000.0    # the UV's will be random
    tel_antposz     = np.arange(nant)*1000.0    # later one
    tel_antdiam     = [tel_dish] * nant         # all dish sizes the same

    # Numbers of vis per pointing and for all pointings
    tvis            = 1.0                       # integ time per vis
    tpnt            = tvis * nvgrp              # integ time per ptgs
    ttot            = tpnt * npnt               # tot int time for all pnt
    tstart          = -ttot/2                   # set start/end time of obs,
    tend            = +ttot/2                   # so that (tend-tstart)/tvis
                                                # = num of vis per point

    # Print parameters
    # ================

    print( "TP2VISBL Parameters")
    print( "   input image name:                    %s" % (imagename))
    print( "   image shape:                         %s" % (repr(cb_shape)))
    print( "   number of pointings:                 %d" % (npnt))
    print( "   number of visibilities per pointing: %d" % (tpnt*npair))
    print( "   start frequency [GHz]:               %f" % (spw_fstart))
    print( "   frequency width [GHz]:               %f" % (spw_fwidth))
    print( "   frequency resolution [GHz]:          %f" % (spw_fresolution))
    print( "   freq channels:                       %d" % (spw_nchan))
    print( "   polarizations:                       %s" % (spw_stokes))
    print( "   antenna name:                        %s" % (tel_antname))
    print( "   VI primary beam fwhm [arcsec]:       %f" % (tel_pbFWHM))
    print( "   VI primary beam sigmaFT [m]:         %f" % (vi_beamSigFT*cb_refwave))
    print( "   ttot                                 %f" % (ttot))
    print( "   frame:                               %s" % (spw_refcode))
    print( "   seed:                                %d" % (seed))
    print( "   use_vp:                              %s" % (repr(use_vp)))
    print( "   use_schwab:                          %s" % (repr(use_schwab)))

    # Set parameters in CASA
    # ======================

    spw_fstart        = str(spw_fstart)      + 'GHz'
    spw_fwidth        = str(spw_fwidth)      + 'GHz'
    spw_fresolution   = str(spw_fresolution) + 'GHz'

    if seed >= 0:
        np.random.seed(seed)

    # Generate (empty) visibilities
    # =============================

    # This step generates (u,v,w), based on target coord and antpos
    # following current CASA implementation, but (u,v,w) will be
    # replaced in the next step.
    
    print("Running sm.observemany")
    sources    = []
    starttimes = []
    stoptimes  = []

    tstart_src = tstart
    tend_src   = tstart_src + tpnt
    
    for k in range(npnt):
        src = source + '_%d' % (k)
        sources.append(src)
        starttimes.append(str(tstart_src)+'s')
        stoptimes.append(str(tend_src)+'s')
        tstart_src = tstart_src + tpnt
        tend_src   = tstart_src + tpnt

    sm.observemany(sourcenames=sources,
            spwname=spw_fband,
            starttimes=starttimes,
            stoptimes=stoptimes)

    # Genarate (replace) (u,v,w) to follow Gaussian
    # =============================================

    # Beam size in uv [m]
    beamSigFT = vi_beamSigFT*cb_refwave         # sigmaF=D/lambda -> D [m]

    # Include (u,v) = (0,0)
    uu = np.array([0.0])
    vv = np.array([0.0])

    # Rest follows Gaussian distribution with < uvcut^2
    nuv = 1                                     # (0,0) exists already
    uvcut2 = (uvcut*cb_refwave)**2              # 1/lambda -> meter
    while (nuv<nvis):                           # loop until enough
        nrest = nvis-nuv
        utmp,vtmp = np.random.normal(scale=beamSigFT,size=(2,nrest))
        ok    = utmp**2+vtmp**2 < uvcut2        # generate gauss and
        uu    = np.append(uu,utmp[ok])          # ok for uvdist<uvcut
        vv    = np.append(vv,vtmp[ok])
        nuv   = uu.size

    uu = uu[:nvis]
    vv = vv[:nvis]
    ww = np.zeros(nvis)

    return (uu,vv)


    # Close measurement set
    # =====================
    sm.done()

    # return the baselines....
    return uvw
    
    
## =======================================================
## TP2VISWT: Explore different weights for TP visibilities
## =======================================================
           
def tp2viswt(mslist, value=1.0, mode='statistics', makepsf=True):
    """
    Parameters
    -----------
    mslist     MS(s) to report weights, or compute new weights for
    value      (mode=1,2,3) value to be applied applied to weight
    
    mode       0 or 'statistics'   (default)
               1 or 'constant'
               2 or 'multiply'
               3 or 'rms'
               4 or 'beammatch'
    makepsf    True/False for mode='beammatch'
    Example usage:
    --------------
    Report weights for "v1.ms"
    > tp2viswt("v1.ms",mode='stat')              
                       
    Set weights to 0.01
    > tp2viswt("v1.ms",mode='const',value=0.01)               
  
    Multiply weights by 3
    > tp2viswt("v1.ms",mode='mult',value=3.0)
    Set weights to match beam sizes [need all MSs as input]
    > tp2viswt(["tp.ms","v07m.ms","v12m.ms"],mode='beam',makepsf=True)
      
    """

    # Parameters
    # ----------

    # Separate MS inputs into INT and TP

    if type(mslist) != type([]): mslist = [mslist]
    msINT = []
    msTP  = []
    for ims in mslist:
        array = guessarray(ims)
        if array   == 'ALMA12':
            msINT.append(ims)
        elif array == 'ALMA07':
            msINT.append(ims)
        elif array == 'VIRTUAL':
            msTP.append(ims)

    # Translate mode into operation name
    if type(mode) is str:
        if   'sta' in mode[:3].lower(): oper = 'statistics'
        elif 'con' in mode[:3].lower(): oper = 'constant'
        elif 'mul' in mode[:3].lower(): oper = 'multiply'
        elif 'rms' in mode[:3].lower(): oper = 'rms'
        elif 'bea' in mode[:3].lower(): oper = 'beammatch'

    if type(mode) is int:
        if   mode == 0: oper = 'statistics'
        elif mode == 1: oper = 'constant'
        elif mode == 2: oper = 'multiply'
        elif mode == 3: oper = 'rms'
        elif mode == 4: oper = 'beammatch'

    # Define stat outputs
    # -------------------
    def wtstat(mslist,comment=''):
        print("%-4s%18s %4s %4s %4s %8s %8s %12s %12s %12s %12s" \
            % (comment,'name','spw#','npnt','npol','nvis',\
                   'fwidth','min','max','mean','std'))

        for ims in mslist:

            ms.open(ims,nomodify=True)          # open MS
            ms.selectinit(reset=True)           # all spws
            spwinfo= ms.getspectralwindowinfo() # get spw info
            spwlist= list(spwinfo.keys())       # list of SPWs

            for ispw in spwlist:                # get SPW info and WEIGHT
                spwid     = spwinfo[ispw]['SpectralWindowId']
                numchan   = spwinfo[ispw]['NumChan']
                chan1freq = spwinfo[ispw]['Chan1Freq'] / 1.0e9 # GHz
                chanwidth = spwinfo[ispw]['ChanWidth'] / 1.0e9 # GHz

                ms.selectinit(reset=True)           # new since 5.3.0-97
                ms.selectinit(datadescid=spwid)

                field_id  = np.unique(ms.getdata('field_id')['field_id'])
                npnt      = len(field_id)       # num of fields
                weight    = ms.getdata('weight')['weight'] # (npol,nvis)
                npol      = weight.shape[0]     # num of polarizations
                nvis      = weight.size         # num of visibilities

                wmin      = weight.min()        # weight min
                wmax      = weight.max()        # weight max
                wmean     = weight.mean()       # weight mean
                wstd      = weight.std()        # weight std deviation
             
                wmin1GHz  = wmin  / np.abs(chanwidth)
                wmax1GHz  = wmax  / np.abs(chanwidth)
                wmean1GHz = wmean / np.abs(chanwidth)
                wstd1GHz  = wstd  / np.abs(chanwidth)

                print("%22s %4d %4d %4d %8d %8s %12.6f %12.6f %12.6f %12.6f" \
                    % (ims,spwid,npnt,npol,nvis,'/chanw',wmin,wmax,wmean,wstd))
                print("%46s %8s %12.6f %12.6f %12.6f %12.6f" \
                    % ('','/1GHz',wmin1GHz,wmax1GHz,wmean1GHz,wstd1GHz))


            ms.close()

    # Calculate WEIGHT max & min (default)
    # --------------------------
    if oper == 'statistics':

        print("TP2VISWT: statistics of weights")
        wtstat(mslist)                          # print stat of WEIGHT

        return

    # Set WEIGHT to const.
    # --------------------
    elif oper == 'constant':

        if value == None:
            print("TP2VISWT ERROR: constant weight value not given.")
            return
        else:
            print("TP2VISWT: set the weights = %g, sigmas = %g" \
                % (value,1/np.sqrt(value)))

        wtstat(mslist,comment="Old:")           # stat before operation
        for ims in mslist:                      # loop over MSs
            tb.open(ims,nomodify=False)         # open MS modifiable
            weight = tb.getcol('WEIGHT')        # get WEIGHT array format
            weight[:,:] = value                 # constant WEIGHT[npol,nvis]
            tb.putcol('WEIGHT',weight)          # set WEIGHT
            sigma = 1/np.sqrt(weight)           # SIGMA
            tb.putcol('SIGMA',sigma)            # set SIGMA
            tb.close()                          # close MS
        wtstat(mslist,comment="New:")           # stat after operation

        return

    # Multipy constant to current WEIGHT
    # ----------------------------------
    elif oper == 'multiply':

        if value == None:
            print("TP2VISWT ERROR: multiplication value not given.")
            return
        else:
            print("TP2VISWT: multiply the weights by %g" % (value))

        wtstat(mslist,comment="Old:")           # stat before operation
        for ims in mslist:                      # loop over MSs
            tb.open(ims,nomodify=False)         # open MS modifiable
            weight = tb.getcol('WEIGHT')        # get WEIGHT
            weight = value * weight             # multiply
            tb.putcol('WEIGHT',weight)          # set WEIGHT
            sigma  = 1/np.sqrt(weight)          # SIGMA
            tb.putcol('SIGMA',sigma)            # set SIGMA
            tb.close()                          # close MS
        wtstat(mslist,comment="New:")           # stat after operation

        return

    # From RMS in TP cube and Nvis
    # ----------------------------
    elif oper == 'rms':

        if value == None:
            print("TP2VISWT ERROR: rms value not given. set value=rms")
            return
        else:
            print("TP2VISWT: adjust weights using RMS = %g" % (value))
            print("  Assumption: MS has only (mosaic) pointings of ONE science")
            print("  target, and they are arranged under the Nyquist sampling.")

        wtstat(mslist,comment="Old:")           # stat before operation
        for ims in mslist:                      # loop over MSs
            tb.open(ims + '/FIELD')             # open FIELD table
            src_id = tb.getcol('SOURCE_ID')     # list of source_id
            npnt = len(src_id)                  # obtain # of pointings
            tb.close()                          # close FIELD table
            tb.open(ims,nomodify=False)         # open MS
            weight = tb.getcol('WEIGHT')        # get WEIGHT array
            nvis   = weight.size/npnt           # num of vis *per pnt*
            w      = value * np.sqrt(nvis)      # WEIGHT=1/(RMS*sqrt(nvis))^2
            w      = 1.0/(w*w)
            weight[:,:] = w                     # weight[npol,nvis]
            tb.putcol('WEIGHT',weight)          # set WEIGHT
            sigma  = 1/np.sqrt(weight)          # SIGMA
            tb.putcol('SIGMA',sigma)            # set SIGMA
            tb.close()                          # close MS
        wtstat(mslist,comment="New:")           # stat after operation

        return

    # Matching beam sizes
    # -------------------
    elif oper == 'beammatch':

        # Check relevant MSs in input
        # ---------------------------
        if msINT == []:
            print("TP2VISWT ERROR: no interferometer (12m or 7m) MS in input.")
            return
        else:
            line = "Measurement set (INT): "
            for ims in msINT: line = line +  ", %s" % (ims)
            print(line)

        if msTP == []:
            print("TP2VISWT ERROR: no TP MS in input.")
            return
        else:
            line = "Measurement set (TP) : "
            for ims in msTP: line = line +  ", %s" % (ims)
            print(line)

        wtstat(mslist,comment="Old:")               # stat before operation

        # Generate PSF images
        # ===================

        cms = qa.constants('c')['value']            # Speed of light in m/s
        apr = qa.convert('1.0rad','arcsec')['value']# arcsec per radian
        dd = ''.join(re.findall('[0-9]',str(datetime.datetime.now())))
        baseTP   = 'tmp_msTP'                       # base name of TP images
        baseINT  = 'tmp_msINT'                      # base name of INT images
        dirname  = 'tmp_tp2viswt_' + dd             # temp directory for PSFs

        if makepsf:
            os.makedirs(dirname)                    # create scratchdir

            angmin  = 999.0                         # derive smallest angle
            for ims in msINT:                       # that MSs contain
                ms.open(ims)                        # open MS
                spwinfo = ms.getspectralwindowinfo()# SPW info
                spwlist = list(spwinfo.keys())      # list of SPWs
                for ispw in spwlist:
                    freq0 = spwinfo[ispw]['Chan1Freq']           # ref frq [Hz]
                    uvmax = ms.getdata('uvdist')['uvdist'].max() # max bl [m]
                    am0   = cms/(freq0*uvmax)       # corresponding angle [rad]
                    angmin= np.min([angmin,am0])    # smallest angle [rad]
                ms.close()                          # close MS

            angmin = angmin * apr                   # min angle [arcsec]
            csize  = angmin / 5.0                   # sample 1/5 min angle
            imsize = int(120.0/csize)               # PSF images cover 120"

            print("Generating PSF image for TP")    # tclean for TP PSF
            tclean(vis=msTP, imagename=dirname+'/'+baseTP,niter=0, \
                  weighting='natural',cell=str(csize)+'arcsec',imsize=imsize)
            print("Generating PSF image for 7m+12m")# tclean for INT PSF
            tclean(vis=msINT,imagename=dirname+'/'+baseINT,niter=0, \
                  weighting='natural',cell=str(csize)+'arcsec',imsize=imsize)

        # Calculate BETA - the ratio of INT and TP weights
        # ================================================

        # Calculate Omega_clean
        # ---------------------

        beam_int    = imhead(dirname+'/'+baseINT+'.psf')['restoringbeam']
        bmaj_int    = qa.convert(beam_int['major'],'rad')['value'] # radian
        bmin_int    = qa.convert(beam_int['minor'],'rad')['value'] # radian
        omega_clean = np.pi/(4*np.log(2.0)) * bmaj_int*bmin_int

        # Calculate Omega_TP [= W_TP(0,0)]
        # --------------------------------

        beam_tp     = imhead(dirname+'/'+baseTP+'.psf')['restoringbeam']
        bmaj_tp     = qa.convert(beam_tp['major'],'rad')['value'] # radian
        bmin_tp     = qa.convert(beam_tp['minor'],'rad')['value'] # radian
        omega_tp    = np.pi/(4*np.log(2.0)) * bmaj_tp *bmin_tp

        # Derive beta
        #   omega_syn  = omega_TP  = beta/(1+beta)*W_TP(0,0)
        # --------------------------------------------------
        beta = omega_clean / (omega_tp - omega_clean)

        print("Omega_clean [strad] = ",omega_clean)
        print("Omega_TP    [strad] = ",omega_tp)
        print("Beta               = ",beta)
    
        if beta < 0:
            print("ERROR: TP beam smaller than INT beam")
            return

        # Adjust weights of TP visibilities
        #   w_TP,k = beta/Nvis_TP * sum_k(w_INT,k)
        # ========================================

        # Sumup the weights of INT visibilities [/GHz/pnt/arcmin2]
        # --------------------------------------------------------
        sumw = 0.0
        for ims in msINT:
            ms.open(ims,nomodify=True)              # open MS
            ms.selectinit(reset=True)               # all spws
            spwinfo   = ms.getspectralwindowinfo()  # get spw info
            spwlist   = list(spwinfo.keys())        # list of SPWs
            iarray    = guessarray(ims)             # array name [e.g. ALMA12]
            fwhm0 = t2v_arrays[iarray]['fwhm100']   # beam FHWM @100GHz[arcsec]
            for ispw in spwlist:                    # loop over SPWs
                spwid     = spwinfo[ispw]['SpectralWindowId']  # spw #
                ms.selectinit(reset=True)                      # new since 5.3.0-97
                ms.selectinit(datadescid=spwid)                # this SPW alone
                c1freq = spwinfo[ispw]['Chan1Freq'] / 1.0e9    # 1st chan  [GHz]
                cwidth = spwinfo[ispw]['ChanWidth'] / 1.0e9    # chanwidth [GHz]
                fwhm   = fwhm0*(100.0/c1freq)/60.0             # FWHM [arcmin]
                barea  = np.pi*(fwhm/2.0)**2                   # bm area [amin2]
                npnt   = len(np.unique(ms.getdata('field_id')['field_id']))
                weight = ms.getdata('weight')['weight']        # (npol,nvis)
                weight = weight.sum()/npnt/barea/np.abs(cwidth)# /pnt/amin2/GHz
                sumw   = sumw + weight              # add
            ms.close()                              # close MS
    
        del weight
        print("INT sumw [/GHz/pnt/arcmin2]   = ",sumw)

        # Number of TP visibilities [/pnt]
        # --------------------------------

        nvis = 0
        for ims in msTP:
            ms.open(ims)
            ms.selectinit(reset=True)               # all spws
            for ispw in spwlist:                    # loop over SPWs
                spwid  = spwinfo[ispw]['SpectralWindowId']     # spw id
                ms.selectinit(reset=True)           # new since 5.3.0-97                
                ms.selectinit(datadescid=spwid)     # this SPW alone
                npnt   = len(np.unique(ms.getdata('field_id')['field_id']))
                weight = ms.getdata('weight')['weight']        # (npol,nvis)
                nvis   = nvis + weight.size/npnt    # num of vis
            ms.close()                              # close MS

        del weight
        print("Num of TP vis [per pointing]  = ",nvis)

        # Calcuate weight [/GHz/pointing/arcmin2]
        # ---------------------------------------

        w = beta * sumw / nvis                      # weight to be set
        print("TP nvis,weight [/GHz/pointing/arcmin2] =",nvis,w)

        # set TP weights with respect to INT weights
        # ------------------------------------------

        for ims in msTP:
            ms.open(ims,nomodify=False)             # open MS
            ms.selectinit(reset=True)               # all spws
            spwinfo = ms.getspectralwindowinfo()    # get spw info
            spwlist = list(spwinfo.keys())          # list of SPWs
            iarray  = guessarray(ims)               # array name [e.g. ALMA12]
            fwhm0   = t2v_arrays[iarray]['fwhm100'] # beam FHWM @100GHz [arcsec]
            for ispw in spwlist:                    # loop over SPWs
                spwid     = spwinfo[ispw]['SpectralWindowId']  # spw #
                ms.selectinit(reset=True)                      # new since 5.3.0-97                
                ms.selectinit(datadescid=spwid)                # this SPW alone
                c1freq = spwinfo[ispw]['Chan1Freq'] / 1.0e9    # 1st chan  [GHz]
                cwidth = spwinfo[ispw]['ChanWidth'] / 1.0e9    # chanwidth [GHz]
                fwhm   = fwhm0*(100.0/c1freq)/60.0             # FWHM [arcmin]
                barea  = np.pi*(fwhm/2.0)**2                   # bm area [amin2]
                record = ms.getdata(['weight','sigma'])        # get records
                record['weight'][:,:]=w*barea*np.abs(cwidth)   # set new weight
                record['sigma'][:,:]=1.0/np.sqrt(record['weight'][:,:]) # sigma
                ms.putdata(record)                  # put them back
            ms.close()                              # close MS

        wtstat(mslist,comment="New:")               # stat after operation
        shutil.rmtree(dirname)                      # remove scratchdir
        return

    else:

        print("WEIGHT: Unknown mode ",mode)

    #-end of tp2viswt()


## ============================================
## TP2VISTWEAK: Adjust beam size after (t)clean
## ============================================

def tp2vistweak(dirtyname, cleanname, pbcut=0.8, mask=''):
    """
    Mismatch of dirty and clean/restore beam areas become noticable in
    TP+INT joint-deconvolution. This function compares the two beam areas,
    rescales the flux density in residual map, and re-calculates the cleaned map.
    Note the mismatch problem exists even for INT alone, but without TP,
    the true flux is not known, so the problem is not noticable.
    Parameters
    -----------
    dirtyname   pre-name of dirty images (normally the filename without '.image')
    cleanname   pre-name of clean images
    pbcut       cutoff level of .pb map to define area for flux integration
                @todo clean() was using minpb=,   tclean() now uses pblimit=
    mask        user specified mask
    dirty and clean images must have the same shape, and it is assumed that
    your version of tclean() has also create the corresponding .residual and
    .pb images.
    Example usage:
    --------------
    Adjust beam size of residual image and add model and residual.
    > tp2vistweak('dirty','clean')
    This will expect 'dirty.image' and 'clean.image' as well as
    'clean.pb' and 'clean.residual'
    > tp2vistweak('dirty','clean',pbcut=0.9,mask='test_clean.image>10')
      
    """

    print("TP2VISTWEAK: scale residual image and re-generate cleaned image")
    print("  assumes the same shape for dirty and clean images in input")

    # Files
    # -----

    # Existing File names
    dirty = dirtyname + '.image'
    clean = cleanname + '.image'
    resid = cleanname + '.residual'
    pbmap = cleanname + '.pb'              # '.pb'  for tclean()
    if not os.path.exists(pbmap):          # clean or tclean?
        pbmap = cleanname + '.flux'        # '.flux' for clean()
    
    # New File names
    newclean = cleanname + '.tweak.image'
    newresid = cleanname + '.tweak.residual'
    newpbcor = cleanname + '.tweak.image.pbcor'

    # Check if they exist
    ok = True
    for f in [dirty,clean,resid,pbmap]:
        if not os.path.exists(f): 
            ok = False
            print("%s does not exist" % (f))
    if not ok:
        print("TP2VISTWEAK ERROR: need the above files")
        return

    for f in [newclean,newresid]:               # if output files
        if os.path.exists(f):                   #   already exist,
            shutil.rmtree(f)                    #   remove them
    
    # Temporary files
    dd = ''.join(re.findall('[0-9]',str(datetime.datetime.now())))
    dirname = 'tmp_tp2vistweak_' + dd           # temp directory for PSFs  
    os.makedirs(dirname)                        # make scratch directory

    diff_dirty = dirname + '/image_diff_dirty.im' 
    diff_clean = dirname + '/image_diff_clean.im' 

    # Put missing header key in residual
    imhead(resid,mode='put',hdkey='bunit',hdvalue='Jy/beam')


    # Subtract residual from dirty and clean
    # --------------------------------------
    immath(imagename=[dirty,resid],expr='IM0-IM1',outfile=diff_dirty)
    immath(imagename=[clean,resid],expr='IM0-IM1',outfile=diff_clean)


    # Calculate sum
    # -------------

    apr = qa.convert('1.0rad','arcsec')['value'] # arcsec per radian
    cbm = np.pi/(4.0*np.log(2.0))                # beamarea=cbm*bmaj*bmin

    # Pixel size
    dx_dirty,dy_dirty,dummy,dummy = imhead(diff_dirty)['incr'] * apr
    dx_clean,dy_clean,dummy,dummy = imhead(diff_clean)['incr'] * apr

    # Beam size
    h0 = imhead(diff_dirty)
    if 'perplanebeams' in h0:
        bmaj_dirty=imhead(diff_dirty)['perplanebeams']['beams']['*0']['*0']['major']['value']
        bmin_dirty=imhead(diff_dirty)['perplanebeams']['beams']['*0']['*0']['minor']['value']
        bmaj_clean=imhead(diff_clean)['perplanebeams']['beams']['*0']['*0']['major']['value']
        bmin_clean=imhead(diff_clean)['perplanebeams']['beams']['*0']['*0']['minor']['value']
    else:
        bmaj_dirty=imhead(diff_dirty)['restoringbeam']['major']['value']
        bmin_dirty=imhead(diff_dirty)['restoringbeam']['minor']['value']
        bmaj_clean=imhead(diff_clean)['restoringbeam']['major']['value']
        bmin_clean=imhead(diff_clean)['restoringbeam']['minor']['value']
        

    # Sum over high PB area 
    maskarea  = '\'' + pbmap + '\'' + '>' + str(pbcut)           # CASA LEL friendly
    if mask != '':
        maskarea = maskarea + '&&' + mask
    sum_dirty = imstat(diff_dirty,mask=maskarea)['sum'][0]
    sum_clean = imstat(diff_clean,mask=maskarea)['sum'][0]
    sum_dirty = sum_dirty * np.abs(dx_dirty*dy_dirty) / (cbm*bmaj_dirty*bmin_dirty)
    sum_clean = sum_clean * np.abs(dx_clean*dy_clean) / (cbm*bmaj_clean*bmin_clean)
    
    # Calculate beam ratio
    #    Omega_dirty/Omega_clean = sum_clean/sum_dirty
    # ------------------------------------------------
    omegarat = sum_clean/sum_dirty

    # Scale residual image and re-calculate cleaned image
    # ---------------------------------------------------
    immath(imagename=[resid],expr='IM0*'+str(omegarat),outfile=newresid)
    immath(imagename=[diff_clean,newresid],expr='IM0+IM1',outfile=newclean)
    immath(imagename=[newclean,pbmap],expr='IM0/IM1',outfile=newpbcor)    


    # Remove temp scratch directory
    # -----------------------------
    shutil.rmtree(dirname)

    # Put missing header key in new maps
    imhead(newresid,mode='put',hdkey='bunit',hdvalue='Jy/beam')
    imhead(newclean,mode='put',hdkey='bunit',hdvalue='Jy/beam')
    imhead(newpbcor,mode='put',hdkey='bunit',hdvalue='Jy/beam')    

    # Print
    # -----

    print("\nTP2VISTWEAK: 'ImageExprCalculator::compute+' warning is harmless - ignore.")
    print("Stat: %8s %8s %10s %10s %10s" % \
        ("Bmaj","Bmin","Sum(dirty)","Sum(clean)", "dirty/clean"))
    print("      %8.3f %8.3f %10.4f %10.4f %10.4f" % \
        (bmaj_clean,bmin_clean,sum_dirty,sum_clean,omegarat))
    print("      %8.3f %8.3f" % \
        (bmaj_dirty,bmin_dirty))

    print("Scale residual image %s - multiply %f" % (resid,omegarat))
    print("     New residual image: %s" % (newresid))
    print("Re-compute cleaned image")
    print("     New clean image: %s" % (newclean))

    return

    #-end of tp2vistweak()

## =================================
## TP2VISPL: Plot visibility weights
## =================================

def tp2vispl(mslist, ampPlot=True, uvmax = 150.0, uvzoom=50.0, uvbin=0.5, show=False, outfig='plot_tp2viswt.png'):
    """
    Plotting TP, 7m, and 12m MSs
    MS should have been mstransform'd to the same freq range
    Parameters:
    -----------
    # need at least msTP
    mslist    list of measurement sets to plot
    ampPlot   True     amp-uvdistance plot
              False    weight-uvdistance plot
    show      True     plot in display as well as in file
              False    not plot in display, but in file
    outfig    file name of output figure
    """

    print("TP2VISPL: Plot MSs - ignores flags")

    # Parameters
    # ----------

    bin      = uvbin                            # rad bin width for ave [meter]
    uvMax    = uvmax                            # max uv for plot [meter]
    uvZoom   = uvzoom                           # max uv for zoom plot [meter]
    ampTPMax = 1.0                              # max TP amplitude ( will auto-scale)

    # Separate MSs and find 
    # ---------------------

    if type(mslist) != type([]): mslist = [mslist]
    ms12   = []
    ms07   = []
    msTP   = []
    clist  = []                                 # color for plot
    for ims in mslist:
        array = guessarray(ims)                 # will complain if not a valid one
        if array   == 'ALMA12':
            ms12.append(ims)
            clist.append('b')                   # blue for 12m
        elif array == 'ALMA07':
            ms07.append(ims)
            clist.append('g')                   # grean for 12m
        elif array == 'VIRTUAL':
            msTP.append(ims)
            clist.append('r')                   # grean for 12m
        else:
            return                              # otherwise index error
        

    # Open reference MS (preferably, TP) and obtain max flux channel
    # --------------------------------------------------------------

    if msTP != []:                              # if MS for TP exists
        msfile = msTP[0]                        # use it as freq reference
    else:                                       # otherwise
        msfile = mslist[0]                      # use the first
    ms.open(msfile)                             # open MS
    ms.selectinit(reset=True)                   # all SPWs

    print("Pick up max flux channel in %s" % (msfile))
    cfreq  = ms.getdata('axis_info')['axis_info']['freq_axis']['chan_freq']
                                                # (freq,spw)
    cfreq  = np.transpose(cfreq[:,0]) / 1.0e9   # pick first spw
    asum   = ms.getdata('amplitude')['amplitude'] # (pol,freq,vis)
    asum   = asum.sum(axis=2).sum(axis=0)       # sum over vis & pol
    maxc   = np.argmax(asum)                    # max flux channel
    targetfreq = cfreq[maxc]                    # target freq for plot
    ms.close()

    print("   (chan,freq) = (%d, %f GHz)" % (maxc,targetfreq))

    del asum,maxc

    # Setup figures
    # -------------

    plt.ioff()                                  # no interactive mode
    fig  = plt.figure()                         # set canvas
    axtl = fig.add_subplot(2,2,1)               # top-left
    axtr = fig.add_subplot(2,2,2)               # top-right
    axbl = fig.add_subplot(2,2,3)               # bottom-left
    axbr = fig.add_subplot(2,2,4)               # bottom-right

    # Loop over MSs
    # -------------
    for ims in range(len(mslist)):

        # Open MS and find SPWs that contain targetfreq
        # ---------------------------------------------
        msfile = mslist[ims]                    # this MS
        color  = clist[ims]                     # plot color
        iarray = guessarray(msfile)             # array name
        fwhm0  = t2v_arrays[iarray]['fwhm100']  # FHWM at 100GHz [arcsec]

        ms.open(msfile,nomodify=True)           # open MS

        # Find SPWs that include targetfreq
        ms.selectinit(reset=True)               # all spws
        spwinfo  = ms.getspectralwindowinfo()   # spw info
        spwlist  = []
        for ispw in list(spwinfo.keys()):       # loop over SPWs
            nchan  = spwinfo[ispw]['NumChan']   # num of chan
            c1freq = spwinfo[ispw]['Chan1Freq']/1.0e9  # 1st chan freq [GHz]
            cwidth = spwinfo[ispw]['ChanWidth']/1.0e9  # chan width [GHz]
            cfreq  = c1freq + np.arange(nchan)*cwidth  # chan freqs [GHz]
            f0 = c1freq                         # first chan [GHz]
            f1 = f0 + cwidth * (nchan-1)        # last chan [GHz]
            if nchan==1:
                spwlist.append(ispw)            # append it                
            elif ((f0 - targetfreq)*(f1 - targetfreq)<0):# if incl. target freq
                spwlist.append(ispw)            # append it

        # Read data
        # ---------
        fid = np.array([])                      # field id
        uu  = np.array([])                      # uu
        vv  = np.array([])                      # vv
        wt  = np.array([])                      # weight
        amp = np.array([])                      # amplitude

        # Loop over SPWs
        # --------------
        for ispw in spwlist:

            # SPW info and set constraints to reduce data to load
            spwid  = spwinfo[ispw]['SpectralWindowId'] # SPW info
            nchan  = spwinfo[ispw]['NumChan']          # num of chan
            c1freq = spwinfo[ispw]['Chan1Freq']/1.0e9  # 1st chan freq [GHz]
            cwidth = spwinfo[ispw]['ChanWidth']/1.0e9  # chan width [GHz]
            cfreq  = c1freq + np.arange(nchan)*cwidth  # chan freqs [GHz]
            fwhm   = fwhm0*(100.0/c1freq)/60.0         # FWHM at freq [arcmin]
            barea  = np.pi*(fwhm/2.0)**2               # beam area [amin2]
            ichan  = np.argmin(np.abs(cfreq - targetfreq)) # closest to target

            # Limit data to load
            ms.selectinit(reset=True)                  # needed since casa 5.3.0-97
            if not ms.selectinit(datadescid=spwid):    # this SPW only
                print("MS.SELECTINIT bad selection for spwid=%d - CASA bug?" % spwid)
                continue
            if not ms.select({'uvdist':[0.0,uvMax]}):  # limit uv range
                print("MS.SELECT nothing returned for spwid=%d - CASA bug?" % spwid)
                continue

            # Read parameters [note: wt(pol,vis)]
            fid    = np.append(fid,ms.getdata('field_id')['field_id'])
            uu     = np.append(uu,ms.getdata('u')['u'],axis=0)  # meter
            vv     = np.append(vv,ms.getdata('v')['v'],axis=0)  # meter
            npnt   = len(np.unique(ms.getdata('field_id')['field_id']))
            wtemp  = ms.getdata('weight')['weight'].sum(axis=0) # sum pol
            wtemp  = wtemp/npnt/barea/np.abs(cwidth)            # /pnt/amin2/GHz

            # Append
            wt = np.append(wt, wtemp,axis=0)

            # Amplitude
            if ampPlot:                         # if plot amp
                ms.selectchannel(1,ichan,1,1)   # nchan,start,width,inc
                amp0  = ms.getdata('amplitude')['amplitude'].mean(axis=(0,1))
                                                # ave for pol, spw
                amp   = np.append(amp,amp0)     # append
                if iarray == 'VIRTUAL':         # store max for TP
                    ampTPMax = np.amax([ampTPMax,np.amax(amp0)])

            del wtemp, amp0

            # print
            print("%30s: (spw,chan,freq,fwid) = (%3d, %5d, %10.6f, %10.6f)" \
                % (msfile,spwid,ichan,cfreq[ichan],cwidth))

        ms.close()                              # Close MS

        # Remove data with zero weights and calc params
        # ---------------------------------------------

        idx = wt > 0.0
        uu  = uu[idx]
        vv  = vv[idx]
        wt  = wt[idx]
        if ampPlot: amp = amp[idx]

        uvdist   = np.sqrt(uu*uu + vv*vv)       # uv distance
        fid      = np.unique(fid)               # unique field ids
        nfid     = fid.size                     # num of fields/pointings

        # Calculate averages in bins
        # --------------------------

        uvbins   = np.arange(0.0,uvdist.max() + bin, bin)
        digit    = np.digitize(uvdist,uvbins)
        uvarea   = np.pi*np.diff(uvbins*uvbins)
        wtbins   = [wt[digit==i].sum() for i in range(1,len(uvbins))]
        wtbins   = wtbins/uvarea
        uvbins   = uvbins[1:]
        wtbins   = wtbins/nfid                  # per pointing

        del digit, uvarea

        # Plot
        # ----

        # Top-left: uu vs vv
        axtl.scatter( uu, vv,marker='.',s=0.2,c=color,lw=0)
        axtl.scatter(-uu,-vv,marker='.',s=0.2,c=color,lw=0)

        # Top-right: uvdist vs amplitude or weight [Zoom-up]
        if ampPlot:
            axtr.scatter(uvdist,amp,marker='.',s=0.2,c=color,lw=0)
        else:
            axtr.scatter(uvdist,wt,marker='.',s=0.2,c=color,lw=0)

        # Bottom-right: uvdist vs wtdens [zoom-up]
        axbr.plot(uvbins,wtbins,c=color,drawstyle='steps-mid')

        # Bottom-left: uvdist vs wtdens
        axbl.plot(uvbins,wtbins,c=color,drawstyle='steps-mid',label=ms)

        wtbins = wtbins[wtbins>0]
        print("weight min/max ",wtbins.min(),wtbins.max())
        del uu,vv,uvdist,wt,uvbins,wtbins

    # Plot frames, scales, etc
    # ------------------------
    fontsize=10

    axtl.set_aspect(1.0)                        # top-left
    axtl.set_xlim(-uvZoom, uvZoom)
    axtl.set_ylim(-uvZoom, uvZoom)
    axtl.set_xlabel("u (meter)",fontsize=fontsize)
    axtl.set_ylabel("v (meter)",fontsize=fontsize)
    axtl.tick_params(axis='both',which='major',labelsize=fontsize)

    axtr.set_xlim(0.0, uvZoom)                  # top-right
    axtr.set_xlabel("uvdistance (meter)",fontsize=fontsize)
    if ampPlot:
        axtr.set_ylim(-0.1,ampTPMax*1.1)
        axtr.set_ylabel("amplitude",fontsize=fontsize)
    else:
        axtr.set_ylabel("weight [per visibility]",fontsize=fontsize)
    axtr.tick_params(axis='both',which='major',labelsize=fontsize)

    axbr.set_xlim(0.0,uvZoom)                   # bottom-right
    axbr.set_yscale('log')
    axbr.set_xlabel("uvdistance (meter)",fontsize=fontsize)
    axbr.set_ylabel("weight density [/GHz/pnt/arcmin2]",fontsize=fontsize)
    axbr.tick_params(axis='both',which='major',labelsize=fontsize)

    axbl.set_xlim(0.0, uvMax)                   # bottom-left
    axbl.set_yscale('log')
    axbl.set_xlabel("uvdistance (meter)",fontsize=fontsize)
    axbl.set_ylabel("weight density [/GHz/pnt/arcmin2]",fontsize=fontsize)
    axbl.tick_params(axis='both',which='major',labelsize=fontsize)

    # Legend [conflict with the MS functions of CASA Toolkit]
    #    axtr.legend(loc=1,prop={'size':'x-small'})

    # Draw
    # ----
    plt.savefig(outfig)
    print("Output fig in %s" % (outfig))
    if show:
        plt.show()
    else:
        plt.close('all')

    #-end of tp2vispl()
