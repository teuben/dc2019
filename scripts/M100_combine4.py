#  -*- python -*-
#
#  Based on QAC's workflow6.py
#
#  Within test6/ the following directories are:
#   test6/tp0/clean0    TP
#   test6/tp1/clean0    TP w/ deconv=False
#   test6/tp2/clean0    TP
#   test6/clean1    TP+7m
#   test6/clean2    TP+12m 
#   test6/clean3    TP+7m12m   rms weights   (5.584021/GHz)
#   test6/clean4    -same- but with 10*rms   (55.840208/GHz)
#   test6/clean6    TP+7m12m   beammatch weights   (1.409106/GHz)


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

winpix = 0   # not used yet

#   do the work inside this directory
pdir = 'M100qac'
os.chdir(pdir)
    

#   report
qac_begin("M100")
qac_log("QAC_VERSION")
qac_project('test6')
qac_version()

#   make sure all the files we need are here
QAC.assertf(tpim)
QAC.assertf(ms07)
QAC.assertf(ms12)

# summary
qac_log("SUMMARY-1")
qac_summary(tpim,[ms12,ms07])

ptg = 'test6/M100_aver_12.ptg'
if True:
    qac_ms_ptg(ms12,ptg)
else:
    qac_im_ptg(phasecenter,nsize,pixel,30,outfile=ptg)

qac_log("TP2VIS with rms=0.15")       # rms from imstat() on edge channels   [0.13 seems to be a better value]
qac_project('test6/tp0')
qac_tp_vis('test6/tp0',tpim,ptg,rms=0.15,phasecenter=phasecenter)  
qac_log("TP2VISWT - should show no change; about 0.0107354")
tp2viswt('test6/tp0/tp.ms',value=0.15,mode='rms')
qac_clean1('test6/tp0/clean0','test6/tp0/tp.ms',nsize,pixel,niter=0,phasecenter=phasecenter,**line)


if True:
    psf = ['56.899arcsec', '56.899arcsec', '0deg']
    deconvolve(tpim,'test6/tp.model',psf=psf,alg='clark')
    
    qac_project('test6/tp1')
    qac_tp_vis('test6/tp1','test6/tp.model',ptg,rms=0.15,phasecenter=phasecenter,deconv=False)
    qac_clean1('test6/tp1/clean0','test6/tp1/tp.ms',nsize,pixel,niter=0,phasecenter=phasecenter,**line)

if True:
    is1 = imstat(tpim)
    nppb = is1['sum'][0]/is1['flux'][0]
    print("Scaling Jy/beam map by nppb=%g to fake Jy/pixel" % nppb)
    immath([tpim],'evalexpr','test6/M100_TP_CO_cube.bl.model','IM0/%g' % nppb)
    # imhead('test6/M100_TP_CO_cube.bl.model','put','unit','Jy/pixel')      should file a ticket on this
    imhead('test6/M100_TP_CO_cube.bl.model','put','bunit','Jy/pixel')
    qac_project('test6/tp2')    
    qac_tp_vis('test6/tp2','test6/M100_TP_CO_cube.bl.model',ptg,rms=0.15,phasecenter=phasecenter,deconv=False)
    qac_clean1('test6/tp2/clean0','test6/tp2/tp.ms',nsize,pixel,niter=0,phasecenter=phasecenter,**line)

# decide on which tp.ms we will use (tp1 and tp2 were progressively worse)
tpms = 'test6/tp0/tp.ms'    

if True:
    temp_dict = imregrid(imagename='test6/tp0/clean0/dirtymap.image', template="get")
    imregrid(imagename=tpim,output='test6/M100_TP_CO_cube.bl.smo',template=temp_dict,overwrite=True)
    # Look at the difference between TP and dirty map from TP2VIS (Jin Koda)
    immath(imagename=['test6/clean0/dirtymap.image','test6/M100_TP_CO_cube.bl.smo'],expr='IM0-IM1',outfile='test6/temp.diff')


if True:
    # plot comparing flux of TP
    f0a =  imstat(tpim,                                    axes=[0,1])['flux']     # [::-1]    # revert axis when needed
    f1a =  imstat('test6/tp0/clean0/dirtymap.image',       axes=[0,1])['flux']
    f1b =  imstat('test6/tp1/clean0/dirtymap.image',       axes=[0,1])['flux']
    f1c =  imstat('test6/M100_TP_CO_cube.bl.smo',          axes=[0,1])['flux']
    f1d =  imstat('test6/M100_TP_CO_cube.bl.smo',          axes=[0,1], box=box)['flux']    
    f2a =  imstat('test6/tp0/clean0/dirtymap.image.pbcor', axes=[0,1])['flux']
    f2b =  imstat('test6/tp1/clean0/dirtymap.image.pbcor', axes=[0,1])['flux']
    f2c =  imstat('test6/tp2/clean0/dirtymap.image.pbcor', axes=[0,1])['flux']
    f3a =  imstat('test6/tp.model',                        axes=[0,1])['sum']
    #plot2a([f0a,f2a,f2b,f2c,f1c,f3a],'Flux Comparison %d %g' % (nsize,pixel),'test6/plot2a0.png')
    plot2a([f0a,f2a,f2b,f1c,f3a],'Flux Comparison %d %g' % (nsize,pixel),'test6/plot2a0.png')

qac_log("CLEAN clean1: TP+7m")
qac_clean('test6/clean1',tpms,ms07,nsize,pixel,niter=0,phasecenter=phasecenter,do_int=True,do_concat=True,**line)
qac_beam('test6/clean1/tpint.psf',plot='test6/clean1/qac_beam.png',normalized=True)
# QAC_BEAM: test2c/tpalma.psf  14.8567 11.6334 0.5 783.349 783.349
# QAC_BEAM: Max/Last/PeakLoc 1.34796753314 1.18801575148 43.5

qac_log("CLEAN clean2: TP+12m")
qac_clean('test6/clean2',tpms,ms12,nsize,pixel,niter=0,phasecenter=phasecenter,do_int=True,do_concat=True,**line)
qac_beam('test6/clean2/tpint.psf',plot='test6/clean2/qac_beam.png',normalized=True)
# QAC_BEAM: test2d/tpalma.psf  3.99421 2.63041 0.5 47.6187 47.6187
# QAC_BEAM: Max/Last/PeakLoc 4.11547851528 3.62032676416 76.5

qac_log("CLEAN clean3: TP+7m+12m")
qac_clean('test6/clean3',tpms,[ms12,ms07],nsize,pixel,niter=[0,3000,10000],phasecenter=phasecenter,do_concat=True,do_int=True,**line)
qac_beam('test6/clean3/tpint.psf',plot='test6/clean3/qac_beam.png',normalized=True)
# QAC_BEAM: test2e/tpalma.psf  4.4261 2.94494 0.5 59.0776 59.0776
# QAC_BEAM: Max/Last/PeakLoc 2.95162277943 2.47391209456 76.0
tp2vistweak('test6/clean3/tpint','test6/clean3/tpint_2')
# scale  0.7455
tp2vistweak('test6/clean3/tpint','test6/clean3/tpint_3')
# scale  0.732610

qac_log("TP2VISWT wt*10")
tp2viswt(tpms,mode='multiply',value=10)
# wt -> 0.1073537

qac_log("CLEAN clean4")
qac_clean('test6/clean4',tpms,[ms12,ms07],nsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True,**line)
qac_beam('test6/clean4/tpint.psf',plot='test6/clean4/qac_beam.png',normalized=True)
# QAC_BEAM: test2f/tpalma.psf  4.73778 3.16311 0.5 67.9224 67.9224
# QAC_BEAM: Max/Last/PeakLoc 20.2581768937 19.8506027809 76.5

# beam size weights 
qac_log("TP2VISTWEAK")
tp2viswt([tpms,ms07,ms12], makepsf=True, mode='beammatch')
# wt -> 0.0044103029511 -> 0.00433382295945 -> 0.00465955996837  -> 0.002709 

qac_log("CLEAN clean6")
qac_clean('test6/clean6',tpms,[ms12,ms07],nsize,pixel,niter=[0,3000,10000],phasecenter=phasecenter,do_concat=True,**line)
qac_beam('test6/clean6/tpint.psf',plot='test6/clean6/qac_beam.png',normalized=True)
# -> QAC_BEAM: test2h/tpalma.psf  4.40321 2.92833 0.5 58.4404 58.4404
#    QAC_BEAM: Max/Last/PeakLoc 1.86142086595 0.623532966042 7.5

tp2vistweak('test6/clean6/tpint','test6/clean6/tpint_2')
# scale 3.129287
tp2vistweak('test6/clean6/tpint','test6/clean6/tpint_3')
# scale 2.939141

# f0  =  imstat('M100_TP_CO_cube.regrid',          axes=[0,1],box=box)['flux']
f1  =  imstat('test6/clean6/tpint.image',        axes=[0,1],box=box)['flux']
f2  =  imstat('test6/clean6/tpint_2.image',      axes=[0,1],box=box)['flux']
f3  =  imstat('test6/clean6/tpint_3.image',      axes=[0,1],box=box)['flux']
f4  =  imstat('test6/clean6/tpint_2.tweak.image',axes=[0,1],box=box)['flux']
f5  =  imstat('test6/clean6/tpint_3.tweak.image',axes=[0,1],box=box)['flux']
#
#plot2a([f0,f1,f2,f3],  'plot2h1',       'test6/plot2h1.png',dv=5)
plot2a([f1,f2,f3],  'plot2h1',       'test6/plot2h1.png',dv=5)
plot2a([f1,f4,f5],  'plot2h2 tweak', 'test6/plot2h2.png',dv=5)
#plot2a([f0,f1,f4,f5],  'plot2h2 tweak', 'test6/plot2h2.png',dv=5)

qac_log("PAPER FIGURE-4")
# figure 4 in the paper , comparing without (left) and with (right) 
im1 = 'test6/clean3/int_3.image'
qac_plot(im1, channel=13, range=[-0.05,0.3],box=boxlist,plot='M100_fig4a.png')
qac_plot(im1, channel=17, range=[-0.05,0.3],box=boxlist,plot='M100_fig4c.png')
qac_plot(im1, channel=21, range=[-0.05,0.3],box=boxlist,plot='M100_fig4e.png')
im2 = 'test6/clean3/tpint_3.image'
qac_plot(im2, channel=13, range=[-0.05,0.3],box=boxlist,plot='M100_fig4b.png')
qac_plot(im2, channel=17, range=[-0.05,0.3],box=boxlist,plot='M100_fig4d.png')
qac_plot(im2, channel=21, range=[-0.05,0.3],box=boxlist,plot='M100_fig4f.png')

# qac_log("BEAMCHECK")
# execfile('../beamcheck.py')
# beamcheck('test2h/tpalma','test2i/tpalma')
# -> Dirty (sum,bmaj,bmin):  105.019738839 4.40320777893 2.92832803726
# -> Clean (sum,bmaj,bmin):  269.662882205 4.40320777893 2.92832803726

qac_log("REGRESSION")

regres51 = [
    '1.177256275796271 0.64576812715900356 0.00059684379497741192 7.0609529505808935 0.0',
    '2.5714851372581906 1.4175336201556363 0.0011051818163008522 15.982229345769259 0.0',
    '1.2121874534129664 1.0706370322706797 8.9894598086921097e-05 8.7439785003662109 0.0',
    '0.54682752152594571 1.2847112260328173 -0.89499807357788086 8.8632850646972656 4001.3152006372839',
    '0.17502567644205042 0.29636334974068906 -0.01874225027859211 1.7939578294754028 2023.238938154813',
    '6.4967219206392597e-05 0.090095439430921576 -0.69042855501174927 2.4988367557525635 8.8767026718845621',
    '0.059620662274210548 0.12235698788056612 -0.34523037075996399 2.8235268592834473 7438.3130660632951',
    '-3.2805637128240005e-07 0.015227907834553262 -0.14608184993267059 0.5679050087928772 -0.53773300295131066',
    '0.013743010664281271 0.023264746531751569 -0.082932926714420319 0.63548052310943604 22370.573155800837',
    '4.28581407936708e-06 0.022631811368684605 -0.16905108094215393 0.80271512269973755 5.9360460777592285',
    '0.011506625277348154 0.027128265548915627 -0.11467967182397842 0.8589213490486145 15655.015453119462',
    '0.10499524607530433 0.13873541620859353 -0.024327397346496582 1.3373793363571167 124148.60653471657',
    '1.1068966126089719 1.4509619468478017 0.096944719552993774 7.6039481163024902 6955.9456422021731',
    '0.0050268122414183491 0.023549383849050268 -0.14197352528572083 0.82724666595458984 6896.2735193530361',
    ]

r = regres51

qac_stats(ms12,                       r[0])
qac_stats(ms07,                       r[1])
qac_stats(tpms,                       r[2])
qac_stats(tpim,                       r[3])
qac_stats('test6/clean0/dirtymap.image',   r[4])  
qac_stats('test6/clean1/int.image',        r[5])     # test2c
qac_stats('test6/clean1/tpint.image',      r[6])
qac_stats('test6/clean2/int.image',        r[7])     # test2d
qac_stats('test6/clean2/tpint.image',      r[8])
qac_stats('test6/clean3/int.image',        r[9])     # test2d
qac_stats('test6/clean3/tpint.image',      r[10])
qac_stats('test6/clean4/tpint.image',      r[11])      # test2f
qac_stats('test6/clean5/tpint.image',      r[12])     # test2g
qac_stats('test6/clean6/tpint.image',      r[13])             # test2h series
qac_stats('test6/clean6/tpint_2.image')
qac_stats('test6/clean6/tpint_3.image')
qac_stats('test6/clean6/tpint_2.tweak.image',pb='test6/clean6/tpint.pb')
qac_stats('test6/clean6/tpint_3.tweak.image',pb='test6/clean6/tpint.pb')

qac_end()
