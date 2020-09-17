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
from casatasks import casalog
from casatasks import exportfits
from casatasks import imhead
from casatasks import sdintimaging

from casatools import image as iatool

##########################################

def runsdintimg(vis, sdimage, jointname, spw='', field='', specmode='mfs', sdpsf='',
                threshold=None, sdgain=5, imsize=[], cell='', phasecenter='', dishdia=12.0,
                start=0, width=1, nchan=-1, restfreq=None, interactive=True):
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
    if specmode == 'mfs':
        mydeconvolver = 'mtmfs'
    elif specmode == 'cube':
        mydeconvolver = 'hogbom'
        numchan = nchan

    scales = [0]

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
                     scales=scales,
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
                     scales=scales,
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



