#  -*- python -*-
#
#  Based on M100_combine4.py - but to experiment with different weights and tclean parameters
#
#  Within test6/ the following directories are:
#   test6/tp0/clean0    TP
#   test6/clean3    TP+7m12m   rms weights   (5.584021/GHz)
#
#  CPU: about 3hr per experiment (see below)


# parameters in this workflow
phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'
phasecenter = 'J2000 185.72875deg +15.820833deg'

line = {"restfreq":'115.271202GHz','start':'1400km/s', 'width':'5km/s','nchan':70}
line = {"restfreq":'115.271202GHz','start':'1745km/s', 'width':'-5km/s','nchan':70}

tpim  = '../M100_TP_CO_cube.bl.image'
ms07  = '../M100_aver_7.ms'
ms12  = '../M100_aver_12.ms'

nsize = 800
pixel = 0.5
box1  = '219,148,612,579'       # same box as in workflow6a where we want to compare fluxes (this is for nsize=800, pixel=0.5)
box   = box1
boxlist = QAC.iarray(box)       # convert to an ascii list of ints [219,148,612,579] for qac_plot()

rms = 0.13                      # rms in TP cube

#   wtfacs is a list of scaling factors for tp2viswt() because the rms based weights for M100 seem to large
wtfacs = [0.61]      # _5
wtfacs = [0.25, 0.4] # _6
wtfacs = [1.0]       # _7
wtfacs = [0.18]      # _8
wtfacs = [0.61]      # _9 _10
wtfacs = [1.0, 0.61, 0.40, 0.25, 0.18]   

winpix = 0   # not used yet

niter = [0, 1000, 3000, 10000, 30000, 50000]
niter = [0, 1000]
niter = [0, 1000, 3000, 10000, 1000000, 3000000]                   # about 3hr per weight


#   do the work inside this directory
pdir = 'M100qac'
os.chdir(pdir)
    
#   report
qac_begin("M100")
qac_log("QAC_VERSION")
qac_project('test6a')
qac_version()

#   make sure all the files we need are here
QAC.assertf(tpim)
QAC.assertf(ms07)
QAC.assertf(ms12)

# summary
qac_log("SUMMARY-1")
qac_summary(tpim,[ms12,ms07])

ptg = 'test6a/M100_aver_12.ptg'
if True:
    qac_ms_ptg(ms12,ptg)
else:
    qac_im_ptg(phasecenter,nsize,pixel,30,outfile=ptg)

qac_log("TP2VIS with rms=%g" % rms)       # rms from imstat() on edge channels   [0.13 seems to be a better value]
qac_project('test6a/tp0')
qac_tp_vis('test6a/tp0',tpim,ptg,rms=rms,phasecenter=phasecenter)  
tpms = 'test6a/tp0/tp.ms'

#  some extra parameters for tclean
line['usemask']   = 'pb'
line['pbmask']    = 0.3    # new
line['threshold'] = 0.011  # new   the sigma in the line free channels
line['nsigma']    = 2.0    # new   _9         -> this gave small residuals, no striping
line['nsigma']    = 1.0    # new   for _10    -> this gave striping

for wtfac in wtfacs:
    clean3 = 'clean3_%g' % wtfac
    tp2viswt(tpms,value=rms,mode='rms')
    tp2viswt(tpms,mode='multiply',value=wtfac)

    qac_log("CLEAN %s: TP+7m+12m" % clean3 )
    qac_clean('test6a/%s' % clean3,tpms,[ms12,ms07],nsize,pixel,niter=niter,phasecenter=phasecenter,do_concat=True,do_int=True,**line)
    qac_beam('test6a/%s/tpint.psf'%clean3,plot='test6a/%s/qac_beam.png'%clean3,normalized=True)
    # QAC_BEAM: test2e/tpalma.psf  4.4261 2.94494 0.5 59.0776 59.0776
    # QAC_BEAM: Max/Last/PeakLoc 2.95162277943 2.47391209456 76.0
    qac_stats('test6a/%s/tpint.image.pbcor'%clean3)
    qac_stats('test6a/%s/tpint.image.pbcor'%clean3, box=box)    
    for i in range(1,len(niter)):
        tp2vistweak('test6a/%s/tpint'%clean3,'test6a/%s/tpint_%d' % (clean3,i+1))
        qac_stats('test6a/%s/int_%d.image.pbcor'%(clean3,i+1))
        qac_stats('test6a/%s/tpint_%d.image.pbcor'%(clean3,i+1))
        qac_stats('test6a/%s/tpint_%d.tweak.image.pbcor'%(clean3,i+1))
        qac_stats('test6a/%s/int_%d.image.pbcor'%(clean3,i+1),box=box)
        qac_stats('test6a/%s/tpint_%d.image.pbcor'%(clean3,i+1),box=box)
        qac_stats('test6a/%s/tpint_%d.tweak.image.pbcor'%(clean3,i+1),box=box)


qac_end()
