"""The datacomb module

Tools for different methods of interferometric/single-dish 
data combination with CASA.

Based on the work at the Workshop
"Improving Image Fidelity on Astronomical Data", 
Lorentz Center, Leiden, August 2019, 
and subsequent follow-up work. 

Run under CASA 6.

"""

import os
import math
import sys
import glob

pythonversion = sys.version[0]

if pythonversion=='3':
    from casatasks import version as CASAvers
    if CASAvers()[0]>=6 and CASAvers()[1]>=1:
        print('Executed in CASA ' +'.'.join(map(str, CASAvers()))) 
        from casatasks import casalog
        from casatasks import exportfits
        from casatasks import imhead
        from casatasks import sdintimaging
        from casatasks import tclean
        from casatasks import immath, imstat, immoments
        from casatasks import imregrid, imtrans
        from casatasks import imsmooth
        from casatasks import feather
        
        from casatools import image as iatool
        from casatools import quanta as qatool
        from casatools import table as tbtool
    else:
        print('###################################################')
        print('Your CASA version does not support sdintimaging.')
        print('Please use at least CASA 5.7.0 or 6.1.x')
        print('Aborting script ...')
        print('###################################################')
        sys.exit()

elif pythonversion=='2':
    import casadef
    if casadef.casa_version == '5.7.0':
        print('Executed in CASA ' +casadef.casa_version)
        #print("Warning: datacomb assuming not in casa6")
    else:
        print('###################################################')
        print('Your CASA version does not support sdintimaging.')
        print('Please use at least CASA 5.7.0 or 6.1.x')
        print('Aborting script ...')
        print('###################################################')
        sys.exit()



##########################################

def runsdintimg(vis, 
                sdimage, 
                jointname, 
                spw='', 
                field='', 
                specmode='mfs', 
                sdpsf='',
                threshold=None, 
                sdgain=5, 
                imsize=[], 
                cell='', 
                phasecenter='', 
                dishdia=12.0,
                start=0, 
                width=1, 
                nchan=-1, 
                restfreq=None, 
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
                maxscale=0.              
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
    jointname - the imagename of the output images
    spw - the standard selection parameter spw of tclean
           default: '' i.e. all SPWs
    field - the standard selection parameter field of tclean
           default: '' i.e. all fields
    specmode - the standard tclean specmode parameter: supported are msf or cube
           default: msf 
    sdpsf - (optional) the SD PSF, must have the same coords as sdimage
           if omitted or set to '' (empty string), a PSF will be derived
           from the beam information in sdimage
    threshold - the tclean threshold 
    sdgain - the weight of the SD data relative to the interferometric data
           default: 5 
             'auto' - determine the scale automatically (experimental)
    imsize - the standard tclean imsize parameter 
            should correspond to the imagesize for the most extended
            interferometer config.
    cell - the standard tclean cell parameter
            should correspond to the cell size for the most extended
            interferometer config, i.e. smallest beam / 5.
    phasecenter - the standard tclean phasecenter parameter
           e.g. 'J2000 12:00:00 -35.00.00.0000'
           default: '' - determine from the input MS with aU.pickCellSize
    dishdia - in metres, (optional) used if no sdpsf is provided
           default: 12.0
    start - the standard tclean start parameter
             default: 0
    width - the standard tclean width parameter
             default: 1
    nchan - the standard tclean nchan parameter
             default: -1
    restfreq - the restfrequency to write to the image for velocity calculations
             default: None, example: '115.271GHz'
    interactive - if True (default) use interactive cleaning with initial mask
                  set using pbmask=0.4
                  if False use non-interactive clean with automasking (you will
                  need to provide the threshold parameter)

    multiscale - if False (default) use hogbom cleaning, otherwise multiscale
       
    maxscale - for multiscale cleaning, use scales up to this value (arcsec)
             Recommended value: 10 arcsec
             default: 0.

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

    if os.path.exists(vis):
        myvis = vis 
    else:
        print(vis+' does not exist')
        return False

    if os.path.exists(sdimage):
        mysdimage = sdimage
    else:
        print(sdimage+' does not exist')
        return False

    mysdpsf = ''
    if sdpsf!='':
        if os.path.exists(sdpsf):
            mysdpsf = sdpsf
        else:
            print(sdpsf+' does not exist')
            return False

    if specmode not in ['mfs', 'cube']:
        print('specmode \"'+specmode+'\" is not supported.')
        return False

    if not type(threshold) == str or 'Jy' not in threshold:
        if not interactive:
            print("You must provide a valid threshold, example '1mJy'")
            return False
        else:
            print("You have not set a valid threshold. Please do so in the graphical user interface!")
            threshold = '1mJy'

    myia = iatool()
    myqa = qatool()

    myhead = imhead(mysdimage)
    myaxes = list(myhead['axisnames'])
    numchan = myhead['shape'][myaxes.index('Frequency')] 
            
    print('Testing whether the sd image has per channel beams ...')
    myia.open(mysdimage)
    try:
        mybeam = myia.restoringbeam()
    except:
        myia.close()
        casalog.post('ERROR: sdimage does not contain beam information.', 'SEVERE', 
                     origin='runsdintimg')
        return False

    haspcb=False
    if 'beams' in mybeam.keys():
        haspcb=True
        casalog.post("The sdimage has a per channel beam.", 'INFO', 
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
            tmpia = myia.imageconcat(outfile=mysdimage+'_mod', infiles=[mysdimage, mysdimage+'_copy'], 
                                   axis=3, overwrite=True)
            tmpia.close()
            mysdimage = mysdimage+'_mod'
            numchan = 2

        myia.open(mysdimage)
        myia.setrestoringbeam(remove=True)
        for i in range(numchan):
            myia.setrestoringbeam(beam=mybeam, log=True, channel=i, polarization=0) 
        myia.close()

        casalog.post('Needed to give the sdimage a per-channel beam. Modifed image is in '+mysdimage, 'WARN', 
                     origin='runsdintimg')

    # specmode and deconvolver
    if multiscale:
        if specmode == 'mfs':
            mydeconvolver = 'mtmfs'   # needed bc the only mfs mode implemented into sdint
        elif specmode == 'cube':
            mydeconvolver = 'multiscale'
            numchan = nchan        #not really needed here?
        mycell = myqa.convert(myqa.quantity(cell),'arcsec')['value']
        myscales = [0]
        for i in range(0, int(math.log(maxscale/mycell,3))):
            myscales.append(3**i*5)

        print("My scales (units of pixels): "+str(myscales))

    else:    
        myscales = [0]
        if specmode == 'mfs':
            mydeconvolver = 'mtmfs'   # needed bc the only mfs mode implemented into sdint
        elif specmode == 'cube':
            mydeconvolver = 'hogbom'
            numchan = nchan        #not really needed here?


    #mygridder='mosaic'

    # image and cell size
    npnt = 0
    if imsize==[] or cell=='':
        casalog.post('You need to provide values for the parameters imsize and cell.', 'SEVERE', origin='runsdintimg')
        return False

    if phasecenter=='':
        phasecenter = npnt

    if restfreq==None:
        therf = []
    else:
        therf = [restfreq]

    if niter==0:
        niter = 1
        casalog.post('You set niter to 0 (zero, the default), but sdintimaging can only produce an output for niter>1. niter = 1 set automatically. ', 'WARN')


    os.system('rm -rf '+jointname+'.*')


    sdint_arg=dict(vis=myvis,
                   imagename=jointname,
                   sdimage=mysdimage,
                   field = field,
                   phasecenter=phasecenter,
                   imsize=imsize,
                   cell=cell,                                   
                   spw=spw,
                   specmode=specmode,
                   deconvolver=mydeconvolver,
                   scales=myscales,
                   nterms=1,                  # turns mtmfs into mfs
                   start=start,
                   width=width,
                   nchan = numchan, 
                   restfreq=therf,
                   gridder='mosaic',          #mygridder,
                   weighting='briggs',
                   robust = 0.5,
                   restoringbeam = 'common',   # SD-cube has only one beam - INT-cube needs it, too, else feather etc. fail
                   niter=niter,
                   #cycleniter = niter,        # bogus if = niter
                   cyclefactor=2.0,
                   threshold=threshold,
                   interactive = interactive,
                   #perchanweightdensity=False, # better True (=default)?                  
                   #pblimit=0.2,               # default
                   pbcor=True,               
                   sdpsf=mysdpsf,
                   dishdia=dishdia,
                   sdgain=sdgain,
                   usedata='sdint',
                   #interpolation='linear',    # default
                   #wprojplanes=1,             # default & not needed
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



    #if interactive:

        #sdint_arg['cycleniter']=100
        #sdint_arg['usemask']='pb'
        #sdint_arg['pbmask']=0.4

        
    #else: # non-interactive, use automasking

        #sdint_arg['cycleniter'] = 100000
        #sdint_arg['cyclefactor']=2.0
        #sdint_arg['usemask']='auto-multithresh' #,
        

                 
    sdintimaging(**sdint_arg)

                 
    #oldnames=glob.glob(imname+'.joint.multiterm*')
    #for nam in oldnames:
    #    os.system('mv '+nam+' '+nam.replace('.joint.multiterm',''))
    #oldnames=glob.glob(imname+'*.tt0*')
    #for nam in oldnames:
    #    os.system('mv '+nam+' '+nam.replace('.tt0',''))
    #oldnames=glob.glob(imname+'.joint.cube*')
    #for nam in oldnames:
    #    os.system('mv '+nam+' '+nam.replace('.joint.cube',''))
                          


    print('Exporting final pbcor image to FITS ...')
    if mydeconvolver=='mtmfs' and niter>0:
        oldnames=glob.glob(jointname+'.joint.multiterm*')
        for nam in oldnames:
            os.system('mv '+nam+' '+nam.replace('.joint.multiterm',''))
        oldnames=glob.glob(jointname+'*.tt0*')
        for nam in oldnames:
            os.system('mv '+nam+' '+nam.replace('.tt0',''))     

        os.system('rm -rf '+jointname+'.int.cube*')
        os.system('rm -rf '+jointname+'.sd.cube*')
        os.system('rm -rf '+jointname+'.joint.cube*')

        exportfits(jointname+'.image.pbcor', jointname+'.image.pbcor.fits')
        
    elif mydeconvolver=='hogbom':
        os.system('rm -rf '+jointname+'.int.cube*')
        os.system('rm -rf '+jointname+'.sd.cube*')     
        
        oldnames=glob.glob(jointname+'.joint.cube*')
        for nam in oldnames:
            os.system('mv '+nam+' '+nam.replace('.joint.cube',''))
        
        #exportfits(jointname+'.joint.cube.image.pbcor', jointname+'.joint.cube.image.pbcor.fits')
        exportfits(jointname+'.image.pbcor', jointname+'.image.pbcor.fits')

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
           restfreq=None,
           threshold='',
           niter=0,
           usemask='auto-multithresh' ,
           sidelobethreshold=2.0,
           noisethreshold=4.25,
           lownoisethreshold=1.5, 
           minbeamfrac=0.3,
           growiterations=75,
           negativethreshold=0.0,
           sdmasklev=0.3,           
           mask='', 
           pbmask=0.4,
           interactive=True, 
           multiscale=False, 
           maxscale=0.,
           sdfactorh=1.0
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
    sdmasklev - if usemask='user', then use SD image at this level to draw a mask.
             default: 0.3
    interactive - the standard tclean interactive option
             default: True
    
    multiscale - if False (default) use hogbom cleaning, otherwise multiscale
       
    maxscale - for multiscale cleaning, use scales up to this value (arcsec)
             Recommended value: 10 arcsec
             default: 0.
    sdfactorh - Scale factor to apply to Single Dish image (same as for feather)



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


    if os.path.exists(vis):
        myvis = vis 
    else:
        print(vis+' does not exist')
        return False

    if os.path.exists(sdimage):
        mysdimage = sdimage
    else:
        print(sdimage+' does not exist')
        return False

    if imhead(mysdimage)['unit']=='Jy/beam': print('SD units {}. OK, will convert to Jy/pixel.'.format(imhead(mysdimage)['unit']))
    elif imhead(mysdimage)['unit']=='Jy/pixel': print('SD units {}. SKIP conversion. '.format(imhead(mysdimage)['unit']))
    else: print('SD units {}. NOT OK, needs conversion. '.format(imhead(mysdimage)['unit']))

    ##CHECK: header units
    SingleDishResolutionArcsec = imhead(mysdimage)['restoringbeam']['major']['value'] #in Arcsec
    CellSizeArcsec = abs(imhead(mysdimage)['incr'][0])*206265. #in Arcsec
    toJyPerPix = CellSizeArcsec**2/(1.1331*SingleDishResolutionArcsec**2)
    SDEfficiency = 1.0 #--> Scaling factor
    fluxExpression = "(IM0 * {0:f} / {1:f})".format(toJyPerPix,SDEfficiency)
    #scaled_name = mysdimage.split('/')[-1]+'.Jyperpix'
    scaled_name = mysdimage+'.Jyperpix'

    os.system('rm -rf '+scaled_name)
    immath(imagename=mysdimage,
           outfile=scaled_name,
           mode='evalexpr',
           expr=fluxExpression)
    hdval = 'Jy/pixel'
    dummy = imhead(imagename=scaled_name,
                   mode='put',
                   hdkey='BUNIT',
                   hdvalue=hdval)
    ### TO DO: MAY NEED TO REMOVE BLANK 
    ### and/or NEGATIVE PIXELS IN SD OBSERVATIONS


    ## SETUP mask if usemask='user' and mask=''
    #if usemask=='user' and mask=='':
    #    if os.path.exists(+'.SDint.mask') ###HELP!!
    #    mask = make_SDint_mask(vis, sdreordered, imname, 
    #                             sdmasklev, 
    #                             SDint_mask_root, 
    #                             phasecenter=phasecenter, 
    #                             spw=        spw, 
    #                             field=      field, 
    #                             imsize=     imsize, 
    #                             cell=       cell)
        #  casalog.post("Generating a mask based on SD image", 'INFO', 
        #               origin='runWSM')
        #  #get max in SD image
        #  maxSD = imstat(scaled_name)['max'][0]
        #  sdmasklev=0.3
        #  sdmaskval = sdmasklev*maxSD
        #  os.system('rm -rf SD*.mask')     
        #  #try: 
        #  immath(imagename=[scaled_name],expr='iif(IM0>'+str(round(sdmaskval,6))+',1,0)',outfile='SD.mask')
        #  #except: print('### SD.mask already exists, will proceed')
        #  
        #  print('### Creating a mask based on SD mask and auto-mask')
        #  print('### Step 1 of 2: load the SD mask into interferometric tclean image data' )
        #  print('### Please check the result!')
        #  os.system('rm -rf '+imname+'_setmask*')        
        #  
        #  runtclean(myvis,imname+'_setmask',
        #          phasecenter=phasecenter, 
        #          spw=spw, field=field, imsize=imsize, cell=cell,
        #          niter=1,usemask='user',mask='SD.mask',restart=True,interactive=False, continueclean=True)
        #  print('### Step 2 of 2: add first auto-masking guess of bright emission regions (interferometric!) to the SD mask')
        #  print('### Please check the result!')        
        #  os.system('cp -rf '+imname+'_setmask.mask SD2.mask')
        #  os.system('rm -rf '+imname+'_setmask.image.pbcor.fits')        
        #  runtclean(myvis,imname+'_setmask', phasecenter=phasecenter, 
        #          spw=spw, field=field, imsize=imsize, cell=cell,
        #          niter=1,usemask='auto-multithresh',mask='',restart=True,interactive=False, continueclean=True)
        #  os.system('cp -rf '+imname+'_setmask.mask SDint.mask')
        #############  
        #  #print('### Creating a mask based on SD mask and auto-mask')
        #  #print('### Step 2 of 2: first auto-masking guess of bright emission regions (interferometric!) to the SD mask')
        #  #print('### Please check the result!')
        #  #runtclean(myvis,imname+'_setmask', phasecenter=phasecenter, 
        #  #        spw=spw, field=field, imsize=imsize, cell=cell,
        #  #        niter=1,usemask='auto-multithresh',mask='',restart=True,interactive=False, continueclean=True)
        #  #os.system('cp -rf '+imname+'_setmask.mask int-AM0.mask')
        #  #os.system('rm -rf '+imname+'_setmask.pbcor.fits')                 
        #  #print('### Step 1 of 2: load the SD mask into interferometric tclean image data' )
        #  #print('### Please check the result!')                  
        #  #runtclean(myvis,imname+'_setmask',
        #  #        phasecenter=phasecenter, 
        #  #        spw=spw, field=field, imsize=imsize, cell=cell,
        #  #        niter=1,usemask='user',mask='SD.mask',restart=True,interactive=False, continueclean=True)
        #  #os.system('cp -rf '+imname+'_setmask.mask SDint.mask')
        #  
        #  print('### Done! Created an SDint mask from SD and auto-mask')                
        #  mask='SDint.mask'  
        #  #mask='SD.mask'  

    ## TCLEAN METHOD WITH START MODEL
    print('### Start hybrid clean')                    
    runtclean(myvis,
              imname, 
              startmodel=scaled_name,
              spw=spw, 
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
              maxscale=maxscale)
    
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

    if os.path.exists(sdimage):
        mysdimage = sdimage
    else:
        print(sdimage+' does not exist')
        return False

    if os.path.exists(intimage):
        myintimage = intimage
    else:
        print(intimage+' does not exist')
        return False

    if os.path.exists(intpb):
        myintpb = intpb
    else:
        print(intpb+' does not exist')
        return False


    # use function for reordering instead of commented code down here 

    print('### Start feather')                    

    os.system('rm -rf lowres.* ')


    # Reorder the axes of the low to match high/pb 
    #mysdimage = reorder_axes(myintimage,mysdimage,'lowres.ro')
    mysdimage = reorder_axes(mysdimage,'lowres.ro')



    # TO DO: Improve this bit, because it's messy
    #
    # #####################################
    # #            PROCESS DATA           #
    # #####################################
    # # Reorder the axes of the low to match high/pb 

    # myfiles=[myintimage,mysdimage]
    # mykeys=['cdelt1','cdelt2','cdelt3','cdelt4']

    # os.system('rm -rf lowres.* ')
  

    # im_axes={}
    # print('Making dictionary of axes information for high and lowres images')
    # for f in myfiles:
    #    print(f)
    #    print('------------')
    #    axes = {}
    #    i=0
    #    for key in mykeys:
    #        q = imhead(f,mode='get',hdkey=key)
    #        axes[i]=q
    #        i=i+1
    #        print(str(key)+' : '+str(q))
    #    im_axes[f]=axes
    #    print(' ')

    # order=[]           

    # for i in range(4):
    #    hi_ax = im_axes[myintimage][i]['unit']
    #    lo_ax = im_axes[myintimage][i]['unit']
    #    if hi_ax == lo_ax:
    #        order.append(str(i))
    #    else:
    #        lo_m1 = im_axes[mysdimage][i-1]['unit']
    #        if hi_ax == lo_m1:
    #            order.append(str(i-1))
    #        else:
    #            lo_p1 = im_axes[mysdimage][i+1]['unit']
    #            if hi_ax == lo_p1:
    #                order.append(str(i+1))
    # order = ''.join(order)
    # print('order is '+order)

    # if order=='0,1,2,3':
    #    print('No reordering necessary')
    # else:
    #   imtrans(imagename=mysdimage,outfile='lowres.ro',order=order)
    #   lowres='lowres.ro'
    #   print('Had to reorder!')



    # Regrid low res Image to match high res image

    print('Regridding lowres image...')
    imregrid(imagename=mysdimage,
           template=myintimage,
           axes=[0,1,2],
           output='lowres.regrid')

    # Multiply the lowres image with the highres primary beam response

    print('Multiplying lowres by the highres pb...')
    immath(imagename=['lowres.regrid',
                      myintpb],
         expr='IM0*IM1',
         outfile='lowres.multiplied')


    # Feather together the low*pb and hi images

    print('Feathering...')
    feather(imagename=featherim+'.image',
          highres=myintimage,
          lowres='lowres.multiplied',
          sdfactor = sdfactor,
          lowpassfiltersd = True )

    os.system('rm -rf '+featherim+'.image.pbcor')
    immath(imagename=[featherim+'.image',
                      myintpb],
       expr='IM0/IM1',
       outfile=featherim+'.image.pbcor')
    
    print('Exporting final pbcor image to FITS ...')
    os.system('rm -rf '+featherim+'.image.pbcor.fits')
    exportfits(featherim+'.image.pbcor', featherim+'.image.pbcor.fits')

    os.system('rm -rf lowres.*')



    return True



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
              restart=True,
              continueclean = False
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

    Example: runtclean('gmc_120L.alma.all_int-weighted.ms', 
                'gmc_120L', phasecenter='J2000 12:00:00 -35.00.00.0000', 
                spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec',
                threshold='12mJy',niter=100000,
                usemask='auto-multithresh')

    """


    if os.path.exists(vis):
        myvis = vis 
    else:
        print(vis+' does not exist')
        return False

    
    #print('')
    print('Start tclean ...')
    #mymaskname = ''
    if usemask == 'auto-multithresh':
        #print('Run with {0} mask'.format(usemask))
        mymask = usemask
        if os.path.exists(mask):
           mymaskname = mask
           print('Run with {0} mask and {1} '.format(mymask,mymaskname))
        else: print('Run with {0} mask'.format(mymask))        

    elif usemask =='pb':
        print('Run with {0} mask on PB level {1}'.format(usemask,pbmask))
    elif usemask == 'user':
        if os.path.exists(mask):
           print('Run with {0} mask {1}'.format(usemask,mask))

        else:
           print('### WARNING:   mask '+mask+' does not exist, or not specified')
           #return False
    else:
        print('check the mask options')
        return False

    # specmode and deconvolver
    if multiscale:
        mydeconvolver = 'multiscale'
        myqa = qatool()
        mycell = myqa.convert(myqa.quantity(cell),'arcsec')['value']
        myscales = [0]
        for i in range(0, int(math.log(maxscale/mycell,3))):
            myscales.append(3**i*5)

        print("My scales (units of pixels): "+str(myscales))

    else:    
        myscales = [0]
        mydeconvolver = 'hogbom'

    if niter==0:
        casalog.post('You set niter to 0 (zero, the default). Only a dirty image will be created.', 'WARN')



    tclean_arg=dict(vis = myvis,
                    imagename = imname, #+'.TCLEAN',
                    startmodel = startmodel,
                    field = field,
                    #intent = 'OBSERVE_TARGET#ON_SOURCE',  #really needed?
                    phasecenter = phasecenter,
                    #stokes = 'I',                  # default, but maybe for polarization?
                    imsize = imsize,
                    cell = cell,
                    spw = spw,
                    #outframe = 'LSRK',             # default
                    specmode = specmode,
                    deconvolver = mydeconvolver,   
                    scales = myscales,             
                    #nterms = 1,                    # needed by sdint for mtmfs
                    start = start, 
                    width = width, 
                    nchan = nchan, 
                    restfreq = restfreq,
                    gridder = 'mosaic',
                    weighting = 'briggs',
                    robust = 0.5,
                    restoringbeam = 'common',   # SD-cube has only one beam - INT-cube needs it, too, else feather etc. fail
                    niter = niter,
                    #cycleniter = niter,        # bogus if = niter
                    cyclefactor=2.0,
                    threshold = threshold,
                    interactive = interactive,
                    pbcor = True,
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
                    pbmask=pbmask,    # used by all usemasks! perhaps needed for fastnoise-calc!
                    verbose=True, 
                    restart=restart)  # should switch off bc default



    #if os.path.exists(imname+'.TCLEAN.image'):
    #    casalog.post('Image '+imname+'.TCLEAN already exists.  Running with restart='+str(restart), 'WARN')        
    ##os.system('rm -rf '+imname+'.TCLEAN.*')

    if continueclean == False:
        os.system('rm -rf '+imname+'.*') #+'.TCLEAN.*')   
        # if to be switched off add command to delete "*.pbcor.fits"
    
    tclean(**tclean_arg)
    
   

    print('Exporting final pbcor image to FITS ...')
    #exportfits(imname+'.TCLEAN.image.pbcor', imname+'.TCLEAN.pbcor.fits')
    exportfits(imname+'.image.pbcor', imname+'.image.pbcor.fits')


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
    if (not os.path.exists(vis)):
        print("Dataset not found")
        return
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
            print(msg[i])
        elif (search == ''): # origin is set
            if (origins[i]==origin):
                print(msg[i])
        else: # search is set
            for search in searches:
                if msg[i].find(search)>=0:
                    if origin == '' or origin == origins[i]:
                        print(msg[i])
                        return msg[i].split(' ')     # added
                        break
    if search != '':
        print("Searched %d messages" % (len(msg)))
        
        
        
        
        





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

    #print('startchan', startchan, 'endchan', endchan)
    if startchan==None or endchan==None:
        print('No channel cutout requested...')
    elif startchan!=None and endchan!=None: 
        print('Reduce channel range to '+str(startchan)+'-'+str(endchan))   
        os.system('rm -rf '+new_image)
        
        immath(imagename=old_image,
               expr='IM0', chans=str(startchan)+'~'+str(endchan),
               outfile=new_image) 
            
        width   = imhead(imagename = old_image, 
                         mode='get', hdkey='cdelt4')['value']
        ref_old = imhead(imagename = old_image, 
                         mode='get', hdkey='crval4')['value'] 
        ref_new = ref_old + startchan*width  
        
        imhead(imagename = new_image, 
               mode='put', hdkey='crval4', hdvalue=str(ref_new))
        
        #if perplanebeams, then smooth
        check_beam=imhead(new_image, mode='summary')
        if 'perplanebeams' in check_beam.keys():
            imsmooth(imagename = new_image,
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


    imregrid(imagename=old_image,
                     template=template_image,
                     axes=[0,1,2,3],
                     output=new_image)  


    #if perplanebeams, then smooth
    check_beam=imhead(new_image, mode='summary')
    if 'perplanebeams' in check_beam.keys():
        imsmooth(imagename = new_image,
            kernel    = 'commonbeam',                                                     
            outfile   = new_image+'_1',            
            overwrite = True)       
                    
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

    os.system('rm -rf '+reordered_image)
    imtrans(imagename=to_reorder,
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
            imtrans(imagename=to_reorder,outfile=reordered_image,order=order)
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

def make_SDint_mask(vis, SDimage, imname, sdmasklev, SDint_mask_root, 
                    phasecenter='', spw='', field='', imsize=[], cell='',
                    specmode='mfs', 
                    start = 0, width = 1, nchan = -1, restfreq = ''):

    """
    make_SDint_mask (A. Plunkett, L. Moser-Fischer)
    a tool to generate a mask from an SD image and the first auto-masking 
    step in tclean of an interferometric image

    steps:
    - create mask from SD image at a user given fraction of the peak flux
    - call 'runtclean' with relevant inputs to create the wanted grid/raster 
       and niter=1 to load the SD mask into a clean mask
    - rerun 'runtclean' with same parameters except from usemask='auto-multithresh', mask=''
       to add the auto-detected compact emission regions (smoothed out in SD image) 
       to the existing clean mask
    - rename clean mask to wanted output name (root)



    vis - the MS containing the interferometric data
    sdimage - the Single Dish image
             Note that in case you are creating a cube, this image must be a cube
             with the same spectral grid as the one you are trying to create.
    imname - the root name of the output images
    sdmasklev - if usemask='user', then use SD image at this level to draw a mask.
             typically: 0.3
    SDint_mask_root - the root name of the output mask, extention '.mask' will 
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
           default: 'msf'
    start - the standard tclean start parameter
             default: 0
    width - the standard tclean width parameter
             default: 1
    nchan - the standard tclean nchan parameter
             default: -1
    restfreq - the restfrequency to write to the image for velocity calculations
             default: '', example: '115.271GHz'

       
    Example: make_SDint_mask('gmc_120L.alma.all_int-weighted.ms',
                'gmc_120L.sd.image', 'gmc_120L.get_mask', 0.3, 'INT-SD', 
                phasecenter='J2000 12:00:00 -35.00.00.0000', 
                spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec', 
                specmode='cube', start= '1550km/s', width= '5km/s', 
                nchan= 10, restfreq = '115.271202GHz')                    
                    
    """

    

    casalog.post("Generating a mask based on SD image", 'INFO', 
                 origin='make_SDint_mask')
    #get max in SD image
    maxSD = imstat(SDimage)['max'][0]
    #sdmasklev=sdmasklev
    sdmaskval = sdmasklev*maxSD
    
    SDoutname1 = SDint_mask_root + '_pre1.mask'
    SDoutname2 = SDint_mask_root + '_pre2.mask'
    finalSDoutname = SDint_mask_root + '.mask'
    
    os.system('rm -rf '+SDint_mask_root + '*mask')     
    #try: 
    immath(imagename=[SDimage],expr='iif(IM0>'+str(round(sdmaskval,6))+',1,0)',
           outfile=SDoutname1)
    #except: print('### SD.mask already exists, will proceed')

    print('')
    print('### Creating a mask based on SD mask and auto-mask')
    print('### Step 1 of 2: load the SD mask into interferometric tclean image data' )
    print('### Please check the result!')
    os.system('rm -rf '+imname+'*')        
    
    runtclean(vis,imname, 
            phasecenter=phasecenter, 
            spw=spw, field=field, imsize=imsize, cell=cell, specmode=specmode,
            start = start, width = width, nchan = nchan, restfreq = restfreq,
            niter=1,usemask='user',mask=SDoutname1,restart=True,interactive=False, continueclean=True)
    print('### Step 2 of 2: add first auto-masking guess of bright emission regions (interferometric!) to the SD mask')
    print('### Please check the result!')        
    os.system('cp -r '+imname+'.mask '+SDoutname2)
    os.system('rm -rf '+imname+'.image.pbcor.fits')        
    runtclean(vis,imname,
            phasecenter=phasecenter, 
            spw=spw, field=field, imsize=imsize, cell=cell, specmode=specmode,
            start = start, width = width, nchan = nchan, restfreq = restfreq,
            niter=1,usemask='auto-multithresh',mask='',restart=True,interactive=False, continueclean=True)
    os.system('cp -r '+imname+'.mask '+finalSDoutname)
    
    #print('### Creating a mask based on SD mask and auto-mask')
    #print('### Step 2 of 2: first auto-masking guess of bright emission regions (interferometric!) to the SD mask')
    #print('### Please check the result!')
    #runtclean(myvis,imname+'_setmask', phasecenter=phasecenter, 
    #        spw=spw, field=field, imsize=imsize, cell=cell,
    #        niter=1,usemask='auto-multithresh',mask='',restart=True,interactive=False, continueclean=True)
    #os.system('cp -rf '+imname+'_setmask.mask int-AM0.mask')
    #os.system('rm -rf '+imname+'_setmask.pbcor.fits')                 
    #print('### Step 1 of 2: load the SD mask into interferometric tclean image data' )
    #print('### Please check the result!')                  
    #runtclean(myvis,imname+'_setmask',
    #        phasecenter=phasecenter, 
    #        spw=spw, field=field, imsize=imsize, cell=cell,
    #        niter=1,usemask='user',mask='SD.mask',restart=True,interactive=False, continueclean=True)
    #os.system('cp -rf '+imname+'_setmask.mask SDint.mask')
    
    print('### Done! Created an SDint mask from SD and auto-mask')                
    mask=finalSDoutname  
    #mask='SD.mask'  

    return mask 





######################################

def derive_threshold(vis, imname, threshmask,
                    phasecenter='', spw='', field='', imsize=[], cell='',
                    specmode='mfs', 
                    start = 0, width = 1, nchan = -1, restfreq = '', 
                    overwrite=False, smoothing = 5, 
                    RMSfactor = 0.5, cube_rms = 3.,   
                    cont_chans ='2~4'):

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
                threshold values from existing template INT image
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

    

    casalog.post("derive_threshold", 'INFO', 
                 origin='derive_threshold')

    imnameth = imname #+'_template'



    if overwrite == True:      # False if used by a combi method to get threshold

        os.system('rm -rf '+imnameth+'*')        
        
        runtclean(vis,imnameth, 
                phasecenter=phasecenter, 
                spw=spw, field=field, imsize=imsize, cell=cell, specmode=specmode,
                start = start, width = width, nchan = nchan, restfreq = restfreq,
                niter=0, interactive=False)
        #print('### Step 2 of 2: add first auto-masking guess of bright emission regions (interferometric!) to the SD mask')
        #print('### Please check the result!') 
    else: 
        pass        

    #### get threshold 

    if not os.path.exists(threshmask + '.mask') and overwrite == False:
        print('please, execute this function with overwrite = True!')
        thresh = 0.0
    else:       
        #### continuum
        if specmode == 'mfs':
            full_RMS = imstat(imnameth+'.image')['rms'][0]
            #peak_val = imstat(imnameth+'.image')['max'][0]
            thresh = full_RMS*RMSfactor
        
        
        #### cube
        elif specmode == 'cube':
            os.system('rm -rf '+imnameth+'.mom6')
            immoments(imagename=imnameth+'.image', moments=[6], 
                       outfile=imnameth+'.mom6', chans=cont_chans)
            cube_RMS = imstat(imnameth+'.mom6')['rms'][0]
        
            thresh = cube_RMS*cube_rms   # 3 sigma level
        
            #immmoments(imagename=imname+'_template.image', mom=[8], 
            #           outfile=imname+'_template.mom8', chans='' )
            #peak_val = imstat(imname+'_template.mom8')['max'][0]
        
        #print(full_RMS)
        #print(peak_val)
        
        
        threshmask1 = threshmask+'_1.mask'
        os.system('rm -rf '+threshmask+'*.mask')     
        
        immath(imagename=[imnameth+'.image'],
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
 
        BeamMaj = imhead(imnameth+'.image', mode='get', hdkey='bmaj')['value']
        BeamMin = imhead(imnameth+'.image', mode='get', hdkey='bmin')['value']
        BeamPA  = imhead(imnameth+'.image', mode='get', hdkey='bpa' )['value']
 
 
        
        imsmooth(imagename = threshmask1,
            kernel    = 'gauss',               
            targetres = False,                                                             
            major     = str(convfactor*round(BeamMaj, 6))+'arcsec',                                                     
            minor     = str(convfactor*round(BeamMin, 6))+'arcsec',    
            pa        = str(round(BeamPA, 3))+'deg',                                       
            outfile   = threshmaskconv,            
            overwrite = True)                 
        
        immath(imagename=[threshmaskconv],
               expr='iif(IM0>'+str(0.2)+',1,0)',  # cut-off value is arbitrary!
               outfile=threshmask+'.mask')
        
        
    return thresh
 




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
    combined - output image name 
    sdfactor - scaling factor for the SD/TP contribution

    Example: ssc(highres='INT.image', lowres='SD.image', pb='INT.pb',
                 combined='INT_SD_1.7.image', sdfactor=1.7)

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


    if os.path.exists(lowres):
        pass
    else:
        print(lowres+' does not exist')
        return False

    if os.path.exists(highres):
        pass
    else:
        print(highres+' does not exist')
        return False

    os.system('rm -rf lowres.*')


    # Reorder the axes of the low to match high/pb 
    #lowres = reorder_axes(highres,lowres,'lowres.ro')
    lowres = reorder_axes(lowres,'lowres.ro')

    # Regrid low res Image to match high res image
    lowres_regrid1 = 'lowres.regrid'
    
    print('Regridding lowres image...')
    imregrid(imagename=lowres,
                     template=highres,
                     axes=[0,1,2,3],
                     output=lowres_regrid1)
                     
    lowres_unit = imhead(lowres_regrid1, mode='get', hdkey='Bunit')['value']

    # Multiply the lowres image with the highres primary beam response
    print('Multiplying lowres by the highres pb...')
    immath(imagename=[lowres_regrid1, pb],
                 expr='IM0*IM1',
                 outfile='lowres.multiplied')

    lowres_regrid = 'lowres.multiplied'

    imhead(lowres_regrid, mode='put', hdkey='Bunit', hdvalue=lowres_unit)


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
    sub = 'sub.im'
    sub_bc = 'sub_bc.im'
    combined = combined + '.image'

    #os.system('rm -rf '+highres_conv)
    os.system('rm -rf '+sub)
    os.system('rm -rf '+sub_bc)
    
    print('Computing the obtained flux only by single-dish ...')
    immath([lowres_regrid, highres_conv], 'evalexpr', sub, '%s*IM0-IM1' % sdfactor)
    print('Flux difference has been determined' + '\n')
    print('Units', getBunit(lowres_regrid))
    print(lowres_regrid)


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
    os.system('rm -rf lowres.*')
    #os.system('rm -rf lowres.regrid')
    #os.system('rm -rf lowres.multiplied')
    os.system('rm -rf '+highres_conv)
    os.system('rm -rf '+sub)
    os.system('rm -rf '+sub_bc)
    #os.system('rm -rf '+combined)
    #os.system('rm -rf '+combined+'.pbcor')
    
    return True

