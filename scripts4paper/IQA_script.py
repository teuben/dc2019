#########################################################
## Image Quality Assessment (IQA) scripts for CASA
##
## Created: Feb. 2020
## Last modified: Nov. 2020
## Authors:
##  1.- Genearal IQA tests: Alvaro Hacar (alvaro.hacar@univie.ac.at)
##  2.- Power spectra: Nickolas Pingel (Nickolas.Pingel@anu.edu.au), Dirk Petry (dpetry@eso.org)
##  3.- Aperture methods: Brian Mason (bmason@nrao.edu), Alvaro Hacar (alvaro.hacar@univie.ac.at)
##
#########################################################

##############################################################################################
# 1.- General IQA tests
# Script to obtain general IQA tests (Aperture, Fidelity, Differences) for both continuum and cube images
#
# authors: Alvaro Hacar (alvaro.hacar@univie.ac.at)

## Functions

## keywords
##
## FITSfile = path to FITS file
## convo_file = path to CASA image to be convolved
## beam_final = final beamsize (in arcsec)
## target_image = target image (e.g., Interferometric image)
## ref_image = reference image (e.g., TP image)
##

##-------------------------------------------------------
## Imports

from scipy import fftpack
from astropy.io import fits
import numpy as np
import pylab as py
import matplotlib.pyplot as plt
import os
import copy
from numpy import inf
from matplotlib.colors import LogNorm 
from scipy.stats import kurtosis, skew

#import casatools# as cto
#import casatasks# as cta
from casatasks import *

## IQA colours
IQA_colours = ["red", "blue", "orange", "green" , "cyan", "pink", "brown","yellow","magenta","black"]

##-------------------------------------------------------
## Image manipulation

## Convert FITS files into CASA images
def fits2CASA(FITSfile):
    print(FITSfile)
    os.system("rm -rf "+  FITSfile+".image")
    importfits(fitsimage=FITSfile,imagename=FITSfile+'.image')

## Convert FITS files into CASA images
def CASA2fits(CASAfile):
    print(CASAfile)
    os.system("rm -rf "+  CASAfile+".fits")
    exportfits(imagename=CASAfile,fitsimage=CASAfile+".fits")

## same as fits2CASA but for a list of FITS
def fitslist2CASA(FITSfile):
    for i in FITSfile:
        print(i)
        os.system("rm -rf "+ i+".image")
        importfits(fitsimage=i,imagename=i+'.image')

## Convolve CASA image with a final resolution (beam_final)
def get_convo(convo_file,beam_final):
    imsmooth(imagename= convo_file,
        outfile= convo_file + '_conv' + str(beam_final),
        kernel='gauss',
        major=str(beam_final)+'arcsec',
        minor=str(beam_final)+'arcsec',
        pa='0deg',
        targetres=True)

## same as get_convo but for FITS files
def getFITS_convo(FITSfile,beam_final):
    # FITS into CASA
    convo_file = FITSfile+'.image'
    os.system("rm -rf "+convo_file)
    importfits(fitsimage=FITSfile,imagename=convo_file)
    # convolution
    imsmooth(imagename= convo_file,
        outfile= convo_file + '_conv' + str(beam_final),
        kernel='gauss',
        major=str(beam_final)+'arcsec',
        minor=str(beam_final)+'arcsec',
        pa='0deg',
        targetres=True)

## Convolve CASA image with a final resolution (beam_final)
def get_convo2target(convo_file,ref_image):
    # Get beam info from refence image
    hdr = imhead(ref_image,mode='summary')
    beam_major = hdr['restoringbeam']['major']
    beam_minor = hdr['restoringbeam']['minor']
    beam_PA = hdr['restoringbeam']['positionangle']
    # Convolution into the same beam as the reference
    os.system("rm -rf " + convo_file + '_conv' + str(round(beam_major['value'])))
    imsmooth(imagename= convo_file,
        outfile= convo_file + '_conv' + str(round(beam_major['value'])),
        kernel='gauss',
        major=beam_major,
        minor=beam_minor,
        pa=beam_PA,
        targetres=True)

def get_beam(image):
    # Get beam info from image: return [maj, min, pa, effbeamsize]
    hdr = imhead(image,mode='summary')
    beam_major = hdr['restoringbeam']['major']
    beam_minor = hdr['restoringbeam']['minor']
    beam_PA = hdr['restoringbeam']['positionangle']
    effbeamsize = np.sqrt((beam_major.get("value")**2.)/2. + (beam_minor.get("value")**2.)/2.)

    return [beam_major, beam_minor, beam_PA, effbeamsize]
    
## same as get_convo2target but for FITS
def getFITS_convo2target(convo_file,ref_image):
    # FITS into CASA
    convo_file = FITSfile+'.image'
    os.system("rm -rf "+convo_file)
    importfits(fitsimage=FITSfile,imagename=convo_file)
    # Get beam info from refence image
    hdr = imhead(ref_image,mode='summary')
    beam_major = hdr['restoringbeam']['major']
    beam_minor = hdr['restoringbeam']['minor']
    beam_PA = hdr['restoringbeam']['positionangle']
    # Convolution into the same beam as the reference
    os.system("rm -rf tmp.tmp")
    imsmooth(imagename= convo_file,
        outfile= "tmp.tmp",
        kernel='gauss',
        major=beam_major,
        minor=beam_minor,
        pa=beam_PA,
        targetres=True)
    os.system("rm -rf convo2ref")
    imregrid(imagename= "tmp.tmp",
         template= ref_image,
         output= 'convo2ref')
    os.system("rm -rf tmp.tmp")

## Convolve CASA image with a final resolution (beam_final)
def get_convo2target(convo_file,ref_image):
    # Get beam info from refence image
    hdr = imhead(ref_image,mode='summary')
    beam_major = hdr['restoringbeam']['major']
    beam_minor = hdr['restoringbeam']['minor']
    beam_PA = hdr['restoringbeam']['positionangle']
    ref_unit = hdr['unit']
    # Convolution into the same beam as the reference
    os.system("rm -rf tmp.tmp")
    imsmooth(imagename= convo_file,
        outfile= "tmp.tmp",
        kernel='gauss',
        major=beam_major,
        minor=beam_minor,
        pa=beam_PA,
        targetres=True)
    #imhead(convo_file, mode='put', hdkey='Bunit', hdvalue=ref_unit)
    os.system("rm -rf convo2ref")
    imregrid(imagename= "tmp.tmp",
         template= ref_image,
         output= 'convo2ref')
    imhead('convo2ref', mode='put', hdkey='Bunit', hdvalue=ref_unit)   # Lydia's modification to avoid lost bunits

    os.system("rm -rf tmp.tmp")

## Resample 
def resample_velaxis(image,template):
    os.system('rm -rf '+image+'_resvel')
    imregrid(imagename= image,
         template= template,
         axes=[2],
         output= image+'_resvel')

# Mask data (typically reference image)
def mask_image(myimage,threshold=0.0,relative=False):
    """
    mask_image (A. Hacar, Univ. of Vienna)

    Mask an image (typicaly your reference) below an intensity threshold.
    Thresholding is recommended to avoid noisy data in many of the IQA tests
    Arguments:
      myimage - image to be masked
      threshold - value for thresholding
      relative - (default False) 
         False = threshold is taken as absolute value (see image flux units)
         True = threshold value is measured as rms fraction (aka sigma)
    """
    print("=========================================")
    print(" mask_image(): masking image ")
    print("=========================================")
    print(" Original image : " + str(myimage))
    # Create a copy of your image
    os.system('rm -rf masked.tmp')
    os.system('cp -r ' + str(myimage) + ' masked.tmp')
    # Create your mask
    ia.open('masked.tmp')
    if (relative == False):
        ia.calcmask(mask= 'masked.tmp >= '+str(threshold), name='mymask')
    if (relative == True):
        ima_sigma = imstat(myimage)["rms"][0]
        ia.calcmask(mask= 'masked.tmp >= '+str(threshold*ima_sigma), name='mymask')
    ia.close()
    os.system('mv masked.tmp ' + str(myimage) + '_masked')
    #makemask(mode='copy',inpimage='masked.tmp',inpmask=['masked.tmp:mymask'],output=str(myimage) + '_masked',overwrite=True)
    print(" New masked image : " + str(myimage) + '_masked')
    print("-----------------------------------------")
    print(" mask_image(): DONE ")
    print("=========================================")

# Check if images have the same axis order as reference
def check_axis(ref_image,target_im=[]):
    print("=========================================")
    print(" check_axis(): checking axis consistency ")
    print("=========================================")
    # reference: check axis 
    axis_ref = imhead(ref_image).get("axisnames")
    print(" Reference image: " + str(ref_image))
    print(" Axis : ("),
    for j in np.arange(np.shape(axis_ref)[0]):
        print(axis_ref[j] + " "),
    print(")")
    print("-----------------------------------------")
    # Targets: check axis
    n = 0
    for i in target_im:
        n = n+1
        axis_target = imhead(i).get("axisnames")
        print(" Target image #" + str(n) + ": " + str(i))
        print(" Axis : ("),
        transpose = -1
        for j in np.arange(np.shape(axis_target)[0]):
            print(axis_target[j] + " "),
            if (axis_ref[j] != axis_target[j]):
                transpose = j
        print(")")
        if (transpose != -1):
            print(" WARNING: Axis do not match reference -> transpose OR drop axis")
            print("          (see also drop_axis function)")
        print("-----------------------------------------")
    print(" check_axis(): DONE ")
    print("=========================================")



def drop_axis(myimage):
    """
    drop_axis (A. Hacar, Univ. of Vienna)
    
    Drop unnecesary axis (e.g. Stokes)
    Arguments:
     myimage : image wher drop_axis will be applied (CASA image)

    Notes:
     Check axis consistency with check_axis()

    Usage:
     drop_axis(myimage)  
    """
    print("=================================================")
    print(" drop_axis(): drop additional axis (e.g. Stokes) ")
    print("=================================================")
    # reference: check axis 
    os.system("rm -rf " + myimage + "_subimage")
    imsubimage(imagename=myimage,outfile=myimage + "_subimage",dropdeg=True)
    print(" Reference image: " + str(myimage))
    print(" New image: " + str(myimage) +"_subimage")
    print("-----------------------------------------")
    print(" drop_axis(): DONE ")
    print("=========================================")

##-------------------------------------------------------
## Quality estimators
## see a detailed discussion in: https://library.nrao.edu/public/memos/ngvla/NGVLA_67.pdf

## Calculate Image Accuracy parameter (Apar)
def image_Apar(image,ref_image):
    """
    image_Apar (A. Hacar, Univ. of Vienna)

    Function to generate A-par maps
    A-par is defined as the relative error between the target and reference images:
    Apar = (image-reference)/abs(reference)

    Arguments:
      image - target image
      ref_image - reference image
    (Note that the target image should have the same resolution as the target one)

    Outputs:
      str(image)+'_Apar' - A-par image

    Description:
      A=0 - Perfect image
      A>1 - target image overestimates the expected flux in the reference
      A<1 - target image underestimates the expected flux in the reference
      A value - relative difference (in %) between the target and the reference
    """
    # Resampling
    os.system('rm -rf tmp_resampled')
    imregrid(imagename= image,
         template= ref_image,
         #axes=[0, 1],
         output= 'tmp_resampled')
    os.system('rm -rf ' + image + '_Apar')
    # Q parameter
    immath(imagename=['tmp_resampled',ref_image], 
        outfile= image + '_Apar',
        expr='(IM0-IM1)/abs(IM1)')
    # Clean-up
    os.system('rm -rf tmp_resampled')

## Calculate image Fidelity
def image_Fidelity(image,ref_image):
    """
    image_Fidelity (A. Hacar, Univ. of Vienna)

    Function to generate Fidelity maps
    Fidelity is defined as the ratio between the reference image and the difference between
    target and the reference images all in absolute terms:
    Fidelity = abs(reference)/abs(image-reference)

    Arguments:
      image - target image
      ref_image - reference image
    (Note that the target image should have the same resolution as the target one)

    Outputs:
      str(image)+'_fidelity' - Fidelity image

    Description:
      The higher the fidelity, the better correspondance between the target and the reference images
    """
    # Resampling
    os.system('rm -rf tmp_resampled')
    imregrid(imagename= image,
         template= ref_image,
         #axes=[0, 1],
         output= 'tmp_resampled')
    # Fidelity parameter
    os.system('rm -rf ' + image + '_Fidelity')
    immath(imagename=['tmp_resampled',ref_image], 
        outfile= image + '_Fidelity',
        expr='abs(IM1)/abs(IM1-IM0)')
    # Clean-up
    os.system('rm -rf tmp_resampled')


## Calculate image Difference
def image_Diff(image,ref_image):
    """
    Generate difference image: Difference = reference-image
    Arguments:
      image - target CASA image
      ref_image - CASA image used as reference
    Output:
      str(image)+'_Diff' = Difference CASA image
    """
    # Resampling
    os.system('rm -rf tmp_resampled')
    imregrid(imagename= image,
         template= ref_image,
         #axes=[0, 1],
         output= 'tmp_resampled')
    # Fidelity parameter
    os.system('rm -rf ' + image + '_Diff')
    immath(imagename=['tmp_resampled',ref_image], 
        outfile= image + '_Diff',
        expr='IM1-IM0')
    # Clean-up
    os.system('rm -rf tmp_resampled')

def noise_image(fitsfile,noise=0.1,noisefile="noise"):
    """
    Generate a nosie FITS with similar properties than fitsfile
    Arguments:
      fitsfile - FITS file used as template
      noise - noise level (in whatever units if fitsfile)
      noisefile - name of the file where the results will be stored (default = "noise"+".fits"
    Output:
      str(noisefile)+'.fits' - FITS noise file
    """
    # Read Templeate
    hdu = fits.open(fitsfile)
    # Copy maks
    mask = np.isnan(hdu[0].data)
    # Create a noise dataset
    hdu[0].data = np.random.normal(0.,noise,(hdu[0].data.shape[0],hdu[0].data.shape[1])) # Noise image
    # 
    hdu[0].data[mask] = np.nan
    # Write to file
    fits.writeto(noisefile+".fits",data=hdu[0].data,header=hdu[0].header,overwrite=True)


##-------------------------------------------------------
## Wrappers

# IQA methods: Accuracy, Fidelity, etc...
def get_IQA(ref_image = '',target_image=[''], pb_image=None, masking_RMS=None, target_beam_index=0):
    """
    get_IQA (A. Hacar, Univ. of Vienna; Dirk Petry, ESO)
    
    Obtain all Image Quality Assesment images
    Arguments:
      ref_image - image used as reference
      target_image - list of images to be compared with reference
      pb_image - primary beam image needed to evaluate assessment area
      masking_RMS - masking RMS in units of Jy/beam of the targer_image (e.g. Interferometric image)
                    Assesssing Mask: AM = 3*masking_RMS*1/PB*(beam_ref/beam_target)
                    (see main paper for further details)
          Note that ideally masking_RMS should correspond to 3*RMS_target, that is, the noise level of the Interferometric images
      target_beam_index - defines which target_image is used to evaluate the targetbeam
    Procedure:
     1.- Each target image will be convolved and resapled into the ref_image resolution and grid.
         Results are stored in: target_image[i]_convo2ref
     2.- The new target_image[i]_convo2ref image is then used to obtain different IQA tests, namely:
        a) Accuracy: target_image[i]_convo2ref_Apar
        b) Fidelity: target_image[i]_convo2ref_Fidelity
     3.- All results are exported into FITS
    Notes:
        - Depending on the image/cube size, this process may take a while
        - Exectute this script to procude the Apar, Fidelity,... images. This script only needs to be executed once
    Example:
      get_IQA(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'], pb_image='Feather.pb', masking_RMS=0.1, target_beam_index=0)

    """
    # Reference image
    print("=============================================")
    print(" get_IQA(): Obtain IQA estimators")
    print(" Reference : "+ str(ref_image))
    print(" Depending on the image/cube size, this process may take a while...")
    print("---------------------------------------------")
    # Target images
    do_mask=False
    if(pb_image!=None and masking_RMS!=None):
        do_mask=True
        myrefbeaminfo = get_beam(ref_image)
        effrefbeam = myrefbeaminfo[3]

        # convolve PB image to reference resolution
        get_convo2target(pb_image,ref_image)
        os.system("mv convo2ref " + pb_image + "_convo2ref")

        mybeaminfo = get_beam(target_image[target_beam_index])
        efftargetbeam = mybeaminfo[3]
       
        # compute masking threshold image temp.mask
        os.system("rm -rf " + target_image[target_beam_index]+'_thrsh')
        immath(imagename=[pb_image+'_convo2ref'], outfile=target_image[target_beam_index]+'_thrsh', expr='3*'+str(masking_RMS)+'*'+str(effrefbeam)+'/'+str(efftargetbeam)+'/IM0')
        os.system("rm -rf temp.mask")
        immath(imagename=[ref_image,target_image[target_beam_index]+'_thrsh'], outfile='temp.mask', expr='iif(IM0>IM1,1,0)')
        # Masking also the reference
        os.system("rm -rf "+ ref_image + "_masked")
        # drop axis leads to crash!
        #drop_axis("temp.mask")  # Regridding mask to ref_image (remove/add extra dim)
        immath(imagename=ref_image,mode='evalexpr',expr='IM0',outfile=ref_image+'_masked',mask='temp.mask')#_subimage')
        exportfits(imagename=ref_image + "_masked",fitsimage=ref_image + "_masked.fits",dropdeg=True,overwrite=True)

    for j in np.arange(0,np.shape(target_image)[0],1):
        # print file
        print(" Target image " + str(j+1) + " : " + str(target_image[j]))
        # Convolve data into reference resolution
        get_convo2target(target_image[j],ref_image)

        # Mask it
        os.system("rm -rf " + target_image[j] + "_convo2ref_masked") 
        if do_mask:
                immath(imagename='convo2ref',mode='evalexpr',expr='IM0',outfile='convo2ref_masked',mask='temp.mask')
        else:
                immath(imagename='convo2ref',mode='evalexpr',expr='IM0',outfile='convo2ref_masked',mask='mask("'+str(ref_image)+'")')
        os.system("rm -rf " + target_image[j] + "_convo2ref")
        os.system("mv convo2ref_masked " + target_image[j] + "_convo2ref")
        #
        # Get Apar, Fidelity, etc... images
        image_Apar(target_image[j] + "_convo2ref",ref_image)
        image_Fidelity(target_image[j] + "_convo2ref",ref_image)
        image_Diff(target_image[j] + "_convo2ref",ref_image)
        # export into FITS
        os.system('rm -rf '+target_image[j] + "_convo2ref*.fits")
        exportfits(imagename=target_image[j] + "_convo2ref",fitsimage=target_image[j] + "_convo2ref.fits",dropdeg=True)
        exportfits(imagename=target_image[j] + "_convo2ref_Apar",fitsimage=target_image[j] + "_convo2ref_Apar.fits",dropdeg=True)
        exportfits(imagename=target_image[j] + "_convo2ref_Fidelity",fitsimage=target_image[j] + "_convo2ref_Fidelity.fits",dropdeg=True)
        exportfits(imagename=target_image[j] + "_convo2ref_Diff",fitsimage=target_image[j] + "_convo2ref_Diff.fits",dropdeg=True)       
        print(" See results in " +target_image[j] + "_convo2ref* images")
        print("---------------------------------------------")
    print(" IQA estimators... DONE")
    print("=============================================")


# Tools for continuum and/or mom0 maps

# Accuracy parameter comparisons
def Compare_Apar(ref_image = '',target_image=[''],
                  save=False, plotname='', 
                  labelname=[''], titlename=''):
    """
    Compare all Apar images (continuum or mom0 maps) (A. Hacar, Univ. of Vienna)

    Arguments:
      ref_image - image used as reference
      target_image - list of images to be compared with reference
      save - save plot? (default = False)
    Requires:
      The script will look for target_image[i]_convo2ref_Apar.fits images produced by the get_IQA() script
    
    Results:
      1- Histogram including the Apar distributions for all input images
      2- Numerical results: Total flux in the image, mean + std + kurtosis + skewness of each histogram 

    Example:
      Compare_Apar(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])

    """
    # Reference image
    print("=============================================")
    print(" Accuracy parameter: comparisons")
    print(" Reference : "+str(ref_image))
    flux0 = np.round(imstat(ref_image)["flux"][0])
    print(" Total Flux = " + str(flux0) + " Jy")
    print("---------------------------------------------")
    # Number of plots
    Nplots = np.shape(target_image)[0]
    # Global comparisons 
    plt.figure(figsize=(8,11))
    grid = plt.GridSpec(ncols=1,nrows=5, wspace=0.3, hspace=0.3)
    ax1 = plt.subplot(grid[0:4, 0])
    # Loop over all images
    for m in np.arange(Nplots):
        # Get total flux in image
        flux = np.round(imstat(target_image[m]+"_convo2ref.fits")["flux"][0])
        # Extract values from file
        nchans, b, mids, h = get_ALLvalues(FITSfile=target_image[m]+"_convo2ref_Apar.fits",xmin=-1.525,xmax=1.525,xstep=0.05)
        # Get mean and std
        meanvalue = np.round(np.average(mids,weights=h),2)
        sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=h)),2)
        # Get skewness and kurtosis of the Apar image
        hdu = fits.open(target_image[m]+"_convo2ref_Apar.fits")
        Adist = hdu[0].data.flatten()
        Adist = Adist[(Adist <= 10.) & (Adist >= -10.)] # remove big outlayers
        skewness = np.round(skew(Adist),3)
        kurt = np.round(kurtosis(Adist),3)
        # Plot results
        if labelname[m]=='':            
            ax1.plot(mids,h,label=target_image[m] + "; A = "+ str(meanvalue) + " +/- " + str(sigmavalue),linewidth=3,c=IQA_colours[m])
        else:
            ax1.plot(mids,h,label=labelname[m] + "; A = "+ str(meanvalue) + " +/- " + str(sigmavalue),linewidth=3,c=IQA_colours[m])
        # Print results on screen
        print(" Target image " + str(m+1) + " : " + str(target_image[m]))
        print(" Total Flux = " + str(flux) + " Jy ("+str(np.round(flux/flux0,2))+"\%)")
        print(" Accuracy:")
        print(" Mean +/- Std. = " + str(meanvalue) + " +/- " + str(sigmavalue))
        print(" Skewness, Kurtosis = " + str(skewness) + " , " + str(kurt) )
        print("................................................")
    # Add Goal line
    plt.vlines(0.,np.min(h[h>0]),np.max(h),linestyle="--",color="black",linewidth=3,label="Goal",alpha=1.,zorder=-2)
    # Plot limits, legend, labels...
    plt.xlim(-1.5,1.5)
    plt.yscale('log')   # Make y axis in log scale
    #plt.legend(loc='lower right')
    plt.legend(bbox_to_anchor=(0.5, -0.1),loc='upper center', borderaxespad=0.)
    plt.xlabel("Accuracy",fontsize=20)
    plt.ylabel(r'# pixels',fontsize=20)
    if titlename=='':
        plt.title("Accuracy Parameter: comparisons",fontsize=16)
    else: 
        plt.title(titlename,fontsize=16)

    # Save plot?
    if save == True:
        if plotname == '':
            plotname="AparALL_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        plt.close()
    # out
    print("---------------------------------------------")
    print(" Accuracy parameter comparisons... DONE")
    print("=============================================")
    return True

def Compare_Apar_signal(ref_image = '',target_image=[''],
            save=False, noise=0.0, plotname='', 
            labelname=[''], titlename=''
            ):
    """
    Compare_Apar_signal (A. Hacar, Univ. of Vienna) 
    
    Compare all Apar images vs signal (continuum or mom0 maps).
    If No. of targets = 1, the mean and std of A-par will be calculated.
    This function can be applied in both cont/mom0 and cubes FITS files.
    
    Arguments:
      ref_image - image used as reference
      target_image - list of images to be compared with reference 
        (recommended to <= 4 targets)
      save - (optional) save plot? (default = False)
      noise - (optional) if noise > 0.0 the evolution of the noise level
        will be displayed  
    
    Requires:
      The script will look for target_image[i]_convo2ref_Apar.fits images produced by the get_IQA() script
    
    Results:
      Apar as function of reference & target signals
    
    Example 1: compare a list of targets
      Compare_Apar_signal(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])
    
    Example 2: investigate singel target (incl. A-par statistics)
      Compare_Apar_signal(ref_image = 'TP_image',target_image=['Feather.image'],noise=0.5)
    
    """
    # Reference image
    print("=============================================")
    print(" A-par vs Signal")
    print("---------------------------------------------")
    # Number of plots
    Nplots = np.shape(target_image)[0]
    # These plots get too crowded with a high number of targets. If No. targets > 4 then exit this function
    if (Nplots > 4):
        print(" Too many targets. Please use <= 4.")
        print(" No plot shown.")
        print("---------------------------------------------")
        print(" A-par vs Signal... DONE")
        print("=============================================")
        return None

    # Figure parameters 
    plt.figure(figsize=(8,14))
    grid = plt.GridSpec(ncols=1,nrows=7, wspace=0.3, hspace=0.3)
    
    # Plot #1: Reference vs A-par
    ax0 = plt.subplot(grid[0:2, 0])
    # Loop over all images
    xmax0 = 0.0; xmin0 = 1E6    # Dummy values
    for m in np.arange(Nplots):
        # Images
        im1 = fits.open(ref_image+".fits")
        im2 = fits.open(target_image[m]+"_convo2ref_Apar.fits")
        # Define plot limits
        ##xmin = np.min(im1[0].data[np.isnan(im1[0].data)==False])
        xmin = np.percentile(im1[0].data[np.isnan(im1[0].data)==False],0.01) #np.im replaced by 0.01 percentile to avoid outlayers
        xmax = np.max(im1[0].data[np.isnan(im1[0].data)==False])
        if (xmax > xmax0):
            xmax0=xmax+xmax/10. # Slightly larger
        if (xmin < xmin0):       
            xmin0=xmin
        if (xmin < 0.0):          #Lydia's modification to avoid negative values!
            xmin0=0.0001
        # Plot results
        ax0.scatter(im1[0].data,im2[0].data,c=IQA_colours[m],marker="o",rasterized=True,edgecolor='none',alpha=0.01)

    # Goal (A-par = 0)
    ax0.hlines(0.,xmin,xmax0,linestyle="--",color="black",linewidth=3,alpha=1.,zorder=2)

    # Calculate mean and sigma if there is only one target
    if (Nplots == 1):
        print("---------------------------------------------")
        print(" A-par values per bin: ")
        # Calculate bins & step in log-scale
        steplog=(np.log10(xmax0)-np.log10(xmin0))/10.
        xvalueslog=np.arange(np.log10(xmin0),np.log10(xmax0),steplog)
        # back to linear scale
        step=10.**steplog
        xvalues=10.**xvalueslog
        # Define stats vectors
        means=np.zeros(len(xvalues))    # Mean
        stds=np.zeros(len(xvalues)) # STD
        medians=np.zeros(len(xvalues))  # Median
        q1values=np.zeros(len(xvalues)) # Q1
        q3values=np.zeros(len(xvalues)) # Q2
  
        # helpers for debugging
        #print(xmin, xmax)        
        #print(xmin0, xmax0)
        #print(xvalues)

        count=0
        for j in xvalueslog:
            # Define bin ranges in log-space
            idx = (im1[0].data >= 10.**j) & (im1[0].data < 10.**(j+steplog)) & (np.isnan(im1[0].data)==False) & (np.isfinite(im1[0].data)==True)
            values = im2[0].data[idx]
            values = values[ (np.isnan(values)==False) & (np.isfinite(values)==True) ] # remove Nan & Inf.
            # Stats
            if (np.shape(values)[0] > 0):
                means[count] = np.mean(values)  # Mean
                stds[count] = np.std(values)    # STD
                medians[count] = np.median(values)  # Median
                q1values[count] = np.percentile(values, 10) # 10% Quartile
                q3values[count] = np.percentile(values, 90) # 90% Quartile
            # Show results on screen
            print("Bin "+str(count+1)+": Ref.Flux = " + str(np.round(10.**(j+steplog/2.),2)) + " ; A = " + str(np.round(means[count],2)) + " +/- " + str(np.round(stds[count],2)) + " ; [Q10,Q90] = ["+ str(np.round(q1values[count],3)) + " , " + str(np.round(q3values[count],3)) +"]")
            # Counter +1
            count+=1
            #
        # Display mean and STD
        ax0.errorbar(10.**(xvalueslog+steplog/2.),means, yerr=stds, fmt='o',c="blue",label=r"|y|$\pm 1 \sigma$ ",linewidth=2,markersize=10,zorder=2,capsize=5)
        #ax0.errorbar(10.**(xvalueslog+steplog/2.),medians, yerr=[q1values,q3values], fmt='o',c="cyan",label=r"[Q1,Median,Q3]",linewidth=2)
        ax0.vlines(10.**(xvalueslog+steplog/2.),q1values,q3values,color="cyan",label=r"[Q10,Q90]",linewidth=5,zorder=1)

    # Show noise effects?
    if (noise > 0):
        xvalues=np.arange(np.log10(xmin0),np.log10(xmax0),(np.log10(xmax0)-np.log10(xmin0))/20.)
        xvalues=10.**xvalues
        ax0.plot(xvalues,noise/np.abs(xvalues),c="blue",zorder=2,linewidth=4,linestyle="dotted")
        ax0.plot(xvalues,-noise/np.abs(xvalues),c="blue",zorder=2,linewidth=4,linestyle="dotted")

    # Plot limits, legend, labels...
    ax0.legend()
    ax0.set_yticks(np.arange(-2.,2.,0.25))
    ax0.set_xlim(xmin0,xmax0)
    ax0.set_ylim(-0.65, 0.65)
    # Adjust ylims if the results are really bad!
    if (np.mean(im2[0].data[np.isnan(im2[0].data)==False]) <= -0.5):
        ax0.set_ylim(-1.5, 0.5)
    ax0.set_xscale('log')
    ax0.set_ylabel(r" A-par",fontsize=20)
    if titlename=='':
        plt.title("Accuracy vs. Signal",fontsize=16)
    else: 
        plt.title(titlename,fontsize=16)


    # Plot #2: Reference vs Target
    ax1 = plt.subplot(grid[2:6, 0])
    # Loop over all images
    xmax0 = 0.0; xmin0 = 1E6    # Dummy values
    for m in np.arange(Nplots):
        # Images
        im1 = fits.open(ref_image+".fits")
        im2 = fits.open(target_image[m]+"_convo2ref.fits")
        # Define plot limits
        ##xmin = np.min(im1[0].data[np.isnan(im1[0].data)==False])
        xmin = np.percentile(im1[0].data[np.isnan(im1[0].data)==False],0.01) #np.im replaced by 0.01 percentile to avoid outlayers
        xmax = np.max(im1[0].data[np.isnan(im1[0].data)==False])
        if (xmax > xmax0):
            xmax0=xmax+xmax/10. # Slightly larger
        if (xmin < xmin0):
            xmin0=xmin
        if (xmin < 0.0):          #Lydia's modification to avoid negative values!
            xmin0=0.0001

        # Plot results
        if labelname[m]=='':
            ax1.scatter(im1[0].data,im2[0].data,c=IQA_colours[m],marker="o",rasterized=True,label=target_image[m],edgecolor='none',alpha=0.01)
        else:    
            ax1.scatter(im1[0].data,im2[0].data,c=IQA_colours[m],marker="o",rasterized=True,label=labelname[m],edgecolor='none',alpha=0.01)

        count=0
        for j in xvalueslog:
            # Define bin ranges in log-space
            idx = (im1[0].data >= 10.**j) & (im1[0].data < 10.**(j+steplog)) & (np.isnan(im1[0].data)==False) & (np.isfinite(im1[0].data)==True)
            values = im2[0].data[idx]
            values = values[ (np.isnan(values)==False) & (np.isfinite(values)==True) ] # remove Nan & Inf.
            # Stats
            if (np.shape(values)[0] > 0):
                means[count] = np.mean(values)  # Mean
                stds[count] = np.std(values)    # STD
                medians[count] = np.median(values)  # Median
                q1values[count] = np.percentile(values, 10) # 10% Quartile
                q3values[count] = np.percentile(values, 90) # 90% Quartile
            # Counter +1
            count+=1
            #
        # Display mean and STD
        ax1.errorbar(10.**(xvalueslog+steplog/2.),means, yerr=stds, fmt='o',c="blue",label=r"|y|$\pm 1 \sigma$ ",linewidth=2,markersize=10,zorder=2,capsize=5)
        #ax0.errorbar(10.**(xvalueslog+steplog/2.),medians, yerr=[q1values,q3values], fmt='o',c="cyan",label=r"[Q1,Median,Q3]",linewidth=2)

    # Show A values lines
    xvalues=np.arange(xmin0,xmax0,(xmax0-xmin0)/20.)
    plt.plot(xvalues,xvalues,c="k",zorder=2,linewidth=3,linestyle="--",label="Goal (linear correlation; A-par = 0.0)")
    plt.text((xmax0-xmin0)/3.,(xmax0-xmin0)/3.,"A=0",rotation=45,ha='center',va='center',rotation_mode="anchor",bbox=dict(boxstyle='square',facecolor='white', edgecolor='black'))
    # Note that the value of A=-1 needs values of Target=0, which is not allowed in ylog-plots
    for k in np.array([-0.75,-0.5,-0.25,0.25,0.5,0.75,1.0]):
        def Avalues(A,x):
            return A*x+x
        yvalues=Avalues(A=k,x=xvalues)
        ax1.plot(xvalues,yvalues,c="grey",zorder=2,linestyle="dashed",alpha=0.5)
        ax1.text((xmax0-xmin0)/3.,Avalues(A=k,x=(xmax0-xmin0)/3.),"A="+str(k),rotation=45,ha='center',va='center',rotation_mode="anchor",clip_on=True,size=10.,color="grey",zorder=2)

    # Show noise effects?
    if (noise > 0):
        xvalues=np.arange(np.log10(xmin0),np.log10(xmax0),(np.log10(xmax0)-np.log10(xmin0))/20.)
        xvalues=10.**xvalues
        plt.plot(xvalues,xvalues-noise,c="blue",zorder=2,linewidth=4,linestyle="dotted",label=r"White noise:  $\sigma = $"+str(np.round(noise,2))+" (image units)")
        plt.plot(xvalues,xvalues+noise,c="blue",zorder=2,linewidth=4,linestyle="dotted")

    # Plot limits, legend, labels...
    plt.xlim(xmin0,xmax0)
    plt.ylim(xmin0,xmax0)
    plt.xscale('log')
    plt.yscale('log')
    # Legend and labels
    plt.legend(bbox_to_anchor=(0.5, -0.15),loc='upper center', borderaxespad=0.)
    plt.ylabel(r" Target flux (image units)",fontsize=20)
    plt.xlabel(r" Reference flux (image units)",fontsize=20)


    # Save plot?
    if save == True:
        if plotname == '':
            plotname="Apar_signal_ALL_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        plt.close()
    # out
    print("---------------------------------------------")
    print(" A-par vs Signal... DONE")
    print("=============================================")
    return True

# Fidelity comparisons
def Compare_Fidelity(ref_image = '',target_image=[''],
                    save=False, plotname='', 
                    labelname=[''], titlename=''):
    """
    Compare all Fidelity images (continuum or mom0 maps) (A. Hacar, Univ. of Vienna)

    Arguments:
      ref_image - image used as reference
      target_image - list of images to be compared with reference
      save - save plot? (default = False)
    Requires:
      The script will look for target_image[i]_convo2ref_Fidelity.fits images produced by the get_IQA() script
    
    Results:
      1- Histogram including the Fidelity distributions for all input images
      2- Numerical results: Total flux in the image, mean + std + kurtosis + skewness of each histogram 

    Example:
      Compare_Fidelity(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])

    """
    # Reference image
    print("=============================================")
    print(" Fidelity comparisons:")
    print(" Reference : "+str(ref_image))
    print("---------------------------------------------")
    # Number of plots
    Nplots = np.shape(target_image)[0]
    # Global comparisons 
    plt.figure(figsize=(8,11))
    grid = plt.GridSpec(ncols=1,nrows=5, wspace=0.3, hspace=0.3)
    ax1 = plt.subplot(grid[0:4, 0])
    for m in np.arange(Nplots):
        print(" Target image " + str(m+1) + " : " + str(target_image[m]))
        nchans, b, mids, h = get_ALLvalues(FITSfile=target_image[m]+"_convo2ref_Fidelity.fits",xmin=0.,xmax=100.,xstep=0.5)
        # Calculate mean value
        hdu = fits.open(target_image[m]+"_convo2ref_Fidelity.fits")
        Fdist = hdu[0].data.flatten()
        Fdist = Fdist[(Fdist < 100.) & (Fdist > 0)]
        meanvalue = np.round(np.mean(Fdist),1)
        medianvalue = np.round(np.median(Fdist),1)
        q1value = np.round(np.percentile(Fdist, 25),1)  # Quartile 1st
        q3value = np.round(np.percentile(Fdist, 75),1)  # Quartile 3rd
        #meanvalue = np.round(np.average(mids,weights=h),1)
        if labelname[m]=='':
            plt.plot(mids,h,label=target_image[m] + "; <Fidelity> = "+ str(meanvalue),linewidth=3,c=IQA_colours[m])
        else:    
            plt.plot(mids,h,label=labelname[m] + "; <Fidelity> = "+ str(meanvalue),linewidth=3,c=IQA_colours[m])
        # Display on screen
        print(" Fidelity")
        print("  Mean = " + str(meanvalue))
        print("  [Q1,Median,Q3] = ["+str(q1value)+" , "+ str(medianvalue)+" , "+str(q3value)+"]")
    # plot lims, axis, labels, etc...
    plt.xlim(1,100.)
    plt.xscale('log')
    plt.yscale('log')   # Make y axis in log scale
    #plt.ylim(1,)
    #plt.legend(loc="lower left")
    plt.legend(bbox_to_anchor=(0.5, -0.1),loc='upper center', borderaxespad=0.)
    plt.xlabel("Fidelity",fontsize=20)
    plt.ylabel(r'# pixels',fontsize=20)
    if titlename=='':
        plt.title("Fidelity Comparisons",fontsize=16)
    else:
        plt.title(titlename,fontsize=16)
    if save == True:
        if plotname == '':
            plotname="FidelityALL_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        plt.close()
    print("---------------------------------------------")
    print(" Fidelity comparisons... DONE")
    print("=============================================")

def Compare_Fidelity_signal(ref_image = '',target_image=[''],
             save=False,noise=0.0, plotname='', 
             labelname=[''], titlename=''
             ):
    """
    Compare all Fidelity images vs signal (continuum or mom0 maps) (A. Hacar, Univ. of Vienna)

    Arguments:
      ref_image - image used as reference
      target_image - list of images to be compared with reference (better only one)
      save - save plot? (default = False)
    Requires:
      The script will look for target_image[i]_convo2ref_Apar.fits images produced by the get_IQA() script
    
    Results:
      Fidelity vs signal in the original image

    Example:
      Compare_Fidelity_signal(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])

    """
    # Reference image
    print("=============================================")
    print(" Fidelity vs Signal")
    print("---------------------------------------------")
    # Number of plots
    Nplots = np.shape(target_image)[0]
    # Global comparisons 
    plt.figure(figsize=(8,11))
    grid = plt.GridSpec(ncols=1,nrows=5, wspace=0.3, hspace=0.3)
    ax1 = plt.subplot(grid[0:4, 0])
    # Loop over all images
    xmin0 = 100; xmax0 = 0.
    for m in np.arange(Nplots):
        # Images
        ##im1 = fits.open(target_image[m]+"_convo2ref.fits")    # signal
        im1 = fits.open(ref_image+".fits")
        im2 = fits.open(target_image[m]+"_convo2ref.fits") # parameter
        xmin = np.min(im1[0].data[np.isnan(im1[0].data)==False])
        xmax = np.max(im1[0].data[np.isnan(im1[0].data)==False])
        ymin = np.min(im2[0].data[np.isnan(im2[0].data)==False])
        ymax = np.max(im2[0].data[np.isnan(im2[0].data)==False])
        if (xmax > xmax0):
            xmax0=xmax
        if (xmin < xmin0):
            xmin0=xmin
        if (xmin < 0.0):          #Lydia's modification to avoid negative values!
            xmin0=0.0001
        # Plot results
        if labelname[m]=='':            ax1.scatter(im1[0].data,im2[0].data,c=IQA_colours[m],marker="o",rasterized=True,label=target_image[m],edgecolor='none')
        else:    
            ax1.scatter(im1[0].data,im2[0].data,c=IQA_colours[m],marker="o",rasterized=True,label=labelname[m],edgecolor='none')
    # Plot limits, legend, labels...
    plt.xlim(xmin0,xmax0+xmax0/5)
    plt.ylim(xmin0,xmax0+xmax0/5)
    plt.xscale('log')
    plt.yscale('log')   
    # Get A values lines
    xvalues=np.arange(xmin0,xmax0,(xmax0-xmin0)/20.)
    plt.plot(xvalues,xvalues,linestyle="dashed",c="k",label="Goal (linear correlation)",zorder=2,linewidth=3)
    # Fidelities
    for k in np.array([2.,5.,10.]):
        def Fvalues(F,x):
            return F*x/(F+1.)
        yvalues=Fvalues(F=k,x=xvalues)
        plt.plot(xvalues,yvalues,c="grey",zorder=2,linestyle="dashed")
        plt.text((xmax0-xmin0)/2.,Fvalues(F=k,x=(xmax0-xmin0)/2.),"Fid.="+str(k),rotation=45,ha='center',va='center',rotation_mode="anchor",bbox=dict(boxstyle='square',facecolor='white', edgecolor='black'))
        def Fvalues(F,x):
            return F*x/(F-1.)
        yvalues=Fvalues(F=k,x=xvalues)
        plt.plot(xvalues,yvalues,c="grey",zorder=2,linestyle="dashed")
        plt.text((xmax0-xmin0)/2.,Fvalues(F=k,x=(xmax0-xmin0)/2.),"Fid.="+str(k),rotation=45,ha='center',va='center',rotation_mode="anchor",bbox=dict(boxstyle='square',facecolor='white', edgecolor='black'))
    #plt.legend(loc='lower right')
    plt.legend(bbox_to_anchor=(0.5, -0.1),loc='upper center', borderaxespad=0.)
    plt.ylabel(r" Target flux (image units)",fontsize=20)
    plt.xlabel(r'# Reference flux (image units)',fontsize=20)
    if titlename=='':
        plt.title("Fidelity vs. Signal",fontsize=16)
    else: 
        plt.title(titlename,fontsize=16)
    
    # Save plot?
    if save == True:
        if plotname == '':
            plotname="Fidelity_signal_ALL_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        plt.close()
    # out
    print("---------------------------------------------")
    print(" Fidelity vs Signal... DONE")
    print("=============================================")
    return True


#  Tools for cubes

#  Compare Accuracy parameter (cubes) 
def Compare_Apar_cubes(ref_image = '',target_image=[''],save=False, plotname='', 
             labelname=[''], titlename=''
             ):
    """
    Compare all Apar cubes (per channel) (A. Hacar, Univ. of Vienna)

    Arguments:
      ref_image - image used as reference
      target_image - list of images to be compared with reference
      save - save plot? (default = False)
    Requires:
      The script will look for target_image[i]_convo2ref_Apar.fits cubes produced by the get_IQA() script
    
    Results: (for each target)
      1- (left) A-par Spectrogram (density plot per channel)
      2- (right) vertical histogram per channel (grey) + average (red)

    Example:
      Compare_Apar_cubes(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])

    """
    # Reference image
    print("=============================================")
    print(" Display Accuracy parameter:")
    print(" Reference : "+str(ref_image))
    print("---------------------------------------------")
    # Number of plots
    Nplots = np.shape(target_image)[0]
    # Generate figure
    plt.show()

    ysizeplots = 4.
    fig = plt.figure(figsize=(15,Nplots*ysizeplots))
    if titlename=='':
        fig.suptitle("Apar vs. channels",fontsize=16)
    else: 
        fig.suptitle(titlename,fontsize=16)
    grid = plt.GridSpec(ncols=3,nrows=Nplots, wspace=0.1, hspace=0.2)
    # Create plots per channel
    for j in np.arange(0,Nplots,1):
        #xvalues, yvalues = plot_Apar(image2plot=target_image[j]+"_convo2ref_Apar.fits",Nplots=Nplots,Ny=j,title=str(target_image[j]))
        xvalues, yvalues = plot_Apar(image2plot=target_image[j]+"_convo2ref_Apar.fits",Nplots=Nplots,Ny=j,title=str(labelname[j]))
        # Store results for comparison
        if (j == 0):
            results = yvalues
        else:
            results = np.row_stack([results,yvalues])
        #
        print(" Target image " + str(j+1) + " : " + str(target_image[j]))
        print("---------------------------------------------")

    # Save?
    if save == True:
        #plt.savefig("Apar_channels_tmp.png")
        if plotname == '':
            plotname="Apar_channels_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        plt.close()

    # Global comparisons (all channels are considered together in cubes)
    plt.figure(figsize=(8,11))
    grid = plt.GridSpec(ncols=1,nrows=5, wspace=0.3, hspace=0.3)
    ax1 = plt.subplot(grid[0:4, 0])
    # Loop over images
    for m in np.arange(Nplots):
        # Get values
        nchans, b, mids, h = get_ALLvalues(FITSfile=target_image[m]+"_convo2ref_Apar.fits",xmin=-1.525,xmax=1.525,xstep=0.05)
        plt.plot(mids,h,label=str(labelname[m]),linewidth=3,c=IQA_colours[m])
        #plt.plot(mids,h,label=str(target_image[m]),linewidth=3,c=IQA_colours[m])
        # Get mean + std
        meanvalue = np.round(np.average(mids,weights=h),2)
        sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=h)),2)
        # Print on screen
        print(" Target image " + str(m+1) + " : " + str(target_image[m]))
        print(" A-parameter = " + str(meanvalue) + " +/- " + str(sigmavalue))
    # Display goal
    plt.axvline(0.,0.,np.max(results),linestyle="--",color="black",linewidth=3,label="Goal",alpha=1.,zorder=-2)
    # Plot limits, legend, labels...
    plt.xlim(-1.0,1.0)
    plt.yscale('log')   # Make y axis in log scale
    plt.ylim(1,)
    #plt.legend()
    plt.legend(bbox_to_anchor=(0.5, -0.1),loc='upper center', borderaxespad=0.)
    plt.xlabel("Accuracy",fontsize=25)
    plt.ylabel(r'# pixels',fontsize=20)

    if titlename=='':
        plt.title("ALL Apar vs. channels",fontsize=16)
    else: 
        plt.title(titlename,fontsize=16)
    # Save?
    if save == True:
        #plt.savefig("AparALL_channels_tmp.png")
        if plotname == '':
            plotnameALL="AparALL_channels_tmp"
        else:
            plotnameALL=plotname+'_ALL'
        plt.savefig(plotnameALL+'.png')
        print(" See results: "+plotnameALL+".png")
        plt.close()
        print(' See results: '+plotname+'.png, '+plotnameALL+'.png')
    print("---------------------------------------------")
    print(" Display Accuracy parameter... DONE")
    print("=============================================")
    return True

# Fidelity comparisons (cubes)
def Compare_Fidelity_cubes(ref_image = '',target_image=[''],save=False, plotname='', 
             labelname=[''], titlename=''
             ):
    """
    Compares all Fidelity cubes (per channel) (A. Hacar, Univ. of Vienna)

    Arguments:
      ref_image - image used as reference
      target_image - list of images to be compared with reference
      save - save plot? (default = False)
    Requires:
      The script will look for target_image[i]_convo2ref_Fidelity.fits cubes produced by the get_IQA() script
    
    Results: (for each target)
      1- (left) Fidelity Spectrogram (density plot per channel)
      2- (right) vertical histogram per channel (grey) + average (red)

    Example:
      Compare_Fidelity_cubes(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])

    """
    # Reference image
    print("=============================================")
    print(" Display Fidelity:")
    print(" Reference : "+str(ref_image))
    print("---------------------------------------------")
    # Number of plots
    Nplots = np.shape(target_image)[0]
    # Generate figure
    plt.show()
    ysizeplots = 4.
    fig = plt.figure(figsize=(15,Nplots*ysizeplots))
    if titlename=='':
        fig.suptitle("Fidelity vs. channels",fontsize=16)
    else: 
        fig.suptitle(titlename,fontsize=16)    
    grid = plt.GridSpec(ncols=3,nrows=Nplots, wspace=0.1, hspace=0.2)
    # Create Q-plots
    for j in np.arange(0,Nplots,1):
        #xvalues, yvalues = plot_Fidelity(image2plot=target_image[j]+"_convo2ref_Fidelity.fits",Nplots=Nplots,Ny=j,title=str(target_image[j]))
        xvalues, yvalues = plot_Fidelity(image2plot=target_image[j]+"_convo2ref_Fidelity.fits",Nplots=Nplots,Ny=j,title=str(labelname[j]))
        # Store results for comparison
        if (j == 0):
            results = yvalues
        else:
            results = np.row_stack([results,yvalues])
        #
        print(" Target image " + str(j+1) + " : " + str(target_image[j]))
        print("---------------------------------------------")
    # Save plot?
    if save == True:
        #plt.savefig("Fidelity_tmp.png")
        if plotname == '':
            plotname="Fidelity_channels_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        plt.close()        
        
    # Global comparisons (all channels are considered together)
    plt.figure(figsize=(8,11))
    grid = plt.GridSpec(ncols=1,nrows=5, wspace=0.3, hspace=0.3)
    ax1 = plt.subplot(grid[0:4, 0])
    # Loop over images
    for m in np.arange(Nplots):
        nchans, b, mids, h = get_ALLvalues(FITSfile=target_image[m]+"_convo2ref_Fidelity.fits",xmin=0,xmax=100,xstep=0.5)
        plt.plot(mids,h,label=str(labelname[m]),linewidth=3,c=IQA_colours[m])
        #plt.plot(mids,h,label=str(target_image[m]),linewidth=3,c=IQA_colours[m])
    # Plot parameters
    plt.yscale('log')   # Make y axis in log scale
    plt.xscale('log')
    plt.xlim(1,100)
    plt.ylim(1,)
    #plt.legend()
    plt.legend(bbox_to_anchor=(0.5, -0.1),loc='upper center', borderaxespad=0.)
    plt.xlabel("Fidelity",fontsize=20)
    #plt.ylabel(r'log$_{10}(\# pixels)$',fontsize=20)
    plt.ylabel(r'log$_{10}(\# pixels)$',fontsize=16)
    
    if titlename=='':
        plt.title("ALL Apar vs. channels",fontsize=16)
    else: 
        plt.title(titlename,fontsize=16)
        
    # Save plot?
    if save == True:
        #plt.savefig("FidelityALL_tmp.png")
        if plotname == '':
            plotnameALL="FidelityALL_channels_tmp"
        else:
            plotnameALL=plotname+'_ALL'
        plt.savefig(plotnameALL+'.png')
        print(" See results: "+plotnameALL+".png")
        plt.close()
        print(' See results: '+plotname+'.png, '+plotnameALL+'.png')        
        #print(" See results: Fidelity_tmp.png, FidelityALL_tmp.png")
    print("---------------------------------------------")
    print(" Display Fidelity... DONE")
    print("=============================================")



##-------------------------------------------------------
## Plot functions

# get values from FITS (ALL)
def get_ALLvalues(FITSfile,xmin,xmax,xstep):
    # FITS file
    image = fits.open(FITSfile)
    # Histogram
    bins_histo = np.arange(xmin,xmax,xstep)
    bins_mids = bins_histo[1:]-xstep/2.
    subimage = image[0].data.flatten()
    idxs = np.isfinite(subimage)
    hist, bin_edges = np.histogram(subimage[idxs],bins=bins_histo)
    ## values in log scale
    ##values_log = np.log10(hist.T)
    # return
    return 0. , bins_histo, bins_mids, hist.T

# get values from FITS for a given channel
def get_CHANvalues(FITSfile,xmin,xmax,xstep,channel):
    # FITS file
    image = fits.open(FITSfile)
    # Histogram
    bins_histo = np.arange(xmin,xmax,xstep)
    bins_mids = bins_histo[1:]-xstep/2.
    subimage = image[0].data[channel].flatten()
    idxs = np.isfinite(subimage)
    hist, bin_edges = np.histogram(subimage[idxs],bins=bins_histo)
    ## values in log scale
    ##values_log = np.log10(hist.T)
    # return
    return 0. , bins_histo, bins_mids, hist.T

# get values from FITS (per channel)
def get_values(FITSfile,xmin,xmax,xstep):
    # FITS file
    image = fits.open(FITSfile)
    # Histogram per channel
    nchan = image[0].shape[0]
    bins_histo = np.arange(xmin,xmax,xstep)
    bins_mids = bins_histo[1:]-xstep/2. 
    for i in np.arange(0,nchan):
        subimage = image[0].data[i,:,:].flatten()
        idxs = np.isfinite(subimage)
        hist, bin_edges = np.histogram(subimage[idxs],bins=bins_histo)
        # values in log scale
        values_log = np.log10(hist.T)
        if (i == 0):
            Histogram = copy.deepcopy(values_log)   
        else:
            Histogram = np.column_stack((Histogram,values_log))
    return nchan, bins_histo, bins_mids, Histogram




def plot_Apar(image2plot,Nplots,Ny,title):
    grid = plt.GridSpec(ncols=3,nrows=Nplots, wspace=0.1, hspace=0.2)
    # A-par plot
    xminplot = -1.5; xmaxplot = 1.5
    nchans, b, mids, h = get_values(FITSfile=image2plot,xmin=xminplot,xmax=xmaxplot,xstep=0.1)
    h[h == -inf] = np.nan
    # 2D plot per channel
    ax1 = plt.subplot(grid[Ny, :2])
    #plt.title(title,fontsize=20,x=0,ha="left",position=(0.1,0.8))
    plt.title(title,fontsize=20,x=0,ha="left",position=(0.1,0.7))
    #plt.title("Q parameter",fontsize=10,x=1,ha="right",color='grey', style='italic')
    plt.imshow(h, extent =(-0.5,nchans-0.5,xminplot,xmaxplot), aspect='auto',vmin=0,cmap="jet", interpolation='none',origin='lower')
    plt.hlines(0,-0.5,nchans-0.5,linestyle="--",color="black",linewidth=3,label="Goal") 
    plt.xlabel("Channel number",fontsize=15)
    #plt.ylabel("Accuracy (per channel)",fontsize=18)
    plt.ylabel("Accuracy (per channel)",fontsize=15)
    h[np.isnan(h)] = 0.0
    cbar = plt.colorbar()
    cbar.set_label(r'log$_{10}(\# pixels)$',fontsize=15)
    # Histogram
    ax2 = plt.subplot(grid[Ny, 2])
    plt.hlines(0,0.1,max(h.flat),linestyle="--",color="black",linewidth=3,label="Goal",alpha=1.,zorder=-2)
    # Get mean values (only orientative)
    for i in np.arange(0,nchans):
        plt.step(h[:,i],mids,color="grey",linewidth=1, alpha=0.1)
    ##h[h == 0.0] = np.nan
    # We use linear weights rather than log10
    plt.step(np.log10(np.average(10.**h,axis=1)),mids,color="red",linewidth=3,label="mean")
    meanvalue = np.round(np.average(mids,weights=np.log10(np.average(10.**h,axis=1))),2)
    sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=np.log10(np.average(10.**h,axis=1)))),2)
    # The alternative would be
    #plt.step(np.nanmean(h,axis=1)[:],mids,color="red",linewidth=3,label="mean")
    #meanvalue = np.round(np.average(mids,weights=np.nanmean(h,axis=1)[:]),2)
    #sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=np.nanmean(h,axis=1)[:])),2)
    plt.title('{:.2f}'.format(meanvalue)+"+/-"+'{:.2f}'.format(sigmavalue),fontsize=15,x=0,ha="left",position=(0.6,0.1),color="blue")
    plt.hlines(meanvalue,0.1,max(h.flat),color="blue",linewidth=3,label="average",alpha=0.5,zorder=-2)
    # Plot parameters
    plt.xlim(0,max(h.flat))
    plt.ylabel("Accuracy (per channel)",fontsize=15)
    #plt.ylabel("Accuracy (per channel)",fontsize=18)
    plt.xlabel(r'log$_{10}(\# pixels)$',fontsize=15)
    plt.legend(loc="upper left",prop={"size":10})
    ax2.tick_params(labelbottom=True, labelleft=False, labelright=True,bottom=True, top=True, left=True, right=True)
    ax2.yaxis.set_label_position("right")
    # return for comparisons
    return mids, np.nanmean(h,axis=1)[:]

def plot_Fidelity(image2plot,Nplots,Ny,title):
    grid = plt.GridSpec(ncols=3,nrows=Nplots, wspace=0.1, hspace=0.2)
    # Fidelity plot
    xminplot = -1; xmaxplot = 100.
    nchans, b, mids, h = get_values(FITSfile=image2plot,xmin=xminplot,xmax=xmaxplot,xstep=1)
    h[h == -inf] = np.nan
    # 2D plot per channel
    ax1 = plt.subplot(grid[Ny, :2])
    #plt.title(title,fontsize=20,x=0,ha="left",position=(0.1,0.8))
    plt.title(title,fontsize=20,x=0,ha="left",position=(0.1,0.7))
    #plt.title("Q parameter",fontsize=10,x=1,ha="right",color='grey', style='italic')
    plt.imshow(h, extent =(-0.5,nchans-0.5,xminplot,xmaxplot), aspect='auto',vmin=0,cmap="jet", interpolation='none',origin='lower')
    #plt.hlines(0,-0.5,nchans-0.5,linestyle="--",color="black",linewidth=3,label="Goal")    
    plt.xlabel("Channel number",fontsize=15)
    #plt.ylabel("Fidelity (per channel)",fontsize=18)
    plt.ylabel("Fidelity (per channel)",fontsize=15)
    h[np.isnan(h)] = 0.0
    cbar = plt.colorbar()
    cbar.set_label(r'log$_{10}(\# pixels)$',fontsize=15)
    # Histogram
    ax2 = plt.subplot(grid[Ny, 2])
    plt.hlines(0,0.1,max(h.flat),linestyle="--",color="black",linewidth=3,label="Goal",alpha=1.,zorder=-2)
    # Get mean values (only orientative)
    for i in np.arange(0,nchans):
        plt.step(h[:,i],mids,color="grey",linewidth=1, alpha=0.1)
    ##h[h == 0.0] = np.nan
    # We use linear weights rather than log10
    plt.step(np.log10(np.average(10.**h,axis=1)),mids,color="red",linewidth=3,label="mean")
    meanvalue = np.round(np.average(mids,weights=np.log10(np.average(10.**h,axis=1))),2)
    sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=np.log10(np.average(10.**h,axis=1)))),2)
    # The alternative would be
    #plt.step(np.nanmean(h,axis=1)[:],mids,color="red",linewidth=3,label="mean")
    #meanvalue = np.round(np.average(mids,weights=np.nanmean(h,axis=1)[:]),2)
    #sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=np.nanmean(h,axis=1)[:])),2)
    plt.title('{:.2f}'.format(meanvalue)+"+/-"+'{:.2f}'.format(sigmavalue),fontsize=15,x=0,ha="left",position=(0.6,0.1),color="blue")
    # Plot parameters
    plt.xlim(0,max(h.flat))
    plt.ylabel("Fidelity (per channel)",fontsize=15)
    #plt.ylabel("Fidelity (per channel)",fontsize=18)
    plt.xlabel(r'log$_{10}(\# pixels)$',fontsize=15)
    plt.legend(loc="upper left",prop={"size":10})
    ax2.tick_params(labelbottom=True, labelleft=False, labelright=True,bottom=True, top=True, left=True, right=True)
    ax2.yaxis.set_label_position("right")
    # return for comparisons
    return mids, np.nanmean(h,axis=1)[:]

def show_Apar_map(ref_image,target_image,
                  channel=0, 
                  save=False, plotname='',
                  labelname='', titlename=''
                  ):
    """
    Display Accuracy maps (A. Hacar, Univ. of Vienna)
    Arguments:
     ref_image - reference image
     target_image - imaged to be compared
     channel - (for cubes only) channel to be compared (default = 0, aka continuum)

    Note:
     Generate the necessary imaged (e.g. target_image_convo2ref.fits) using get_IQA()

    Results: show_Apar_map will display a figure with 4 subpanels:
     - [1] (Upper left)  Reference image
     - [2] (Upper right) Target image at the resolution of the referenec
     - [3] (Lower left)  Accuracy map
     - [4] (Lower right) Histogram

    """
    # Figure
    fig = plt.figure(figsize=(11,12))
    #fig = plt.figure(figsize=(15,10))
    if titlename=='':   
        fig.suptitle('Accurray map', fontsize=16)
    else:    
        fig.suptitle(titlename, fontsize=16)

    grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.5, hspace=0.3)
    #grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.3, hspace=0.3)

    # Panel #1: Reference
    ax1 = plt.subplot(grid[0, 0])
    image = fits.open(ref_image+".fits")
    # get min/max values
    #vmin , vmax = np.min(image[0].data[-np.isnan(image[0].data)]), np.max(image[0].data[-np.isnan(image[0].data)])
    vmin , vmax = np.min(image[0].data[~np.isnan(image[0].data)]), np.max(image[0].data[~np.isnan(image[0].data)])
    # Continuum or cube?
    Ndims = np.shape(np.shape(image[0].data))
    channel=int(channel)
    if (Ndims[0] == 2):
        # Continuum
        im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
    else:
        # Cubes
        im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
    # Plot parameters, limits, axis, labels ...
    plt.gca().invert_yaxis()
    cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    cbar.ax.set_ylabel('Flux (image units)', fontsize=15)
    plt.text(0.1,0.1,"Reference", bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Reference (Chan.# " + str(channel) + ")")

    # Panel #2: Target image at Reference resolution
    ax1 = plt.subplot(grid[0, 1])
    image = fits.open(target_image+"_convo2ref.fits")
    # Continuum or cube?
    Ndims = np.shape(np.shape(image[0].data))
    if (Ndims[0] == 2):
        # Continuum
        im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
    else:
        # Cubes
        im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
    # Plot parameters, limits, axis, labels ...
    plt.gca().invert_yaxis()
    cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    cbar.ax.set_ylabel('Flux (image units)', fontsize=15)
    #plt.text(0.1,0.1,"Target", bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    if labelname=='':
        plt.text(0.1,0.1,"Target", bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    else:
        plt.text(0.1,0.1,labelname, bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)

    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Target at ref. resolution (Chan.# " + str(channel) + ")")

    # Panel #3: A-par map
    ax1 = plt.subplot(grid[1, 0])
    image = fits.open(target_image+"_convo2ref_Apar.fits")
    # Number of axis = Dimentions (Cont vs cubes)
    Ndims = np.shape(np.shape(image[0].data))
    contours = np.array([-1.0,-0.5,-0.25,0.25,0.5,1.0])
    contours = np.arange(-1.,1,0.1)
    # Continuum or cube?
    if (Ndims[0] == 2):
        # Continuum
        im = ax1.imshow(image[0].data,vmin=-1.1,vmax=1.1,cmap='bwr_r')
        cp = ax1.contour(image[0].data,levels=contours,colors="grey")
        ax1.clabel(cp,fontsize=10,colors="grey",fmt="%.2f",inline=1)
    else:
        # Cubes
        im = ax1.imshow(image[0].data[channel],vmin=-1.1,vmax=1.1,cmap='bwr_r')
        cp = ax1.contour(image[0].data[channel],levels=contours,colors="grey")
        ax1.clabel(cp,fontsize=10,colors="grey",fmt="%.2f")
    # Plot parameters, limits, axis, labels ...
    cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    cbar.ax.set_ylabel('Accuracy parameter', fontsize=15)
    plt.gca().invert_yaxis()
    plt.show()
    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Accuracy map (Chan.# " + str(channel) + ")")

    # Panel #4: Histogram
    ax2 = plt.subplot(grid[1, 1])
    nchans, b, mids, h = get_ALLvalues(FITSfile=target_image+"_convo2ref_Apar.fits",xmin=-1.525,xmax=1.525,xstep=0.05)
    plt.plot(mids,h,label="ALL pixels",linewidth=3,c="red")
    # Mean value
    meanvalue = np.round(np.average(mids,weights=h),2)
    sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=h)),2)
    plt.vlines(meanvalue,np.min(h[h>0]),np.max(h),linestyle="dotted",color="red",linewidth=3,label="A = "+str(meanvalue)+ " +/- " + str(sigmavalue),alpha=1.,zorder=-2)
    # Print results on screen
    print(" Accuracy = " + str(meanvalue) + " +/- " + str(sigmavalue))
    # Continuum or cube
    if (Ndims[0] > 2): # cubes only
        nchans_chan, b_chan, mids_chan, h_chan = get_CHANvalues(FITSfile=target_image+"_convo2ref_Apar.fits",xmin=-1.525,xmax=1.525,xstep=0.05,channel=channel)
        plt.plot(mids_chan,h_chan,label="Channel # " +str(channel),c="blue",linewidth=3,linestyle="dotted")
    # Plot limits, labels, axis...
    plt.vlines(0.,np.min(h[h>0]),np.max(h),linestyle="--",color="black",linewidth=3,label="Goal",alpha=1.,zorder=-2)
    plt.xlim(-1.1,1.1)
    plt.yscale('log')   # Make y axis in log scale
    plt.legend(loc="lower right")
    plt.xlabel("Accuracy parameter",fontsize=20)
    plt.ylabel(r'Number of pixels',fontsize=20)
    # Save plot?
    if save == True:
        if plotname == '':
            plotname="Accuracy_map_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        
        
        
        
        plt.close()
    # out
    print("---------------------------------------------")
    return True


def show_Fidelity_map(ref_image,target_image,
                       channel=0, save=False, plotname='',
                       labelname='', titlename=''
                       ):
    """
    Display Fifelity maps (A. Hacar, Univ. of Vienna)
    Arguments:
     ref_image - reference image
     target_image - imaged to be compared
     channel - (for cubes only) channel to be compared (default = 0, aka continuum)

    Note:
     Generate the necessary imaged (e.g. target_image_convo2ref.fits) using get_IQA()

    Results: show_Apar_map will display a figure with 4 subpanels:
     - [1] (Upper left)  Reference image
     - [2] (Upper right) Target image at the resolution of the referenec
     - [3] (Lower left)  Fidelity map
     - [4] (Lower right) Histogram

    """
    # Figure
    fig = plt.figure(figsize=(11,12))
    #fig = plt.figure(figsize=(15,10))
    if titlename=='':   
        fig.suptitle('Fidelity map', fontsize=16)
    else:    
        fig.suptitle(titlename, fontsize=16)
    grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.5, hspace=0.3)
    #grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.3, hspace=0.3)

    # Panel #1: Reference
    ax1 = plt.subplot(grid[0, 0])
    image = fits.open(ref_image+".fits")
    # get min/max values
    #vmin , vmax = np.min(image[0].data[-np.isnan(image[0].data)]), np.max(image[0].data[-np.isnan(image[0].data)])
    vmin , vmax = np.min(image[0].data[~np.isnan(image[0].data)]), np.max(image[0].data[~np.isnan(image[0].data)])
    # Continuum or cube?
    Ndims = np.shape(np.shape(image[0].data))
    channel=int(channel)
    if (Ndims[0] == 2):
        # Continuum
        im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
    else:
        # Cubes
        im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
    # Plot parameters, limits, axis, labels ...
    plt.gca().invert_yaxis()
    cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    cbar.ax.set_ylabel('Flux (image units)', fontsize=15)
    plt.text(0.1,0.1,"Reference", bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Reference (Chan.# " + str(channel) + ")")

    # Panel #2: Target image at Reference resolution
    ax1 = plt.subplot(grid[0, 1])
    image = fits.open(target_image+"_convo2ref.fits")
    # Continuum or cube?
    Ndims = np.shape(np.shape(image[0].data))
    if (Ndims[0] == 2):
        # Continuum
        im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
    else:
        # Cubes
        im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
    # Plot parameters, limits, axis, labels ...
    plt.gca().invert_yaxis()
    cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    cbar.ax.set_ylabel('Flux (image units)', fontsize=15)
    if labelname=='':
        plt.text(0.1,0.1,"Target", bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    else:
        plt.text(0.1,0.1,labelname, bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Target at ref. resolution (Chan.# " + str(channel) + ")")

    # Panel #3: Fidelity map
    ax1 = plt.subplot(grid[1, 0])
    image = fits.open(target_image+"_convo2ref_Fidelity.fits")
    # Number of axis = Dimentions (Cont vs cubes)
    Ndims = np.shape(np.shape(image[0].data))
    # Continuum or cube?
    if (Ndims[0] == 2):
        # Continuum
        im = ax1.imshow(image[0].data,vmin=1.,vmax=100,cmap='hot',norm=LogNorm())
    else:
        # Cubes
        im = ax1.imshow(image[0].data[channel],vmin=1.,vmax=100,cmap='hot',norm=LogNorm())
    # Plot parameters, limits, axis, labels ...
    cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    cbar.ax.set_ylabel('Fidelity', fontsize=15)
    plt.gca().invert_yaxis()
    plt.show()
    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Fidelity map (Chan.# " + str(channel) + ")")

    # Panel #4: Histogram
    ax2 = plt.subplot(grid[1, 1])
    nchans, b, mids, h = get_ALLvalues(FITSfile=target_image+"_convo2ref_Fidelity.fits",xmin=0,xmax=100,xstep=0.5)
    plt.plot(mids,h,label="ALL pixels",linewidth=3,c="red")
    # Continuum or cube
    if (Ndims[0] > 2): # cubes only
        nchans_chan, b_chan, mids_chan, h_chan = get_CHANvalues(FITSfile=target_image+"_convo2ref_Fidelity.fits",xmin=0,xmax=100,xstep=0.5,channel=channel)
        plt.plot(mids_chan,h_chan,label="Channel # " +str(channel),c="blue",linewidth=3,linestyle="dotted")
    # Plot limits, labels, axis...
    plt.xlim(1,100)
    plt.xscale('log')
    plt.yscale('log')   # Make y axis in log scale
    plt.legend()
    plt.xlabel("Fidelity",fontsize=20)
    plt.ylabel(r'Number of pixels',fontsize=20)
    # Save plot?
    if save == True:
        if plotname == '':
            plotname="Fidelity_map_tmp"
        plt.savefig(plotname+'.png')        
        plt.close()
    # out
    print("---------------------------------------------")
    return True


##############################################################################################
# 2.- Power Spectra
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
from scipy import stats
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


def genmultisps(fitsimages, save=False, plotname='', labelname='',
                titlename=''):
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

    
    # Note: we use new IQA_colours instead

    if type(fitsimages) != list or len(fitsimages)==0:
        print("ERROR: fitsimages needs to be non-empty list")
        return False


    # initialise plotting
    fig, ax = pyplot.subplots(figsize = (8,8))

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
        fit = False

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

        if not noBeamInfo:
            print('pixSize bmaj bmin ', pixSize, bmaj, bmin)

            ## convert image to Jy/pixel 
            image*=(pixSize.value)**2/(1.1331*bmaj.value*bmin.value)

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

            if lowCut_idx == highCut_idx: ## likely dealing with single-dish/tp image => DON'T FIT
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
        ######ax.plot(logAngScales, logPwr, label='Data '+str(imnumber), color=IQA_colours[imnumber])
        if labelname[fitsimages.index(fitsimage)]=='':
            ax.plot(logAngScales, logPwr, label=str(fitsName), color=IQA_colours[imnumber])
        else:    
            ax.plot(logAngScales, logPwr, label=labelname[fitsimages.index(fitsimage)], color=IQA_colours[imnumber])
        #ax.plot(logAngScales, logPwr, label=str(fitsName), color=IQA_colours[imnumber])

        ## fill inbetween for errors ##
        #ax.fill_between(logAngScales, logPwr-logErrors, logPwr+logErrors, color=IQA_colours[1])

        if fit:
            ax.plot(logAngScales[lowCut_idx:highCut_idx], linFunc(logAngScales[lowCut_idx:highCut_idx], coeffs[0], coeffs[1]), color='black', linestyle='--', label = 'PL: %.1f+/-%.1f' % (coeffs[0], perr[0]))
        
        ## set x and y limits ##
        ax.set_xlim(np.max(logAngScales)+0.25, np.min(logAngScales) - 0.25)

        ## show fit limits ##
        ax.axvline(logAngScales[lowCut_idx], color = IQA_colours[imnumber], linestyle = '-.')
        ax.axvline(logAngScales[highCut_idx], color= IQA_colours[imnumber], linestyle = '--')

        imnumber += 1
    # end for


    if pixUnits == True:
        ax.set_xlabel(r'$log_{10}\left(\rm 1/pix\right)$')
    else:
        ax.set_xlabel(r'$log_{10}\left(\rm arcsec\right)$')

    ax.set_ylabel(r'$log_{10}\left(\rm Power\right)$')
    #pyplot.legend(loc='upper right', fontsize=6)
    pyplot.legend(loc='lower left')
    if titlename=='':
        plt.title("Power spectra",fontsize=16)
    else:
        plt.title(titlename,fontsize=16)

    pyplot.show()

    if save == True:
        #pyplot.savefig(fitsimages[0]+'_and_others.sps.pdf')
        if plotname == '':
            plotname="Power_spectra_ALL_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
        plt.close()


    return True








##############################################################################################
# 3.- Aperture methods (under development)
# Script to calculate flux in different apertures
#
# authors: Brian Mason bmason@nrao.edu
#      Alvaro Hacar alvaro.hacar@univie.ac.at
#
#

def sum_region_fluxes(imvals,peak_indices,radius=4.0):
    fluxes = np.zeros(np.shape(peak_indices)[0])
    x_flux = np.zeros(np.shape(peak_indices)[0])
    y_flux = np.zeros(np.shape(peak_indices)[0])
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
        subimage = imvals[i_low:i_high,j_low:j_high]
        fluxes[k] = subimage.sum()
        #print k,fluxes[k]
    
    return fluxes,x_flux,y_flux


def sum_region_fluxes2(imvals,pixel,max_radius,pix_beam):
    """
    Total flux within a square region at different radii center at a position (x,y) 
    Script based on the same one produce by B.Mason
    Arguments:
     imvals - 2D array
     pixel - (x,y) central coordinates (in pixel units)
     max_radius - maximum number of beams in which it will be calculated (in beam units)
     pix_beam - pixels per beam
    """
    radii = np.arange(0,max_radius*pix_beam,pix_beam/3.)
    fluxes = np.zeros(np.shape(radii)[0])
    radius = np.zeros(np.shape(radii)[0])
    # radius to extract in pixels -
    counter = 0
    for k in radii:
        i_low = pixel[1] - np.int(k)
        i_high = pixel[1] + np.int(k)
        j_low = pixel[0] - np.int(k)
        j_high = pixel[0] + np.int(k)
    if k == 0:
        i_high = pixel[1] + 1
        j_high = pixel[0] + 1
        if i_low < 0:
            i_low = 0
        if i_high >= np.shape(imvals)[0]:
            i_high = np.shape(imvals)[0]-1
        if j_low < 0:
            j_low = 0
        if j_high >= np.shape(imvals)[1]:
            j_high = np.shape(imvals)[1]-1
        subimage = imvals[i_low:i_high,j_low:j_high]
        fluxes[counter] = sum(subimage[np.isnan(subimage)==False])
    radius[counter] = k
    counter+=1

    return fluxes,radius


def get_aperture(fitslist,position=(1,1),Nbeams=10):
    """
     Generate aperture plot ata given position (x,y) (A. Hacar, Univ. of Vienna)
     Arguments:
      fitslits = list of FITS files. The first one is taken as reference.
        Note: ALL FITS files should be have the same beam + grid
      position - (x,y) central coordinates (in pixel units)
      Nbeams - maximum number of beams included (aka max radius)
    """
    # Figure
    fig = plt.figure(figsize=(23,7))
    grid = plt.GridSpec(ncols=3,nrows=3, wspace=0.3, hspace=0.3)

    # Panel #1: Reference
    ax1 = plt.subplot(grid[:, 0])
    image = fits.open(fitslist[0])
    # get min/max values
    vmin , vmax = np.min(image[0].data[~np.isnan(image[0].data)]), np.max(image[0].data[~np.isnan(image[0].data)])

    # Plot image
    im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet',aspect='equal')
    # Get a marker at the position
    ax1.scatter(position[0],position[1],marker="+",c="white",s=300,linewidth=5)
    ax1.scatter(position[0],position[1],marker="+",c="red",s=300,linewidth=2)
    # Plot labels, axis, etc...
    plt.gca().invert_yaxis()
    #cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    #cbar.ax.set_ylabel('Flux (image units)', fontsize=15)
    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Reference image")
    plt.show()

    # Panel #2: Zoom (x20)
    ax2 = plt.subplot(grid[1:3, 1])
    im = ax2.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet',aspect='equal')
    zoomin = np.shape(image[0].data)[0]/20.
    ax2.set_xlim(position[0]-zoomin,position[0]+zoomin)
    ax2.set_ylim(position[1]-zoomin,position[1]+zoomin)
    # Get a marker at the position
    ax2.scatter(position[0],position[1],marker="+",c="white",s=300,linewidth=5)
    ax2.scatter(position[0],position[1],marker="+",c="red",s=300,linewidth=2)
    # Plot labels, axis, etc...
    ax2.text(0.5,0.8,"("+str(position[0])+","+str(position[1])+")",color="red",transform = ax2.transAxes,ha="center",fontsize=20)
    plt.xlabel("X (pixel units)",fontsize=15)
    plt.ylabel("Y (pixel units)",fontsize=15)
    plt.title(" Zoom-in")
    plt.show()

    # Panel #3: 
    ax3 = plt.subplot(grid[:,2])
    for i in fitslist:
        # Open FITS file
        image = fits.open(i)
        # Get pixel information
        pixSize = image[0].header['CDELT2']*3600. #*u.arcsec
        Beamsize = image[0].header['BMAJ']*3600. #*u.arcsec
        pix_beam = Beamsize/pixSize
        # Get fluxes at different radii
        flux, radius = sum_region_fluxes2(image[0].data,pixel=position,max_radius=Nbeams,pix_beam=pix_beam)
        # Use image 0 as reference
        if i == fitslist[0]:
            flux0 = flux
            plt.axvline(Beamsize,c="k", linewidth=2,linestyle="dotted",label="Beamsize")
            ymin0 = 1.0
        else:
            # Plot
            plt.plot(radius*pixSize,flux/flux0,label=i,linewidth=2)
            ymin = np.min(flux/flux0)
            if (ymin <= ymin0):
                ymin0 = ymin
    plt.axhline(1.0,c="k", linewidth=2,linestyle="dashed",label="Goal")
    plt.scatter(0,1,c="white")
    plt.xlim(0,np.max(radius*pixSize))
    plt.ylim(ymin0,1.2)
    #plt.legend(bbox_to_anchor=(1.05, 1), loc=4, borderaxespad=0.)
    plt.legend(bbox_to_anchor=(-0.2, 0.7), loc=4, borderaxespad=0.)
    plt.xlabel("Radius (arcsec)",fontsize=20)
    plt.ylabel(r"Relative Flux",fontsize=20)









##############################################################################################
# 4.- map residuals and tclean feedback 
#
# based on show_Apar_map
# authors: L. Moser-Fischer 
# 
#

def show_residual_maps(target_image,target_mask,
                  channel=0, 
                  save=False, plotname='',
                  labelname='', titlename='',
                  stop_crit=[],
                  cleanthresh=[],
                  cleaniterdone=[]
                  ):
    """
    Display Residual maps (L. Moser-Fischer)
    Arguments:
     target_image - list of images to be compared (FITS)
     channel - (for cubes only) channel to be compared (default = 0, aka continuum)



    Note: plots up to 4 plots!
    
    Results: show_Apar_map will display the residual map for each tclean instance used by the chosen
    combination method and the corresponding tclean feedback (stopping criteria etc.)


    """
    #import matplotlib.gridspec as gridspec
    
    #from mpl_toolkits.axes_grid1 import make_axes_locatable

    # Figure
    #fig = plt.figure(constrained_layout=True)
    fig = plt.figure(figsize=(10,25))#, constrained_layout=True)
    #fig = plt.figure(figsize=(15,10))
    if titlename=='':   
        fig.suptitle('Residual maps from the tclean instances used by the chosen combination methods', fontsize=16)
    else:    
        fig.suptitle(titlename, fontsize=16)

    #grid = gridspec.GridSpec(2,3, wspace=0.01, hspace=0.01, top=5.0, figure=fig) 
    # even gridspec definition from https://matplotlib.org/stable/tutorials/intermediate/constrainedlayout_guide.html#sphx-glr-tutorials-intermediate-constrainedlayout-guide-py
    # does not change anything here ...

    #grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.3, hspace=0.3)
    grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.5, hspace=0.7)
    #grid = plt.GridSpec(2, 3, wspace=0.3, hspace=0.3)
    


    for i in range(0, min(4,len(target_image))):
        # Panel #i: 
        # 0 -> [0,0]         [int(i/2)  ,i % 2] #modulo
        # 1 -> [0,1]
        # 2 -> [1,0]
        # 3 -> [1,1]
        # 4 -> [2,0]
        # 5 -> [2,1]
        
        #ax1 = plt.subplot(grid[int(i/2),i % 2])
        ax1 = fig.add_subplot(grid[int(i/2),i % 2])
        plt.subplots_adjust(top=0.84, wspace=0.1, hspace=0.1)
        image = fits.open(target_image[i]+".fits")
        mask = fits.open(target_mask[i]+".fits")
        # get min/max values
        #vmin , vmax = np.min(image[0].data[-np.isnan(image[0].data)]), np.max(image[0].data[-np.isnan(image[0].data)])
        vmin , vmax = np.min(image[0].data[~np.isnan(image[0].data)]), np.max(image[0].data[~np.isnan(image[0].data)])
        # Continuum or cube?
        Ndims = np.shape(np.shape(image[0].data))
        channel=int(channel)
        if (Ndims[0] == 2):
            # Continuum
            im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
            mask= ax1.contour(mask[0].data, levels=[1], colors='white', alpha=0.5)
            #mask= ax1.contour(mask[0].data, levels=np.logspace(-4.7, -3., 10), colors='white', alpha=0.5)
        else:
            # Cubes
            im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
            mask= ax1.contour(mask[0].data[channel], levels=[1], colors='white', alpha=0.5)

        # Plot parameters, limits, axis, labels ...
        plt.gca().invert_yaxis()
        #divider = make_axes_locatable(ax1)
        #cax = divider.append_axes('right', size='5%', pad=0.05)
        
        cbar = plt.colorbar(im, ax=ax1,orientation='vertical')#, shrink=0.5)
        cbar.ax.set_ylabel('Flux (image units)', fontsize=12)

        if stop_crit == [] or cleaniterdone == [] or cleanthresh == []:
            summarytxt='clean summary '+labelname[i]+ \
                         '\nnot available'
        else:
            summarytxt='clean summary '+labelname[i]+ \
                         '\nstopping criterion:' +str(stop_crit[i])+ \
                         '\niter done (all planes):' + str(cleaniterdone[i])+ \
                         '\nrequested threshold:' +str(round(cleanthresh[i],6))+'Jy'
        
        plt.text(0.055,-0.3, summarytxt, fontsize=10, bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
        #plt.annotate(summarytxt,(0,0),(0,-20), fontsize=12, xycoords='axes fraction', textcoords='offset points', va='top')
        ax1.xaxis.tick_top()
        ax1.xaxis.set_label_position('top') 
        plt.xlabel("X (pixel units)",fontsize=10)
        plt.ylabel("Y (pixel units)",fontsize=10)
        plt.title(labelname[i] +" (Chan.# " + str(channel) + ")", fontsize=12)
        #plt.tight_layout(pad=1., w_pad=1., h_pad=1.0)
        


    # Save plot?
    if save == True:
        if plotname == '':
            plotname="Residual_maps_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
     
        plt.close()
    # out
    print("---------------------------------------------")
    return True

    # # Panel #2: Target image at Reference resolution
    # ax1 = plt.subplot(grid[0, 1])
    # image = fits.open(target_image+"_convo2ref.fits")
    # # Continuum or cube?
    # Ndims = np.shape(np.shape(image[0].data))
    # if (Ndims[0] == 2):
    #     # Continuum
    #     im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
    # else:
    #     # Cubes
    #     im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
    # # Plot parameters, limits, axis, labels ...
    # plt.gca().invert_yaxis()
    # cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    # cbar.ax.set_ylabel('Flux (image units)', fontsize=15)
    # plt.text(0.1,0.1,"Target", bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    # plt.xlabel("X (pixel units)",fontsize=15)
    # plt.ylabel("Y (pixel units)",fontsize=15)
    # plt.title(" Target at ref. resolution (Chan.# " + str(channel) + ")")
    # 
    # # Panel #3: A-par map
    # ax1 = plt.subplot(grid[1, 0])
    # 





##############################################################################################
# 4.- map residuals and tclean feedback 
#
# based on show_Apar_map
# authors: L. Moser-Fischer 
# 
#

def show_combi_maps(target_image,#target_mask,
                  channel=0, 
                  save=False, plotname='',
                  labelname='', titlename='',
                  stop_crit=[],
                  cleanthresh=[],
                  cleaniterdone=[]
                  ):
    """
    Display combination image maps (L. Moser-Fischer)
    Arguments:
     target_image - list of images to be compared (FITS)
     channel - (for cubes only) channel to be compared (default = 0, aka continuum)



    Note: plots up to 4 plots!
    
    Results: show_Apar_map will display the residual map for each tclean instance used by the chosen
    combination method and the corresponding tclean feedback (stopping criteria etc.)


    """
    #import matplotlib.gridspec as gridspec
    
    #from mpl_toolkits.axes_grid1 import make_axes_locatable

    # Figure
    #fig = plt.figure(constrained_layout=True)
    fig = plt.figure(figsize=(10,25))#, constrained_layout=True)
    #fig = plt.figure(figsize=(15,10))
    if titlename=='':   
        fig.suptitle('Combined maps from the chosen combination methods', fontsize=16)
    else:    
        fig.suptitle(titlename, fontsize=16)

    #grid = gridspec.GridSpec(2,3, wspace=0.01, hspace=0.01, top=5.0, figure=fig) 
    # even gridspec definition from https://matplotlib.org/stable/tutorials/intermediate/constrainedlayout_guide.html#sphx-glr-tutorials-intermediate-constrainedlayout-guide-py
    # does not change anything here ...

    #grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.3, hspace=0.3)
    grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.5, hspace=0.7)
    #grid = plt.GridSpec(2, 3, wspace=0.3, hspace=0.3)
    


    for i in range(0, min(4,len(target_image))):
        # Panel #i: 
        # 0 -> [0,0]         [int(i/2)  ,i % 2] #modulo
        # 1 -> [0,1]
        # 2 -> [1,0]
        # 3 -> [1,1]
        # 4 -> [2,0]
        # 5 -> [2,1]
        
        #ax1 = plt.subplot(grid[int(i/2),i % 2])
        ax1 = fig.add_subplot(grid[int(i/2),i % 2])
        plt.subplots_adjust(top=0.84, wspace=0.1, hspace=0.1)
        image = fits.open(target_image[i]+".fits")
        #mask = fits.open(target_mask[i]+".fits")
        # get min/max values
        #vmin , vmax = np.min(image[0].data[-np.isnan(image[0].data)]), np.max(image[0].data[-np.isnan(image[0].data)])
        vmin , vmax = np.min(image[0].data[~np.isnan(image[0].data)]), np.max(image[0].data[~np.isnan(image[0].data)])
        #print('vmin, vmax', vmin, vmax)



        # Continuum or cube?
        Ndims = np.shape(np.shape(image[0].data))
        #print(np.shape(image[0].data), np.shape(image[0].data)[0] )
        #col=0
        #if Ndims==4 and np.shape(image[0].data)[0]==1:
        #    col=1    

        channel=int(channel)
        if (Ndims[0] == 2):
            # Continuum
            im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
            #mask= ax1.contour(mask[0].data, levels=[1], colors='white', alpha=0.5)
            ###mask= ax1.contour(mask[0].data, levels=np.logspace(-4.7, -3., 10), colors='white', alpha=0.5)
        else:
            # Cubes

            if Ndims[0]==4 and np.shape(image[0].data)[0]==1:
                im = ax1.imshow(image[0].data[0][channel],vmin=vmin,vmax=vmax,cmap='jet')
            else:
                im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
    
            #mask= ax1.contour(mask[0].data[channel], levels=[1], colors='white', alpha=0.5)

        # Plot parameters, limits, axis, labels ...
        plt.gca().invert_yaxis()
        #divider = make_axes_locatable(ax1)
        #cax = divider.append_axes('right', size='5%', pad=0.05)
        
        cbar = plt.colorbar(im, ax=ax1,orientation='vertical')#, shrink=0.5)
        cbar.ax.set_ylabel('Flux (image units)', fontsize=12)

        if stop_crit == [] or cleaniterdone == [] or cleanthresh == []:
            summarytxt='clean summary '+labelname[i]+ \
                         '\nnot available'
        else:
            summarytxt='clean summary '+labelname[i]+ \
                         '\nstopping criterion:' +str(stop_crit[i])+ \
                         '\niter done (all planes):' + str(cleaniterdone[i])+ \
                         '\nrequested threshold:' +str(round(cleanthresh[i],6))+'Jy'
        
        #plt.text(0.055,-0.3, summarytxt, fontsize=10, bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
        #plt.annotate(summarytxt,(0,0),(0,-20), fontsize=12, xycoords='axes fraction', textcoords='offset points', va='top')
        ax1.xaxis.tick_top()
        ax1.xaxis.set_label_position('top') 
        plt.xlabel("X (pixel units)",fontsize=10)
        plt.ylabel("Y (pixel units)",fontsize=10)
        plt.title(labelname[i] +" (Chan.# " + str(channel) + ")", fontsize=12)
        #plt.tight_layout(pad=1., w_pad=1., h_pad=1.0)
        


    # Save plot?
    if save == True:
        if plotname == '':
            plotname="Combined_maps_tmp"
        plt.savefig(plotname+'.png')
        print(" See results: "+plotname+".png")
     
        plt.close()
    # out
    print("---------------------------------------------")
    return True

    # # Panel #2: Target image at Reference resolution
    # ax1 = plt.subplot(grid[0, 1])
    # image = fits.open(target_image+"_convo2ref.fits")
    # # Continuum or cube?
    # Ndims = np.shape(np.shape(image[0].data))
    # if (Ndims[0] == 2):
    #     # Continuum
    #     im = ax1.imshow(image[0].data,vmin=vmin,vmax=vmax,cmap='jet')
    # else:
    #     # Cubes
    #     im = ax1.imshow(image[0].data[channel],vmin=vmin,vmax=vmax,cmap='jet')
    # # Plot parameters, limits, axis, labels ...
    # plt.gca().invert_yaxis()
    # cbar = plt.colorbar(im, ax=ax1,orientation='vertical')
    # cbar.ax.set_ylabel('Flux (image units)', fontsize=15)
    # plt.text(0.1,0.1,"Target", bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
    # plt.xlabel("X (pixel units)",fontsize=15)
    # plt.ylabel("Y (pixel units)",fontsize=15)
    # plt.title(" Target at ref. resolution (Chan.# " + str(channel) + ")")
    # 
    # # Panel #3: A-par map
    # ax1 = plt.subplot(grid[1, 0])
    # 
