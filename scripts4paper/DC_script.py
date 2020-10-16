"""
Script to use the datacomb module

Based on the work at the Workshop
"Improving Image Fidelity on Astronomical Data", 
Lorentz Center, Leiden, August 2019, 
and subsequent follow-up work. 

Run under CASA 6.

"""





import sys 
sys.path.append('/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/dc2019/scripts4paper/')

import datacomb as dc



pathtoconcat = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/ToshiSim/gmcSkymodel_120L/gmc_120L/'   # path to the folder with the files to be concatenated

pathtoimage = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/DC_Ly_tests/'   # path to the folder where to put the combination and image results

concatms  = pathtoimage + 'skymodel-b_120L.alma.all_int-weighted.ms'       # path and name of concatenated file


TPimage      = pathtoconcat + 'gmc_120L.sd.image'

imname = pathtoimage + 'skymodel-b_120L'                                   # image base name





# general clean parameters:

tclean_param = dict(
    vis=[concatms], 
    overwrite=overwrite,
    phasecenter=model_refdir, mode='channel',
    nchan=model_nchan, start=0, width=1)

vis, 
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
                
threshold='', # SDINT: None 

interactive=True, 
                
multiscale=False, 
maxscale=0.



### tclean specific 

startmodel='',  # ---> sdimage in WSM





### runtclean/WSM specific
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







#### WSM specific
 
sdimage,  ### startmodel 



# SDint specific

sdimage, 
jointname, ### = imname 

sdpsf='',
sdgain=5, 
dishdia=12.0,









tclean_param['gridfunction'] = 'SF'
runtclean(**tclean_param)                    
                                                      
# feather parameters:


# Faridani parameters:


# Hybrid feather paramteters:


# SDINT parameters:





# methods for combining agg. bandwidth image with TP image - cube not yet tested/provided








thesteps = []
step_title = {0: 'Concat',
              1: 'Clean for Feather/Faridani'
              1: 'Feather', 
              2: 'Faridani',
              3: 'Hybrid (startmodel clean + Feather)',
              4: 'SDINT',
              5: 'TP2VIS'}


mystep = 0
if(mystep in thesteps):
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    print('Step ', mystep, step_title[mystep])
    
    thevis = [pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-02.ms',
              pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-02.ms',
              pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-03.ms',
              pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-03.ms',
              pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-04.ms',
              pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-04.ms',
              pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-05.ms',
              pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-05.ms',
              pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-20.ms',
              pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-21.ms',
              pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-22.ms',
              pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-23.ms']
    
    weightscale = [1., 1., 1., 1., 1., 1., 1., 1.,
                   0.116, 0.116, 0.116, 0.116]
    
    concat(vis = thevis, 
           concatvis = concatms,
           visweightscale = weightscale)





mystep = 1
if(mystep in thesteps):
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    print('Step ', mystep, step_title[mystep])

    runtclean(vis, imname, startmodel='',spw='', field='', specmode='mfs', 
                imsize=[], cell='', phasecenter='',
                start=0, width=1, nchan=-1, restfreq=None,
                threshold='', niter=0, usemask='auto-multithresh' ,
                sidelobethreshold=2.0, noisethreshold=4.25, lownoisethreshold=1.5, 
                minbeamfrac=0.3, growiterations=75, negativethreshold=0.0,
                mask='', pbmask=0.4, interactive=True, 
                multiscale=False, maxscale=0.)




mystep = 2
if(mystep in thesteps):
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    print('Step ', mystep, step_title[mystep])



    runfeather(intimage,intpb, sdimage, featherim='featherim'):




#mystep = 3
#if(mystep in thesteps):
#    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
#    print('Step ', mystep, step_title[mystep])
#



mystep = 4
if(mystep in thesteps):
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    print('Step ', mystep, step_title[mystep])

    runWSM(vis, sdimage, imname, spw='', field='', specmode='mfs', 
                imsize=[], cell='', phasecenter='',
                start=0, width=1, nchan=-1, restfreq=None,
                threshold='',niter=0,usemask='auto-multithresh' ,
                sidelobethreshold=2.0,noisethreshold=4.25,lownoisethreshold=1.5, 
                minbeamfrac=0.3,growiterations=75,negativethreshold=0.0,
                mask='', pbmask=0.4,interactive=True, 
                multiscale=False, maxscale=0.)

mystep = 5
if(mystep in thesteps):
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    print('Step ', mystep, step_title[mystep])

    runsdintimg(vis, sdimage, jointname, spw='', field='', specmode='mfs', sdpsf='',
                threshold=None, sdgain=5, imsize=[], cell='', phasecenter='', dishdia=12.0,
                start=0, width=1, nchan=-1, restfreq=None, interactive=True, 
                multiscale=False, maxscale=0.)
#mystep = 5
#if(mystep in thesteps):
#    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
#    print('Step ', mystep, step_title[mystep])




















sdint default




    +usedata                 = 'sdint'                 # Output image type(int, sd, sdint)
    +   sdimage              = ''                      # Input single dish image
    +   sdpsf                = ''                      # Input single dish PSF image
    +   sdgain               = 1.0                     # A factor or gain to adjust single dish flux scale
    +   dishdia              = 100.0                   # Effective dish diameter
    +vis                     = ''                      # Name of input visibility file(s)
selectdata              = True                    # Enable data selection parameters
   field                = ''                      # field(s) to select
       +spw                  = ''                      # spw(s)/channels to select
   timerange            = ''                      # Range of time to select from data
   uvrange              = ''                      # Select data within uvrange
   antenna              = ''                      # Select data based on antenna/baseline
   scan                 = ''                      # Scan number range
   observation          = ''                      # Observation ID range
   intent               = ''                      # Scan Intent(s)
datacolumn              = 'corrected'             # Data column to image(data,corrected)
    +imagename               = ''                      # Pre-name of output images
    +imsize                  = []                      # Number of pixels
    +cell                    = []                      # Cell size
    +phasecenter             = ''                      # Phase center of the image
stokes                  = 'I'                     # Stokes Planes to make
projection              = 'SIN'                   # Coordinate projection
startmodel              = ''                      # Name of starting model image
    +specmode                = 'mfs'                   # Spectral definition mode (mfs,cube,cubedata, cubesource)
    +   reffreq              = ''                      # Reference frequency
nchan                   = -1                      # Number of channels in the output image
start                   = ''                      # First channel (e.g. start=3,start='1.1GHz',start='15343km/s')
width                   = ''                      # Channel width (e.g. width=2,width='0.1MHz',width='10km/s')
outframe                = 'LSRK'                  # Spectral reference frame in which to interpret 'start' and 'width'
veltype                 = 'radio'                 # Velocity type (radio, z, ratio, beta, gamma, optical)
restfreq                = []                      # List of rest frequencies
interpolation           = 'linear'                # Spectral interpolation (nearest,linear,cubic)
chanchunks              = 1                       # Number of channel chunks
perchanweightdensity    = True                    # whether to calculate weight density per channel in Briggs style
                                                  # weighting or not
gridder                 = 'standard'              # Gridding options (standard, wproject, widefield, mosaic, awproject)
   vptable              = ''                      # Name of Voltage Pattern table
   pblimit              = 0.2                     # PB gain level at which to cut off normalizations
deconvolver             = 'hogbom'                # Minor cycle algorithm
                                                  # (hogbom,clark,multiscale,mtmfs,mem,clarkstokes)
restoration             = True                    # Do restoration steps (or not)
   restoringbeam        = []                      # Restoring beam shape to use. Default is the PSF main lobe
   pbcor                = False                   # Apply PB correction on the output restored image
    +weighting               = 'natural'               # Weighting scheme (natural,uniform,briggs, briggsabs[experimental])
   uvtaper              = []                      # uv-taper on outer baselines in uv-plane
niter                   = 0                       # Maximum number of iterations
usemask                 = 'user'                  # Type of mask(s) for deconvolution: user, pb, or auto-multithresh
   mask                 = ''                      # Mask (a list of image name(s) or region file(s) or region string(s)
                                                  # )
   pbmask               = 0.0                     # primary beam mask
fastnoise               = True                    # True: use the faster (old) noise calculation. False: use the new
                                                  # improved noise calculations
restart                 = True                    # True : Re-use existing images. False : Increment imagename
savemodel               = 'none'                  # Options to save model visibilities (none, virtual, modelcolumn)
calcres                 = True                    # Calculate initial residual image
calcpsf                 = True                    # Calculate PSF
parallel                = False                   # Run major cycles in parallel



runsdintimg(
vis, 
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
interactive=True, 
multiscale=False, 
maxscale=0.)
                
                
       sdintimaging( °vis=myvis,
                     °sdimage=mysdimage,
                     °sdpsf=mysdpsf,
                     °dishdia=dishdia,
                     °sdgain=sdgain,
                     usedata='sdint',
                     °imagename=jointname,
                     °imsize=imsize,
                     °cell=cell,
                     °phasecenter=phasecenter,
                     weighting='briggs',
                     robust = 0.5,
                     °specmode=specmode,
                     gridder=mygridder,
                     pblimit=0.2, 
                     pbcor=True,
                     interpolation='linear',
                     wprojplanes=1,
                     °deconvolver=mydeconvolver,
                     scales=myscales,
                     nterms=1,
                     niter=10000000,
                     °spw=spw,
                     °start=start,
                     °width=width,
                     °nchan = numchan, 
                     °field = field,
                     °threshold=threshold,
                     °restfreq=therf,
                     perchanweightdensity=False,
                     °*#interactive=True,
                     *#cycleniter=100,
                     *#usemask='pb',
                     #pbmask=0.4,
                 )

        sdintimaging(vis=myvis,
                     sdimage=mysdimage,
                     sdpsf=mysdpsf,
                     dishdia=dishdia,
                     sdgain=sdgain,
                     usedata='sdint',
                     *#imagename=jointname,
                     imsize=imsize,
                     cell=cell,
                     phasecenter=phasecenter,
                     weighting='briggs',
                     robust = 0.5,
                     specmode=specmode,
                     *#gridder=mygridder, # mosaic
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
                     *#interactive=False,
                     *#cycleniter = 100000, 
                     #cyclefactor=2.0,
                     *#usemask='auto-multithresh',
                     #sidelobethreshold=2.0,
                     #noisethreshold=4.25,
                     #lownoisethreshold=1.5, 
                     #minbeamfrac=0.3,
                     #growiterations=75,
                     #negativethreshold=0.0
                 )




    tclean(°vis = myvis,
         °*#imagename = imname+'.TCLEAN',
         °#startmodel = startmodel,
         °field = field,
         #intent = 'OBSERVE_TARGET#ON_SOURCE',
         °phasecenter = phasecenter,
         #stokes = 'I',
         spw = spw,
         #outframe = 'LSRK',             # DEFAULT
         °specmode = specmode,
         nterms = 1,
         °imsize = imsize,
         °cell = cell,
         deconvolver = mydeconvolver,
         scales = myscales,
         °*#niter = niter,
         *#cycleniter = niter,
         *#cyclefactor=2.0,
         weighting = 'briggs',
         robust = 0.5,
         *#gridder = 'mosaic',
         pbcor = True,
         °threshold = threshold,
         °*#interactive = interactive,
         ++++# Masking Parameters below this line 
         ++++# --> Should be updated depending on dataset
         °*#usemask=mymask,
         *#sidelobethreshold=sidelobethreshold,
         *#noisethreshold=noisethreshold,
         *#lownoisethreshold=lownoisethreshold, 
         *#minbeamfrac=minbeamfrac,
         *#growiterations=growiterations,
         *#negativethreshold=negativethreshold,
         °mask=mask,
         °*#pbmask=pbmask,
         verbose=True
         )
                °start=0, width=1, nchan=-1, restfreq=None,
                °multiscale=False, maxscale=0.):


