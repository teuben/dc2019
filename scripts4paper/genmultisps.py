# Script to plot the power spectra of multiple user provided general 2D FITS files
#
# authors: Nickolas Pingel Nickolas.Pingel@anu.edu.au"
#          Dirk Petry dpetry@eso.org
#
# 
#  For CASA 6.1.0, the following packages need to be pip installed:
#   turbustat
#   sklearn
#   statsmodels
#   radio_beam
#   scikit-image

## imports
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit
import argparse
from turbustat.statistics import PowerSpectrum
import astropy.units as u
import matplotlib 
import matplotlib.pyplot as pyplot
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

## define linear fitting function
def linFunc(x, slope, b):
    return x*slope+b


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

        ## check for degenerate stokes axis and remove
        if len(image.shape) > 3:
            image = image[0, :, :]

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
            print('Missing beam information in header, we will continue with units of pixels')

        if not noBeamInfo:
            print('pixSize bmaj bmin ', pixSize, bmaj, bmin)

        ## set up power spectrum object
        pspec = PowerSpectrum(image, header = hdu[0].header)
        ## compute power spectrum
        if pixUnits == True and noBeamInfo == False:
            pix_units = u.pix**-1
            pspec.run(verbose = False, xunit = pix_units, fit_2D = False, radial_pspec_kwargs={'mean_func': np.nanmedian})
            angularScales = pspec.freqs**(-1)
            lowCut = pspec.low_cut**(-1)
            highCut = pspec.high_cut**(-1)
        elif noBeamInfo == True and pixUnits == True:
            pix_units = u.pix**-1
            pspec.run(verbose = False, xunit = pix_units, fit_2D = False, radial_pspec_kwargs={'mean_func': np.nanmedian})
            angularScales = pspec.freqs**(-1)
            lowCut = pspec.low_cut**(-1)
            highCut = pspec.high_cut**(-1)
        elif noBeamInfo == True and pixUnits == False:
            pspec.run(verbose = False, xunit = u.arcsec**-1, fit_2D = False, radial_pspec_kwargs={'mean_func': np.nanmedian})
            angularScales = pspec.freqs**(-1)*pixSize/60.*u.arcmin/u.pix ## in arcmins
            lowCut = pspec.low_cut**(-1)*pixSize/60.0*u.arcmin/u.pix 
            highCut = pspec.high_cut**(-1)*pixSize/60.0*u.arcmin/u.pix	
        else: # i.e.  noBeamInfo == False and pixUnits == False
            myhighcut = 1/bmaj
            print('my highcut ', myhighcut)
            pspec.run(verbose = False, xunit = u.arcsec**-1, high_cut = myhighcut, fit_2D = False, radial_pspec_kwargs={'mean_func': np.nanmedian})
            angularScales = pspec.freqs**(-1)*pixSize/60.*u.arcmin/u.pix ## in arcmins
            lowCut = pspec.low_cut**(-1)*pixSize/60.0*u.arcmin/u.pix 
            highCut = pspec.high_cut**(-1)*pixSize/60.0*u.arcmin/u.pix	

        ## unpack the output
        powerVals = pspec.ps1D
        powerValsStd = pspec.ps1D_stddev
        powerSpecIm = pspec.ps2D

        ## convert to log space
        logErrors= powerValsStd/(powerVals*np.log(10))
        logPwr = np.log10(powerVals)
        logAngScales= np.log10(angularScales.value)
        logPowerSpecIm = np.log10(powerSpecIm)

        if noBeamInfo == True:
            ## fit from large-scale to brk 
            coeffs, matcov = curve_fit(linFunc, logAngScales, logPwr, [1,1])
            perr = np.sqrt(np.diag(matcov))
        else:
            beamInd = np.where(logAngScales > np.log10(bmaj/u.arcsec/60.))
            print(beamInd)
            print(beamInd[-1])
            coeffs, matcov = curve_fit(linFunc, logAngScales[:beamInd[0][-1]], logPwr[:beamInd[0][-1]], [1,1])
            perr = np.sqrt(np.diag(matcov))

        ## finally, do the plotting

        ## plot full power spectra ##
        ax.plot(logAngScales[1:], logPwr[1:], label='Data '+str(imnumber), color=tableau20[imnumber])

        ## fill inbetween for errors ##
        #ax.fill_between(logAngScales, logPwr-logErrors, logPwr+logErrors, color=tableau20[1])

        ## overplot fit ##
        if noBeamInfo == False:
            ax.plot(logAngScales[:beamInd[0][-1]], linFunc(logAngScales[:beamInd[0][-1]], coeffs[0], coeffs[1]), color='black', linestyle='--', label = 'PL: %.2f+/-%.2f' % (coeffs[0], perr[1]))
        else:
            ax.plot(logAngScales, linFunc(logAngScales, coeffs[0], coeffs[1]), color='black', linestyle='--', label = 'PL: %.1f+/-%.1f' % (coeffs[0], perr[0]))
        ## set x and y limits ##
        ax.set_xlim(np.max(logAngScales)+0.25, np.min(logAngScales) - 0.25)

        ## show fit limits ##
        ax.axvline(np.log10(lowCut.value), color = tableau20[imnumber], linestyle = '-.')
        ax.axvline(np.log10(highCut.value), color= tableau20[imnumber], linestyle = '--')

        imnumber += 1

    # end for


    if pixUnits == True:
        ax.set_xlabel(r'$log_{10}\left(\rm 1/pix\right)$')
    else:
        ax.set_xlabel(r'$log_{10}\left(\rm arcmin\right)$')

    ax.set_ylabel(r'$log_{10}\left(\rm Power\right)$')
    pyplot.legend(loc='upper right', fontsize=6)

    if save == True:
        pyplot.savefig(fitsimages[0]+'_and_others.sps.pdf')
    
    pyplot.show()

    return True
