#
#  SSC = Short Spacing Correction
#
#        taken from Faridani's "snippet.txt",
#        adapted to work under QAC - Peter Teuben
#        adapted to work as part of DC2019 project - Sept 30th, 2020 - Lydia Moser-Fischer
#
#
# Last Update: 2017.09.30
# - Fill free to use and modify this pipeline.
# - Please consider citing the following publications
#    1) https://arxiv.org/abs/1709.09365
#    2) http://adsabs.harvard.edu/abs/2014A%26A...563A..99F
# - Or contact Shahram Faridani (shahram.faridani@gmail.com)
#
#  @todo      use PSF instead of beam header to compute? -> no, highres image has zero flux in the PSF

# modified by N. Pingel  



import os
import math
import sys


pythonversion = sys.version[0]

if pythonversion=='3':
    from casatasks import casalog
    from casatasks import exportfits
    from casatasks import imhead
    from casatasks import imsmooth      #### NEW!
#    from casatasks import sdintimaging
#    from casatasks import tclean
    from casatasks import immath
    from casatasks import imregrid, imtrans
#    from casatasks import feather
#
    from casatools import image as iatool   # compare iatool in datacomb.py
#    from casatools import quanta as qatool
else:
    pass #print("Warning: datacomb assuming not in casa6")
#




# Helper Functions

# BUNIT from the header
def getBunit(imName):     
        myia=iatool() 	
        myia.open(str(imName))
        summary = myia.summary()
        myia.close()    
        
        return summary['unit']

# BMAJ beam major axis in units of arcseconds
def getBmaj(imName):
        myia=iatool() 
        myia.open(str(imName))
        summary = myia.summary()
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
        myia.close()                    
                
        return major_value

# BMIN beam minor axis in units of arcseconds
def getBmin(imName):
        myia=iatool() 
        myia.open(str(imName))
        summary = myia.summary()
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
        myia.close()    
            
        return minor_value

# Position angle of the interferometeric data
def getPA(imName):
        myia=iatool() 
        myia.open(str(imName))
        summary = myia.summary()
        if 'perplanebeams' in summary:
                n = summary['perplanebeams']['nChannels']//2
                b = summary['perplanebeams']['beams']['*%d' % n]['*0']
        else:
                b = summary['restoringbeam']

        pa_value = b['positionangle']['value']
        pa_unit  = b['positionangle']['unit']
        myia.close()    
        
        return pa_value, pa_unit




#################################
## Faridani
## adopted from script, ssc_DC.py
## written by Lydia Moser-Fischer
#################################


def ssc(highres=None, lowres=None, pb=None, combined=None, 
        sdfactor=1.0):
    """
        highres     high res (interferometer) image
        lowres      low res (SD/TP) image
        pb          high res (interferometer) primary beam
        sdfactor    scaling factor for the SD/TP contribution

    """

    #####################################
    #             USER INPUTS           #
    #####################################
    # Only user inputs required are the 
    # high res, low res, pb name, combined name and sdfactor (scaling factor)
    
    #####sdfactor = 1.0
    #####
    #####highres='skymodel-b_120L.inter.auto.image'
    #####lowres='skymodel-b_120L.sd.image/'
    ######lowres='gmc_reorder.image'
    #####pb='skymodel-b_120L.inter.auto.pb'

    #####################################
    #            PROCESS DATA           #
    #####################################
    # Reorder the axes of the low to match high/pb 

    print('##### CHANGES ########')

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

    # Check if axes order is the same, if not run imtrans to fix, 
    # could be improved
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
    combined = combined + '.image'

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

    # Combination 
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
        #highresbase = highres.split('/')[-1].split('.image')[0]  
        #combined = highresbase + 'ssc_f%s.image'  % sdfactor
        os.system('rm -rf %s' % combined)        
        immath([highres, sub_bc], 'evalexpr', combined, 'IM0+IM1')
        print('The missing flux has been restored' + '\n')

    if getBunit(lowres_regrid) == 'Kelvin':
        print('Combining the single-dish and interferometer cube [K-mode]')
        os.system('rm -rf %s' % combined)                
        immath([highres, sub], 'evalexpr', combined, 'IM0 + IM1')
        print('The missing flux has been restored' + '\n')

    # primary beam correction
    os.system(combined +'.pbcor')
    immath(imagename=[combined,
        pb],
        expr='IM0/IM1',
        outfile=combined +'.pbcor')


#myimages = [highres]
#
#for myimagebase in myimages:
#    exportfits(imagename = myimagebase+'.pbcor',
#                         fitsimage = myimagebase+'.pbcor.fits',
#                         overwrite = True
#                         )
#
#    exportfits(imagename = myimagebase,
#                         fitsimage = myimagebase+'.fits',
#                         overwrite = True
#                         )
#myimages = [pb]
#
#for myimagebase in myimages: 
#    exportfits(imagename = myimagebase,
#                         fitsimage = myimagebase+'.fits',
#                         overwrite = True
#                         )
#
#myimages = [lowres]
#
#for myimagebase in myimages:
#    exportfits(imagename = myimagebase+'.image',
#                         fitsimage = myimagebase+'.fits',
#                         overwrite = True
#                         )
#
    myimages = [combined]
    
    for myimagebase in myimages:
         exportfits(imagename = myimagebase+'.pbcor',
                             fitsimage = myimagebase+'.pbcor.fits',
                             overwrite = True
                             )
    
         exportfits(imagename = myimagebase,
                             fitsimage = myimagebase+'.fits',
                             overwrite = True
                             )
     
 
    # Tidy up 
    os.system('rm -rf lowres.regrid')
    os.system('rm -rf lowres.multiplied')
    os.system('rm -rf '+highres_conv)
    os.system('rm -rf '+sub)
    os.system('rm -rf '+sub_bc)
    #os.system('rm -rf '+combined)
    #os.system('rm -rf '+combined+'.pbcor')
    
