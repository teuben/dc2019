# SDINT example:

# First we combine the 7m INT with the 12m TP data; we use the benchmark M100 data

# to prepare PSF, run QAC/workflows/workflow6.py first

vis     = 'M100_aver_7.ms'
sdimage = 'M100_TP_CO_cube.bl.image'
sdpsf   = 'test6/tp0/clean0/dirtymap.psf'

deconvolver = 'clark'
specmode    = 'cube'
gridder     = 'mosaic'

phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'
imsize      = 800
cell        = '0.5arcsec'
reffreq     = '115GHz'
dishdia     = 10.0 # in meters
niter       = 10000
cycleniter  = 500
#scales      = [0,12,20,40,60,80,100]
scales      = [0,5,20]
pblimit     = 0.2
mythresh    = '.050mJy'
mask        = 'M100.im.masklist'  ## region file, or mask image with 1,0.

#Joint reconstruction file name
jointname   = 'tryit'

os.system('rm -rf '+jointname+'*')

jointim = SDINT_imager(vis=vis,
                           
                       sdimage=sdimage,
                       sdpsf=sdpsf,
                       sdgain=1.0,
                       dishdia=dishdia,
                       
                       usedata='sdint',  ## or 'sdonly' or 'intonly'
                           
                       imagename=jointname,
                       imsize=imsize,
                       cell=cell,
                       phasecenter=phasecenter,
                       weighting='natural',
                       specmode=specmode,
                       
                       gridder=gridder,
                       nchan=70,
                       reffreq=reffreq,
                       width='',
                       pblimit=pblimit, 
                       # interpolation='nearest',
                       # wprojplanes=1,
                           
                       deconvolver=deconvolver,
                       scales=scales,
                       # nterms=2,
                       pbmask=0.2,
                           
                       niter=niter,
                       cycleniter=cycleniter,
                       threshold=mythresh,
                       # mask=mask,
)
    

decname = jointim.do_reconstruct()

###################################



