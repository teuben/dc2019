"""The datacomb module

Tools for different methods of interferometric/single-dish 
data combination with CASA.

Based on the work at the Workshop
"Improving Image Fidelity on Astronomical Data", 
Lorentz Center, Leiden, August 2019, 
and subsequent follow-up work. 

Run under CASA 6, no support for CASA 5

"""

import os
import math
import sys
import glob
import numpy as np
import re
from importlib import reload

import analysisUtils as au


import tp2vis as t2v

# new style
#import casatools as cto   # is it used anywhere? 
import casatasks as cta

# old style
from casatools import table  as tbtool
from casatools import image  as iatool
from casatools import quanta as qatool
from casatools import msmetadata as msmdtool


reload(t2v)





##########################################


def export_fits(imname, clean_origin=''):

    """
    standardized output from a combination method  (Moser-Fischer, L.)

    imname - file name base
    clean_origin - file name base of intermediate cleaning products that imname is based on (e.g. feather products is based on tclean products)
                   
    """

    print('')
    print('Exporting following final image products to FITS:')

    for suffix in ['.image.pbcor', '.pb']:
        if clean_origin!='' and suffix=='.pb':
            os.system('cp -r '+clean_origin+suffix+' '+imname+suffix)
        os.system('rm -rf '+imname+suffix+'.fits')   
        print('-', suffix)
        cta.exportfits(imname+suffix, imname+suffix+'.fits')
    print('Export done.')
    print('')
    
    return True






##########################################


def convert_JypB_JypP(sdimage):

    """
    convert image brightness unit from Jy/beam to Jy/pixel  (Moser-Fischer, L.)
    a helper for runWSM to prepare the startmodel format

    usemask - masking mode parameter as for tclean
    mask - file name of mask
    pbmask - PB mask cut-off level 
    niter - number of iterations spent on this mask

    """

    myimhead = cta.imhead(sdimage)


    print('Checking SD units...')
    if myimhead['unit']=='Jy/beam': 
        print('SD units {}. OK, will convert to Jy/pixel.'.format(myimhead['unit']))
        ##CHECK: header units
        SingleDishResolutionArcsec = myimhead['restoringbeam']['major']['value'] #in Arcsec
        CellSizeArcsec = abs(myimhead['incr'][0])*206265. #in Arcsec
        toJyPerPix = CellSizeArcsec**2/(1.1331*SingleDishResolutionArcsec**2)
        SDEfficiency = 1.0 #--> Scaling factor
        fluxExpression = "(IM0 * {0:f} / {1:f})".format(toJyPerPix,SDEfficiency)
        #scaled_name = sdimage.split('/')[-1]+'.Jyperpix'
        scaled_name = sdimage+'.Jyperpix'
        
        os.system('rm -rf '+scaled_name)
        cta.immath(imagename=sdimage,
                   outfile=scaled_name,
                   mode='evalexpr',
                   expr=fluxExpression)
        hdval = 'Jy/pixel'
        dummy = cta.imhead(imagename=scaled_name,
                           mode='put',
                           hdkey='BUNIT',
                           hdvalue=hdval)
        ### TO DO: MAY NEED TO REMOVE BLANK 
        ### and/or NEGATIVE PIXELS IN SD OBSERVATIONS
        return scaled_name
    elif myimhead['unit']=='Jy/pixel': 
        print('SD units {}. SKIP conversion. '.format(myimhead['unit']))
        return sdimage
    else: 
        print('SD units {}. NOT OK, needs conversion by user to Jy/beam or Jy/pixel. '.format(myimhead['unit']))
        return sys.exit()










##########################################

def derive_maxscale(vis, restfreq=''):

    """
    get maxscale for multiscale-deconvolver (Moser-Fischer, L.)
    a helper for runsdintimg and runtclean

    usemask - masking mode parameter as for tclean
    mask - file name of mask
    pbmask - PB mask cut-off level 
    niter - number of iterations spent on this mask

    """

    #file_check_vis(vis)     
        
        
    print('### Deriving maxscale for multiscale')
    p05 = au.getBaselineStats(vis, percentile=5, verbose=False)[0]
    if restfreq!='':
        if 'GHz' in restfreq:
            repfreq = float(restfreq.replace('GHz',''))*10**9
        elif 'MHz' in restfreq:
            repfreq = float(restfreq.replace('MHz',''))*10**6
        elif 'kHz' in restfreq:
            repfreq = float(restfreq.replace('kHz',''))*10**3   
        elif 'Hz' in restfreq:
            repfreq = float(restfreq.replace('Hz',''))
    else:
        if type(vis) is str:
            repfreq=au.medianFrequencyOfIntent(vis, verbose=False)  #[Hz]
        elif isinstance(vis, list):
            refreqs=[]
            for i in range(0,len(vis)):
                repfreqi=au.medianFrequencyOfIntent(vis[i], verbose=False) #[Hz]
                refreqs.append(refreqsi)
            refreq=np.mean(refreqs)
            
                
    # following ALMA technical handbook:
    # maximum recoverable scale = 0.983* lambda[m]/5th_percentile_baseline[m]*206265.
    c=2.99*10**8
    freq= float(repfreq)
    radiantoarcsec = 3600. * 180 / np.pi
    
    mrs = round((0.983 * c / freq / p05 * radiantoarcsec),3)
    mrsfac=0.5
    maxscale = round((mrs * mrsfac),3)
    freqout=round(freq/10**9,3)
    
    print('')
    print('### Maximum recoverable scale (mrs) for ' + vis + ' at', freqout ,'GHz is', mrs, 'arcsec')
    print('### Will use', mrsfac, 'of it as maxscale, i.e.', maxscale, 'arcsec' )
                  
    return maxscale
    
    
    
    

##########################################

def report_mask(usemask, mask, pbmask, niter       
                ):

    """
    report selected mask used for tclean/sdint (Moser-Fischer, L.)
    a helper for runsdintimg and runtclean

    usemask - masking mode parameter as for tclean
    mask - file name of mask
    pbmask - PB mask cut-off level 
    niter - number of iterations spent on this mask

    """
     
    print('')
    if usemask == 'auto-multithresh':
        print('### Run with {0} mask for {1} iterations ###'.format(usemask,niter))        
    elif usemask =='pb':
        print('### Run with {0} mask on PB level {1} for {2} iterations ###'.format(usemask,pbmask,niter))
    elif usemask == 'user':
        if os.path.exists(mask):
           print('### Run with {0} mask {1} for {2} iterations ###'.format(usemask,mask,niter))
        else:
           print('### WARNING:   mask '+mask+' does not exist, or is not specified. ###')
           #return False
    else:
        print("### Invalid usemask '"+usemask+"'. Please, check the mask options. ###")
        return False
    print('---------------------------------------------------------')







##########################################

def check_prep_tclean_param(  
                vis,     
                spw, 
                field, 
                specmode,                                 
                imsize, 
                cell, 
                phasecenter,         
                start, 
                width, 
                nchan, 
                restfreq,
                threshold, 
                niter,
                usemask,
                sidelobethreshold,
                noisethreshold,
                lownoisethreshold, 
                minbeamfrac,
                growiterations,
                negativethreshold,                
                mask, 
                pbmask,
                interactive,               
                multiscale, 
                maxscale,
                loadmask,
                fniteronusermask
                ):

    """
    check validity of parameters and set up tclean parameters in a uniform manner
    (Moser-Fischer, L.)
    a helper for runsdintimg and runtclean
    Currently, it provides 'cube' and 'mfs' as spectral modes - 'mtmfs'
    might be implemented later.
    
    steps:
    - check 

    
    vis  
    spw - 
    field, 
    specmode,                                 
    imsize, 
    cell, 
    phasecenter,         
    start, 
    width, 
    nchan, 
    restfreq,
    threshold, 
    niter,
    usemask,
    sidelobethreshold,
    noisethreshold,
    lownoisethreshold, 
    minbeamfrac,
    growiterations,
    negativethreshold,                
    mask, 
    pbmask,
    interactive,               
    multiscale, 
    maxscale,
    loadmask,
    fniteronusermask      

    """

    # valid specmode?
    if specmode not in ['mfs', 'cube']:
        print('specmode \"'+specmode+'\" is not supported.')
        return sys.exit()


    # valid threshold?
    if not type(threshold) == str or 'Jy' not in threshold and niter>1:
        if not interactive:
            print("You must provide a valid threshold, example '1mJy'")
            return sys.exit()
        else:
            print("You have not set a valid threshold. Please do so in the graphical user interface!")
            threshold = '1mJy'
    
    
    # valid image and cell size?
    if imsize==[] or cell=='':
        cta.casalog.post('You need to provide values for the parameters imsize and cell.', 'SEVERE', origin='runsdintimg')
        return sys.exit()    
    

    if loadmask==True and fniteronusermask>1.0 or fniteronusermask<0.0:
        print('fniteronusermask is out of range: ' +fniteronusermask+' Please choose a value between 0 and 1 (inclusively)')
        return sys.exit()    
    else:
        pass    
    

    #   # specmode, deconvolver and multiscale setup
    #   if multiscale:
    #       if specmode == 'mfs':
    #           mydeconvolver = 'mtmfs'   # needed bc it's the only mfs mode implemented into sdint
    #       elif specmode == 'cube':
    #           mydeconvolver = 'multiscale'
    #           #numchan = nchan           # not really needed here?
    #       mycell = myqa.convert(myqa.quantity(cell),'arcsec')['value']
    #       myscales = [0]
    #       for i in range(0, int(math.log(maxscale/mycell,3))):
    #           myscales.append(3**i*5)
    #   
    #       print("My scales (units of pixels): "+str(myscales))
    #   
    #   else:    
    #       myscales = [0]
    #       if specmode == 'mfs':
    #           mydeconvolver = 'mtmfs'   # needed bc the only mfs mode implemented into sdint
    #       elif specmode == 'cube':
    #           mydeconvolver = 'hogbom'
    #           #numchan = nchan           # not really needed here?





    
    # specmode, deconvolver and multiscale setup
    if multiscale:
        mydeconvolver = 'multiscale'
        if maxscale==-1:
            maxscale=derive_maxscale(vis, restfreq=restfreq)
        myqa = qatool()
        mycell = myqa.convert(myqa.quantity(cell),'arcsec')['value']
        myscales = [0]
        for i in range(0, int(math.log(maxscale/mycell,3))):
            myscales.append(3**i*5)

        print("My scales (units of pixels): "+str(myscales))

    else:    
        myscales = [0]
        mydeconvolver = 'hogbom'


    # weighting schemes
    if specmode == 'mfs':
        weightingscheme ='briggs'     # cont mode 
    elif specmode == 'cube':
        weightingscheme ='briggs'#bwtaper'   # special briggs for cubes --- WAIT FOR IMPLEMENTATION IN SDINT 

        



    # others
    npnt = 0    
    if phasecenter=='':
        phasecenter = npnt

    if restfreq=='':
        therf = []
    else:
        therf = [restfreq]


    clean_arg=dict(vis=vis,
                   field = field,
                   phasecenter=phasecenter,
                   imsize=imsize,
                   cell=cell,                                   
                   spw=spw,
                   specmode=specmode,
                   deconvolver=mydeconvolver,
                   scales=myscales,
                   nterms=1,                  # nterms=1 turns mtmfs into mfs, CASA 6.2 needs nterms=2 to run (bug?)
                   start=start,
                   width=width,
                   nchan = nchan, #numchan, 
                   restfreq=therf,
                   gridder='mosaic',          
                   weighting = weightingscheme,
                   robust = 0.5,
                   restoringbeam = 'common',   # SD-cube has only one beam - INT-cube needs it, too, else feather etc. fail
                   niter=niter,
                   cyclefactor=2.0,
                   threshold=threshold,
                   interactive = interactive,
                   pbcor=True,               
                   # Masking Parameters below this line 
                   # --> Should be updated depending on dataset
                   usemask=usemask,
                   sidelobethreshold=sidelobethreshold,
                   noisethreshold=noisethreshold,
                   lownoisethreshold=lownoisethreshold, 
                   minbeamfrac=minbeamfrac,
                   growiterations=growiterations,
                   negativethreshold=negativethreshold,
                   mask=mask,
                   pbmask=pbmask,
                   verbose=True)

    return clean_arg











##########################################

def runsdintimg(vis, 
                sdimage, 
                imname, 
                sdpsf='',
                sdgain=5, 
                dishdia=12.0,                
                spw='', 
                field='', 
                specmode='mfs',                                 
                imsize=[], 
                cell='', 
                phasecenter='',         
                start=0, 
                width=1, 
                nchan=-1, 
                restfreq='',
                threshold='', 
                niter=0,
                usemask= 'auto-multithresh',
                sidelobethreshold=2.0,
                noisethreshold=4.25,
                lownoisethreshold=1.5, 
                minbeamfrac=0.3,
                growiterations=75,
                negativethreshold=0.0,                
                mask   = '', 
                pbmask = 0.4,
                interactive=True,               
                multiscale=False, 
                maxscale=0.,
                continueclean=False,
                renameexport=True,
                loadmask=False,
                fniteronusermask=0.3
                ):

    """
    runsdintimg (D. Petry, ESO)
    a wrapper around the CASA task "sdintimaging"
    Currently, it provides 'cube' and 'mfs' as spectral modes - 'mtmfs'
    might be implemented later.
    
    steps:
    - check if SD image has a beam
    - if not present, create perplanebeams in SD image
    - derive multiscale sizes for 'multiscale=True'
    - clean parameter definition as known from tclean (analoguously to 'runtclean')
    --- important fixed parameters you should be aware of: 
    restoring beam = common, nterms=1 (to get mfs from mtmfs),
    weighting='briggs', robust = 0.5, gridder = 'mosaic'
    - tidy up file names and rename to a uniform output-naming style 
    - exportfits pcbor 
    
      
   

    vis - the MS containing the interferometric data
    sdimage - the Single Dish image
             Note that in case you are creating a cube, this image must be a cube
             with the same spectral grid as the one you are trying to create.
    imname - the imagename of the output images
    sdpsf - (optional) the SD PSF, must have the same coords as sdimage
           if omitted or set to '' (empty string), a PSF will be derived
           from the beam information in sdimage    
    sdgain - the weight of the SD data relative to the interferometric data
           default: 5 
             'auto' - determine the scale automatically (experimental)
    dishdia - in metres, (optional) used if no sdpsf is provided
           default: 12.0                 
    spw - the standard selection parameter spw of tclean
           default: '' i.e. all SPWs
    field - the standard selection parameter field of tclean
           default: '' i.e. all fields
    specmode - the standard tclean specmode parameter: supported are msf or cube
           default: msf 
    imsize - the standard tclean imsize parameter 
            should correspond to the imagesize for the most extended
            interferometer config.
    cell - the standard tclean cell parameter
            should correspond to the cell size for the most extended
            interferometer config, i.e. smallest beam / 5.
    phasecenter - the standard tclean phasecenter parameter
           e.g. 'J2000 12:00:00 -35.00.00.0000'
           default: '' - determine from the input MS with aU.pickCellSize
    start - the standard tclean start parameter
             default: 0
    width - the standard tclean width parameter
             default: 1
    nchan - the standard tclean nchan parameter
             default: -1
    restfreq - the restfrequency to write to the image for velocity calculations
             default: None, example: '115.271GHz'
    threshold - the tclean threshold     
    niter - the standard tclean niter parameter
             default: 0, example: niter=1000000
    usemask - the standard tclean mask parameter.  If usemask='auto-multithresh', can specify:
             sidelobethreshold, noisethreshold, lownoisethreshold, minbeamfrac, growiterations - 
             if usemask='user', must specify mask='maskname.mask' 
             if usemask='pb', can specify pbmask=0.4, or some level.
             default: 'auto-multithresh'
    interactive - if True (default) use interactive cleaning with initial mask
                  set using pbmask=0.4
                  if False use non-interactive clean with automasking (you will
                  need to provide the threshold parameter)

    multiscale - if False (default) use hogbom cleaning, otherwise multiscale
      
    maxscale - for multiscale cleaning, use scales up to this value (arcsec)
              Recommended value: 10 arcsec
             default: 0.  
    continueclean - if True, continue the runsdintimg on the sdintimaging products
              from a previous run. ALERT: previous run must have used renameexport=False,
              else the needed products have been renamed or deleted 
             default: False
    renameexport - sort out the relevant imaging products and rename them according to 
              the DC naming scheme, delete the rest.
              ALERT: if you plan to call runsdintimg again to continue work on the 
              image products of the current run, set renameexport=False to keep the sdintimaging 
              products in their native output form
             default: True
    loadmask - run sdintimaging with user-specified mask for fniteronusermask*niter iterations 
              and continue with auto-masking (usemask='auto-multithresh') for the remaining 
              niter*(1-fniteronusermask) iterations 
             default: False
    fniteronusermask - adjusting the amount of iterations spend on a usermask for loadmask=True
              allowed values: 0.0 (none in theory, in fact: 1 iteration) - 1.0 (all)
             default: 0.3         
             
             

    Examples: runsdintimg('gmc_120L.alma.all_int-weighted.ms','gmc_120L.sd.image', 
                'gmc_120L.joint-sdgain2.5', phasecenter='J2000 12:00:00 -35.00.00.0000', 
                 sdgain=2.5, spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec')

              ... will do an interactive clean for an agg. bw. image. 
                  A pbmask at level 0.4 will be suggested as a start.

              runsdintimg('gmc_120L.alma.all_int-weighted.ms','gmc_120L.sd.reimported.image', 
                 'deepclean-automask-sdgain1.25', phasecenter='J2000 12:00:00 -35.00.00.0000', 
                  sdgain=1.25, spw='0',field='0~68', imsize=[1120,1120], cell='0.21arcsec', 
                  threshold='0.012Jy', interactive=False) 

              ... will run a non-interactive clean for an agg. bw. image using automasking.

              runsdintimg('ngc253.ms','ngc253-b6-tp-cube-200chan.image', 
                          'ngc253-sdgain5', spw='0', specmode='cube', field='NGC_253',
                          imsize=[500, 500], cell='1.2arcsec', phasecenter=3, nchan = 200, 
                          start=150, width=1, restfreq='230.538GHz')

              ... will run an interactive clean on a cube.
                          

    """


    # file checks

    #   if type(vis) is str:
    #       myvis = file_check(vis)
    #         
    #   if isinstance(vis, list):
    #       for i in range(0,len(vis)):
    #           file_check(vis[i])          # if one of the files does not exist, script will exit here
    #       myvis = vis
    #   
    #   #myvis = file_check(vis)
    

    myvis = file_check_vis(vis)

    mysdimage = file_check(sdimage)
    
    mysdpsf = ''
    if sdpsf!='':
        mysdpsf = file_check(sdpsf)



    #if os.path.exists(vis):
    #    myvis = vis 
    #else:
    #    print(vis+' does not exist')
    #    return False
    #
    #
    #if os.path.exists(sdimage):
    #    mysdimage = sdimage
    #else:
    #    print(sdimage+' does not exist')
    #    return False
    #
    #mysdpsf = ''
    #if sdpsf!='':
    #    if os.path.exists(sdpsf):
    #        mysdpsf = sdpsf
    #    else:
    #        print(sdpsf+' does not exist')
    #        return False


    #   # valid specmode?
    #   if specmode not in ['mfs', 'cube']:
    #       print('specmode \"'+specmode+'\" is not supported.')
    #       return False
    #   
    #   
    #   # valid threshold?
    #   if not type(threshold) == str or 'Jy' not in threshold:
    #       if not interactive:
    #           print("You must provide a valid threshold, example '1mJy'")
    #           return False
    #       else:
    #           print("You have not set a valid threshold. Please do so in the graphical user interface!")
    #           threshold = '1mJy'


    # SDINT specific: check perplanebeams and create them if needed
    myia = iatool()
    myqa = qatool()

    myhead = cta.imhead(mysdimage)
    myaxes = list(myhead['axisnames'])
    numchan = myhead['shape'][myaxes.index('Frequency')] 
            
    print('Testing whether the sd image has per channel beams ...')
    myia.open(mysdimage)
    try:
        mybeam = myia.restoringbeam()
    except:
        myia.close()
        cta.casalog.post('ERROR: sdimage does not contain beam information.', 'SEVERE', 
                         origin='runsdintimg')
        return False

    haspcb=False
    if 'beams' in mybeam.keys():
        haspcb=True
        cta.casalog.post("The sdimage has a per channel beam.", 'INFO', 
                         origin='runsdintimg')

    myia.close()

    if not haspcb:
        os.system('rm -rf '+mysdimage+'_*')
        os.system('cp -R '+mysdimage+' '+mysdimage+'_copy')
        if numchan == 1:
            # image has only one channel; need workaround for per-channel-beam problem
            myia.open(mysdimage+'_copy')
            mycoords = myia.coordsys().torecord()
            mycoords['spectral2']['wcs']['crval'] += mycoords['spectral2']['wcs']['cdelt']
            myia.setcoordsys(mycoords)
            myia.close()
            tmpia = myia.imageconcat(outfile=mysdimage+'_pcb', infiles=[mysdimage, mysdimage+'_copy'], 
                                   axis=3, overwrite=True)
            tmpia.close()
            #mysdimage = mysdimage+'_pcb'
            numchan = 2
        else:
            os.system('cp -R '+mysdimage+' '+mysdimage+'_pcb')
            
        #os.system('cp -R '+mysdimage+' '+mysdimage+'_pcb')
      
        mysdimage = mysdimage+'_pcb'

        myia.open(mysdimage)
        myia.setrestoringbeam(remove=True)
        for i in range(numchan):
            myia.setrestoringbeam(beam=mybeam, log=True, channel=i, polarization=0) 
        myia.close()

        cta.casalog.post('Needed to give the sdimage a per-channel beam. Modifed image is in '+mysdimage, 'WARN', 
                         origin='runsdintimg')


    #   # specmode, deconvolver and multiscale setup
    #   if multiscale:
    #       if specmode == 'mfs':
    #           mydeconvolver = 'mtmfs'   # needed bc it's the only mfs mode implemented into sdint
    #       elif specmode == 'cube':
    #           mydeconvolver = 'multiscale'
    #           # mfs with nterms=1 uses numchan=2 despite nchan=-1 
    #           # (due to artificial perplanebeams created above)
    #           # nchan=numchan is the parameter handed to sdintimaging below
    #           # --> set numchan=nchan, if cube          
    #           numchan = nchan           
    #       mycell = myqa.convert(myqa.quantity(cell),'arcsec')['value']
    #       myscales = [0]
    #       for i in range(0, int(math.log(maxscale/mycell,3))):
    #           myscales.append(3**i*5)
    #   
    #       print("My scales (units of pixels): "+str(myscales))
    #   
    #   else:    
    #       myscales = [0]
    #       if specmode == 'mfs':
    #           mydeconvolver = 'mtmfs'   # needed bc the only mfs mode implemented into sdint
    #       elif specmode == 'cube':
    #           mydeconvolver = 'hogbom'
    #           # mfs with nterms=1 uses numchan=2 despite nchan=-1 
    #           # (due to artificial perplanebeams created above)
    #           # nchan=numchan is the parameter handed to sdintimaging below
    #           # --> set numchan=nchan, if cube 
    #           numchan = nchan           
    #   
    #   
    #   # weighting schemes
    #   if specmode == 'mfs':
    #       weightingscheme ='briggs'     # cont mode 
    #   elif specmode == 'cube':
    #       weightingscheme ='briggs'#bwtaper'   # special briggs for cubes --- WAIT FOR IMPLEMENTATION IN SDINT 
    #   
    #       
    #   # valid image and cell size?
    #   npnt = 0
    #   if imsize==[] or cell=='':
    #       cta.casalog.post('You need to provide values for the parameters imsize and cell.', 'SEVERE', origin='runsdintimg')
    #       return False
    #   
    #   
    #   # others
    #   if phasecenter=='':
    #       phasecenter = npnt
    #   
    #   if restfreq=='':
    #       therf = []
    #   else:
    #       therf = [restfreq]
    
       
    if niter==0:
        niter = 1
        cta.casalog.post('You set niter to 0 (zero, the default), but sdintimaging can only produce an output for niter>0. niter = 1 set automatically. ', 'WARN')
    



    #   sdint_arg=dict(vis=myvis,
    #                  imagename=imname,
    #                  sdimage=mysdimage,
    #                  field = field,
    #                  phasecenter=phasecenter,
    #                  imsize=imsize,
    #                  cell=cell,                                   
    #                  spw=spw,
    #                  specmode=specmode,
    #                  deconvolver=mydeconvolver,
    #                  scales=myscales,
    #                  nterms=1,                  # nterms=1 turns mtmfs into mfs, CASA 6.2 needs nterms=2 to run (bug?)
    #                  start=start,
    #                  width=width,
    #                  nchan = numchan, 
    #                  restfreq=therf,
    #                  gridder='mosaic',          
    #                  #weighting='briggs',
    #                  weighting = weightingscheme,
    #                  robust = 0.5,
    #                  restoringbeam = 'common',   # SD-cube has only one beam - INT-cube needs it, too, else feather etc. fail
    #                  niter=niter,
    #                  #cycleniter = niter,        # bogus if = niter
    #                  cyclefactor=2.0,
    #                  threshold=threshold,
    #                  interactive = interactive,
    #                  #perchanweightdensity=False, # better True (=default)?                  
    #                  #pblimit=0.2,               # default
    #                  pbcor=True,               
    #                  sdpsf=mysdpsf,
    #                  dishdia=dishdia,
    #                  sdgain=sdgain,
    #                  usedata='sdint',
    #                  #interpolation='linear',    # default
    #                  #wprojplanes=1,             # default & not needed
    #                  usemask=usemask,
    #                  sidelobethreshold=sidelobethreshold,
    #                  noisethreshold=noisethreshold,
    #                  lownoisethreshold=lownoisethreshold, 
    #                  minbeamfrac=minbeamfrac,
    #                  growiterations=growiterations,
    #                  negativethreshold=negativethreshold,
    #                  mask=mask,
    #                  pbmask=pbmask,
    #                  verbose=True)



    if specmode == 'cube':
        # mfs with nterms=1 uses numchan=2 despite nchan=-1 
        # (due to artificial perplanebeams created above)
        # nchan=numchan is the sdint_arg parameter handed to sdintimaging below
        # --> set numchan=nchan, if cube 
        numchan = nchan 


    sdint_arg = check_prep_tclean_param(
                myvis,     
                spw, 
                field, 
                specmode,                                 
                imsize, 
                cell, 
                phasecenter,         
                start, 
                width, 
                numchan, 
                restfreq,
                threshold, 
                niter,
                usemask,
                sidelobethreshold,
                noisethreshold,
                lownoisethreshold, 
                minbeamfrac,
                growiterations,
                negativethreshold,                
                mask, 
                pbmask,
                interactive,               
                multiscale, 
                maxscale,
                loadmask,
                fniteronusermask
                )
    
    
    #sdint_arg['vis']        =myvis
    sdint_arg['imagename']  =imname
    sdint_arg['sdimage']    =mysdimage
    sdint_arg['sdpsf']      =mysdpsf
    sdint_arg['dishdia']    =dishdia
    sdint_arg['sdgain']     =sdgain
    sdint_arg['usedata']    ='sdint'
    
    
    if specmode == 'mfs':
        sdint_arg['deconvolver'] = 'mtmfs'
    

    if continueclean == False:   
        # continueclean=True needs previous runsdint call to be executed 
        # with renameexport=False !!!! 
        os.system('rm -rf '+imname+'.*')  
        # if to be switched off, add command to delete "*.pbcor.fits"
    

    if loadmask==True:

        sdint_arg['usemask']='user'
        if fniteronusermask==0 or fniteronusermask==0.0:
            sdint_arg['niter']=1
        else:   
            sdint_arg['niter']=int(niter*fniteronusermask)

        # load mask into tclean with fniteronusermask*niter
        print('')
        print('### Load mask into sdintimaging with iterations = fniteronusermask*niter = ', fniteronusermask, ' * ', niter)
        report_mask(sdint_arg['usemask'],sdint_arg['mask'],sdint_arg['pbmask'],sdint_arg['niter'])
        tcleansresults = cta.sdintimaging(**sdint_arg)
        
        sdint_arg['usemask']=usemask
        sdint_arg['mask']=''
        # if startmodel used, it would have been loaded in tclean step before 
        # -> clear startmodel parameter for next tclean call, else crash!
        sdint_arg['startmodel']=''

        sdint_arg['niter']=niter-sdint_arg['niter']

        if sdint_arg['niter']<=0:    #avoid negative niter values and pointless executions 
            pass
        else:
            # clean and get tclean-feedback 
            print('')
            print('### Continue sdintimaging with iterations = (1-fniteronusermask)*niter = ', (1.0-fniteronusermask), ' * ', niter)
            report_mask(sdint_arg['usemask'],sdint_arg['mask'],sdint_arg['pbmask'],sdint_arg['niter'])
            tcleansresults = cta.sdintimaging(**sdint_arg)
                         
    else: 
        # clean and get tclean-feedback 
        report_mask(sdint_arg['usemask'],sdint_arg['mask'],sdint_arg['pbmask'],sdint_arg['niter'])
        tcleansresults = cta.sdintimaging(**sdint_arg)
        
    # store feedback in a file 
    pydict_to_file2(tcleansresults, imname)
    
    os.system('cp -r summaryplot_1.png '+imname+'.png')   
 


    ### SDINT Traditional OUTPUTS
    
    ## MTMFS - nterms=1
    
    #   *.int.cube.model/
    #   *.int.cube.pb/
    #   *.int.cube.psf/
    #   *.int.cube.residual/
    #   *.int.cube.sumwt/
    #   *.int.cube.weight/
    #   *.joint.cube.psf/
    #   *.joint.cube.residual/
    #   *.joint.multiterm.image.tt0/
    #   *.joint.multiterm.image.tt0.pbcor/
    #   *.joint.multiterm.image.tt0.pbcor.fits
    #   *.joint.multiterm.mask/
    #   *.joint.multiterm.model.tt0/
    #   *.joint.multiterm.pb.tt0/
    #   *.joint.multiterm.psf.tt0/
    #   *.joint.multiterm.residual.tt0/
    #   *.joint.multiterm.sumwt.tt0/
    #   *.joint.multiterm.weight.tt0/
    #   *.sd.cube.image/
    #   *.sd.cube.psf/
    #   *.sd.cube.residual/
    
    
    
    
    if renameexport == True:
        # rename SDINT outputs to common style
        print('Exporting final pbcor image to FITS ...')
        if sdint_arg['deconvolver'] =='mtmfs' and niter>0:
            oldnames=glob.glob(imname+'.joint.multiterm*')
            for nam in oldnames:
                os.system('mv '+nam+' '+nam.replace('.joint.multiterm',''))
            oldnames=glob.glob(imname+'*.tt0*')
            for nam in oldnames:
                os.system('mv '+nam+' '+nam.replace('.tt0',''))     
        
            os.system('rm -rf '+imname+'.int.cube*')
            os.system('rm -rf '+imname+'.sd.cube*')
            os.system('rm -rf '+imname+'.joint.cube*')
        
            # cta.exportfits(imname+'.image.pbcor', imname+'.image.pbcor.fits')
            # cta.exportfits(imname+'.pb', imname+'.pb.fits')
            export_fits(imname)

            
        elif sdint_arg['deconvolver'] =='hogbom' or sdint_arg['deconvolver'] =='multiscale':
            os.system('rm -rf '+imname+'.int.cube*')
            os.system('rm -rf '+imname+'.sd.cube*')     
            
            oldnames=glob.glob(imname+'.joint.cube*')
            for nam in oldnames:
                os.system('mv '+nam+' '+nam.replace('.joint.cube',''))
            
            #exportfits(imname+'.joint.cube.image.pbcor', imname+'.joint.cube.image.pbcor.fits')
            # cta.exportfits(imname+'.image.pbcor', imname+'.image.pbcor.fits')
            # cta.exportfits(imname+'.pb', imname+'.pb.fits')
            export_fits(imname)

    else:
        print('Keeping native file names - no export!')


    return True

##########################################



def runWSM(vis, 
           sdimage, 
           imname, 
           spw='', 
           field='', 
           specmode='mfs', 
           imsize=[], 
           cell='', 
           phasecenter='',
           start=0, 
           width=1, 
           nchan=-1, 
           restfreq='',
           threshold='',
           niter=0,
           usemask='auto-multithresh' ,
           sidelobethreshold=2.0,
           noisethreshold=4.25,
           lownoisethreshold=1.5, 
           minbeamfrac=0.3,
           growiterations=75,
           negativethreshold=0.0,
           #sdmasklev=0.3,           
           mask='', 
           pbmask=0.4,
           interactive=True, 
           multiscale=False, 
           maxscale=0.,
           sdfactorh=1.0,
           continueclean=False,
           loadmask=False,
           fniteronusermask=0.3
           ):

    """
    runWSM (A. Plunkett, NRAO)
    a wrapper around the CASA tasks "TCLEAN" and "FEATHER"
    in order to run TCLEAN with a single dish start model, then combine with FEATHER
   
    steps:
    - check brightness units of SD image 
    - if needed, convert SD image to Jy/pix
    - call 'runtclean' with with SD image as startmodel
    - call 'runfeather'



    vis - the MS containing the interferometric data
    sdimage - the Single Dish image
             Note that in case you are creating a cube, this image must be a cube
             with the same spectral grid as the one you are trying to create.
             ---- DEPRECATED HERE??? -----    
    imname - the imagename of the output images
    spw - the standard selection parameter spw of tclean
           default: '' i.e. all SPWs
    field - the standard selection parameter field of tclean
           default: '' i.e. all fields
    specmode - the standard tclean specmode parameter: supported are msf or cube
           default: msf 
    imsize - (optional) the standard tclean imsize parameter 
            should correspond to the imagesize for the most extended
            interferometer config.
           default: determine from the input MS with aU.pickCellSize
    cell - (optional) the standard tclean cell parameter
            should correspond to the cell size for the most extended
            interferometer config, i.e. smallest beam / 5.
           default: determine from the input MS with aU.pickCellSize
    phasecenter - the standard tclean phasecenter parameter
           e.g. 'J2000 12:00:00 -35.00.00.0000'
           default: '' - determine from the input MS with aU.pickCellSize
    start - the standard tclean start parameter
             default: 0
    width - the standard tclean width parameter
             default: 1
    nchan - the standard tclean nchan parameter
             default: -1
    restfreq - the restfrequency to write to the image for velocity calculations
             default: None, example: '115.271GHz'
    threshold - the threshold for cleaning
             default: None, example: '12mJy'
    niter - the standard tclean niter parameter
             default: 0, example: niter=1000000
    usemask - the standard tclean mask parameter.  If usemask='auto-multithresh', can specify:
             sidelobethreshold, noisethreshold, lownoisethreshold, minbeamfrac, growiterations - 
             if usemask='user', must specify mask='maskname.mask' 
             if usemask='pb', can specify pbmask=0.4, or some level.
             default: 'auto-multithresh'
    ##### sdmasklev - if usemask='user', then use SD image at this level to draw a mask.
    #####          default: 0.3
    interactive - the standard tclean interactive option
             default: True
    
    multiscale - if False (default) use hogbom cleaning, otherwise multiscale
       
    maxscale - for multiscale cleaning, use scales up to this value (arcsec)
             Recommended value: 10 arcsec
             default: 0.
    sdfactorh - Scale factor to apply to Single Dish image (same as for feather)
    continueclean - see runtclean
    loadmask - run sdintimaging with user-specified mask for fniteronusermask*niter iterations 
              and continue with auto-masking (usemask='auto-multithresh') for the remaining 
              niter*(1-fniteronusermask) iterations 
             default: False
    fniteronusermask - adjusting the amount of iterations spend on a usermask for loadmask=True
              allowed values: 0.0 (none in theory, in fact: 1 iteration) - 1.0 (all)
             default: 0.3 

    Example: runtclean('gmc_120L.alma.all_int-weighted.ms', 
                'gmc_120L', phasecenter='J2000 12:00:00 -35.00.00.0000', 
                spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec',
                threshold='12mJy',niter=100000,
                usemask='auto-multithresh')
    
    Example: runWSM('gmc_120L.alma.all_int-weighted.ms','gmc_120L.sd.image', 
                'gmc_120L.WSM', phasecenter='J2000 12:00:00 -35.00.00.0000', 
                spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec',
                threshold='12mJy',niter=100000,
                usemask='auto-multithresh')

    """

    # file checks
    #   myvis = file_check(vis)

    myvis = file_check_vis(vis)
    
    mysdimage = file_check(sdimage)
    
    #if os.path.exists(vis):
    #    myvis = vis 
    #else:
    #    print(vis+' does not exist')
    #    return False
    #
    #if os.path.exists(sdimage):
    #    mysdimage = sdimage
    #else:
    #    print(sdimage+' does not exist')
    #    return False



    # convert image brightness unit from Jy/beam to Jy/pixel, if needed
    scaled_name = convert_JypB_JypP(mysdimage)


    #   myimhead = cta.imhead(mysdimage)
    #   
    #   if myimhead['unit']=='Jy/beam': print('SD units {}. OK, will convert to Jy/pixel.'.format(myimhead['unit']))
    #   elif myimhead['unit']=='Jy/pixel': print('SD units {}. SKIP conversion. '.format(myimhead['unit']))
    #   else: print('SD units {}. NOT OK, needs conversion. '.format(myimhead['unit']))
    #   
    #   ##CHECK: header units
    #   SingleDishResolutionArcsec = myimhead['restoringbeam']['major']['value'] #in Arcsec
    #   CellSizeArcsec = abs(myimhead['incr'][0])*206265. #in Arcsec
    #   toJyPerPix = CellSizeArcsec**2/(1.1331*SingleDishResolutionArcsec**2)
    #   SDEfficiency = 1.0 #--> Scaling factor
    #   fluxExpression = "(IM0 * {0:f} / {1:f})".format(toJyPerPix,SDEfficiency)
    #   #scaled_name = mysdimage.split('/')[-1]+'.Jyperpix'
    #   scaled_name = mysdimage+'.Jyperpix'
    #   
    #   os.system('rm -rf '+scaled_name)
    #   cta.immath(imagename=mysdimage,
    #              outfile=scaled_name,
    #              mode='evalexpr',
    #              expr=fluxExpression)
    #   hdval = 'Jy/pixel'
    #   dummy = cta.imhead(imagename=scaled_name,
    #                      mode='put',
    #                      hdkey='BUNIT',
    #                      hdvalue=hdval)
    #   ### TO DO: MAY NEED TO REMOVE BLANK 
    #   ### and/or NEGATIVE PIXELS IN SD OBSERVATIONS
 

    ## TCLEAN METHOD WITH START MODEL
    print('### Start hybrid clean')                    
    #runtclean
    WSM_arg=dict(spw=spw, 
              field=field, 
              specmode=specmode,
              imsize=imsize, 
              cell=cell,
              phasecenter=phasecenter, 
              start=start,
              width=width,
              nchan=nchan,
              restfreq=restfreq,
              threshold=threshold,
              niter=niter,
              usemask=usemask,
              sidelobethreshold=sidelobethreshold,  
              noisethreshold=noisethreshold,
              lownoisethreshold=lownoisethreshold,
              minbeamfrac=minbeamfrac,
              growiterations=growiterations,
              negativethreshold=negativethreshold,         
              mask=mask,              
              pbmask=pbmask,
              interactive=interactive,
              multiscale=multiscale,
              maxscale=maxscale,
              continueclean=continueclean,
              loadmask=loadmask,
              fniteronusermask=fniteronusermask)

    runtclean(myvis, imname, startmodel=scaled_name, **WSM_arg)
 

    #if doautomask == True:
    #    WSM_arg['continueclean'] = True 
    #    WSM_arg['usemask'] = 'auto-multithresh' 
    #    runtclean(myvis, imname, **WSM_arg)
   

    ## then FEATHER METHOD 
    highres = imname+'.image'
    pb= imname+'.pb'
    featherim = imname+str(sdfactorh)
    
    runfeather(intimage=highres,intpb=pb,sdimage=sdimage,sdfactor = sdfactorh, 
               featherim=featherim)    
    return True

#################################

def runfeather(intimage,intpb, sdimage, sdfactor = 1.0, featherim='featherim'):
    """
    runfeather (A. Plunkett, NRAO)
    a wrapper around the CASA task "FEATHER,"

    steps:
    - outsourced?: reorder axes of SD image 
    - outsourced?: regrid reordered SD image 
    - regrid reordered SD image * INT primary beam = PB attenuated SD image 
    - feather INT image with PB attenuated SD image 
    - PB correct feather output
    - exportfits pbcor


    intimage - the interferometry image
             default: None, example: 'imagename.image'
    intpb - the interferometry primary beam
             default: None, example: 'imagename.pb'
    sdimage - the Single Dish image
             Note that in case you are creating a cube, this image must be a cube
             with the same spectral grid as the one you are trying to create.
             default: None, example: 'TPimage.image'
    sdfactor - Scale factor to apply to Single Dish image
    featherim - the name of the output feather image
             default: 'featherim'


    Example: runfeather(intimage='',intpb='',sdimage='',featherim='')
    """
    ## Call Feather module

    # file checks
    mysdimage = file_check(sdimage)

    myintimage = file_check(intimage)

    myintpb = file_check(intpb)


    #if os.path.exists(sdimage):
    #    mysdimage = sdimage
    #else:
    #    print(sdimage+' does not exist')
    #    return False
    #
    #if os.path.exists(intimage):
    #    myintimage = intimage
    #else:
    #    print(intimage+' does not exist')
    #    return False
    #
    #if os.path.exists(intpb):
    #    myintpb = intpb
    #else:
    #    print(intpb+' does not exist')
    #    return False
    #

    # use function for reordering instead of commented code down here 

    print('')                    
    print('### Start feather for sdfactor', sdfactor)       
    print('')                    
             

    os.system('rm -rf lowres.* ')

    os.system('cp -r '+mysdimage+' lowres.regrid')

    lowres_unit = cta.imhead('lowres.regrid', mode='get', hdkey='Bunit')

    # Multiply the lowres image with the highres primary beam response

    print('Multiplying lowres by the highres pb...')
    cta.immath(imagename=['lowres.regrid', myintpb],
               expr='IM0*IM1',
               outfile='lowres.multiplied')

    cta.imhead('lowres.multiplied', mode='put', hdkey='Bunit', hdvalue=lowres_unit)

    # Feather together the low*pb and hi images

    print('Feathering...')
    os.system('rm -rf '+featherim+'.*')
    cta.feather(imagename=featherim+'.image',
                highres=myintimage,
                lowres='lowres.multiplied',
                sdfactor = sdfactor,
                lowpassfiltersd = True )
    
    
    # Testing SDINT based feather
    #
    #chanwt = np.ones( len(getFreqList('lowres.multiplied')))
    #
    #feather_int_sd(sdcube='lowres.multiplied', 
    #               intcube=myintimage, 
    #               jointcube=featherim+'.image',
    #               sdgain=sdfactor,
    #               dishdia=12.0,
    #               chanwt=chanwt)

    #os.system('rm -rf '+featherim+'.image.pbcor')
    cta.immath(imagename=[featherim+'.image', myintpb],
               expr='IM0/IM1',
               outfile=featherim+'.image.pbcor')
    
    highres_unit = cta.imhead(featherim+'.image', mode='get', hdkey='Bunit')
    cta.imhead(featherim+'.image.pbcor', mode='put', hdkey='Bunit', hdvalue=highres_unit)
    
    # print('Exporting final pbcor image to FITS ...')
    # os.system('rm -rf '+featherim+'.image.pbcor.fits')
    # cta.exportfits(featherim+'.image.pbcor', featherim+'.image.pbcor.fits')
	# 
    # os.system('cp -r '+myintpb+' '+featherim+'.pb')
    # os.system('rm -rf '+featherim+'.pb.fits')
    # cta.exportfits(myintpb, featherim+'.pb.fits')
    
    export_fits(featherim, clean_origin=myintimage.replace('.image', ''))

    os.system('rm -rf lowres.*')

    return True



######################################



def feather_int_sd(sdcube='', intcube='', jointcube='',
                   sdgain=1.0,dishdia=100.0, usedata='sdint',         
                   chanwt = ''): 
    #, pbcube='',applypb=False, pblimit=0.2):
    """
    Taken from the SDINT_helper module inside CASA 5.8, state: July, 2021), 
    modified by Lydia Moser-Fischer
    _____________________________________________________________________

    Run the feather task to combine the SD and INT Cubes. 
    
    There's a bug in feather for cubes. Hence, do each channel separately.
    FIX feather and then change this. CAS-5883 is the JIRA ticket that contains a fix for this issue.... 

    TODO : Add the effdishdia  usage to get freq-indep feathering.

    """
     
    ### Do the feathering.
    if usedata=='sdint':
        ## Feather runs in a loop on chans internally, but there are issues with open tablecache images
        ## Also, no way to set effective dish dia separately for each channel.
        #feather(imagename = jointcube, highres = intcube, lowres = sdcube, sdfactor = sdgain, effdishdiam=-1)

        freqlist = getFreqList(sdcube)
        
        os.system('rm -rf '+jointcube)
        os.system('cp -r ' + intcube + ' ' + jointcube)

        _ia = iatool()
        _ib = iatool() #image()
        
        from casatools import imager  as imtool

        _ia.open(jointcube)
        _ia.set(0.0) ## Initialize this to zero for all planes
       
        for i in range(len(freqlist)):  
            if chanwt[i] != 0.0 : ## process only the nonzero channels
                freqdishdia = dishdia ## * (freqlist[0] / freqlist[i]) # * 0.5
            
                os.system('rm -rf tmp_*')
                #imsubimage(imagename = sdcube, outfile = 'tmp_sdplane', chans = str(i));
                #imsubimage(imagename = intcube, outfile = 'tmp_intplane', chans = str(i));
                createplaneimage(imagename=sdcube, outfile='tmp_sdplane', chanid = str(i));
                createplaneimage(imagename=intcube, outfile='tmp_intplane', chanid = str(i));

                #feather(imagename = 'tmp_jointplane', highres = 'tmp_intplane', lowres = 'tmp_sdplane', sdfactor = sdgain, effdishdiam=freqdishdia)
                # feathering via toolkit
                try: 
                    cta.casalog.post("start Feathering.....")
                    imFea=imtool( )
                    imFea.setvp(dovp=True)
                    imFea.setsdoptions(scale=sdgain)
                    imFea.feather(image='tmp_jointplane',highres='tmp_intplane',lowres='tmp_sdplane', effdishdiam=freqdishdia)
                    imFea.done( )
                    del imFea
                except Exception as instance:
                    cta.casalog.post('*** Error *** %s' % instance, 'ERROR')
                    raise 

                _ib.open('tmp_jointplane')
                pixjoint = _ib.getchunk()
                _ib.close()
                _ia.putchunk(pixjoint, blc=[0,0,0,i])
        
        _ia.close()

    if usedata=='sd':
        ## Copy sdcube to joint.
        os.system('rm -rf '+jointcube)
        os.system('cp -r ' + sdcube + ' ' + jointcube)
    if usedata=='int':
        ## Copy intcube to joint
        os.system('rm -rf '+jointcube)
        os.system('cp -r ' + intcube + ' ' + jointcube)

    return True


def getFreqList(imname=''):
    
    """
    Taken from the SDINT_helper module inside CASA 5.8, state: July, 2021), 
    modified by Lydia Moser-Fischer
    _____________________________________________________________________
    
    """

    _ia = iatool()
    
    _ia.open(imname)
    csys =_ia.coordsys()
    shp = _ia.shape()
    _ia.close()
    
    if(csys.axiscoordinatetypes()[3] == 'Spectral'):
         restfreq = csys.referencevalue()['numeric'][3]#/1.0e+09; # convert more generally..
         freqincrement = csys.increment()['numeric'][3]# /1.0e+09;
         freqlist = [];
         for chan in range(0,shp[3]):
               freqlist.append(restfreq + chan * freqincrement);
    elif(csys.axiscoordinatetypes()[3] == 'Tabular'):
         freqlist = (csys.torecord()['tabular2']['worldvalues']) # /1.0e+09;
    else:
         cta.casalog.post('Unknown frequency axis. Exiting.','SEVERE');
         return False;
    
    csys.done()
    return freqlist
  


def createplaneimage(imagename, outfile, chanid):
    """
    Taken from the SDINT_helper module inside CASA 5.8, state: July, 2021), 
    modified by Lydia Moser-Fischer
    _____________________________________________________________________
    
    extract a channel plane image 
    """
    from casatools import regionmanager  as rgtool

    _tmpia=iatool() #image()
    _tmprg=rgtool()
    outia=None

    _tmpia.open(imagename)
    theregion = _tmprg.frombcs(csys=_tmpia.coordsys().torecord(), shape=_tmpia.shape(), chans=chanid) 
    try:
        outia=_tmpia.subimage(outfile=outfile, region=theregion)
    except Exception as instance:
        cta.casalog.post("*** Error \'%s\' in creating subimage" % (instance), 'WARN')

    _tmpia.close()
    _tmpia.done()
    _tmprg.done()
    if outia != None and outia.isopen():
        outia.done()
        
                  

######################################

def runtclean(vis, 
              imname, 
              startmodel='',
              spw='', 
              field='', 
              specmode='mfs', 
              imsize=[], 
              cell='', 
              phasecenter='',
              start=0, 
              width=1, 
              nchan=-1, 
              restfreq='',
              threshold='', 
              niter=0, 
              usemask='auto-multithresh' ,
              sidelobethreshold=2.0, 
              noisethreshold=4.25, 
              lownoisethreshold=1.5, 
              minbeamfrac=0.3, 
              growiterations=75, 
              negativethreshold=0.0,
              mask='', 
              pbmask=0.4, 
              interactive=True, 
              multiscale=False, 
              maxscale=0.,
              #restart=True,
              continueclean = False,
              loadmask=False,
              fniteronusermask=0.3
              ):

    """
    runtclean (A. Plunkett, NRAO, D. Petry, ESO)
    a wrapper around the CASA task "TCLEAN,"


    steps:
    - return mask setup
    - derive multiscale sizes for 'multiscale=True'
    - clean parameter definition as known from tclean (analoguously to 'runsdintimg')
    --- important fixed parameters you should be aware of: 
    restoring beam = common, gridder = 'mosaic',
    weighting='briggs', robust = 0.5
    - exportfits pcbor 


    vis - the MS containing the interferometric data
    imname - the root name of the output images
    startmodel - start model for cleaning
          default: '' i.e. no start model, example: 'TP.scaled.image'
    spw - the standard selection parameter spw of tclean
           default: '' i.e. all SPWs
    field - the standard selection parameter field of tclean
           default: '' i.e. all fields
    specmode - the standard tclean specmode parameter: supported are msf or cube
           default: msf 
    imsize - (optional) the standard tclean imsize parameter 
            should correspond to the imagesize for the most extended
            interferometer config.
           default: determine from the input MS with aU.pickCellSize
    cell - (optional) the standard tclean cell parameter
            should correspond to the cell size for the most extended
            interferometer config, i.e. smallest beam / 5.
           default: determine from the input MS with aU.pickCellSize
    phasecenter - the standard tclean phasecenter parameter
           e.g. 'J2000 12:00:00 -35.00.00.0000'
           default: '' - determine from the input MS with aU.pickCellSize
    start - the standard tclean start parameter
             default: 0
    width - the standard tclean width parameter
             default: 1
    nchan - the standard tclean nchan parameter
             default: -1
    restfreq - the restfrequency to write to the image for velocity calculations
             default: None, example: '115.271GHz'
    threshold - the threshold for cleaning
             default: None, example: '12mJy'
    niter - the standard tclean niter parameter
             default: 0, example: niter=1000000
    usemask - the standard tclean mask parameter.  If usemask='auto-multithresh', can specify:
             sidelobethreshold, noisethreshold, lownoisethreshold, minbeamfrac, growiterations - 
             if usemask='user', must specify mask='maskname.mask' 
             if usemask='pb', can specify pbmask=0.4, or some level.
             default: 'auto-multithresh'
    interactive - the standard tclean interactive option
             default: True
    multiscale - if False (default) use hogbom cleaning, otherwise multiscale
    maxscale - for multiscale cleaning, use scales up to this value (arcsec)
             Recommended value: 10 arcsec
             default: 0.
    restart - True (default): Re-use existing images. False: Increment imagename
    continueclean - True: same as 'restart', False(default): Delete old version
    loadmask - run sdintimaging with user-specified mask for fniteronusermask*niter iterations 
              and continue with auto-masking (usemask='auto-multithresh') for the remaining 
              niter*(1-fniteronusermask) iterations 
             default: False
    fniteronusermask - adjusting the amount of iterations spend on a usermask for loadmask=True
              allowed values: 0.0 (none in theory, in fact: 1 iteration) - 1.0 (all)
             default: 0.3 


    Example: runtclean('gmc_120L.alma.all_int-weighted.ms', 
                'gmc_120L', phasecenter='J2000 12:00:00 -35.00.00.0000', 
                spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec',
                threshold='12mJy',niter=100000,
                usemask='auto-multithresh')

    """


    myvis = file_check_vis(vis)


    #   if type(vis) is str:
    #       myvis = file_check(vis)
    #   
    #           
    #   if isinstance(vis, list):
    #       #acceptinput=True
    #       for i in range(0,len(vis)):
    #           file_check(vis[i])          # if one of the files does not exist, script will exit here
    #           #if os.path.exists(vis[i]):
    #           #    #myvis = vis 
    #           #    pass 
    #           #else:
    #           #    acceptinput=False 
    #           #    print(vis[i]+' does not exist')
    #       #if acceptinput==False:
    #       #    return False             
    #       #else:
    #       #    myvis = vis 
    #       myvis = vis    
            
    #   if loadmask==True and fniteronusermask>1 or fniteronusermask<0:
    #       print('fniteronusermask is out of range: ' +fniteronusermask+' Please choose a value between 0 and 1 (inclusively)')
    #       return False        
    #   else:
    #       pass
            
        
    #print('')

    print('Start tclean ...')

    #mymaskname = ''
    #   if usemask == 'auto-multithresh':
    #       #print('Run with {0} mask'.format(usemask))
    #       mymask = usemask
    #       if os.path.exists(mask):
    #          mymaskname = mask
    #          print('Run with {0} mask and {1} '.format(mymask,mymaskname))
    #       else: print('Run with {0} mask'.format(mymask))        
    #   
    #   elif usemask =='pb':
    #       print('Run with {0} mask on PB level {1}'.format(usemask,pbmask))
    #   elif usemask == 'user':
    #       if os.path.exists(mask):
    #          print('Run with {0} mask {1}'.format(usemask,mask))
    #   
    #       else:
    #          print('### WARNING:   mask '+mask+' does not exist, or not specified')
    #          #return False
    #   else:
    #       print('check the mask options')
    #       return False

    #   # specmode and deconvolver
    #   if multiscale:
    #       mydeconvolver = 'multiscale'
    #       myqa = qatool()
    #       mycell = myqa.convert(myqa.quantity(cell),'arcsec')['value']
    #       myscales = [0]
    #       for i in range(0, int(math.log(maxscale/mycell,3))):
    #           myscales.append(3**i*5)
    #   
    #       print("My scales (units of pixels): "+str(myscales))
    #   
    #   else:    
    #       myscales = [0]
    #       mydeconvolver = 'hogbom'

    if niter==0:
        cta.casalog.post('You set niter to 0 (zero, the default). Only a dirty image will be created.', 'WARN', origin='runtclean')


    #   if specmode == 'mfs':
    #       weightingscheme ='briggs'   # cont mode
    #   elif specmode == 'cube':
    #       weightingscheme ='briggs' #bwtaper'   # special briggs for cubes --- WAIT FOR IMPLEMENTATION IN SDINT 
    #   

    #   tclean_arg=dict(vis = myvis,
    #                   imagename = imname, #+'.TCLEAN',
    #                   startmodel = startmodel,
    #                   field = field,
    #                   phasecenter = phasecenter,
    #                   imsize = imsize,
    #                   cell = cell,
    #                   spw = spw,
    #                   specmode = specmode,
    #                   deconvolver = mydeconvolver,   
    #                   scales = myscales,             
    #                   #nterms = 1,                    # needed by sdint for mtmfs
    #                   start = start, 
    #                   width = width, 
    #                   nchan = nchan, 
    #                   restfreq = restfreq,
    #                   gridder = 'mosaic',
    #                   weighting = weightingscheme,
    #                   robust = 0.5,
    #                   restoringbeam = 'common',   # SD-cube has only one beam - INT-cube needs it, too, else feather etc. fail
    #                   niter = niter,
    #                   cyclefactor=2.0,
    #                   threshold = threshold,
    #                   interactive = interactive,
    #                   pbcor = True,
    #                   # Masking Parameters below this line 
    #                   # --> Should be updated depending on dataset
    #                   usemask=usemask,
    #                   sidelobethreshold=sidelobethreshold,
    #                   noisethreshold=noisethreshold,
    #                   lownoisethreshold=lownoisethreshold, 
    #                   minbeamfrac=minbeamfrac,
    #                   growiterations=growiterations,
    #                   negativethreshold=negativethreshold,
    #                   mask=mask,
    #                   pbmask=pbmask,    # used by all usemasks! perhaps needed for fastnoise-calc!
    #                   verbose=True)#, 
    #                   #restart=restart)  # should switch off bc default



    tclean_arg = check_prep_tclean_param( 
                myvis,       
                spw, 
                field, 
                specmode,                                 
                imsize, 
                cell, 
                phasecenter,         
                start, 
                width, 
                nchan, 
                restfreq,
                threshold, 
                niter,
                usemask,
                sidelobethreshold,
                noisethreshold,
                lownoisethreshold, 
                minbeamfrac,
                growiterations,
                negativethreshold,                
                mask, 
                pbmask,
                interactive,               
                multiscale, 
                maxscale,
                loadmask,
                fniteronusermask
                )

    #tclean_arg['vis']        = myvis
    tclean_arg['imagename']  = imname #+'.TCLEAN',
    tclean_arg['startmodel'] = startmodel


    #if os.path.exists(imname+'.TCLEAN.image'):
    #    casalog.post('Image '+imname+'.TCLEAN already exists.  Running with restart='+str(restart), 'WARN')        
    ##os.system('rm -rf '+imname+'.TCLEAN.*')

    if continueclean == False:
        os.system('rm -rf '+imname+'.*') #+'.TCLEAN.*')   
        # if to be switched off add command to delete "*.pbcor.fits"
    

    if loadmask==True:

        tclean_arg['usemask']='user'
        if fniteronusermask==0 or fniteronusermask==0.0:
            tclean_arg['niter']=1
        else:   
            tclean_arg['niter']=int(niter*fniteronusermask)
        # load mask into tclean with limited iterations
        print('')
        print('### Load mask into tclean with iterations = fniteronusermask*niter = ', fniteronusermask, ' * ', niter)
        report_mask(tclean_arg['usemask'],tclean_arg['mask'],tclean_arg['pbmask'],tclean_arg['niter'])
        tcleansresults = cta.tclean(**tclean_arg)
        
        tclean_arg['usemask']=usemask
        tclean_arg['mask']=''
        # if startmodel used, it would have been loaded in tclean step before 
        # -> clear startmodel parameter for next tclean call, else crash!
        tclean_arg['startmodel']=''        
        
        tclean_arg['niter']=niter-tclean_arg['niter']
        
        if tclean_arg['niter']<=0:    #avoid negative niter values and pointless executions 
            pass
        else:               
            # clean and get tclean-feedback 
            print('')
            print('### Continue tclean with iterations = (1-fniteronusermask)*niter = ', (1.0-fniteronusermask), ' * ', niter)
            report_mask(tclean_arg['usemask'],tclean_arg['mask'],tclean_arg['pbmask'],tclean_arg['niter'])
            tcleansresults = cta.tclean(**tclean_arg)
        
        #### store feedback in a file 
        ###pydict_to_file2(tcleansresults, imname)
        ###
        ###os.system('cp -r summaryplot_1.png '+imname+'.png')   

    else: 
        # clean and get tclean-feedback 
        report_mask(tclean_arg['usemask'],tclean_arg['mask'],tclean_arg['pbmask'],tclean_arg['niter'])
        tcleansresults = cta.tclean(**tclean_arg)
        
    # store feedback in a file 
    pydict_to_file2(tcleansresults, imname)
    
    os.system('cp -r summaryplot_1.png '+imname+'.png') 



    # print('Exporting final pbcor image to FITS ...')
    # #exportfits(imname+'.TCLEAN.image.pbcor', imname+'.TCLEAN.pbcor.fits')
    # os.system('rm -rf '+imname+'.image.pbcor.fits') #+'.TCLEAN.*')   
    # os.system('rm -rf '+imname+'.pb.fits') #+'.TCLEAN.*')   
    # cta.exportfits(imname+'.image.pbcor', imname+'.image.pbcor.fits')
    # cta.exportfits(imname+'.pb', imname+'.pb.fits')

    export_fits(imname)


    return True





    

######################################

def visHistory(vis, origin='applycal', search='version',includeVis=False):
    """
    Taken from analysisUtils.py (state: Jan 19th, 2021), modified by 
    Lydia Moser-Fischer to get the CASA version used for the calibration of the ms.
    Use search='ms.hifa' to detect pipeline calibration (need to verify for cycle 2 data)!
    
    -------------------------
    
    Print the history information from a measurement set.
    origin: if specified, only print messages from this (task) origin
    search: if specified, only print messages containing this string
    includeVis: if True, then include the basename of the vis parameter is the search string
    Example: to see the flux scale that was set:
      au.visHistory('uid___A002_Xd1ff61_X5cd_target.ms','setjy','field,fluxde,spw',includeVis=True)
    -Todd Hunter
    
    """

    file_check_vis_str_only(vis)
    #if (not os.path.exists(vis)):
    #    print("Dataset not found")
    #    return
    mytb = tbtool()                                # modified
    mytb.open(vis+'/HISTORY')
    messages = mytb.getcol('MESSAGE')
    origins = mytb.getcol('ORIGIN')
    mytb.close()
    msg = []
    myorigins = []
    for i in range(len(messages)):
        newmessages = messages[i].split('\n')
        msg += newmessages
        myorigins += [origins[i]]*len(newmessages)
    # msg is now longer than origins
    origins = myorigins
    if type(search) == str:
        searches = search.split(',')
    else:
        searches = search
    if includeVis:
        searches.append(os.path.basename(vis))
        searches.append(os.path.basename(vis).replace('_target',''))
    for i in range(len(msg)):
        if (search == '' and origin == ''):
            pass
            #print(msg[i])
        elif (search == ''): # origin is set
            if (origins[i]==origin):
                pass
                #print(msg[i])
        else: # search is set
            for search in searches:
                if msg[i].find(search)>=0:
                    if origin == '' or origin == origins[i]:
                        #print(msg[i])
                        return msg[i].split(' ')     # added
                        break
    #if search != '':
    #    print("Searched %d messages" % (len(msg)))
    
    return msg    
    # version: 4.3.0 branches rev. 31966 Tue 2014/12/23 13:10:39 UTC
    
        
        
        
def check_CASAcal(vis):
    """
    wrapper for visHistory to check the CASA version used for calibration 
    and the use of the calibration pipeline in CASA 4.2.2, specifically.
    Following the instructions on 
    https://casaguides.nrao.edu/index.php/DataWeightsAndCombination
    this funtion tells the user when to double check/correct the combination 
    weights, i.e. weight != 1.0 anymore, for concat.
    
    """
    
    file_check_vis_str_only(vis)
    
    msgVers = visHistory(vis, origin='applycal', search='version',includeVis=False)
    #print(msgVers)
    if msgVers==[''] or msgVers[0]=='':
        print(' ')
        print('---WARNING ---')
        print(vis) 
        print('seems to be a simulated data set.')
        print('See how to set the weights correctly to consider the difference in antenna dish size at')
        print('https://casaguides.nrao.edu/index.php/DataWeightsAndCombination')
        #print('---WARNING ---')
        print(' ')
    else:    
        #CASAcalVers='3.2.2' #msgVers[1] # for testing purpose
        CASAcalVers = msgVers[1]
        #print(CASAcalVers)
        CalV=CASAcalVers.split('.')
        if int(CalV[0])<4 or (int(CalV[0])==4 and int(CalV[1])<3 and int(CalV[2])<2):
            print(' ')
            print('---WARNING ---')
            print('The CASA version used for the calibration of your data set')
            print(vis) 
            print('is', CASAcalVers,' and therefore older than 4.3.0.')
            print('The weights might be wrong, please correct them following the instructions at')
            print('https://casaguides.nrao.edu/index.php/DataWeightsAndCombination')
            #print('---WARNING ---')
            print(' ')
        elif int(CalV[0])==4 and int(CalV[1])<3 and int(CalV[2])==2:
            msgpipe = visHistory(vis, origin='applycal', search='ms.hifa',includeVis=False)
            # "['/lustre/opsw/work/pipeproc/autopipeline/tmp/WORK7084/analysis/2018.1.01044.S/science_goal.uid___A001_X133d_X290f/group.uid___A001_X133d_X2910/member.uid___A001_X133d_X2911/calibrated/working/uid___A002_Xd60a42_X8600.ms.h_tsyscal.s6_1.tsyscal.tbl',",
            # "'/lustre/opsw/work/pipeproc/autopipeline/tmp/WORK7084/analysis/2018.1.01044.S/science_goal.uid___A001_X133d_X290f/group.uid___A001_X133d_X2910/member.uid___A001_X133d_X2911/calibrated/working/uid___A002_Xd60a42_X8600.ms.hifa_antpos.s8_1.ants.tbl',",
            # "'/lustre/opsw/work/pipeproc/autopipeline/tmp/WORK7084/analysis/2018.1.01044.S/science_goal.uid___A001_X133d_X290f/group.uid___A001_X133d_X2910/member.uid___A001_X133d_X2911/calibrated/working/uid___A002_Xd60a42_X8600.ms.hifa_wvrgcalflag.s9_4.sm2_016s.wvrcal.tbl',",
            # "'/lustre/opsw/work/pipeproc/autopipeline/tmp/WORK7084/analysis/2018.1.01044.S/science_goal.uid___A001_X133d_X290f/group.uid___A001_X133d_X2910/member.uid___A001_X133d_X2911/calibrated/working/uid___A002_Xd60a42_X8600.ms.hifa_bandpassflag.s12_7.spw5_7_17_19.channel.solintinf.bcal.final.tbl',",
            # "'/lustre/opsw/work/pipeproc/autopipeline/tmp/WORK7084/analysis/2018.1.01044.S/science_goal.uid___A001_X133d_X290f/group.uid___A001_X133d_X2910/member.uid___A001_X133d_X2911/calibrated/working/uid___A002_Xd60a42_X8600.ms.hifa_spwphaseup.s13_3.spw5_7_17_19.solintinf.gpcal.tbl',",
            # "'/lustre/opsw/work/pipeproc/autopipeline/tmp/WORK7084/analysis/2018.1.01044.S/science_goal.uid___A001_X133d_X290f/group.uid___A001_X133d_X2910/member.uid___A001_X133d_X2911/calibrated/working/uid___A002_Xd60a42_X8600.ms.hifa_timegaincal.s16_3.spw5_7_17_19.solintinf.gpcal.tbl',",
            # "'/lustre/opsw/work/pipeproc/autopipeline/tmp/WORK7084/analysis/2018.1.01044.S/science_goal.uid___A001_X133d_X290f/group.uid___A001_X133d_X2910/member.uid___A001_X133d_X2911/calibrated/working/uid___A002_Xd60a42_X8600.ms.hifa_timegaincal.s16_6.spw5_7_17_19.solintinf.gacal.tbl']"]
            #print(msgpipe)
            if msgpipe[-1].find('ms.hifa')<=0:
                print(' ')
                print('---WARNING ---')            
                print('Your data set', vis)
                print('is was manually calibrated in CASA', CASAcalVers)
                print('The weights might be wrong, please correct them following the instructions at')
                print('https://casaguides.nrao.edu/index.php/DataWeightsAndCombination')
                #print('---WARNING ---')
                print(' ')        
            
            #print('pipe', msgpipe)



######################################


def get_SD_cube_params(sdcube =''):
    """
    Taken from the SDINT_helper module inside CASA 5.7 (originally called 
    'setup_cube_params(self,sdcube='')', state: Dec, 2020), 
    modified by Lydia Moser-Fischer
    _____________________________________________________________________

    Read coordinate system from the SD cube
    Decide parameters to input into sdintimaging for the INT cube to match. 

    This is a helper method, not currently used in the sdintimaging task.
    We will add this later (after 6.1), and also remove some parameters from the task level.
    """

    file_check(sdcube)

    _ia = iatool()
    _qa = qatool()

    

    _ia.open(sdcube)
    csys = _ia.coordsys()
    shp = _ia.shape()
    ctypes = csys.axiscoordinatetypes()
    print("Shape of SD cube : "+str(shp))
    print("Coordinate ordering : "+str(ctypes))
    if len(ctypes) !=4 or ctypes[3] != 'Spectral':
        print("The SD cube needs to have 4 axes, in the RA/DEC/Stokes/Spectral order")
        _ia.close()
        return False
    nchan = shp[3]
    start = str( csys.referencevalue()['numeric'][3] ) + csys.units()[3]
    width = str( csys.increment()['numeric'][3]) + csys.units()[3] 
    ## Number of channels
    print("nchan = "+str(nchan))
    ## Start Frequency
    print("start = " + start  )
    ## Width
    print("width = " + width  ) 
    ## Test for restoringbeams
    rbeams = _ia.restoringbeam()
    #if not rbeams.has_key('nChannels') or rbeams['nChannels']!= shp[3]:
    if not 'nChannels' in rbeams or rbeams['nChannels']!= shp[3]:
        print("The SD Cube needs to have per-plane restoringbeams")
        _ia.close()
        #return False                                # switched off by DC-team
    else:
        print("Found " + str(rbeams['nChannels']) + " per-plane restoring beams")
    print("\n(For specmode='mfs' in sdintimaging, please remember to set 'reffreq' to a value within the freq range of the cube)\n")
    _ia.close()
    return {'nchan':nchan, 'start':start, 'width':width}






######################################

def channel_cutout(old_image, new_image, startchan = None,
    endchan = None):

    """
    channel_cutout (L. Moser-Fischer)
    a tool to cut out a range of channels from a cube. 
    In contrast to pure IMMATH, this procedure updates the reference frequency of the new cube.
    IMMATH sets perplane beam eventhough the input image has a common beam.
    This procedure fixes the per plane beams in the new cube to a common beam 
    again.
    
    steps:
    - check if channels are set
    - cut out channel range with immath
    - update reference frequency in new cube
    - merge perplanebeams to a common beam 
    
    
    old_image - the image cube whose channel should be extracted
             default: None, example: 'SD.image'
    new_image - the outputname for the extracted channels
             default: None, example: 'SD_ch3-15.image'
    startchan - first channel to be included (format: int)
             default: None, example: 3
    endchan - last channel to be included (format: int)     
             default: None, example: 15

    Example: channel_cutout('SD.image', 'SD_ch3-15.image', startchan = 3, endchan = 15)
    
    
    """
    
    file_check(old_image)

    #print('startchan', startchan, 'endchan', endchan)
    if startchan==None or endchan==None:
        print('No channel cutout requested...')
    elif startchan!=None and endchan!=None: 
        print('Reduce channel range to '+str(startchan)+'-'+str(endchan))   
        os.system('rm -rf '+new_image)
        
        cta.immath(imagename=old_image,
                   expr='IM0', chans=str(startchan)+'~'+str(endchan),
                   outfile=new_image) 
            
        width   = cta.imhead(imagename = old_image, 
                             mode='get', hdkey='cdelt4')['value']
        ref_old = cta.imhead(imagename = old_image, 
                             mode='get', hdkey='crval4')['value'] 
        ref_new = ref_old + startchan*width  
        
        cta.imhead(imagename = new_image, 
                   mode='put', hdkey='crval4', hdvalue=str(ref_new))
        
        #if perplanebeams, then smooth
        check_beam=cta.imhead(new_image, mode='summary')
        if 'perplanebeams' in check_beam.keys():
            cta.imsmooth(imagename = new_image,
                         kernel    = 'commonbeam',                                                     
                         outfile   = new_image+'_1',            
                         overwrite = True)       
                        
            os.system('rm -rf '+new_image)
            os.system('cp -r '+new_image+'_1 ' +new_image)
        else:
            pass        






######################################

def regrid_SD(old_image, new_image, template_image):

    """
    regrid_SD (L. Moser-Fischer)
    (maybe rename to 'regrid_image' - need to check if 'SD only' is mandatory)
    IMREGRID alone does not fix any perplanebeam issues
    - need to smooth to common beam.
    
    steps:
    - regrid image
    - merge perplanebeams to a common beam 

    
    old_image - the image to be be regridded
             default: None, example: 'SD.image'
    new_image - the outputname of the regridded image
             default: None, example: 'SD.reg'
    template_image - the template image to regrid the input image to
             default: None, example: 'INT.image'             

    Example: regrid_SD('SD.image', 'SD.reg', 'INT.image' )
    """

    file_check(old_image)

    file_check(template_image)

    rstfrq = cta.imhead(template_image, mode='get', hdkey='restfreq')
    cta.imhead(old_image, hdkey='restfreq', mode='put', hdvalue=str(rstfrq['value'])+rstfrq['unit'])

    cta.imregrid(imagename=old_image,
                 template=template_image,
                 axes=[0,1,2,3], #decimate=10,
                 output=new_image)  


    #if perplanebeams, then smooth
    check_beam=cta.imhead(new_image, mode='summary')
    if 'perplanebeams' in check_beam.keys():
        cta.imsmooth(imagename = new_image,
                     kernel    = 'commonbeam',                                                     
                     outfile   = new_image+'_1',            
                     overwrite = True) 
        print('Got rid of perplanebeams...')                  
                    
        os.system('rm -rf '+new_image)
        os.system('cp -r '+new_image+'_1 ' +new_image)
    else:
        pass       
    
            
            
            
            
            
######################################

def reorder_axes(to_reorder, reordered_image):

    """
    reorder_axes (L. Moser-Fischer)
    a tool to reorder the axes according to a fixed order defined here

    steps:
    - simple imtrans

    to_reorder - the image whose axes should be reordered
             default: None, example: 'SD.image'
    reordered - the outputname whose axes have been reordered
             default: None, example: 'lowres.ro'

    Example: reorder_axes('SD.image', 'lowres.ro')
    """

    file_check(to_reorder)

    os.system('rm -rf '+reordered_image)
    cta.imtrans(imagename=to_reorder,
                outfile=reordered_image,
                order = ['rig', 'declin', 'stok', 'frequ'])

    #return True 
    return reordered_image





######################################

def reorder_axes2(template, to_reorder, reordered):

    """
    reorder_axes2 (M. Hoffmann, D. Kunneriath, N. Pingel, L. Moser-Fischer)
    a tool to reorder the axes according to a reference/template image
    Replaced by clearer reorder_axes function 

    steps:
    - read axes information of template and image to reorder
    - compare axis units and list 'to_reorder' axes according to template's order of units
    - apply the new axis order list to the image to be reordered if the new 
      order deviates from the standard order 



    template - the reference image
             default: None, example: 'INT.image'
    to_reorder - the image whose axes should be reordered
             default: None, example: 'SD.image'
    reordered - the outputname whose axes have been reordered
             default: None, example: 'lowres.ro'

    Example: reorder_axes('INT.image', 'SD.image', 'lowres.ro')
    """

    file_check(template)

    file_check(to_reorder)

    print('##### Check axis order ########')

    myfiles=[template,to_reorder]
    mykeys=['cdelt1','cdelt2','cdelt3','cdelt4']

    im_axes={}
    print('Making dictionary of axes information for template and to-reorder images')
    for f in myfiles:
             print(f)
             print('------------')
             axes = {}
             i=0
             for key in mykeys:
                     q = cta.imhead(f,mode='get',hdkey=key)
                     axes[i]=q
                     i=i+1
                     print(str(key)+' : '+str(q))
             im_axes[f]=axes
             print(' ')

    # Check if axes order is the same, if not run imtrans to fix, 
    # could be improved
    order=[]           

    for i in range(4):
             hi_ax = im_axes[template][i]['unit']
             lo_ax = im_axes[to_reorder][i]['unit']
             if hi_ax == lo_ax:
                     order.append(str(i))
             else:
                     lo_m1 = im_axes[to_reorder][i-1]['unit']
                     if hi_ax == lo_m1:
                             order.append(str(i-1))
                     else:
                             lo_p1 = im_axes[to_reorder][i+1]['unit']
                             if hi_ax == lo_p1:
                                     order.append(str(i+1))
    order = ''.join(order)
    print('order is '+order)

    if order=='0123':
             print('No reordering necessary')
             outputname = to_reorder
    else:
            reordered_image=reordered
            os.system('rm -rf '+reordered_image)
            cta.imtrans(imagename=to_reorder,outfile=reordered_image,order=order)
            print('Had to reorder!')
            outputname = reordered_image
    
    ### just testing what happens:        
    #reordered_image=reordered
    #imtrans(imagename=to_reorder,outfile=reordered_image,order=order)
    #print('Had to reorder!')
    #outputname = reordered_image            
            
    print(outputname)
    return outputname





######################################

def make_SD_mask(#vis, 
                 SDimage, #imname, 
                 sdmasklev, SD_mask_root 
                    #phasecenter='', spw='', field='', imsize=[], cell='',
                    #specmode='mfs', 
                    #start = 0, width = 1, nchan = -1, restfreq = ''
                    ):

    """
    make_SD_mask (A. Plunkett, L. Moser-Fischer)
    a tool to generate a mask from an SD image
     ##### and the first auto-masking step in tclean of an interferometric image

    steps:
    - create mask from SD image at a user given fraction of the peak flux
    #####- call 'runtclean' with relevant inputs to create the wanted grid/raster 
    #####   and niter=1 to load the SD mask into a clean mask
    #####- rerun 'runtclean' with same parameters except from usemask='auto-multithresh', mask=''
    #####   to add the auto-detected compact emission regions (smoothed out in SD image) 
    #####   to the existing clean mask
    #####- rename clean mask to wanted output name (root)



    #####vis - the MS containing the interferometric data
    sdimage - the Single Dish image
             Note that in case you are creating a cube, this SD image must be a cube
             with the same spectral grid as the one you are trying to create from vis.
    #####imname - the root name of the output images
    sdmasklev - if usemask='user', then use SD image at this level to draw a mask.
             typically: 0.3
    SDint_mask_root - the root name of the output mask, extention '.mask' will 
             be added automatically             
    #####phasecenter - the standard tclean phasecenter parameter
           e.g. 'J2000 12:00:00 -35.00.00.0000'
           default: '' - determine from the input MS with aU.pickCellSize   
    #####spw - the standard selection parameter spw of tclean
           default: '' i.e. all SPWs
    #####field - the standard selection parameter field of tclean
           default: '' i.e. all fields
    #####imsize - (optional) the standard tclean imsize parameter 
            should correspond to the imagesize for the most extended
            interferometer config.
           default: determine from the input MS with aU.pickCellSize
    #####cell - (optional) the standard tclean cell parameter
            should correspond to the cell size for the most extended
            interferometer config, i.e. smallest beam / 5.
           default: determine from the input MS with aU.pickCellSize                    
    #####specmode - the standard tclean specmode parameter: supported are msf or cube
           default: 'msf'
    #####start - the standard tclean start parameter
             default: 0
    #####width - the standard tclean width parameter
             default: 1
    #####nchan - the standard tclean nchan parameter
             default: -1
    #####restfreq - the restfrequency to write to the image for velocity calculations
             default: '', example: '115.271GHz'

       
    ##### Example: make_SDint_mask('gmc_120L.alma.all_int-weighted.ms',
                'gmc_120L.sd.image', 'gmc_120L.get_mask', 0.3, 'INT-SD', 
                phasecenter='J2000 12:00:00 -35.00.00.0000', 
                spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec', 
                specmode='cube', start= '1550km/s', width= '5km/s', 
                nchan= 10, restfreq = '115.271202GHz')                    
                    
    """

    #   #file_check(vis)
    #   file_check_vis(vis)


    file_check(SDimage)

    #   file_check(imname)



    cta.casalog.post("Generating a mask based on SD image", 'INFO', 
                     origin='make_SD_mask')
    #get max in SD image
    maxSD = cta.imstat(SDimage)['max'][0]
    #sdmasklev=sdmasklev
    sdmaskval = sdmasklev*maxSD
    
    #SDoutname1 = SDint_mask_root + '_pre1.mask'
    #SDoutname2 = SDint_mask_root + '_pre2.mask'
    finalSDoutname = SD_mask_root + '.mask'
    
    #os.system('rm -rf '+SD_mask_root + '*mask')     
    os.system('rm -rf '+finalSDoutname)     
     
    #cta.immath(imagename=[SDimage],expr='iif(IM0>'+str(round(sdmaskval,6))+',1,0)',
    #           outfile=SDoutname1)

    cta.immath(imagename=[SDimage],expr='iif(IM0>'+str(round(sdmaskval,6))+',1,0)',
               outfile=finalSDoutname)               
                  

    #print('')
    #print('### Creating a mask based on SD mask and auto-mask')
    #print('### Step 1 of 2: load the SD mask into interferometric tclean image data' )
    #print('### Please check the result!')
    #os.system('rm -rf '+imname+'*')        
    #
    #runtclean(vis,imname, 
    #        phasecenter=phasecenter, 
    #        spw=spw, field=field, imsize=imsize, cell=cell, specmode=specmode,
    #        start = start, width = width, nchan = nchan, restfreq = restfreq,
    #        niter=1,usemask='user',mask=SDoutname1,restart=True,interactive=False, continueclean=True)
    #print('### Step 2 of 2: add first auto-masking guess of bright emission regions (interferometric!) to the SD mask')
    #print('### Please check the result!')        
    #os.system('cp -r '+imname+'.mask '+SDoutname2)
    #os.system('rm -rf '+imname+'.image.pbcor.fits')        
    #runtclean(vis,imname,
    #        phasecenter=phasecenter, 
    #        spw=spw, field=field, imsize=imsize, cell=cell, specmode=specmode,
    #        start = start, width = width, nchan = nchan, restfreq = restfreq,
    #        niter=1,usemask='auto-multithresh',mask='',restart=True,interactive=False, continueclean=True)
    #os.system('cp -r '+imname+'.mask '+finalSDoutname)
    
    #    #print('### Creating a mask based on SD mask and auto-mask')
    #    #print('### Step 2 of 2: first auto-masking guess of bright emission regions (interferometric!) to the SD mask')
    #    #print('### Please check the result!')
    #    #runtclean(myvis,imname+'_setmask', phasecenter=phasecenter, 
    #    #        spw=spw, field=field, imsize=imsize, cell=cell,
    #    #        niter=1,usemask='auto-multithresh',mask='',restart=True,interactive=False, continueclean=True)
    #    #os.system('cp -rf '+imname+'_setmask.mask int-AM0.mask')
    #    #os.system('rm -rf '+imname+'_setmask.pbcor.fits')                 
    #    #print('### Step 1 of 2: load the SD mask into interferometric tclean image data' )
    #    #print('### Please check the result!')                  
    #    #runtclean(myvis,imname+'_setmask',
    #    #        phasecenter=phasecenter, 
    #    #        spw=spw, field=field, imsize=imsize, cell=cell,
    #    #        niter=1,usemask='user',mask='SD.mask',restart=True,interactive=False, continueclean=True)
    #    #os.system('cp -rf '+imname+'_setmask.mask SDint.mask')
    
    #print('### Done! Created an SDint mask from SD and auto-mask')                
    print('### Done! Created an SD mask from SD image')                

    mask=finalSDoutname  
    #mask='SD.mask'  

    return mask 





######################################

def derive_threshold(#vis, 
                    imname, threshmask,
                    #phasecenter='', spw='', field='', imsize=[], cell='',
                    specmode='mfs', 
                    #start = 0, width = 1, nchan = -1, restfreq = '', 
                    #overwrite=False, 
                    smoothing = 5, 
                    threshregion = '',
                    RMSfactor = 0.5, 
                    cube_rms = 3.,   
                    cont_chans ='2~4',
                    makemask=True):

    """
    derive_threshold (L. Moser-Fischer)
    a tool to derive a reasonable clean threshold and mask for an 
    interferometric image
    
    steps: 
    - create dirty image if needed, 
    - get an RMS (continuum: RMS of full image (!including emission), 
    cube: RMS of moment 6 (RMS) map - right choice of cont_chans makes this 
    the true RMS of the cube!), 
    - create threshold by applying a user defined factor to the RMS (different 
    for continuum and cube due to different RMS definition),
    - make mask from threshold
    - smooth mask by Gaussian with "smoothing"*beam_major and "smoothing"*beam_minor axes
    - turn smoothed mask into a 1,0-mask
    
    

    vis - the MS containing the interferometric data
    imname - the root name of the output images
    threshmask - the root name of the threshold mask, extention '.mask' will 
             be added automatically             
    phasecenter - the standard tclean phasecenter parameter
           e.g. 'J2000 12:00:00 -35.00.00.0000'
           default: '' - determine from the input MS with aU.pickCellSize   
    spw - the standard selection parameter spw of tclean
           default: '' i.e. all SPWs
    field - the standard selection parameter field of tclean
           default: '' i.e. all fields
    imsize - (optional) the standard tclean imsize parameter 
            should correspond to the imagesize for the most extended
            interferometer config.
           default: determine from the input MS with aU.pickCellSize
    cell - (optional) the standard tclean cell parameter
            should correspond to the cell size for the most extended
            interferometer config, i.e. smallest beam / 5.
           default: determine from the input MS with aU.pickCellSize                    
    specmode - the standard tclean specmode parameter: supported are msf or cube
           default: msf 
    start - the standard tclean start parameter
             default: 0
    width - the standard tclean width parameter
             default: 1
    nchan - the standard tclean nchan parameter
             default: -1
    restfreq - the restfrequency to write to the image for velocity calculations
             default: None, example: '115.271GHz'
    overwrite - True: generate new template INT image: False: just derive 
                threshold values and image mask from existing template INT image
    smoothing factor - smooth thresholdmask to multiples beamsizes (smoothing*beamaxis) 
            to avoid unphysical mask shapes (too few pixels, straight lines, sharp corners)
    RMSfactor - to apply to a continuum RMS of the full image to define a threshold at which 
            as much emission as possible/reasonable is contained; user needs to play with it
            typically: 0.5
    cube_rms - factor to apply to a a cube RMS to define a threshold. channels
            If cont_chans is set to line-free channels, this factor can be used
            to set the threshold as 3sigma, 10sigma, etc level) 
    cont_chans - define the line-free channels here to get a pure noise RMS of a cube 
    
                                    
    Example: derive_threshold('gmc_120L.alma.all_int-weighted.ms',
                'gmc_120L.get_mask', 'gmc_120L.threshmask',
                phasecenter='J2000 12:00:00 -35.00.00.0000', 
                spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec', 
                specmode='cube', start= '1550km/s', width= '5km/s', 
                nchan= 55, restfreq = '115.271202GHz', 
                overwrite=False, smoothing = 5, 
                RMSfactor = 0.5, cube_rms = 3.,   
                cont_chans ='2~13;44~54')                
                  
                    
    """


    #   file_check(vis)
    #file_check_vis(vis)


    cta.casalog.post("derive_threshold", 'INFO', 
                     origin='derive_threshold')

    imnameth = imname #+'_template'



    #if overwrite == True:      # False if used by a combi method to get threshold
    #
    #    os.system('rm -rf '+imnameth+'*')        
    #    
    #    runtclean(vis,imnameth, 
    #            phasecenter=phasecenter, 
    #            spw=spw, field=field, imsize=imsize, cell=cell, specmode=specmode,
    #            start = start, width = width, nchan = nchan, restfreq = restfreq,
    #            niter=0, interactive=False)
    #    #print('### Please check the result!') 
    #else: 

    print('Use existing template ',  imnameth+'.image', 'to derive threshold and mask')       

    #### get threshold 

    #if not os.path.exists(threshmask + '.mask'): #and overwrite == False:
    #    print('please, execute this function with overwrite = True!')
    #    thresh = 0.0
    #else:  
     
    #### continuum
    if specmode == 'mfs':
        full_RMS = cta.imstat(imnameth+'.image', box=threshregion)['rms'][0]
        #print('full_RMS', full_RMS)
        #peak_val = imstat(imnameth+'.image')['max'][0]
        thresh = full_RMS*RMSfactor
        print('The "RMS" of the entire image (incl emission) is ', round(full_RMS,6), 'Jy')
        print('You set the mask threshold to ', round(RMSfactor,6), ' times the RMS, i.e. ', round(thresh,6), 'Jy')
    
    #### cube
    elif specmode == 'cube':
        os.system('rm -rf '+imnameth+'.mom6')
        cta.immoments(imagename=imnameth+'.image', moments=[6], 
                      outfile=imnameth+'.mom6', chans=cont_chans)
        cube_RMS = cta.imstat(imnameth+'.mom6', box=threshregion)['rms'][0]
    
        thresh = cube_RMS*cube_rms   # 3 sigma level
 
        print('The RMS of the cube (check cont_chans for emission-free channels) is ', round(cube_RMS,6), 'Jy')
        print('You set the mask threshold to ', round(cube_rms,6), ' times the RMS, i.e. ', round(thresh,6), 'Jy')
     
    
        #immmoments(imagename=imname+'_template.image', mom=[8], 
        #           outfile=imname+'_template.mom8', chans='' )
        #peak_val = imstat(imname+'_template.mom8')['max'][0]
    
    #print(full_RMS)
    #print(peak_val)
    

    if makemask == True:
        print('Creating a mask from threshold of', round(thresh,6), 'Jy with a smoothing of', smoothing)

        threshmask1 = threshmask+'_1.mask'
        os.system('rm -rf '+threshmask+'*.mask')     
        
        cta.immath(imagename=[imnameth+'.image'],
                   expr='iif(IM0>'+str(round(thresh,6))+',1,0)',
                   outfile=threshmask1)
           
        convfactor = smoothing
        
        threshmaskconv = threshmask+'_conv.mask'
        os.system('rm -rf '+threshmaskconv+'*')
        
        # special treatment for cubes not needed when restoringbeam='common',
        # which is required for feather etc. to work
        #
        # #### continuum
        # if specmode == 'mfs':
        #     BeamMaj = imhead(imnameth+'.image', mode='get', hdkey='bmaj')['value']
        #     BeamMin = imhead(imnameth+'.image', mode='get', hdkey='bmin')['value']
        #     BeamPA  = imhead(imnameth+'.image', mode='get', hdkey='bpa' )['value']
        # 
        # #### cube
        # elif specmode == 'cube':
        #     midchan = int(imhead(imnameth+'.image', mode='summary')['perplanebeams']['nChannels']/2)
        #     BeamMaj = imhead(imnameth+'.image', mode='summary')['perplanebeams']['beams']['*'+str(midchan)]['*0']['major']['value']
        #     BeamMin = imhead(imnameth+'.image', mode='summary')['perplanebeams']['beams']['*'+str(midchan)]['*0']['minor']['value']
        #     BeamPA  = imhead(imnameth+'.image', mode='summary')['perplanebeams']['beams']['*'+str(midchan)]['*0']['positionangle']['value']
        
        BeamMaj = cta.imhead(imnameth+'.image', mode='get', hdkey='bmaj')['value']
        BeamMin = cta.imhead(imnameth+'.image', mode='get', hdkey='bmin')['value']
        BeamPA  = cta.imhead(imnameth+'.image', mode='get', hdkey='bpa' )['value']
        
        
        
        cta.imsmooth(imagename = threshmask1,
                     kernel    = 'gauss',               
                     targetres = False,                                                             
                     major     = str(convfactor*round(BeamMaj, 6))+'arcsec',                                                     
                     minor     = str(convfactor*round(BeamMin, 6))+'arcsec',    
                     pa        = str(round(BeamPA, 3))+'deg',                                       
                     outfile   = threshmaskconv,            
                     overwrite = True)                 
        
        cta.immath(imagename=[threshmaskconv],
                   expr='iif(IM0>'+str(0.2)+',1,0)',  # cut-off value is arbitrary!
                   outfile=threshmask+'.mask')
        
    else:
        pass      
    
    return thresh
 


######################################

def make_masks_and_thresh(imnameth, threshmask,
                                     #overwrite=True,
                    sdimage, sdmasklev, SD_mask_root,
                    combined_mask,
                    specmode = 'mfs',
                    smoothing = 5, 
                    threshregion = '',
                    RMSfactor = 0.5, 
                    cube_rms = 3.,   
                    cont_chans ='2~4',
                    makemask=True
                    ):
    """
    make_masks_and_thresh (L. Moser-Fischer)
    wrapper for making all masks for DC_run

    steps:
    - helper functions for header information (beam, etc.)

   


    highres  - high resolution (interferometer) image


    Example: ssc(highres='INT.image', lowres='SD.image', pb='INT.pb',
                 combined='INT_SD_1.7.image', sdfactor=1.7)

    """


    # derive a simple threshold and make a mask from it 
    print(' ')         
    print('--- Derive a simple threshold from a dirty image and make a mask from it --- ')                                  

    thresh = derive_threshold(#vis, 
                                 imnameth, 
                                 threshmask,
                                 #overwrite=True,
                                 specmode = specmode,
                                 smoothing = smoothing,
                                 threshregion = threshregion,
                                 RMSfactor = RMSfactor,
                                 cube_rms   = cube_rms,    
                                 cont_chans = cont_chans,
                                 makemask=True) #, 
                                 #**mask_tclean_param) 
                      
    print('--- Threshold and mask done! --- ')         


    # make SD+AM mask (requires regridding to be run; currently)
    print(' ')         
    #   print('--- Make single dish (SD) + automasking (AM) mask --- ')                                          
    #   SDint_mask = dc.make_SDint_mask(vis, sdimage, imnameth, 
    #                                   sdmasklev, 
    #                                   SDint_mask_root,
    #                                   **mask_tclean_param) 
    #   print('--- SD+AM mask done! --- ') 
    #   
    print(' ')         
    print('--- Make single dish (SD) mask --- ')                                          
    SD_mask = make_SD_mask(sdimage, sdmasklev, SD_mask_root) 
    print('--- SD mask done! --- ')                 



    # merge masks 
    print(' ')        
    print('--- Combine SD and threshold mask --- ')                                          

    os.system('rm -rf '+combined_mask)
    cta.immath(imagename=[SD_mask_root+'.mask', threshmask+'.mask'],
               expr='iif((IM0+IM1)>'+str(0)+',1,0)',
               outfile=combined_mask)    
               
               # ! terminal complains about bunit issues !
    print('--- Combined mask done! --- ')    
    
    
    return thresh #, SDmask










######################################

def ssc(highres=None, lowres=None, pb=None, combined=None, 
        sdfactor=1.0):
    """
    ssc (P. Teuben, N. Pingel, L. Moser-Fischer)
    an implementation of Faridani's short spacing combination method
    https://bitbucket.org/snippets/faridani/pRX6r
    https://onlinelibrary.wiley.com/doi/epdf/10.1002/asna.201713381

    steps:
    - helper functions for header information (beam, etc.)
    - outsourced?: reorder axes of SD image 
    - outsourced?: regrid reordered SD image 
    - regrid reordered SD image * INT primary beam = PB attenuated SD image 
    - fix brightness unit of PB attenuated SD image
    - smooth INT image to resolution of PB attenuated SD image = SD convolved INT image
    - PB attenuated SD image - SD convolved INT image = INT subtracted SD image
    - define weightfactor = INT beam area / SD beam area
    - if SD in Jy/beam: INT image + INT subtracted SD image * weightfactor = combined image
    - if SD in Kelvin:  INT image + INT subtracted SD image = combined image
    - PB correct SSC output
    - exportfits pbcor and nopbcorr
   


    highres  - high resolution (interferometer) image
    lowres   - low resolution (single dish (SD)/ total power (TP)) image
    pb       - high resolution (interferometer) primary beam image 
    combined - output image name base 
    sdfactor - scaling factor for the SD/TP contribution

    Example: ssc(highres='INT.image', lowres='SD.image', pb='INT.pb',
                 combined='INT_SD_1.7', sdfactor=1.7)

    """

    
    ######################  Helper Functions  ##################### 
    
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
    
    
    ###################### SSC main body #####################


    file_check(lowres)

    file_check(highres)

    file_check(pb)


    #   if os.path.exists(lowres):
    #       pass
    #   else:
    #       print(lowres+' does not exist')
    #       return False
    #   
    #   if os.path.exists(highres):
    #       pass
    #   else:
    #       print(highres+' does not exist')
    #       return False
    #   
    #   if os.path.exists(pb):
    #       pass
    #   else:
    #       print(pb+' does not exist')
    #       return False



    print('')                    
    print('### Start Faridani SSC for sdfactor', sdfactor)       
    print('')  



    #  @todo   this is dangerous, need to find temp names 
    os.system('rm -rf lowres.*')

    lowres_regrid1 = 'lowres.regrid'

    #  --- EXPECTING regridded and reordered images! ----> comment this out
    #
    # # Reorder the axes of the low to match high/pb 
    # #lowres = reorder_axes(highres,lowres,'lowres.ro')
    # lowres = reorder_axes(lowres,'lowres.ro')
    # 
    # # Regrid low res Image to match high res image
    # 
    # print('Regridding lowres image...[%s]' % lowres)
    # cta.imregrid(imagename=lowres,
    #              template=highres,
    #              axes=[0,1,2,3],
    #              output=lowres_regrid1)

    os.system('cp -r '+lowres+' '+lowres_regrid1)
                     
    #lowres_unit = imhead(lowres_regrid1, mode='get', hdkey='Bunit')['value']
    lowres_unit = cta.imhead(lowres_regrid1, mode='get', hdkey='Bunit')

    # Multiply the lowres image with the highres primary beam response
    print('Multiplying lowres by the highres pb...')
    cta.immath(imagename=[lowres_regrid1, pb],
               expr='IM0*IM1',
               outfile='lowres.multiplied')

    lowres_regrid = 'lowres.multiplied'

    cta.imhead(lowres_regrid, mode='put', hdkey='Bunit', hdvalue=lowres_unit)


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
    #print('imsmooth',major,minor,pa)
    cta.imsmooth(highres, 'gauss', major, minor, pa, True, outfile=highres + '_conv', overwrite=True)

    highres_conv = highres + '_conv'
    
    # Missing flux    
    sub = 'sub.im'
    sub_bc = 'sub_bc.im'
    combined = combined + '.image'

    #os.system('rm -rf '+highres_conv)
    os.system('rm -rf '+sub)
    os.system('rm -rf '+sub_bc)
    
    print('Computing the obtained flux only by single-dish ...')
    cta.immath([lowres_regrid, highres_conv], 'evalexpr', sub, '%s*IM0-IM1' % sdfactor)
    print('Flux difference has been determined' + '\n')
    #print('Units', getBunit(lowres_regrid))
    #print(lowres_regrid)
    #print('Units', getBunit(sub))
    #print('Units', getBunit(highres_conv))
    #print('Units', getBunit(highres))


    cta.imhead(sub, mode='put', hdkey='Bunit', hdvalue=lowres_unit)


    # Combination 
    if getBunit(lowres_regrid) == 'Jy/beam':
        print('Computing the weighting factor according to the surface of the beam ...')
        weightingfac = (float(getBmaj(str(highres))) * float(getBmin(str(highres)))
                ) / (float(getBmaj(str(lowres_regrid))) * float(getBmin(str(lowres_regrid))))
        print('Weighting factor: ' + str(weightingfac) + '\n')
        print('Considering the different beam sizes ...')
        os.system('rm -rf %s' % sub_bc)        
        cta.immath(sub, 'evalexpr', sub_bc, 'IM0*' + str(weightingfac))
        print('Fixed for the beam size' + '\n')
        print('Combining the single-dish and interferometer cube [Jy/beam mode]')
        os.system('rm -rf %s' % combined)        
        cta.immath([highres, sub_bc], 'evalexpr', combined, 'IM0+IM1')
        print('The missing flux has been restored' + '\n')

    if getBunit(lowres_regrid) == 'Kelvin':
        print('Combining the single-dish and interferometer cube [K-mode]')
        os.system('rm -rf %s' % combined)                
        cta.immath([highres, sub], 'evalexpr', combined, 'IM0 + IM1')
        print('The missing flux has been restored' + '\n')

    #print('Units', getBunit(combined))
    cta.imhead(combined, mode='put', hdkey='Bunit', hdvalue=lowres_unit)


    # primary beam correction
    os.system('rm -rf '+combined +'.pbcor')
    cta.immath(imagename=[combined, pb],
               expr='IM0/IM1',
               outfile=combined +'.pbcor')

    highres_unit = cta.imhead(combined, mode='get', hdkey='Bunit')
    cta.imhead(combined +'.pbcor', mode='put', hdkey='Bunit', hdvalue=highres_unit)

    # os.system('cp -r '+pb+' '+combined.replace('.image','.pb'))
	# 
    # myimages = [combined]
	# 
	# 
    # 
    # for myimagebase in myimages:
    #      cta.exportfits(imagename = myimagebase+'.pbcor',
    #                     fitsimage = myimagebase+'.pbcor.fits',
    #                     overwrite = True
    #      )
    # 
    #      cta.exportfits(imagename = myimagebase,
    #                     fitsimage = myimagebase+'.fits',
    #                     overwrite = True
    #      )
	# 
	
    export_fits(combined.replace('.image',''), clean_origin=pb.replace('.pb', ''))



    # Tidy up 
    os.system('rm -rf lowres.*')
    #os.system('rm -rf lowres.regrid')
    #os.system('rm -rf lowres.multiplied')
    os.system('rm -rf '+highres_conv)
    os.system('rm -rf '+sub)
    os.system('rm -rf '+sub_bc)
    #os.system('rm -rf '+combined)
    #os.system('rm -rf '+combined+'.pbcor')
    
    return True







######################################

def listobs_ptg(TPpointingTemplate, 
                listobsOutput, 
                TPpointinglist, Epoch='J2000'):
    """
    listobs_ptg (L. Moser-Fischer)
    based on Jin Koda's approach to get 12m pointings from listobs()
    https://github.com/tp2vis/distribute

    TPpointingTemplate - an ALMA 12m data set (before concat?) (ending on *.ms)
    listobsOutput - file name to store the listobs-output      (ending on *.log)
    TPpointinglist - final pointing list for TP2VIS            (ending on *.ptg)

    Example: ssc(highres='INT.image', lowres='SD.image', pb='INT.pb',
                 combined='INT_SD_1.7.image', sdfactor=1.7)

    """


    file_check(TPpointingTemplate)


    os.system('rm -rf '+listobsOutput)
    os.system('rm -rf '+TPpointinglist)     
    cta.listobs(TPpointingTemplate, listfile=listobsOutput)
    pointings=[]
    with open(listobsOutput, 'r') as f1:
        data = f1.readlines()
        for line in data:
            if re.search(Epoch, line):                     # look for first target entry and             
                words = line.split()
                epoch=words[-3]
                decl=words[-4]
                ra=words[-5].split('*')[-1]
                pointings.append(epoch+' '+ra+' '+decl)
   
    np.savetxt(TPpointinglist, pointings, fmt='%.40s')



def ms_ptg(msfile, outfile=None, uniq=True):
    """ 
    Taken from the Quick Array Combinations (QAC) module, state: March, 2021, 
    originally called qac_ms_ptg in
    https://github.com/teuben/QAC/blob/master/src/qac.py

    modified by Lydia Moser-Fischer

    # NOTE: seems to expect a target-only data set!
    _____________________________________________________________________

    get the ptg's from an MS into a list and/or ascii ptg file
    'J2000 19h00m00.00000 -030d00m00.000000',...
    This is a little trickier than it sounds, because the FIELD table has more entries than
    you will find in the FIELD_ID column (often central coordinate may be present as well,
    if it's not part of the observing fields, and locations of the Tsys measurements
    For 7m data there may also be some jitter amongst each "field" (are multiple SB used?)
    Note that the actual POINTING table is empty for the 12m and 7m data
    # @todo: should get the observing frequency and antenna size, so we also know the PB size
    #
    # @todo: what if DELAY_DIR, PHASE_DIR and REFERENCE_DIR are not the same???
    
    """

    def hms(val):
        """
        Decimal value to 3-element tuple of hour, min, sec. Just calls dms/15
        from https://github.com/teuben/QAC/blob/master/src/utils/constutils.py
        """
        return dms(val/15.0)
    
    def dms(val):
        """
        Decimal value to 3-element tuple of deg, min, sec.
        from https://github.com/teuben/QAC/blob/master/src/utils/constutils.py

        """
        if type(val) == type(np.array([1,2,3])):
            val_abs = np.abs(val)
            d = np.floor(val_abs)
            m = np.floor((val_abs - d)*60.0)
            s = ((val_abs - d - m/60.0))*3600.0
            d *= +2.0*(val >= 0.0) - 1.0
        else:
            val_abs = abs(val)
            d = math.floor(val_abs)
            m = math.floor((val_abs - d)*60.0)
            s = ((val_abs - d - m/60.0))*3600.0
            d *= +2.0*(val >= 0.0) - 1.0
        return (d, m, s)


    def sixty_string(inp_val,hms=False,colons=False):
        """
        Convert a numeric vector to a string. Again, QA should do this.
        from https://github.com/teuben/QAC/blob/master/src/utils/constutils.py
        """    
        if hms==True:
            out_str = "%02dh%02dm%05.3fs" % (inp_val[0], inp_val[1], inp_val[2])
        elif colons==True:
            out_str = "%+02d:%02d:%05.3f" % (inp_val[0], inp_val[1], inp_val[2])
        else:
            out_str = "%+02dd%02dm%05.3fs" % (inp_val[0], inp_val[1], inp_val[2])
        return out_str


    file_check_vis_str_only(msfile)

    #   file_check(msfile)


    mytb = tbtool()                                # modified

    if uniq:
        mytb.open('%s' % msfile)
        field_id = list(set(mytb.getcol("FIELD_ID")))
        mytb.close()
    #li = [a[i] for i in b]
    mytb.open('%s/FIELD' % msfile)
    #col = 'DELAY_DIR'
    #col = 'PHASE_DIR'
    col = 'REFERENCE_DIR'
    # get all the RA/DEC fields
    ptr0 = mytb.getcol(col)[0,0,:]
    ptr1 = mytb.getcol(col)[1,0,:]
    n1 = len(ptr0)
    if uniq:
        # narrow this down to those present in the visibility data
        ptr0 = [ptr0[i] for i in field_id]
        ptr1 = [ptr1[i] for i in field_id]
    n2 = len(ptr0)
    print("%d/%d fields are actually used in %s" % (n2,n1,msfile))
    mytb.close()
    #
    pointings = []
    for i in range(len(ptr0)):
        ra  = ptr0[i] * 180.0 / math.pi
        dec = ptr1[i] * 180.0 / math.pi
        if ra < 0:   # don't allow negative HMS
            ra = ra + 360.0
        ra_string = sixty_string(hms(ra),hms=True)
        dec_string = sixty_string(dms(dec),hms=False)
        pointings.append('J2000 %s %s' % (ra_string, dec_string))
    if outfile != None:
        fp = open(outfile,"w")
        for p in pointings:
            fp.write("%s\n" %p)
        fp.close()
    return pointings

    #-end of qac_ms_ptg()




def create_TP2VIS_ms(imTP=None, TPresult=None,
    TPpointinglist=None, mode='mfs', vis=None, imname=None, TPnoiseRegion=None,
    TPnoiseChannels=None
    ):
    """ 
    create_TP2VIS_ms (L. Moser-Fischer)
    tool to turn SD image into visibilities
    
    steps:
    - get rms from SD image/cube
    - make SD visibilities with tp2vis
    - tp2vispl - plots weights of the TP and of the INT data
    _____________________________________________________________________

    mode - specmode
    imTP - SD image (reordered, but not regridded)
    TPresult - output name of the TP visibilities (*.ms)
    TPpointinglist - 12m pointing list (ALMA, *.ptg) 
    vis - INT ms-file to compare TP ms-file to
    inmame - output praefix for weightplot
    TPnoiseRegion - if mode='mfs', emission-free box in cont image is used to determine noise
    TPnoiseChannels - if mode='cube', line-free channels in cube are used to determine noise

 
   """


    file_check(imTP)

    file_check(TPpointinglist)
    
    #   file_check_vis_str_only(vis)
    file_check_vis(vis)
    


    os.system('rm -rf '+TPresult)    


    # define region/channel range in your input TP image/cube to derive the rms
    specmode=mode
    
    #### continuum
    if specmode == 'mfs':
        cont_RMS = cta.imstat(imTP, box=TPnoiseRegion)['rms']#[0]
        #peak_val = imstat(imnameth+'.image')['max'][0]
        #thresh = full_RMS*RMSfactor
        rms = cont_RMS
        
        #t2v.tp2vis(imTP,TPresult,TPpointinglist,nvgrp=5,rms=rms)# winpix=3)  # in CASA 6.x
        print('Deriving TP.ms from deconvolved image')        
        t2v.tp2vis(imTP,TPresult,TPpointinglist,deconv=True,maxuv=10,nvgrp=4)


  
    
    #### cube
    elif specmode == 'cube':
        TPmom6=imTP.replace('.image','.mom6')
        os.system('rm -rf '+TPmom6)
        cta.immoments(imagename=imTP, moments=[6], 
                      outfile=TPmom6, chans=TPnoiseChannels)
        cube_RMS = cta.imstat(TPmom6)['rms'][0]
        rms = cube_RMS
    
        #thresh = cube_RMS*cube_rms   # 3 sigma level
        
        print('Deriving TP.ms using image rms')
        print('rms in image:', rms)    
        t2v.tp2vis(imTP,TPresult,TPpointinglist,nvgrp=5,rms=rms)# winpix=3)  # in CASA 6.x
        #t2v.tp2vis(imTP,TPresult,TPpointinglist,deconv=True,maxuv=10,nvgrp=4)
        #print('Derived TP.ms from deconvolved image')



    #### weights-plot for INT and unscaled TP

    t2v.tp2vispl([TPresult, vis],outfig=imname+'_weightplot.png')  # in CASA 6.x
    # use '_' instead of '.', because runtclean deletes all imname+'.*' !          
          


def transform_INT_to_SD_freq_spec(TPresult, imTP, vis, 
    transvis, datacolumn='DATA', outframe='LSRK'
    ):
    """ 
    transform_INT_to_SD_freq_spec (L. Moser-Fischer)
    tool to transform the INT data to the same reference frame
    and same frequency range as the SD cube has
    
    else tclean with TP.ms and INT.ms together causes trouble. 

    steps:
    - use get_SD_cube_params to derive the frequency range covered by the SD cube
    - mstransform fo given datacolumn to SD cube's freq-range and reference frame
    
    ----- not applied: mstransforms to spectral setup of the spw with the least number of 
    spectral  channels and takes its spectral setup over to all other spw in the data. 
    This assumes a similar frequency range for all spws so that not much information 
    would be lost. Therefore, beware of mixed data set with strongly differing 
    frequnecy coverages!

    _____________________________________________________________________

    imTP - SD image (reordered, but not regridded)
    TPresult - name of the TP visibilities (*.ms)  (actually ....this part of the script
    is not really used anymore  ---- need to modify)
    vis - input name of the INT visibilities (*.ms)
    transvis - output name of the INT visibilities (*.ms)
    datacolumn - data from which column to use (typilcay CASA parameter) 
    outframe - reference frame of the transvis output


    """


    file_check(TPresult)

    file_check(imTP)

    #   file_check(vis)
    file_check_vis_str_only(vis)



    # tclean segmentation fault -
    # maybe due to different numbers of spw in INT and SD ms-files
    # we can expect TP.ms to have only one spw
    # put relevant INT data range (i.e SD range) in one spw

    mytb = tbtool()                                # modified
    mytb.open(TPresult+'/SPECTRAL_WINDOW', nomodify=False)
    # expect only one spw
    bandwidth = mytb.getcell("TOTAL_BANDWIDTH",0)
    min_freq = min(mytb.getcell("CHAN_FREQ",0)/10**9)  # in GHz
    max_freq = max(mytb.getcell("CHAN_FREQ",0)/10**9)  # in GHz
    freq_width = mytb.getcell("CHAN_WIDTH",0)[0]/10**9
    mytb.putcell("TOTAL_BANDWIDTH",0, abs(bandwidth))
    mytb.flush()
    bandwidth2 = mytb.getcell("TOTAL_BANDWIDTH",0)/10**9
    mytb.close()
    
    print(' ')
    print('min_freq, max_freq', 'freq_width', 'bandwidth', '|max-min|',
           min_freq, max_freq, freq_width, bandwidth2, abs(abs(max_freq-min_freq)+abs(freq_width)))
    print(' ')

    cube_dict = get_SD_cube_params(sdcube = imTP) #out: {'nchan':nchan, 'start':start, 'width':width}

    edges=[float(cube_dict['start'].replace('Hz','')), float(cube_dict['start'].replace('Hz',''))+(cube_dict['nchan'])*float(cube_dict['width'].replace('Hz',''))]
    im_min_freq = min(edges)/10**9 # one width smaller than from ms-table for width<0
    im_max_freq = max(edges)/10**9 # one width smaller than from ms-table for width>0

    print('im_min_freq, im_max_freq', im_min_freq, im_max_freq)
    print(' ')                      


    # #### workaround for not allowed combinespw=True in case of differing numbers of channels in the spws:
    # # bring all spw on the same channels a the spw with lowest number of channels
    # # get smallest number of channels (expected to have largest chan width in concat file...?)
    # 
    # mymsmd=msmdtool()
    # mymsmd.open(vis)  
    # # get the spectral window IDs associated with "*"  
    # num_spws = mymsmd.spwsforintent("*")  
    # # got all the spw IDs associated with all intents which contain ’WVR’  
    # mymsmd.done()     
    # 
    # 
    # mytb.open(vis+'/SPECTRAL_WINDOW', nomodify=False)
    # # expect several spw
    # numchan=[]
    # for i in range(0,len(num_spws)):
    #     numchan.append(mytb.getcell("NUM_CHAN",i))
    # minnumchan=min(numchan)
    # idx=numchan.index(minnumchan)
    # min_freq = min(mytb.getcell("CHAN_FREQ",idx)/10**9)  # in GHz
    # chan_width = abs(mytb.getcell("CHAN_WIDTH",idx)[0]/10**9)  # in GHz
    # mytb.close()    
        
    
    
    os.system('rm -rf '+transvis)
                
    cta.mstransform(vis=vis,
                    outputvis=transvis,
                    datacolumn=datacolumn,
                    regridms=True,
                    #nchan=minnumchan,
                    #start=str(min_freq)+'GHz',
                    #width=str(chan_width)+'GHz',
                    outframe=outframe,
                    #field='',
                    spw = str(im_min_freq)+'~'+str(im_max_freq)+'GHz', # general_tclean_param['spw'], 
                    combinespws=False          # combinespw=True not allowed in case of differing numbers of channels in the spws
    ) 
    
    # PS: turns out that parmeter spw does not reproduce the given frequency range 
    # but selects the full spw that is covered by these frequencies 
    # (what happens for df > 2 neighborung spw --- would it select both or give an error?)

    
    
    
    
    


def runtclean_TP2VIS_INT(TPresult, TPfac, 
    #imTP=imTP, 
    #vis=vis, 
    #transvis=transvis, 
    vis, 
    imname, 
    startmodel='',
    spw='', 
    field='', 
    specmode='mfs', 
    imsize=[], 
    cell='', 
    phasecenter='',
    start=0, 
    width=1, 
    nchan=-1, 
    restfreq='',
    threshold='', 
    niter=0, 
    usemask='auto-multithresh' ,
    sidelobethreshold=2.0, 
    noisethreshold=4.25, 
    lownoisethreshold=1.5, 
    minbeamfrac=0.3, 
    growiterations=75, 
    negativethreshold=0.0,
    mask='', 
    pbmask=0.4, 
    interactive=True, 
    multiscale=False, 
    maxscale=0.,
    RMSfactor=1.0,
    threshregion='',
    cube_rms=3.0,
    cont_chans ='2~4',
    loadmask=False,
    fniteronusermask=0.3,
    rederivethresh=True
    ):
    
    """ 
    runtclean_TP2VIS_INT (L. Moser-Fischer)
    
    tclean with TP.ms and INT.ms together

    steps:
    - make copy of TP.ms and scale it with tp2viswt (multiply with TPfac)
    - tp2vispl - plot of weights for scaled copy of TP and of the INT data
    - concat scaled TP data and INT data
    - tclean dirty image of concat data
    - derive new threshold
    - tclean with given niter and new threshold
    - correct for beam ratios (true PSF vs. Gaussian restoring) with tp2vistweak
    - export
    
    _____________________________________________________________________

    TPfac - factor to apply to the visibility weights of the TP visibilities
    TPresult - name of the TP visibilities (*.ms)
    
    from vis to continueclean analoguous to runtclean

    next 3 parameters as defined as in derive_threshold:
   
    RMSfactor - to apply to a continuum RMS of the full image to define a threshold at which 
            as much emission as possible/reasonable is contained; user needs to play with it
            typically: 0.5
    cube_rms - factor to apply to a a cube RMS to define a threshold. channels
            If cont_chans is set to line-free channels, this factor can be used
            to set the threshold as 3sigma, 10sigma, etc level) 
    cont_chans - define the line-free channels here to get a pure noise RMS of a cube 
        

    """


    file_check(TPresult)


    #file_check(vis)

    if type(vis) is str:
        file_check(vis)
          
    if isinstance(vis, list):
        for i in range(0,len(vis)):
            file_check(vis[i])          # if one of the files does not exist, script will exit here


    os.system('rm -rf '+imname+'*')
    
    # need to redo TPresult, since each loop modifies it (tp2viswt)!
    
    TPresultTPfac= TPresult.replace('.ms','_TPfac'+str(TPfac)+'.ms')
    os.system('rm -rf '+TPresultTPfac)            
    
    os.system('cp -rf '+TPresult+' '+TPresultTPfac)
    
    t2v.tp2viswt(TPresultTPfac,mode='multiply',value=TPfac)  # in CASA 6.x
                             
    #print ' '
    #print 'Generating corrected weight-plot for ' +msname+ ' with ' +TPresult
    #print ' '
   
    
    t2v.tp2vispl([TPresultTPfac, vis],outfig=imname+'_weightplot.png')  # in CASA 6.x
    # use '_' instead of '.', because runtclean deletes all imname+'.*' !          
    
    
    #print ' '
    #print 'Combining ' +str([msname,TPresult])
    #print ' '
    
    
    #### careful ... sometimes not working in clean:
    TPconcatTPfac= vis.replace('.ms','_TPfac'+str(TPfac)+'.ms')
    os.system('rm -rf '+TPconcatTPfac)            
    
    cta.concat(vis=[vis,TPresultTPfac], concatvis=TPconcatTPfac, copypointing=False)    
    myvis = TPconcatTPfac

    ####myvis = [TPresultTPfac, vis]
    cta.listobs(TPresultTPfac)
    cta.listobs(vis)
    
    #if specmode=='cube':
    #    #specmode_used ='cubedata'
    #    specmode_used ='cube'
    #if specmode=='mfs':
    #    specmode_used ='mfs'        
    #
    
    TP2VIS_arg = dict( 
                  startmodel=startmodel,
                  spw=spw, 
                  field=field, 
                  specmode=specmode, #_used,
                  imsize=imsize, 
                  cell=cell,
                  phasecenter=phasecenter, 
                  start=start,
                  width=width,
                  nchan=nchan,
                  restfreq=restfreq,
                  threshold=threshold,
                  niter=0,
                  usemask=usemask,
                  sidelobethreshold=sidelobethreshold,  
                  noisethreshold=noisethreshold,
                  lownoisethreshold=lownoisethreshold,
                  minbeamfrac=minbeamfrac,
                  growiterations=growiterations,
                  negativethreshold=negativethreshold,         
                  mask=mask,              
                  pbmask=pbmask,
                  interactive=interactive,
                  multiscale=multiscale,
                  maxscale=maxscale,
                  continueclean = False,
                  loadmask=False,
                  fniteronusermask=fniteronusermask)    
        
    
    # make dirty image to correct for beam area

    runtclean(myvis, imname+'_dirty', **TP2VIS_arg)
    

    if rederivethresh==False:
        print('### Use input threshold of ', TP2VIS_arg['threshold']) 
    else:
        # define region/channel range in your input TP image/cube to derive the rms
        specmode=specmode
        TPINTim = imname+'_dirty.image'
        
        #### continuum
        if specmode == 'mfs':
            cont_RMS = cta.imstat(TPINTim, box=threshregion)['rms'][0]
            #peak_val = imstat(imnameth+'.image')['max'][0]
            #thresh = full_RMS*RMSfactor
            thresh = cont_RMS*RMSfactor
        
        
        #### cube
        elif specmode == 'cube':
            TPINTmom6=TPINTim.replace('.image','.mom6')
            os.system('rm -rf '+TPINTmom6)
            cta.immoments(imagename=TPINTim, moments=[6], 
                          outfile=TPINTmom6, chans=cont_chans)
            cube_RMS = cta.imstat(TPINTmom6, box=threshregion)['rms'][0]
            thresh = cube_RMS*cube_rms
        
            #thresh = cube_RMS*cube_rms   # 3 sigma level
        
        
        
        
        # make clean image for the given niter
        
        print(' ')
        print('### Old threshold was ', TP2VIS_arg['threshold']) 
        
        TP2VIS_arg['threshold'] = str(thresh)+'Jy'
        
        print('### Threshold from TP+INT data is ', TP2VIS_arg['threshold'])    
        print(' ')



    TP2VIS_arg['niter'] = niter

    TP2VIS_arg['loadmask'] = loadmask

    runtclean(myvis, imname, **TP2VIS_arg)
    
    #if doautomask == True:
    #    TP2VIS_arg['continueclean'] = True 
    #    TP2VIS_arg['usemask'] = 'auto-multithresh' 
    #    runtclean(myvis, imname, **TP2VIS_arg)

 
 
    # tclean(vis=['M100-B3.alma.all_int-weighted.ms', 
    # 'M100-B3.SD_ro_TPfac1.0.ms'], selectdata=True, 
    #field='', spw='', 
    #imagename='M100-B3.cube_INTpar_HB_SD-AM_nIA_n0.TP2VIS_t1.0_dirty', 
    #imsize=560, cell='0.5arcsec', phasecenter='J2000 12h22m54.9 +15d49m15', 
    #specmode='cube', reffreq='', nchan=10, start='1550km/s', width='5km/s', 
    #restfreq='115.271202GHz', gridder='mosaic', 
    #pblimit=0.2, deconvolver='hogbom', restoringbeam='common', 
    #pbcor=True, weighting='briggs', robust=0.5, niter=0, 
    #threshold='0.055674938585244874Jy', cyclefactor=2.0, 
    #interactive=False, usemask='user', 
    #mask='M100-B3.INTpar_SD-AM-RMS.mask', pbmask=0.4)  ==> segmantation fault (core dumped)!
    
    
    # concat vis and TPms and use concatfile for tclean
    # 2021-03-02 13:16:52   WARN    MSConcat::copySpwAndPol Negative or zero total bandwidth in SPW 0 of MS to be appended.
    # Start tclean ...
    # Run with user mask /vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/DC_Ly_tests/M100-B3.INTpar_SD-AM-RMS.mask
    # 2021-03-02 13:16:57   WARN    concat::::casa  You set niter to 0 (zero, the default). Only a dirty image will be created.
    # 2021-03-02 13:16:59   WARN    MSTransformRegridder::combineSpwsCore   SPW 4 cannot be combined with SPW 3. Non-matching ref. frame.
    # 2021-03-02 13:16:59   SEVERE  MSTransformRegridder::combineSpwsCore   Error combining SpWs
    
    #os.system('rm -rf '+imname+'.tweak.image.pbcor.fits')            
    #os.system('rm -rf '+imname+'.image.pbcor.fits')            


    if niter!=0:
        t2v.tp2vistweak(imname+'_dirty', imname, mask='\'' + imname +'.image' + '\'' + '>0.2') # in CASA 6.x
        export_fits(imname+'.tweak', clean_origin=imname)

        # os.system('rm -rf '+imname+'.tweak.pb')            
        # os.system('cp -r '+imname+'.pb '+imname+'.tweak.pb')            
        # cta.exportfits(imagename=imname+'.tweak.image.pbcor', fitsimage=imname+'.tweak.image.pbcor.fits')
  
    export_fits(imname, clean_origin='')

    # cta.exportfits(imagename=imname+'.image.pbcor', fitsimage=imname+'.image.pbcor.fits')
    ##exportfits(imagename=TP2VISim+'.pb', fitsimage=TP2VISim+'.pb.fits')
    
     
    #os.system('mv ' +combipraefix+'*.png '+imResult)   



def pydict_to_file(pydict, filename):   
    """ 
    save dictionaries (L. Moser-Fischer)
    pydict - a python dictionary
    filename - will store dict under this string +'.txt' 

    """ 
    f = open(filename+'.txt','w')
    f.write(str(pydict))
    f.close()
    
    return True 



def file_to_pydict(filename):
    """ 
    load dictionaries (L. Moser-Fischer)
    filename - will load dict from this string +'.txt'
    return: python dictionary 
    
    problems with arrays, int32, 

    """     

    file_check(filename+'.txt')
    
    
    f = open(filename+'.txt','r')
    data=f.read()
    f.close()
    return eval(data)




def pydict_to_file2(pydict, filename):   
    """ 
    save dictionaries (L. Moser-Fischer)
    pydict - a python dictionary
    filename - will store dict under this string +'.txt' 

    """ 
    import pickle as pk 
    with open(filename+'.pickle', 'wb') as handle:
        pk.dump(pydict, handle, protocol=pk.HIGHEST_PROTOCOL)
    return True 



def file_to_pydict2(filename):
    """ 
    load dictionaries (L. Moser-Fischer)
    filename - will load dict from this string +'.txt'
    return: python dictionary 
    
    """   
    import pickle as pk 
    
    file_check(filename+'.pickle')
    
    with open(filename+'.pickle', 'rb') as handle:
        pydict = pk.load(handle)
    return pydict     



def docstrings_list(filename):
    """ 
    save docstrings of all functions defined for DC project  (L. Moser-Fischer)
    filename - will store docstrings under this string +'.txt' 

    """ 
    
    # get list with dir(dc) and remove imported modules
    
    doclist = [channel_cutout.__doc__,
               check_CASAcal.__doc__,
               check_prep_tclean_param.__doc__,
               convert_JypB_JypP.__doc__,
               create_TP2VIS_ms.__doc__,
               createplaneimage.__doc__,
               derive_maxscale.__doc__,
               derive_threshold.__doc__,
               docstrings_list.__doc__,
               feather_int_sd.__doc__,
               file_check.__doc__,
               file_check_vis.__doc__,
               file_check_vis_str_only__doc__,
               file_to_pydict.__doc__,
               file_to_pydict2.__doc__,
               getFreqList.__doc__,
               get_SD_cube_params.__doc__,
               listobs_ptg.__doc__,
               make_SD_mask.__doc__,
               make_SDint_mask.__doc__,
               ms_ptg.__doc__,
               pydict_to_file.__doc__,
               pydict_to_file2.__doc__,
               regrid_SD.__doc__,
               reorder_axes.__doc__,
               reorder_axes2.__doc__,
               report_mask__doc__,
               runWSM.__doc__,
               runfeather.__doc__,
               runsdintimg.__doc__,
               runtclean.__doc__,
               runtclean_TP2VIS_INT.__doc__,
               ssc.__doc__,
               transform_INT_to_SD_freq_spec.__doc__,
               visHistory.__doc__]
    
    f = open(filename+'.txt','w')
    for doc in doclist:
        f.write(str(doc))      
        f.write(str('\n'))      
        f.write(str('----------------------------------------------------------------------------------')) 
        f.write(str('\n'))      
    f.close()
    
    


def file_check(filename):
    """ 
    file existence check  (L. Moser-Fischer)
    filename - if filename (string) exists, return filename, else exit script 

    """ 
        
    if os.path.exists(filename):
        return filename
    else:
        print('')
        print('')
        print('-------------------------------- ! ERROR ! --------------------------------')
        print('')
        print(filename+' does not exist!')
        print('')
        print('-------------------- ! ABORT PROGRAM WITH SYSTEMEXIT ! --------------------')
        print('')
        print('')
        return sys.exit()
        
        
        
        
        
def file_check_vis(vis):
    """ 
    special file existence check for vis, i.e. one msfile as string or many as list (L. Moser-Fischer)
    vis - if vis (string/list) exists, return vis, else exit script (via file_check)

    """ 
        
    if type(vis) is str:
        return file_check(vis)
        
    if isinstance(vis, list):
        for i in range(0,len(vis)):
            file_check(vis[i])          # if one of the files does not exist, script will exit here
        return vis



def file_check_vis_str_only(vis):
    """ 
    special file existence check for vis accepting only one msfile - no list (L. Moser-Fischer)
    vis - if vis (string/list) exists, return vis, else exit script (via file_check)

    """ 
        
    if type(vis) is str:
        return file_check(vis)
        
    if isinstance(vis, list):
        print('')
        print('')
        print('-------------------------------- ! ERROR ! --------------------------------')
        print('')
        print('Function cannot handle multiple msfiles. Please, give only one msfile for parameter "vis"!')
        print('')
        print('-------------------- ! ABORT PROGRAM WITH SYSTEMEXIT ! --------------------')
        print('')
        print('')
        return sys.exit()




