'''
Instructions on how to create cube of Gaussian beams in casa/python for SD data.


Requirements: 

Previously created SD fits data cube. This will be used for header info and psf cube dimensions. Code below assumes beam per channel.


Notes:

The code below creates a cube of psf's that are based on the FWHM values of the beams in the SD data cube.

This code uses the componentlist toolkit to create Gaussian beams placed in the center of the image for every channel. 

Other single dish telescope data should work with this code as long as the beam can be approximated by a Gaussian. 


IMPORTANT: 

The equation for fluxval below is the integrated flux of the entire Gaussian to ensure that the peak of the Gaussian is at 1 Jy, which is important for deconvolution.


Code:
'''

#############################################################
## Load in some modules in case you need them

import numpy as np
import pyfits
from scipy import constants
import math


## Blank the SD cube. We will fill this new cube with the psf's.




## SD CASA image name

sdname = ''

importfits(imagename=sdname+'.im',fitsimage=sdname+'.fits')

# zero out data cube
immath(imagename=sdname+'.fits',mode='evalexpr',expr='IM0*0.0',outfile='beams.im')

## Get header info and beam per channel info

hdulist = pyfits.open(sdname+'.fits') # load in data, beam info, and headers

beams = hdulist[1].data    # beam info
nchans = len(beams)        # number of chans
crval1 = hdulist[0].header['crval1'] # ra center
the_ra = qa.quantity(str(crval1)+'deg')
the_ra = (qa.angle(the_ra,prec=11,form=['time']))[0]
crval2 = hdulist[0].header['crval2'] # dec center
the_dec = qa.quantity(str(crval2)+'deg')
the_dec = (qa.angle(the_dec,prec=11,form=['dig2']))[0]
crval3 = hdulist[0].header['crval3'] # start freq
imcent = ['J2000',the_ra,the_dec]
cdelt3 = hdulist[0].header['cdelt3']  # the change in freq per chan
cdelt2 = abs(hdulist[0].header['cdelt2']) # the change in dec in degs from pixel to pixel
arcsec_per_pxl = cdelt2*3600.0            # converted to arcsec


!cp -r beams.im beams_axs.im
ia.open('beams_axs.im')       # new image tool
frequency = crval3            # starting freq
cl.close()                    # close any comp lists open
cl.done()
cs=ia.coordsys()              # create coordsys tool from image
ia.setbrightnessunit('Jy/pixel') # set units in image to Jy/pixel

#Start looping over chan/planes creating Gaussian beams.

for i in range(nchans): 

    majornum = beams[i][0]    # the major axis FWHM of the beam
    major = str(majornum)+'arcsec'
    minor = major        # the minor axis FWHM of the beam (the same)

    ## the integrated flux needed for a peak of 1Jy

    fluxval = 2.0*np.pi*((float(majornum)/arcsec_per_pxl/math.sqrt(8.0*math.log(2.0)))**2.0) 

    freqstr = str(frequency)+'Hz'

    ## create region for adding comp list to later
    reg=rg.frombcs(csys=cs.torecord(),shape=ia.shape(),chans=str(i)) 

    ## create Gaussian components
    cl.addcomponent(flux=fluxval,fluxunit='Jy',polarization='Stokes',
                    dir=imcent,shape='gaussian',majoraxis=major,
                    minoraxis=minor,positionangle='0.0deg',
                    freq=freqstr,spectrumtype='constant')

    ia.modify(cl.torecord(),subtract=False,region=reg)        # add the gaussian to the blanked data cube per plane
    cl.close()                                                # close the comp list
    cl.done()
    frequency += cdelt3                                       # advance the frequency by the channel width

ia.setbrightnessunit('')            # ensure the units are Jy/pixel
ia.close()                          # close the image tool (saves the image)

## Switch Stokes and Freq axis so that dimensions = [ra,dec,freq,stokes] for convenience in CASA

imtrans(imagename='beams_axs.im',outfile='SDcube.psf',order='0132')   # switch stokes (2) and freq (3) axes
imtrans(imagename=sdname+'.im',outfile=sdname+'trans.im',order='0132')   # switch stokes (2) and freq (3) axes


#############################################################
