#########################################################
## Image Quality Assessment (IQA) scripts for CASA
##
## Created: Feb. 2020
## Last modified: Aug. 2020
## Created: A. Hacar, IQA group
##
#########################################################
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
## Additional libraries

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

## IQA colours
IQA_colours = ["red", "blue", "orange", "green" , "cyan", "pink", "brown","yellow","magenta","black"]

##-------------------------------------------------------
## Image manipulation

## Convert FITS files into CASA images
def fits2CASA(FITSfile):
	print FITSfile
	os.system("rm -rf "+  FITSfile+".image")
	importfits(fitsimage=FITSfile,imagename=FITSfile+'.image')

## Convert FITS files into CASA images
def CASA2fits(CASAfile):
	print CASAfile
	os.system("rm -rf "+  CASAfile+".fits")
	exportfits(imagename=CASAfile,fitsimage=CASAfile+".fits")

## same as fits2CASA but for a list of FITS
def fitslist2CASA(FITSfile):
	for i in FITSfile:
		print i
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
	print "========================================="
	print " check_axis(): checking axis consistency "
	print "========================================="
	# reference: check axis 
	axis_ref = imhead(ref_image).get("axisnames")
	print " Reference image: " + str(ref_image)
	print " Axis : (",
	for j in np.arange(np.shape(axis_ref)[0]):
		print axis_ref[j] + " ",
	print ")"
	print "-----------------------------------------"
	# Targets: check axis
	n = 0
	for i in target_im:
		n = n+1
		axis_target = imhead(i).get("axisnames")
		print " Target image #" + str(n) + ": " + str(i)
		print " Axis : (",
		transpose = -1
		for j in np.arange(np.shape(axis_target)[0]):
			print axis_target[j] + " ",
			if (axis_ref[j] != axis_target[j]):
				transpose = j
		print ")"
		if (transpose != -1):
			print " WARNING: Axis do not match reference -> transpose OR drop axis"
			print "          (see also drop_axis function)"
		print "-----------------------------------------"
	print " check_axis(): DONE "
	print "========================================="



def drop_axis(myimage):
	"""
	Drop unnecesary axis (e.g. Stokes)
	Arguments:
	 myimage : image wher drop_axis will be applied (CASA image)

	Notes:
	 Check axis consistency with check_axis()

	Usage:
	 drop_axis(myimage)  
	"""
	print "================================================="
	print " drop_axis(): drop additional axis (e.g. Stokes) "
	print "================================================="
	# reference: check axis 
	os.system("rm -rf " + myimage + "_subimage")
	imsubimage(imagename=myimage,outfile=myimage + "_subimage",dropdeg=True)
	print " Reference image: " + str(myimage)
	print " New image: " + str(myimage) +"_subimage"
	print "-----------------------------------------"
	print " drop_axis(): DONE "
	print "========================================="

##-------------------------------------------------------
## Quality estimators
## see a detailed discussion in: https://library.nrao.edu/public/memos/ngvla/NGVLA_67.pdf

## Calculate Image Accuracy parameter (Apar)
## Apar = (image-reference)/abs(reference)
## image & reference have to have the same resolution
## image will be resampled into reference frame
def image_Apar(image,ref_image):
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
## Fidelity = abs(reference)/abs(reference-image)
## image & reference have to have the same resolution
## image will be resampled into reference frame
def image_Fidelity(image,ref_image):
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
## Difference = reference-image
## image & reference have to have the same resolution
## image will be resampled into reference frame
def image_Diff(image,ref_image):
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
def get_IQA(ref_image = '',target_image=['']):
	"""
	Obtain all Image Quality Assesment images
	Arguments:
	  ref_image - image used as reference
	  target_image - list of images to be compared with reference
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
	  get_IQA(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])

	"""
	# Reference image
	print("=============================================")
	print(" get_IQA(): Obtain IQA estimators")
	print(" Reference : "+ str(ref_image))
	print(" Depending on the image/cube size, this process may take a while...")
	print("---------------------------------------------")
	# Target images
	for j in np.arange(0,np.shape(target_image)[0],1):
		# print file
		print " Target image " + str(j+1) + " : " + str(target_image[j])
		# Convolve data into reference resolution
		get_convo2target(target_image[j],ref_image)
		os.system("rm -rf " + target_image[j] + "_convo2ref")
		# Mask it similar to reference
		immath(imagename='convo2ref',mode='evalexpr',expr='IM0',outfile='convo2ref_masked',mask='mask('+str(ref_image)+')')
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
def Compare_Apar(ref_image = '',target_image=[''],save=False):
	"""
	Compare all Apar images (continuum or mom0 maps)

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
	  Compare_Apar_continuum(ref_image = 'TP_image',target_image=['Feather.image','TP2vis.image'])

	"""
	# Reference image
	print("=============================================")
	print(" Accuracy parameter: comparisons")
	print(" Reference : "+str(ref_image))
	flux = np.round(imstat(ref_image)["flux"][0])
	print(" Total Flux = " + str(flux) + " Jy")
	print("---------------------------------------------")
	# Number of plots
	Nplots = np.shape(target_image)[0]
	# Global comparisons 
	plt.figure(figsize=(8,8))
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
		plt.plot(mids,h,label=target_image[m] + "; A = "+ str(meanvalue) + " +/- " + str(sigmavalue),linewidth=3,c=IQA_colours[m])
		# Print results on screen
		print(" Target image " + str(m+1) + " : " + str(target_image[m]))
		print(" Total Flux = " + str(flux) + " Jy")
		print(" Accuracy:")
		print(" Mean +/- Std. = " + str(meanvalue) + " +/- " + str(sigmavalue))
		print(" Skewness, Kurtosis = " + str(skewness) + " , " + str(kurt) )
		print("................................................")
	# Add Goal line
	plt.vlines(0.,np.min(h[h>0]),np.max(h),linestyle="--",color="black",linewidth=3,label="Goal",alpha=1.,zorder=-2)
	# Plot limits, legend, labels...
	plt.xlim(-1.5,1.5)
	plt.yscale('log')	# Make y axis in log scale
	plt.legend(loc='lower right')
	plt.xlabel("Accuracy",fontsize=20)
	plt.ylabel(r'# pixels',fontsize=20)
	plt.title("Accuracy Parameter: comparisons",fontsize=20)
	# Save plot?
	if save == True:
		plt.savefig("AparALL_tmp.png")
		print(" See results: AparALL_tmp.png")
	# out
	print("---------------------------------------------")
	print(" Accuracy parameter comparisons... DONE")
	print("=============================================")
	return True

# Fidelity comparisons
def Compare_Fidelity(ref_image = '',target_image=[''],save=False):
	"""
	Compare all Fidelity images (continuum or mom0 maps)

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
	plt.figure(figsize=(8,8))
	for m in np.arange(Nplots):
		print " Target image " + str(m+1) + " : " + str(target_image[m])
		nchans, b, mids, h = get_ALLvalues(FITSfile=target_image[m]+"_convo2ref_Fidelity.fits",xmin=0.,xmax=100.,xstep=0.5)
		# Calculate mean value
		hdu = fits.open(target_image[m]+"_convo2ref_Fidelity.fits")
		Fdist = hdu[0].data.flatten()
		Fdist = Fdist[(Fdist < 100.) & (Fdist > 0)]
		meanvalue = np.round(np.mean(Fdist),1)
		medianvalue = np.round(np.median(Fdist),1)
		q1value = np.round(np.percentile(Fdist, 25),1)	# Quartile 1st
		q3value = np.round(np.percentile(Fdist, 75),1)	# Quartile 3rd
		#meanvalue = np.round(np.average(mids,weights=h),1)
		plt.plot(mids,h,label=target_image[m] + "; <Fidelity> = "+ str(meanvalue),linewidth=3,c=IQA_colours[m])
		# Display on screen
		print(" Fidelity")
		print("  Mean = " + str(meanvalue))
		print("  [Q1,Median,Q3] = ["+str(q1value)+" , "+ str(medianvalue)+" , "+str(q3value)+"]")
	# plot lims, axis, labels, etc...
	plt.xlim(1,100.)
	plt.xscale('log')
	plt.yscale('log')	# Make y axis in log scale
	#plt.ylim(1,)
	plt.legend(loc="lower left")
	plt.xlabel("Fidelity",fontsize=20)
	plt.ylabel(r'# pixels',fontsize=20)
	plt.title("Fidelity Comparisons")
	if save == True:
		plt.savefig("FidelityALL_tmp.png")
		print(" See results: FidelityALL_tmp.png")
	print("---------------------------------------------")
	print(" Fidelity comparisons... DONE")
	print("=============================================")

#  Tools for cubes

#  Compare Accuracy parameter (cubes) 
def Compare_Apar_cubes(ref_image = '',target_image=[''],save=False):
	"""
	Compare all Apar cubes (per channel)

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
	grid = plt.GridSpec(ncols=3,nrows=Nplots, wspace=0.1, hspace=0.2)
	# Create plots per channel
	for j in np.arange(0,Nplots,1):
		xvalues, yvalues = plot_Apar(image2plot=target_image[j]+"_convo2ref_Apar.fits",Nplots=Nplots,Ny=j,title="Target image"+str(j+1))
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
		plt.savefig("Apar_channels_tmp.png")

	# Global comparisons (all channels are considered together in cubes)
	plt.figure(figsize=(7,7))
	for m in np.arange(Nplots):
		# Get values
		nchans, b, mids, h = get_ALLvalues(FITSfile=target_image[m]+"_convo2ref_Apar.fits",xmin=-1.525,xmax=1.525,xstep=0.05)
		plt.plot(mids,h,label="Target"+str(m+1),linewidth=3)
		# Get mean + std
		meanvalue = np.round(np.average(mids,weights=h),2)
		sigmavalue = np.round(np.sqrt(np.cov(mids, aweights=h)),2)
		# Print on screen
		print(" Target image " + str(m+1) + " : " + str(target_image[m]))
		print(" A-parameter = " + str(meanvalue) + " +/- " + str(sigmavalue))
	# Display goal
	plt.vlines(0.,0.,np.max(results),linestyle="--",color="black",linewidth=3,label="Goal",alpha=1.,zorder=-2)
	# Plot limits, legend, labels...
	plt.xlim(-1.5,1.5)
	plt.yscale('log')	# Make y axis in log scale
	plt.ylim(1,)
	plt.legend()
	plt.xlabel("A-par",fontsize=25)
	plt.ylabel(r'# pixels$',fontsize=20)
	# Save?
	if save == True:
		plt.savefig("AparALL_channels_tmp.png")
		print(" See results: Apar_channels_tmp.png, Apar_channels_tmp.png")
	print("---------------------------------------------")
	print(" Display Accuracy parameter... DONE")
	print("=============================================")
	return True

# Fidelity comparisons (cubes)
def Compare_Fidelity_cubes(ref_image = '',target_image=[''],save=False):
	"""
	Compares all Fidelity cubes (per channel)

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
	grid = plt.GridSpec(ncols=3,nrows=Nplots, wspace=0.1, hspace=0.2)
	# Create Q-plots
	for j in np.arange(0,Nplots,1):
		xvalues, yvalues = plot_Fidelity(image2plot=target_image[j]+"_convo2ref_Fidelity.fits",Nplots=Nplots,Ny=j,title="Target image"+str(j+1))
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
		plt.savefig("Fidelity_tmp.png")
	# Global comparisons (all channels are considered together)
	plt.figure(figsize=(7,7))
	for m in np.arange(Nplots):
		nchans, b, mids, h = get_ALLvalues(FITSfile=target_image[m]+"_convo2ref_Fidelity.fits",xmin=0,xmax=100,xstep=0.5)
		plt.plot(mids,h,label="Target"+str(m+1),linewidth=3,c=IQA_colours[m])
	# Plot parameters
	plt.yscale('log')	# Make y axis in log scale
	plt.xscale('log')
	plt.xlim(1,100)
	plt.ylim(1,)
	plt.legend()
	plt.xlabel("Fidelity",fontsize=20)
	plt.ylabel(r'log$_{10}(\# pixels)$',fontsize=20)
	# Save plot?
	if save == True:
		plt.savefig("FidelityALL_tmp.png")
		print(" See results: Fidelity_tmp.png, FidelityALL_tmp.png")
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
	plt.title(title+" - Accuracy",fontsize=20,x=0,ha="left",position=(0.1,0.8))
	#plt.title("Q parameter",fontsize=10,x=1,ha="right",color='grey', style='italic')
	plt.imshow(h, extent =(-0.5,nchans-0.5,xminplot,xmaxplot), aspect='auto',vmin=0,cmap="jet", interpolation='none',origin='lower')
	plt.hlines(0,-0.5,nchans-0.5,linestyle="--",color="black",linewidth=3,label="Goal")	
	plt.xlabel("Channel number",fontsize=15)
	plt.ylabel("Accuracy",fontsize=18)
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
	plt.ylabel("Accuracy",fontsize=18)
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
	plt.title(title+" - Fidelity",fontsize=20,x=0,ha="left",position=(0.1,0.8))
	#plt.title("Q parameter",fontsize=10,x=1,ha="right",color='grey', style='italic')
	plt.imshow(h, extent =(-0.5,nchans-0.5,xminplot,xmaxplot), aspect='auto',vmin=0,cmap="jet", interpolation='none',origin='lower')
	#plt.hlines(0,-0.5,nchans-0.5,linestyle="--",color="black",linewidth=3,label="Goal")	
	plt.xlabel("Channel number",fontsize=15)
	plt.ylabel("Fidelity",fontsize=18)
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
	plt.ylabel("Fidelity",fontsize=18)
	plt.xlabel(r'log$_{10}(\# pixels)$',fontsize=15)
	plt.legend(loc="upper left",prop={"size":10})
	ax2.tick_params(labelbottom=True, labelleft=False, labelright=True,bottom=True, top=True, left=True, right=True)
	ax2.yaxis.set_label_position("right")
	# return for comparisons
	return mids, np.nanmean(h,axis=1)[:]

def show_Apar_map(ref_image,target_image,channel=0):
	"""
	Display Accuracy maps. 
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
	fig = plt.figure(figsize=(15,10))
	grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.3, hspace=0.3)

	# Panel #1: Reference
	ax1 = plt.subplot(grid[0, 0])
	image = fits.open(ref_image+".fits")
	# get min/max values
	vmin , vmax = np.min(image[0].data[-np.isnan(image[0].data)]), np.max(image[0].data[-np.isnan(image[0].data)])
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
	plt.text(0.1,0.1,"Ref: " + str(ref_image), bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
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
	plt.text(0.1,0.1,"Target: " + str(target_image), bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
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
	plt.yscale('log')	# Make y axis in log scale
	plt.legend(loc="lower right")
	plt.xlabel("Accuracy parameter",fontsize=20)
	plt.ylabel(r'Number of pixels',fontsize=20)


def show_Fidelity_map(ref_image,target_image,channel=0):
	"""
	Display Fifelity maps. 
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
	fig = plt.figure(figsize=(15,10))
	grid = plt.GridSpec(ncols=2,nrows=2, wspace=0.3, hspace=0.3)

	# Panel #1: Reference
	ax1 = plt.subplot(grid[0, 0])
	image = fits.open(ref_image+".fits")
	# get min/max values
	vmin , vmax = np.min(image[0].data[-np.isnan(image[0].data)]), np.max(image[0].data[-np.isnan(image[0].data)])
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
	plt.text(0.1,0.1,"Ref: " + str(ref_image), bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
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
	plt.text(0.1,0.1,"Target: " + str(target_image), bbox={'facecolor': 'white', 'pad': 10},transform=ax1.transAxes)
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
	plt.yscale('log')	# Make y axis in log scale
	plt.legend()
	plt.xlabel("Fidelity",fontsize=20)
	plt.ylabel(r'Number of pixels',fontsize=20)




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
	 Generate aperture plot ata given position (x,y)
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
	vmin , vmax = np.min(image[0].data[-np.isnan(image[0].data)]), np.max(image[0].data[-np.isnan(image[0].data)])
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

