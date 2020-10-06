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
from casatasks import casalog
from casatasks import exportfits
from casatasks import imhead
from casatasks import sdintimaging
from casatasks import tclean
from casatasks import immath
from casatasks import imregrid, imtrans
from casatasks import feather


from casatools import image as iatool
from casatools import quanta as qatool

##########################################

def runsdintimg(vis, sdimage, jointname, spw='', field='', specmode='mfs', sdpsf='',
                threshold=None, sdgain=5, imsize=[], cell='', phasecenter='', dishdia=12.0,
                start=0, width=1, nchan=-1, restfreq=None, interactive=True, 
                multiscale=False, maxscale=0.):
    """
    runsdintimg (D. Petry, ESO)
    a wrapper around the CASA task "sdintimaging"

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
             Recommended value: half the max. primary beam
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
        os.system('rm -rf copy_of_'+mysdimage)
        os.system('cp -R '+mysdimage+' copy_of_'+mysdimage)
        if numchan == 1:
            # image has only one channel; need workaround for per-channel-beam problem
            myia.open('copy_of_'+mysdimage)
            mycoords = myia.coordsys().torecord()
            mycoords['spectral2']['wcs']['crval'] += mycoords['spectral2']['wcs']['cdelt']
            myia.setcoordsys(mycoords)
            myia.close()
            tmpia = myia.imageconcat(outfile='mod_'+mysdimage, infiles=[mysdimage, 'copy_of_'+mysdimage], 
                                   axis=3, overwrite=True)
            tmpia.close()
            mysdimage = 'mod_'+mysdimage
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
            mydeconvolver = 'mtmfs'
        elif specmode == 'cube':
            mydeconvolver = 'multiscale'
            numchan = nchan
        mycell = myqa.convert(myqa.quantity(cell),'arcsec')['value']
        myscales = [0]
        for i in range(1, int(math.log(maxscale/mycell/3.,2))+1):
            myscales.append(2**i*3.)
        print("My scales (units of pixels): "+str(myscales))
    else:    
        myscales = [0]
        if specmode == 'mfs':
            mydeconvolver = 'mtmfs'
        elif specmode == 'cube':
            mydeconvolver = 'hogbom'
            numchan = nchan


    mygridder='mosaic'

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

    os.system('rm -rf '+jointname+'.*')

    if interactive:

        sdintimaging(vis=myvis,
                     sdimage=mysdimage,
                     sdpsf=mysdpsf,
                     dishdia=dishdia,
                     sdgain=sdgain,
                     usedata='sdint',
                     imagename=jointname,
                     imsize=imsize,
                     cell=cell,
                     phasecenter=phasecenter,
                     weighting='briggs',
                     robust = 0.5,
                     specmode=specmode,
                     gridder=mygridder,
                     pblimit=0.2, 
                     pbcor=True,
                     interpolation='linear',
                     wprojplanes=1,
                     deconvolver=mydeconvolver,
                     scales=myscales,
                     nterms=1,
                     niter=10000000,
                     spw=spw,
                     start=start,
                     width=width,
                     nchan = numchan, 
                     field = field,
                     cycleniter=100,
                     threshold=threshold,
                     restfreq=therf,
                     perchanweightdensity=False,
                     interactive=True,
                     usemask='pb',
                     pbmask=0.4,
                 )
        
    else: # non-interactive, use automasking

        sdintimaging(vis=myvis,
                     sdimage=mysdimage,
                     sdpsf=mysdpsf,
                     dishdia=dishdia,
                     sdgain=sdgain,
                     usedata='sdint',
                     imagename=jointname,
                     imsize=imsize,
                     cell=cell,
                     phasecenter=phasecenter,
                     weighting='briggs',
                     robust = 0.5,
                     specmode=specmode,
                     gridder=mygridder,
                     pblimit=0.2, 
                     pbcor=True,
                     interpolation='linear',
                     wprojplanes=1,
                     deconvolver=mydeconvolver,
                     scales=myscales,
                     nterms=1,
                     niter=10000000,
                     spw=spw,
                     start=start,
                     width=width,
                     nchan = numchan, 
                     field = field,
                     threshold=threshold,
                     restfreq=therf,
                     perchanweightdensity=False,
                     interactive=False,
                     cycleniter = 100000, 
                     cyclefactor=2.0,
                     usemask='auto-multithresh',
                     sidelobethreshold=2.0,
                     noisethreshold=4.25,
                     lownoisethreshold=1.5, 
                     minbeamfrac=0.3,
                     growiterations=75,
                     negativethreshold=0.0
                 )

    print('Exporting final pbcor image to FITS ...')
    if mydeconvolver=='mtmfs':
        exportfits(jointname+'.joint.multiterm.image.tt0.pbcor', jointname+'.joint.multiterm.image.tt0.pbcor.fits')
    elif mydeconvolver=='hogbom':
        exportfits(jointname+'.joint.cube.image.pbcor', jointname+'.joint.cube.image.pbcor.fits')

    return True

##########################################



def runWSM(vis, sdimage, imname, spw='', field='', specmode='mfs', 
                imsize=[], cell='', phasecenter='',
                start=0, width=1, nchan=-1, restfreq=None,
                threshold='',niter=0,usemask='auto-multithresh' ,
                sidelobethreshold=2.0,noisethreshold=4.25,lownoisethreshold=1.5, 
                minbeamfrac=0.3,growiterations=75,negativethreshold=0.0,
                mask='', pbmask=0.4,interactive=True):
    """
    runWSM (A. Plunkett, NRAO)
    a wrapper around the CASA tasks "TCLEAN" and "FEATHER"
    in order to run TCLEAN with a single dish start model, then combine with FEATHER

    vis - the MS containing the interferometric data
    sdimage - the Single Dish image
             Note that in case you are creating a cube, this image must be a cube
             with the same spectral grid as the one you are trying to create.
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
    interactive - the standard tclean interactive option
             default: True
    
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
    scaled_name = mysdimage.split('/')[-1]+'.Jyperpix'

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
  
    ## TCLEAN METHOD WITH START MODEL
    runtclean(myvis,imname, startmodel=scaled_name,
                phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cell,threshold=threshold,
                niter=niter,usemask=usemask,pbmask=pbmask,mask=mask,
                interactive=interactive)

    ## then FEATHER METHOD 
    highres = imname+'.TCLEAN.image'
    pb= imname+'.TCLEAN.pb'
    featherim = imname+'.combined'
    
    runfeather(intimage=highres,intpb=pb,sdimage=sdimage,featherim=featherim)    
    return True

#################################

def runfeather(intimage,intpb, sdimage, featherim='featherim'):
    """
    runtcleanFeather (A. Plunkett, NRAO)
    a wrapper around the CASA task "FEATHER,"

    intimage - the interferometry image
             default: None, example: 'imagename.image'
    intpb - the interferometry primary beam
             default: None, example: 'imagename.pb'
    sdimage - the Single Dish image
             Note that in case you are creating a cube, this image must be a cube
             with the same spectral grid as the one you are trying to create.
             default: None, example: 'TPimage.image'
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
          lowpassfiltersd = True )

    os.system('rm -rf '+featherim+'.image.pbcor')
    immath(imagename=[featherim+'.image',
                      myintpb],
       expr='IM0/IM1',
       outfile=featherim+'.image.pbcor')
    
    print('Exporting final pbcor image to FITS ...')
    exportfits(featherim+'.image.pbcor', featherim+'.image.pbcor.fits')

    return True

######################################
def runtclean(vis, imname, startmodel='',spw='', field='', specmode='mfs', 
                imsize=[], cell='', phasecenter='',
                start=0, width=1, nchan=-1, restfreq=None,
                threshold='',niter=0,usemask='auto-multithresh' ,
                sidelobethreshold=2.0,noisethreshold=4.25,lownoisethreshold=1.5, 
                minbeamfrac=0.3,growiterations=75,negativethreshold=0.0,
                mask='', pbmask=0.4,interactive=True):
    """
    runtclean (A. Plunkett, NRAO)
    a wrapper around the CASA task "TCLEAN,"

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

    mymaskname = ''
    if usemask == 'auto-multithresh':
        mymask = usemask
        print('Run with {0} mask'.format(mymask))
    elif usemask =='pb':
        mymask = usemask
        pbmask = pbmask
        print('Run with {0} mask {1}'.format(mymask,pbmask))
    elif usemask == 'user':
        if os.path.exists(maskname):
           mymask = usemask
           mymaskname = mask
           print('Run with {0} mask {1} '.format(mymask,maskname))
        else:
           print('mask '+maskname+' does not exist, or not specified')
           return False
    else:
        print('check the mask options')
        return False

    os.system('rm -rf '+imname+'.TCLEAN.*')
    tclean(vis = myvis,
         imagename = imname+'.TCLEAN',
         startmodel = startmodel,
         field = field,
         intent = 'OBSERVE_TARGET#ON_SOURCE',
         phasecenter = phasecenter,
         stokes = 'I',
         spw = spw,
         outframe = 'LSRK',
         specmode = specmode,
         nterms = 1,
         imsize = imsize,
         cell = cell,
         deconvolver = 'hogbom',
         niter = niter,
         cycleniter = niter,
         cyclefactor=2.0,
         weighting = 'briggs',
         robust = 0.5,
         gridder = 'mosaic',
         pbcor = True,
         threshold = threshold,
         interactive = interactive,
         # Masking Parameters below this line 
         # --> Should be updated depending on dataset
         usemask=mymask,
         sidelobethreshold=sidelobethreshold,
         noisethreshold=noisethreshold,
         lownoisethreshold=lownoisethreshold, 
         minbeamfrac=minbeamfrac,
         growiterations=growiterations,
         negativethreshold=negativethreshold,
         mask=mask,pbmask=pbmask,
         verbose=True)

    print('Exporting final pbcor image to FITS ...')
    exportfits(imname+'.TCLEAN.image.pbcor', imname+'.TCLEAN.pbcor.fits')

    return True

