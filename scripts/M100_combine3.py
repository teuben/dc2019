# SDINT example - needs to have run M100_combine2 and M100_combine4 before

# Timing:
#     7m combination takes about 26min
#  12+7m combination takes about 18min
#

use12m = True

#-- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)



pdir = 'M100qac'

ms1     = '../M100_aver_7.ms'              # from qac_bench5
ms2     = '../M100_aver_12.ms'             # from qac_bench5
ms3     = 'M100_combine_CO.ms'             # from running M100_combine2
sdimage = '../M100_TP_CO_cube.bl.image'    # from qac_bench5
sdpsf   = 'test6/tp0/clean0/dirtymap.psf'  # from running M100_combine4

if use12m:
    # 12+7m
    vis = ms3
else:
    # just 7m
    vis = ms1

os.chdir("M100qac")    

QAC.assertf(ms1)    
QAC.assertf(ms2)    
QAC.assertf(ms3)    
QAC.assertf(sdimage)
QAC.assertf(sdpsf)


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
if use12m:
    jointname = 'M100sdint_12'
else:
    jointname = 'M100sdint_7'    

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



