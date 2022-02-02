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


import math
import os
import sys
#import datetime       # where is it needed? I don't see it

testMode = False

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

# our Main
def ssc(project, highres=None, lowres=None, f=1.0, sdTel = None, regrid=True, cleanup=True, label="", niteridx=0, name="dirtymap"):
    """
        project     directory in which all work will be performed
        highres     high res (interferometer) image
        lowres      low res (SD/TP) image
        sdTEL       if not provided, sdFITS must contain the telescope
        regrid      if you are sure of the same WCS, set this to False
    """
    if niteridx == 0:
        niter_label = ""
    else:
        # otherwise the niter label reflect the tclean naming convention
        # e.g. tclean used niter = [0, 1000, 2000] and returned dirtymap, dirtymap_2, and dirtymap_3
        # to get the second iteration of tclean (niter=1000), niteridx = 1
        niter_label = "_%s"%(niteridx + 1)

    if highres == None:
        highres = "%s/%s%s.image"   % (project,name,niter_label)
    if lowres == None:
        lowres  = "%s/otf%s.image"  % (project,label)   
    
    print('SSC array combination method')
    print('   Single-dish: ',lowres)
    print('   Interferometer: ',highres)
    print('   Single-dish Telescope: ',sdTel)
    print('   f (scaling SD):',f)

    lr = lowres                                  # input low resolution cube
    hr = highres                                 # input high resolution cube

    # temp files
    lr_reg    = project + '/LR_reg.im'             # regridded low resolution cube
    hr_conv   = project + '/HR_conv.im'            # convolved high resolution cube
    sub       = project + '/sub.im'                # observed flux only by single-dish
    sub_bc    = project + '/sub_bc.im'             # Corrected flux by the ratio of beam sizes
    clean_up  = [lr_reg, hr_conv, sub, sub_bc]   # collect filenames we need to clean

    # final results
    highresbase = highres.split('/')[-1].split('.image')[0]       
    combined  = project + highresbase + '_ssc_f%sTP%s%s.image'  % (f,label,niter_label)

    # Re-gridding the lowres Single-dish cube to that of the highres Interferometer cube
    if regrid:
        print('Regridding ... the default interpolation scheme is linear')
        imregrid(lr,hr,lr_reg, overwrite=True, asvelocity=True)
    else:
        lr_reg = lr


    # Check if both data sets are in the same units
    if str(getBunit(lr_reg)) != str(getBunit(hr)):
        print('Bunits of low- and high-resolution data cubes are not identical!')
        return None

    print('')
    print('LR_Bmin: ' + str(getBmin(lr_reg)))
    print('LR_Bmaj: ' + str(getBmaj(lr_reg)))
    print('')
    print('HR_Bmin: ' + str(getBmin(hr)))
    print('HR_Bmaj: ' + str(getBmaj(hr)))
    print('')

    kernel1 = float(getBmaj(lr_reg))**2 - float(getBmaj(hr))**2
    kernel2 = float(getBmin(lr_reg))**2 - float(getBmin(hr))**2
    if kernel1 < 0 or kernel2 < 0:
        print('Lowres image seems to have smaller beam than Hightes image')
        return None
    kernel1 = math.sqrt(kernel1)
    kernel2 = math.sqrt(kernel2)
    
    print('Kernel1: ' + str(kernel1))
    print('Kernel2: ' + str(kernel2))
    print('')

    # Convolve the highres with the appropriate beam so it matches the lowres 
    print('Convolving high resolution cube ...')
    major = str(getBmaj(lr_reg)) + 'arcsec'
    minor = str(getBmin(lr_reg)) + 'arcsec'
    pa = str(getPA(hr)[0]) + str(getPA(hr)[1])
    print('imsmooth',major,minor,pa)
    imsmooth(hr, 'gauss', major, minor, pa, True, outfile=hr_conv, overwrite=True)

    # Missing flux
    print('Computing the obtained flux only by single-dish ...')
    os.system('rm -rf %s' % sub)
    immath([lr_reg, hr_conv], 'evalexpr', sub, '%g*IM0-IM1' % f)
    print('Flux difference has been determined' + '\n')
    print('Units', getBunit(lr_reg))

    if getBunit(lr_reg) == 'Jy/beam':
        print('Computing the weighting factor according to the surface of the beam ...')
        weightingfac = (float(getBmaj(str(hr))) * float(getBmin(str(hr)))
                        ) / (float(getBmaj(str(lr_reg))) * float(getBmin(str(lr_reg))))
        print('Weighting factor: ' + str(weightingfac) + '\n')

        print('Considering the different beam sizes ...')
        os.system('rm -rf %s' % sub_bc)        
        immath(sub, 'evalexpr', sub_bc, 'IM0*' + str(weightingfac))
        print('Fixed for the beam size' + '\n')

        print('Combining the single-dish and interferometer cube [Jy/beam mode]')
        os.system('rm -rf %s' % combined)        
        immath([hr, sub_bc], 'evalexpr', combined, 'IM0+IM1')
        print('The missing flux has been restored' + '\n')

    if getBunit(lr_reg) == 'Kelvin':
        print('Combining the single-dish and interferometer cube [K-mode]')
        os.system('rm -rf %s' % combined)                
        immath([hr, sub], 'evalexpr', combined, 'IM0 + IM1')
        print('The missing flux has been restored' + '\n')

    if cleanup:
        for f in clean_up:
            print(("cleaning %s" % f))
            os.system('rm -rf %s' % f)
    else:
        print(("Preserving following files:" + str(clean_up)))

    if False:
        print('Trololooooo')   # of no use right now
        #qac_stats(lowres)
        #qac_stats(highres)
        #qac_stats(combined)

    return combined



#### to execute we need to adjust for script for "import"
#### for now it's enough to do:
#
# exec(open("ssc_DC.py").read())   
# ssc('.', highres='Nick_gmc_120L.concat.image', lowres='Nick_gmc_120L.sd.image', f = 0.8)  
#



