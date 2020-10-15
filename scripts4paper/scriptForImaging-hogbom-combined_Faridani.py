# ALMA Data Reduction Script, D. Petry (ESO), Aug 2020
# modified by N. Pingel to include Faridani step in Sept 2020, 
# based on edits of M. Hoffman in Aug 2020 to add 
# Feather step in Aug 2020

# Helper Functions

# BUNIT from the header
def getBunit(imName):
		ia.open(str(imName))
		summary = ia.summary()
		return summary['unit']

# BMAJ beam major axis in units of arcseconds
def getBmaj(imName):
		ia.open(str(imName))
		summary = ia.summary()
		if 'perplanebeams' in summary:
				n = summary['perplanebeams']['nChannels']//2
				b = summary['perplanebeams']['beams']['*%d' % n]['*0']
		else:
				b = summary['restoringbeam']
		major = b['major']
		unit  = major['unit']
		major_value = major['value']
		if unit == 'deg':
				major_value = major_value * 3600
				
		return major_value

# BMIN beam minor axis in units of arcseconds
def getBmin(imName):
		ia.open(str(imName))
		summary = ia.summary()
		if 'perplanebeams' in summary:
				n = summary['perplanebeams']['nChannels']//2
				b = summary['perplanebeams']['beams']['*%d' % n]['*0']
		else:
				b = summary['restoringbeam']

		minor = b['minor']
		unit = minor['unit']
		minor_value = minor['value']
		if unit == 'deg':
				minor_value = minor_value * 3600
		return minor_value

# Position angle of the interferometeric data
def getPA(imName):
		ia.open(str(imName))
		summary = ia.summary()
		if 'perplanebeams' in summary:
				n = summary['perplanebeams']['nChannels']//2
				b = summary['perplanebeams']['beams']['*%d' % n]['*0']
		else:
				b = summary['restoringbeam']

		pa_value = b['positionangle']['value']
		pa_unit  = b['positionangle']['unit']
		return pa_value, pa_unit


# Imaging
thesteps = []
step_title = {0: 'Concat the MSs',
							1: 'Make dirty image', 
							2: 'Auto-masking TCLEAN',
							3: 'Faridani combined agg. bandwidth image with TP image',
							4: 'Export images to FITS format',
							5: 'Clean-up'}

try:
	print('List of steps to be executed ...', mysteps)
	thesteps = mysteps
except:
	print('global variable mysteps not set.')
if (thesteps==[]):
	thesteps = range(0,len(step_title))
	print('Executing all steps: ', thesteps)

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]
# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.


# put restfreqs in this dictionary,
# one for each SPW ID, e.g. {17: '350GHz', 19: '356GHz'}
therestfreqs = {0: '115.GHz'}


mystep = 0
if(mystep in thesteps):
	casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
	print('Step ', mystep, step_title[mystep])

	thevis = ['skymodel-b_120L.alma.cycle6.4.2018-10-02.ms',
						'skymodel-b_120L.alma.cycle6.1.2018-10-02.ms',
						'skymodel-b_120L.alma.cycle6.4.2018-10-03.ms',
						'skymodel-b_120L.alma.cycle6.1.2018-10-03.ms',
						'skymodel-b_120L.alma.cycle6.4.2018-10-04.ms',
						'skymodel-b_120L.alma.cycle6.1.2018-10-04.ms',
						'skymodel-b_120L.alma.cycle6.4.2018-10-05.ms',
						'skymodel-b_120L.alma.cycle6.1.2018-10-05.ms',
						'skymodel-b_120L.aca.cycle6.2018-10-20.ms',
						'skymodel-b_120L.aca.cycle6.2018-10-21.ms',
						'skymodel-b_120L.aca.cycle6.2018-10-22.ms',
						'skymodel-b_120L.aca.cycle6.2018-10-23.ms']

	weightscale = [1., 1., 1., 1., 1., 1., 1., 1.,
								 0.116, 0.116, 0.116, 0.116]

	concat(vis=thevis, 
				 concatvis='skymodel-a_120L.alma.all_int-weighted.ms',
				 visweightscale = weightscale)

######################
## Dirty image
######################

mystep = 1
if(mystep in thesteps):
	casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
	print('Step ', mystep, step_title[mystep])

	thevis = 'skymodel-b_120L.alma.all_int-weighted.ms'

	os.system('rm -rf gmc_120L.inter.dirt*')
	tclean(vis = thevis,
				 imagename = 'skymodel-b_120L.inter.dirt',
				 field = '0~68',
				 intent = 'OBSERVE_TARGET#ON_SOURCE',
				 phasecenter = 'J2000 12:00:00 -35.00.00.0000',
				 stokes = 'I',
				 spw = '0',
				 outframe = 'LSRK',
				 specmode = 'mfs',
				 nterms = 1,
				 imsize = [1120, 1120],
				 cell = '0.21arcsec',
				 deconvolver = 'hogbom',
				 niter = 0,
				 weighting = 'briggs',
				 robust = 0.5,
				 mask = 'pb',pbmask=0.2,
				 gridder = 'mosaic',
				 pbcor = True,
				 interactive = False
				 )

######################
## Auto-masking
######################
mystep = 2
if(mystep in thesteps):
	casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
	print('Step ', mystep, step_title[mystep])

	thevis = 'skymodel-a_120L.alma.all_int-weighted.ms'
	threshold = '0.011Jy' ## peak / 1000*3
	#threshold = '0.038Jy' ## peak / 1000
	
	os.system('rm -rf gmc_120L.inter.auto*')
	tclean(vis = thevis,
				 imagename = 'skymodel-b_120L.inter.auto',
				 field = '0~68',
				 intent = 'OBSERVE_TARGET#ON_SOURCE',
				 phasecenter = 'J2000 12:00:00 -35.00.00.0000',
				 stokes = 'I',
				 spw = '0',
				 outframe = 'LSRK',
				 specmode = 'mfs',
				 nterms = 1,
				 imsize = [1120, 1120],
				 cell = '0.21arcsec',
				 deconvolver = 'hogbom',
				 niter = 1000000,
				 cycleniter = 100000,
				 cyclefactor=2.0,
				 weighting = 'briggs',
				 robust = 0.5,
				 gridder = 'mosaic',
				 pbcor = True,
				 threshold = threshold,
				 interactive = True,
				 # Automasking Parameters below this line
				 usemask='auto-multithresh',
				 sidelobethreshold=2.0,
				 noisethreshold=4.25,
				 lownoisethreshold=1.5, 
				 minbeamfrac=0.3,
				 growiterations=75,
				 negativethreshold=0.0,
				 verbose=True)

#################################
## Faridani
## adopted from script, ssc_DC.py
## written by Lydia Moser-Fischer
#################################

mystep = 3
if(mystep in thesteps):
	casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
	print('Step ', mystep, step_title[mystep])

	#####################################
	#             USER INPUTS           #
	#####################################
	# Only user inputs required are the 
	# high res, low res, pb name, and sdfactor (scaling factor)
	sdfactor = 1.0

	highres='skymodel-b_120L.inter.auto.image'
	lowres='skymodel-b_120L.sd.image/'
	#lowres='gmc_reorder.image'
	pb='skymodel-b_120L.inter.auto.pb'

	#####################################
	#            PROCESS DATA           #
	#####################################
	# Reorder the axes of the low to match high/pb 

	myfiles=[highres,lowres]
	mykeys=['cdelt1','cdelt2','cdelt3','cdelt4']

	im_axes={}
	print('Making dictionary of axes information for high and lowres images')
	for f in myfiles:
			 print(f)
			 print('------------')
			 axes = {}
			 i=0
			 for key in mykeys:
					 q = imhead(f,mode='get',hdkey=key)
					 axes[i]=q
					 i=i+1
					 print(str(key)+' : '+str(q))
			 im_axes[f]=axes
			 print(' ')

	# Check if axes order is the same, if not run imtrans to fix, could be improved
	order=[]           

	for i in range(4):
			 hi_ax = im_axes[highres][i]['unit']
			 lo_ax = im_axes[lowres][i]['unit']
			 if hi_ax == lo_ax:
					 order.append(str(i))
			 else:
					 lo_m1 = im_axes[lowres][i-1]['unit']
					 if hi_ax == lo_m1:
							 order.append(str(i-1))
					 else:
							 lo_p1 = im_axes[lowres][i+1]['unit']
							 if hi_ax == lo_p1:
									 order.append(str(i+1))
	order = ''.join(order)
	print('order is '+order)

	if order=='0123':
			 print('No reordering necessary')
	else:
			imtrans(imagename=lowres,outfile='lowres.ro',order=order)
			lowres='lowres.ro'
			print('Had to reorder!')

	# Regrid low res Image to match high res image
	print('Regridding lowres image...')
	imregrid(imagename=lowres,
					 template=highres,
					 axes=[0,1,2,3],
					 output='lowres.regrid')

	# Multiply the lowres image with the highres primary beam response
	print('Multiplying lowres by the highres pb...')
	immath(imagename=['lowres.regrid',
										pb],
				 expr='IM0*IM1',
				 outfile='lowres.multiplied')

	lowres_regrid = 'lowres.multiplied'

	print('')
	print('LR_Bmin: ' + str(getBmin(lowres_regrid)))
	print('LR_Bmaj: ' + str(getBmaj(lowres_regrid)))
	print('')
	print('HR_Bmin: ' + str(getBmin(highres)))
	print('HR_Bmaj: ' + str(getBmaj(highres)))
	print('')

	kernel1 = float(getBmaj(lowres_regrid))**2 - float(getBmaj(highres))**2
	kernel2 = float(getBmin(lowres_regrid))**2 - float(getBmin(highres))**2

	kernel1 = math.sqrt(kernel1)
	kernel2 = math.sqrt(kernel2)
	
	print('Kernel1: ' + str(kernel1))
	print('Kernel2: ' + str(kernel2))
	print('')

	# Convolve the highres with the appropriate beam so it matches the lowres 
	print('Convolving high resolution cube ...')
	major = str(getBmaj(lowres_regrid)) + 'arcsec'
	minor = str(getBmin(lowres_regrid)) + 'arcsec'
	pa = str(getPA(highres)[0]) + str(getPA(highres)[1])
	print('imsmooth',major,minor,pa)
	imsmooth(highres, 'gauss', major, minor, pa, True, outfile=highres + '_conv', overwrite=True)

	highres_conv = highres + '_conv'

	# Missing flux
	print('Computing the obtained flux only by single-dish ...')
	immath([lowres_regrid, highres_conv], 'evalexpr', 'sub.im', '%s*IM0-IM1' % sdfactor)
	print('Flux difference has been determined' + '\n')
	print('Units', getBunit(lowres_regrid))

	sub = 'sub.im'
	sub_bc = 'sub_bc.im'


	# Feather together the low*pb and hi images
	#print('Feathering...')
	#feather(imagename='gmc_120L.Feather.image',
	#        highres=highres,
	#        lowres='lowres.multiplied')

	#os.system('rm -rf gmc_120L.Feather.image.pbcor')
	#immath(imagename=['gmc_120L.Feather.image',
	#                'gmc_120L.alma.all_int-mfs.I.manual-weighted.pb'],
	#     expr='IM0/IM1',
	#     outfile='gmc_120L.Feather.image.pbcor')

	if getBunit(lowres_regrid) == 'Jy/beam':
		print('Computing the weighting factor according to the surface of the beam ...')
		weightingfac = (float(getBmaj(str(highres))) * float(getBmin(str(highres)))
				) / (float(getBmaj(str(lowres_regrid))) * float(getBmin(str(lowres_regrid))))
		print('Weighting factor: ' + str(weightingfac) + '\n')
		print('Considering the different beam sizes ...')
		os.system('rm -rf %s' % sub_bc)        
		immath(sub, 'evalexpr', sub_bc, 'IM0*' + str(weightingfac))
		print('Fixed for the beam size' + '\n')
		print('Combining the single-dish and interferometer cube [Jy/beam mode]')
		highresbase = highres.split('/')[-1].split('.image')[0]  
		combined = highresbase + '_ssc_f%s_TP.image'  % sdfactor
		os.system('rm -rf %s' % combined)        
		immath([highres, sub_bc], 'evalexpr', combined, 'IM0+IM1')
		print('The missing flux has been restored' + '\n')

	if getBunit(lowres_regrid) == 'Kelvin':
		print('Combining the single-dish and interferometer cube [K-mode]')
		os.system('rm -rf %s' % combined)                
		immath([highres, sub], 'evalexpr', combined, 'IM0 + IM1')
		print('The missing flux has been restored' + '\n')

	## finally, perform the primary beamc correction
	os.system(combined +'.pbcor')
	immath(imagename=[combined,
		pb],
		expr='IM0/IM1',
		outfile=combined +'.pbcor')

# Export images to FITS format
mystep = 4
if(mystep in thesteps):
	casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
	print('Step ', mystep, step_title[mystep])

	myimages = ['skymodel-b_120L.inter.auto']

	for myimagebase in myimages:
		exportfits(imagename = myimagebase+'.image.pbcor',
							 fitsimage = myimagebase+'.pbcor.fits',
							 overwrite = True
							 )

		exportfits(imagename = myimagebase+'.image',
							 fitsimage = myimagebase+'.image.fits',
							 overwrite = True
							 )
 
		exportfits(imagename = myimagebase+'.pb',
							 fitsimage = myimagebase+'.pb.fits',
							 overwrite = True
							 )
	
	myimages = ['skymodel-b_120L.sd']
	
	for myimagebase in myimages:
		exportfits(imagename = myimagebase+'.image',
							 fitsimage = myimagebase+'.fits',
							 overwrite = True
							 )

	myimages = ['skymodel-b_120L.inter.auto_ssc_f%s_TP' % sdfactor]
	
	for myimagebase in myimages:
		 exportfits(imagename = myimagebase+'.image.pbcor',
							 fitsimage = myimagebase+'.pbcor.fits',
							 overwrite = True
							 )

		 exportfits(imagename = myimagebase+'.image',
							 fitsimage = myimagebase+'.image.fits',
							 overwrite = True
							 )
 
## clean up
mystep = 5
if (mystep in thesteps):
	casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
	print('Step ', mystep, step_title[mystep])
	os.system('rm -rf lowres.regrid')
	os.system('rm -rf lowres.multiplied')
	os.system('rm -rf skymodel-b_120L.inter.auto.image_conv')
	os.system('rm -rf sub.im')
	os.system('rm -rf sub_bc.im')
	os.system('rm -rf skymodel-b_120L.inter.auto_ssc_f1.0_TP.image')
	os.system('rm -rf skymodel-b_120L.inter.auto_ssc_f1.0_TP.image.pbcor')

	
