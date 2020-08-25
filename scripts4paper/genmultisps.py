# Script to plot the power spectra of multiple user provided general 2D FITS files
#
# authors: Nickolas Pingel Nickolas.Pingel@anu.edu.au
#          Dirk Petry dpetry@eso.org
#
# 
#  For CASA 6.1.0, the following packages need to be pip installed:
#   astropy
#   sklearn
#   statsmodels
#   radio_beam
#   scikit-image

## imports
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit
from scipy import stats
from scipy import signal
from scipy import interpolate
import argparse
#from turbustat.statistics import PowerSpectrum
import astropy.units as u
import matplotlib 
import matplotlib.pyplot as pyplot
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

## define linear fitting function
def linFunc(x, slope, b):
    return x*slope+b

## define function to compute MAD
MAD = lambda x: np.median(np.abs(x - np.median(x)))

## define function to return 1D SPS
def compute_1D_SPS(image):
    ## mask out image NaN's
    nan_inds = np.isnan(image)
    image[nan_inds] = 0.

    ## mask out pixels that are within 10% of the edge
    y_mask = np.int(image.shape[0]*0.05)
    x_mask = np.int(image.shape[1]*0.05)


    image[0:y_mask, :] = 0
    image[-y_mask:, :] = 0
    image[:, 0:x_mask] = 0
    image[:,-y_mask:] = 0

    ## compute 2D power spectrum
    modulusImage = np.abs(np.fft.fftshift(np.fft.fft2(image)))**2

    ## obtain center pixel coordinates (where the DC power component is located)
    center = np.where(modulusImage == np.nanmax(modulusImage))
    center = [center[0][0], center[1][0]]


    ## define pixel grid
    y = np.arange(-center[0], modulusImage.shape[0] - center[0])
    x = np.arange(-center[1], modulusImage.shape[1] - center[1])
    yy, xx = np.meshgrid(y, x, indexing='ij')
    dists = np.sqrt(yy**2 + xx**2)
    
    ## define spatial frequency grid
    yfreqs = np.fft.fftshift(np.fft.fftfreq(modulusImage.shape[0]))
    xfreqs = np.fft.fftshift(np.fft.fftfreq(modulusImage.shape[1]))
    yy_freq, xx_freq = np.meshgrid(yfreqs, xfreqs, indexing='ij')
    freqs_dist = np.sqrt(yy_freq**2 + xx_freq**2)
    zero_freq_val = freqs_dist[np.nonzero(freqs_dist)].min() / 2.
    freqs_dist[freqs_dist == 0] = zero_freq_val
    
    ## define bin spacing
    max_bin = 0.5
    min_bin = 1.0 / np.min(modulusImage.shape)
    nbins = int(np.round(dists.max()) + 1)
    bins = np.linspace(min_bin, max_bin, nbins + 1)
    finite_mask = np.isfinite(modulusImage)
    ## compute the radial profile using median values within each annulus
    ps1D, bin_edges, cts = stats.binned_statistic(freqs_dist[finite_mask].ravel(), modulusImage[finite_mask].ravel(), bins=bins, statistic='median')
    ## compute MAD uncertainties
    ps1D_MADErrs, bin_edges, cts = stats.binned_statistic(freqs_dist[finite_mask].ravel(), modulusImage[finite_mask].ravel(), bins=bins, statistic=MAD)
    bin_cents = (bin_edges[1:] + bin_edges[:-1]) / 2.
    ## return profile & errors (in linear space) and bin centers for x-axis
    return ps1D, ps1D_MADErrs, bin_cents*1/u.pix


def genmultisps(fitsimages, save=False):
    """
    gensps
    Script to plot the power spectra of a user provided general 2D FITS file
     Arguments: 
        fitsimages - list of names of input images
        save      - save plot? (default False)
    """

    matplotlib.rc('font', family='sans-serif') 
    matplotlib.rc('font', serif='Helvetica Neue') 
    matplotlib.rc('text', usetex='false') 

    # These are the "Tableau 20" colors as RGB.
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    # Scale the RGB values to the [0, 1] range, which is the format matplotlib 
    # accepts.
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    if type(fitsimages) != list or len(fitsimages)==0:
        print("ERROR: fitsimages needs to be non-empty list")
        return False

    # initialise plotting
    fig, ax = pyplot.subplots(figsize = (6,6))

    ## set plotting parameters
    majorYLocFactor = 2
    minorYLocFactor = majorYLocFactor/2.
    majorXLocFactor = 0.5
    minorXLocFactor = majorXLocFactor/4.
    
    majorYLocator = MultipleLocator(majorYLocFactor)
    majorYFormatter = FormatStrFormatter('%d')
    minorYLocator = MultipleLocator(minorYLocFactor)
    majorXLocator = MultipleLocator(majorXLocFactor)
    majorXFormatter = FormatStrFormatter('%.1f')
    minorXLocator = MultipleLocator(minorXLocFactor)

    ## set tick mark parameters
    ax.yaxis.set_major_locator(majorYLocator)
    ax.yaxis.set_major_formatter(majorYFormatter)
    ax.yaxis.set_minor_locator(minorYLocator)
    ax.xaxis.set_major_locator(majorXLocator)
    ax.xaxis.set_major_formatter(majorXFormatter)
    ax.xaxis.set_minor_locator(minorXLocator)


    imnumber = 0

    for fitsimage in fitsimages:

        if type(fitsimage) != str or len(fitsimage)==0:
            print('ERROR: empty fitsimage name')
            return False

        fitsName = fitsimage

        ## open the header data unit
        hdu = fits.open(fitsName)

        ## open up 2D image
        image = hdu[0].data

        ## set useful variables
        pixUnits = False
        noBeamInfo = False
        fit = True

        ## check for degenerate stokes axes and remove
        if len(image.shape) == 4:
            image = image[0, 0, :, :]
        elif len(image.shape) == 3:
            image = image[0, :, :]
        else:
            print('No degenerate axes...')

        ## check for relevant header info
        try: 
            pixSize = hdu[0].header['CDELT2']*3600 *u.arcsec
        except (KeyError):
            pixUnits = True
            print('Missing pixel size in header, we will continue with units of pixels')

        try:
            bmaj = hdu[0].header['BMAJ']*3600 * u.arcsec
            bmin = hdu[0].header['BMIN']*3600. * u.arcsec 
        except (KeyError):
            noBeamInfo = True
            print('Missing beam information in header, we will apply no spatial frequency cut-off')
        try:
            fluxUnits = hdu[0].header['BUNIT']
        except (KeyError):
            print('No flux units... assuming Jy/pixel')
            fluxUnits = 'Jy/pixel'

        if fluxUnits == 'Jy/beam':
            print('pixSize bmaj bmin ', pixSize, bmaj, bmin)

            ## convert image to Jy/pixel 
            image*=(pixSize.value)**2/(1.1331*bmaj.value*bmin.value)

        ## apply apodizing kernel to mask pixels within 10% of the edge of the smallest dimension


        ## compute power spectrum
        SPS_1D, MADErrs, spatialFreqs = compute_1D_SPS(image)
        

        ## compute power spectrum
        if pixUnits == True and noBeamInfo == False: ## use pixel units; however, set high spatial frequency cutoff from BMAJ
            angularScales = spatialFreqs**(-1)*u.pix

            ## determine low/high cutoffs indices (where angular scales < 0.5*map/3 & angular scales > BMAJ)
            lowCut_idx = np.where(angularScales < angularScales[0]/3)[0][0]
            bmaj_pix = bmaj/pixSize*u.pix/u.arcsec
            highCut_idx = np.where(angularScales > bmaj_pix)[0][-1]
        elif noBeamInfo == True and pixUnits == True: ## use pixel units with no cutoff from beam (i.e., simulated image)
            angularScales = spatialFreqs**(-1)

            ## determine low/high cutoffs indices (where angular scales < 0.5*map/3 & high cut is the pixel size
            lowCut_idx = np.where(angularScales < angularScales[0]/3)[0][0]
            highCut_idx = -1
        elif noBeamInfo == True and pixUnits == False: ## use angular units but no cutoff from beam (i.e., simulated image)
            angularScales = spatialFreqs**(-1) * pixSize * (1/u.pix)

            ## determine low/high cutoffs indices (where angular scales < 0.5*map/3 & high cut is the pixel size
            lowCut_idx = np.where(angularScales < angularScales[0]/3)[0][0]
            highCut_idx = -1
        else: # i.e.  noBeamInfo == False and pixUnits == False; use angular units and set high-freq cutoff from beam info
            angularScales = spatialFreqs**(-1) * pixSize * (1/u.pix) ## in arcsec
            ## determine low/high cutoffs indices (where angular scales < 0.5*map/3 & angular scales > BMAJ)
            lowCut_idx = np.where(angularScales < angularScales[0]/3)[0][0]
            highCut_idx = np.where(angularScales > bmaj)[0][-1]

            if lowCut_idx >= highCut_idx: ## likely dealing with single-dish/tp image => DON'T FIT
                fit = False

        print('low/high spatial freq. cutoffs [arcsec]: ', angularScales[lowCut_idx].value, angularScales[highCut_idx].value)

        ## convert to log space
        logErrors= MADErrs/(SPS_1D*np.log(10))
        logPwr = np.log10(SPS_1D)
        logAngScales= np.log10(angularScales.value)

        if fit:
            ## fit from large-scale to brk    
            coeffs, matcov = curve_fit(linFunc, logAngScales[lowCut_idx:highCut_idx], logPwr[lowCut_idx:highCut_idx], [1,1])
            perr = np.sqrt(np.diag(matcov))

        ## finally, do the plotting

        ## plot full power spectra ##
        ax.plot(logAngScales, logPwr, label='Data '+str(imnumber), color=tableau20[imnumber])

        ## fill inbetween for errors ##
        #ax.fill_between(logAngScales, logPwr-logErrors, logPwr+logErrors, color=tableau20[1])

        if fit:
            ax.plot(logAngScales[lowCut_idx:highCut_idx], linFunc(logAngScales[lowCut_idx:highCut_idx], coeffs[0], coeffs[1]), color='black', linestyle='--', label = 'PL: %.1f+/-%.1f' % (coeffs[0], perr[0]))
        
        ## set x and y limits ##
        if imnumber == 0:
            ax.set_xlim(np.max(logAngScales)+0.25, np.min(logAngScales) - 0.25)

        ## show fit limits ##
        ax.axvline(logAngScales[lowCut_idx], color = tableau20[imnumber], linestyle = '-.')
        ax.axvline(logAngScales[highCut_idx], color= tableau20[imnumber], linestyle = '--')

        imnumber += 1

    # end for


    if pixUnits == True:
        ax.set_xlabel(r'$log_{10}\left(\rm 1/pix\right)$')
    else:
        ax.set_xlabel(r'$log_{10}\left(\rm arcsec\right)$')

    ax.set_ylabel(r'$log_{10}\left(\rm Power\right)$')
    #pyplot.legend(loc='upper right', fontsize=6)
    pyplot.legend(loc='upper right', prop={'size':8})

    if save == True:
        pyplot.savefig(fitsimages[0]+'_and_others.sps.pdf')
    
    pyplot.show()

    return True
