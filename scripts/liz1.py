# N346 (PI: cagliozzo) debugging by Peter based on Liz' code snippets
#
# This script needs to increase the max # open files
#   unless you use casa 5.4 w/ pipeline which doesn't limit the # open files!
#

QAC.maxofiles(8000)      

npoint      = 1345
phasecenter = 'J2000 00h59m05.089680s -72d10m33.24000s'
phasecenter = 'J2000 14.875deg -72.175deg'

# imstat() doesn't seem to find a good robust value, NEMO found robust rms=0.35
rms_v  = 0.5
rms_v  = 0.35

Qnew   = True      # make a new "all.ms" for tclean
Qsmall = True      # use mstransform() to cut down 7m MS 

#         make a new all.ms
if Qnew:
    if False:
        # this is not correct, these are the 7m pointings
        p = qac_ms_ptg('region3by3-7M-leiden-avg.ms','12m.ptg')
    else:
        # PB is 25", you can also use the OT to create these
        p = qac_im_ptg(phasecenter, 640, 1.4, 15.0, outfile='12m.ptg')
        print("Found %d pointings for 12m.ptg" % len(p))


    if True:
        # this will use all 1345 pointings !!!
        tp2vis('new.cube.spw23-forLeiden.image','new.cube.spw23-forLeiden.image.ms','12m.ptg',rms=rms_v)
    else:
        # use fewer to test if the crash is due to too many fields/pointings
        p1 = p[:npoint]
        tp2vis('new.cube.spw23-forLeiden.image','new.cube.spw23-forLeiden.image.ms',p1,rms=rms_v)

    tp2viswt('new.cube.spw23-forLeiden.image.ms',mode='multiply',value=100.0)
    tp2vispl(['new.cube.spw23-forLeiden.image.ms','region3by3-7M-leiden-avg.ms'])

    # @todo   it would be useful to mstransform()/.... the region3by3-7M-leiden-avg.ms into an MS that has
    #         has just the things we need.  use split() and mstransform() as Yusuke.Miyamoto was showing
    #         on slack

    if Qsmall:
        os.system('rm -rf int.ms')
        mstransform('region3by3-7M-leiden-avg.ms','int.ms',intent='OBSERVE_TARGET#ON_SOURCE',datacolumn='DATA',
                width='3.333MHz',start='230.405GHz',nchan=7,outframe='LSRK')
        concat(vis=['int.ms','new.cube.spw23-forLeiden.image.ms'], concatvis='all.ms',copypointing=False)        
    else:
        concat(vis=['region3by3-7M-leiden-avg.ms','new.cube.spw23-forLeiden.image.ms'], concatvis='all.ms',copypointing=False)

field = '0~4499'          # fails
field = '0~1345'          # this still includes calibrators.
field = '0~%d' % npoint   # ok

niter = 100
niter = 1000
niter = 0

vis = 'all.ms'

if Qsmall:
    tclean(vis     = vis,
       imagename   = 'all_tp2vis.image',
       phasecenter = 3, #00:59:05.089680 -72.10.33.24000 ICRS
       stokes      = 'I',
       spw         = '0',
       outframe    = 'LSRK',
       restfreq    = '230.538GHz', # CO 2-1 lab rest freq
       specmode    = 'cube',
       imsize      = [640, 640], # 3500 arcsec x 2000 arcsec
       cell        = '1.4arcsec',
       deconvolver = 'hogbom',
       niter       = niter, 
       weighting   = 'briggs',
       robust      = 0.5,
       mask        = '',
       gridder     = 'mosaic',
       pbcor       = True,
       threshold   = '0.02Jy',
       width       = '3.333MHz',
       start       = '230.405GHz', 
       nchan       = 7, 
       interactive = False
)

else:    
    tclean(vis     = vis,
       imagename   = 'all_tp2vis.image',
       field       = field,
       intent      = 'OBSERVE_TARGET#ON_SOURCE',
       phasecenter = 3, #00:59:05.089680 -72.10.33.24000 ICRS
       stokes      = 'I',
       spw         = '0',
       outframe    = 'LSRK',
       restfreq    = '230.538GHz', # CO 2-1 lab rest freq
       specmode    = 'cube',
       imsize      = [640, 640], # 3500 arcsec x 2000 arcsec
       cell        = '1.4arcsec',
       deconvolver = 'hogbom',
       niter       = niter, 
       weighting   = 'briggs',
       robust      = 0.5,
       mask        = '',
       gridder     = 'mosaic',
       pbcor       = True,
       threshold   = '0.02Jy',
       width       = '3.333MHz',
       start       = '230.405GHz', 
       nchan       = 7, 
       interactive = False
)
r1 = '0.095995184200857689 1.0827211000573629 -2.4620685577392578 66.1041259765625 4570.3938711809815'
r2 = '0.0028744969513174725 0.1406321131276867 -1.7121779918670654 12.494058609008789 1097.1842429399035'    # mstransform ms
r3 = '0.0022433360673437003 0.13838568018644276 -2.0782339572906494 12.23820972442627 856.27231427154209'    # full ms

qac_stats('new.cube.spw23-forLeiden.image',r1)
qac_stats('all_tp2vis.image.image.pbcor',r2)
qac_stats('all_tp2vis.image.image.pbcor',r3)
