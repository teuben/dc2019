# runsdintimg.py
# D. Petry (ESO), Aug 2020
# - a wrapper around sdintimaging
# - run with CASA 5.7/6.1 or later


import os

def runsdintimg(vis, sdimage, jointname, spw='', field='', specmode='mfs', sdpsf='', 
                sdgain=5, imsize=[], cell='', phasecenter='', dishdia=12.0):

    """
    runsdintimg
    a wrapper around sdintimaging, D. Petry (ESO)
    
    vis - the MS containing the interferometric data
    sdimage - the Single Dish image
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
    sdgain - the weight of the SD data relative to the interferometric data
           default: 5 
             'auto' - determine the scale automatically (experimental)
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
    dishdia - in metres, (optional) used if no sdpsf is provided
           default: 12.0

    Example: runsdintimg('gmc_120L.alma.all_int-weighted.ms','gmc_120L.sd.image', 
                'gmc_120L.joint-sdgain2.5', phasecenter='J2000 12:00:00 -35.00.00.0000', 
                 sdgain=2.5, spw='0', field='0~68', imsize=[1120,1120], cell='0.21arcsec')

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

    myhead = imhead(mysdimage)
    myaxes = list(myhead['axisnames'])
    numchan = myhead['shape'][myaxes.index('Frequency')] 
            
    print('Testing whether the sd image has per channel beams ...')
    ia.open(mysdimage)
    try:
        mybeam = ia.restoringbeam()
    except:
        ia.close()
        casalog.post('ERROR: sdimage does not contain beam information.', 'SEVERE', 
                     origin='runsdintimg')
        return False

    haspcb=False
    if 'beams' in mybeam.keys():
        haspcb=True
        casalog.post("The sdimage has a per channel beam.", 'INFO', 
                     origin='runsdintimg')

    ia.close()


    if not haspcb:
        os.system('rm -rf copy_of_'+mysdimage)
        os.system('cp -R '+mysdimage+' copy_of_'+mysdimage)
        if numchan == 1:
            # image has only one channel; need workaround for per-channel-beam problem
            ia.open('copy_of_'+mysdimage)
            mycoords = ia.coordsys().torecord()
            mycoords['spectral2']['wcs']['crval'] += mycoords['spectral2']['wcs']['cdelt']
            ia.setcoordsys(mycoords)
            ia.close()
            tmpia = ia.imageconcat(outfile='mod_'+mysdimage, infiles=[mysdimage, 'copy_of_'+mysdimage], 
                                   axis=3, overwrite=True)
            tmpia.close()
            mysdimage = 'mod_'+mysdimage
            numchan = 2

        ia.open(mysdimage)
        ia.setrestoringbeam(remove=True)
        for i in range(numchan):
            ia.setrestoringbeam(beam=mybeam, log=True, channel=i, polarization=0) 
        ia.close()

        casalog.post('Needed to give the sdimage a per-channel beam. Modifed image is in '+mysdimage, 'WARN', 
                     origin='runsdintimg')

    # specmode and deconvolver
    if specmode == 'mfs':
        mydeconvolver = 'mtmfs'
    elif specmode == 'cube':
        mydeconvolver = 'hogbom'

    scales = [0]

    mygridder='mosaic'

    # image and cell size
    npnt = 0
    if imsize==[] or cell=='':
        try:
            import analysisUtils as aU
        except:
            casalog.post('Cannot import the analysisUtils. Set up your sys.path or provide imsize and cell.', 'SEVERE', 
                     origin='runsdintimg')
            return False

        cell, imsize, npnt = aU.pickCellSize(myvis, spw=spw, imsize=True, cellstring=True) 

    if phasecenter=='':
        phasecenter = npnt

    mythresh='1mJy' # dummy value
    mask=''

    os.system('rm -rf '+jointname+'.*')

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
                 interpolation='linear',
                 wprojplanes=1,
                 deconvolver=mydeconvolver,
                 scales=scales,
                 nterms=1,
                 pbmask=0.2,
                 niter=10000000,
                 spw=spw,
                 nchan = numchan, 
                 field = field,
                 cycleniter=100,
                 threshold=mythresh,
                 perchanweightdensity=False,
                 interactive=True,
                 mask=mask)

    return True


