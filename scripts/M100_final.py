#  some final analysis / plotting after all the M100_combine* scripts have been run.
#
#  you can also try out 
#          casa -c M100_final.py select=8
#  or
#          casa -c M100_final.py select='[5,6,7]'

import numpy as np
import matplotlib.pyplot as pl

pdir = 'M100qac'              # all operations in this directory

tpim  = '../M100_TP_CO_cube.bl.image'
ms07  = '../M100_aver_7.ms'
ms12  = '../M100_aver_12.ms'

box1  = '219,148,612,579'     # casaguide box in their 800x800 image; flux is 3118
box2  = '252,182,574,524'     # a better box?                   But flux only 2569
box   = box1

select = 0      # 0=do all


# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)



os.chdir(pdir)

if QAC.select(1,select,"Flux comparisons flum-cmp*png"):
    # plot comparing flux of TP ; use [::-1] when an axis needs to be reverted
    f0a =  imstat(tpim,                                    axes=[0,1])['flux']
    f0b =  imstat('../M100/M100_TP_CO_cube.regrid',        axes=[0,1])['flux'][::-1]
    f0c =  imstat('../M100/M100_TP_CO_cube.regrid',        axes=[0,1], box=box)['flux'][::-1]     # TP
    f0e =  imstat('../M100/M100_TP_CO_cube.regrid.subim',  axes=[0,1])['flux'][::-1]
    
    f1a =  imstat('test6/tp0/clean0/dirtymap.image',       axes=[0,1])['flux']
    f1b =  imstat('test6/tp1/clean0/dirtymap.image',       axes=[0,1])['flux']
    f1c =  imstat('test6/M100_TP_CO_cube.bl.smo',          axes=[0,1])['flux']
    f1d =  imstat('test6/M100_TP_CO_cube.bl.smo',          axes=[0,1], box=box)['flux']    
    f2a =  imstat('test6/tp0/clean0/dirtymap.image.pbcor', axes=[0,1], box=box)['flux']
    f2b =  imstat('test6/tp1/clean0/dirtymap.image.pbcor', axes=[0,1], box=box)['flux']
    f2c =  imstat('test6/tp2/clean0/dirtymap.image.pbcor', axes=[0,1], box=box)['flux']
    f3a =  imstat('test6/tp.model',                        axes=[0,1])['sum']

    f4a =  imstat('M100sdint_7.joint.cube.image',          axes=[0,1], box=box)['flux']
    f4b =  imstat('M100sdint_7.sd.cube.image',             axes=[0,1], box=box)['flux']

    f5a =  imstat('M100sdint_12.joint.cube.image',         axes=[0,1], box=box)['flux']
    f5b =  imstat('M100sdint_12.sd.cube.image',            axes=[0,1], box=box)['flux']

    f6a =  imstat('M100_Feather_CO.image.pbcor',           axes=[0,1])['flux'][::-1]              # Feather
    f6b =  imstat('../M100/M100_Feather_CO.image.pbcor',   axes=[0,1])['flux'][::-1]
    
    f7a =  imstat('test6/clean3/tpint.image.pbcor',        axes=[0,1], box=box)['flux']
    f7b =  imstat('test6/clean3/tpint_3.image.pbcor',      axes=[0,1], box=box)['flux']
    f7c =  imstat('test6/clean4/tpint.image.pbcor',        axes=[0,1], box=box)['flux']    # crazy high
    f7d =  imstat('test6/clean6/tpint.image.pbcor',        axes=[0,1], box=box)['flux']    # beam match
    f7e =  imstat('test6/clean6/tpint_2.tweak.image',      axes=[0,1], box=box)['flux']    #

    label = []
    label.append("TP")          # f0a
    label.append("TP-regrid")   # f0b
    label.append("TP-box")      # f0c
    label.append("diff")
    f0d = f0b-f0c
    plot2a([f0a,f0b,f0c,f0d],'Flux Comparison M100 for TP','flux-cmp0.png', dv=5, label=label)    

    label = []
    label.append("TP")                    # f0c
    label.append("TP vis deconv=True")    # f2a
    label.append("TP deconvolver")        # f2b
    label.append("TP model")              # f3a
    plot2a([f0c,f2a,f2b,f3a],'Flux Comparison M100','flux-cmp1.png', dv=5, label=label)

    label = []
    label.append("TP")                    # f0c
    label.append("SDINT 7m")
    label.append("SDINT 7+12m")
    label.append("7 vs 7+12 diff")
    f4d = f4a-f5a
    f5d = f0c-f4b      # checked: these are identical
    
    plot2a([f0c,f4a,f5a,f4d],'Flux Comparison M100 SDINT','flux-cmp2.png', dv=5, label=label)

    label = []
    label.append("TP")                    # f0c
    label.append("Feather")               # f6a
    label.append("SDINT")                 # f5a
    label.append("tp2vis")                # f7e
    
    plot2a([f0c,f6a,f5a,f7e],'Flux Comparison M100','flux-cmp3.png', dv=5, label=label)

    label = []
    label.append("TP")                    # f0a
    label.append("Feather")               # f6a
    label.append("Feather-full")          # f6b

    plot2a([f0a,f6a,f6b],'Flux Comparison M100 sanity check','flux-cmp4.png', dv=5, label=label)

    label = []
    label.append("TP")                    # f0a
    label.append("Feather")               # f6a
    label.append("SDINT 7+12m")           # f5a
    
    plot2a([f0c,f6a,f5a],'Flux Comparison M100','flux-cmp5.png', dv=5, label=label)

    # hardcoded for ALMA / BIMA comparison
    if QAC.exists('../NGC4321.bima12m.cm.fits'):
        f10=imstat('../NGC4321.bima12m.cm.fits', axes=[0,1])['flux']
        v10=np.linspace(1403.4,1403.4+32*9.906266,33)
        # re-use f2c for the TP flux in the box
        v11=np.linspace(1400,1400+69*5,70)
        f11=imstat('../M100/M100_TP_CO_cube.regrid',axes=[0,1], box=box)['flux']
        label = []
        label.append("ALMA TP box")
        label.append("BIMA SONG")
        plot2a([f11,f10], 'Flux comparison M100 ALMA/BIMA','flux-cmp6.png', v=[v11,v10], label=label)


if QAC.select(2,select,"stats"):
    # shows min,max,mean,disp,flux
    qac_stats(tpim)
    qac_stats('test6/tp0/clean0/dirtymap.image.pbcor')
    qac_stats('M100_combine_CO_cube.image.pbcor')
    qac_stats('M100_Feather_CO.image.pbcor') 
    qac_stats('M100sdint_7.joint.cube.image')
    qac_stats('M100sdint_12.joint.cube.image') 
    qac_stats('test6/clean1/tpint.image.pbcor')   
    qac_stats('test6/clean6/tpint_2.image.pbcor')
    qac_stats('test6/clean6/tpint_2.tweak.image')

if QAC.select(3,select,"flux"):    
    # shows the RMS in a noise-flat (for some we don't have that, so use the flux-flat excluding a generous border)
    qac_flux(tpim,                                    edge=8)
    qac_flux('test6/tp0/clean0/dirtymap.image',       edge=8)
    qac_flux('M100_combine_CO_cube.image',            edge=8)
    qac_flux('M100_Feather_CO.image',                 edge=8)
    qac_flux('M100sdint_7.joint.cube.image',          edge=8, border=300) # pbcor
    qac_flux('M100sdint_12.joint.cube.image',         edge=8, border=300) # pbcor
    qac_flux('test6/clean1/tpint.image',              edge=8)
    qac_flux('test6/clean6/tpint_2.image',            edge=8)
    qac_flux('test6/clean6/tpint_2.tweak.image',      edge=8, border=300) # pbcor

if QAC.select(4,select,"fits"):        
    # save some fits cubes for other FITS based analysis
    qac_fits(tpim,                                    'cube0.fits')
    qac_fits('test6/tp0/clean0/dirtymap.image.pbcor', 'cube1.fits')
    qac_fits('M100_combine_CO_cube.image.pbcor',      'cube2.fits')
    qac_fits('M100_Feather_CO.image.pbcor',           'cube3.fits')
    qac_fits('M100sdint_7.joint.cube.image',          'cube4.fits')
    qac_fits('M100sdint_12.joint.cube.image',         'cube5.fits')
    qac_fits('test6/clean1/tpint.image.pbcor',        'cube6.fits')
    qac_fits('test6/clean6/tpint_2.image.pbcor',      'cube7.fits')
    qac_fits('test6/clean6/tpint_2.tweak.image',      'cube8.fits')


if QAC.select(5,select,"M100_weights.png"):        
    # make M100final; open M100qac/test6a_4/M100_weights.png
    if QAC.exists('test6a_4'):
        os.chdir('test6a_4')
        n1 = ['clean3_0.18', 'clean3_0.25', 'clean3_0.4', 'clean3_0.61', 'clean3_1']
        m1 = ['int_4.image', 'tpint_4.image', 'tpint_4.residual', 'tpint_4.tweak.image']
        channel = 35    # central
        channel = 45    # north arc
        channel = 25    # south arc
        images = []
        for n in n1:
            for m in m1:
                images.append('%s/%s' % (n,m))
        xgrid = ['int', 'tpint', 'residual', 'tweak']
        ygrid = ['0.18=bm', '0.25', '0.4', '0.61', '1=rms']
        minmax = [-0.15, 0.15]
        minmax = [-0.05, 0.05]
        qac_plot_grid(images,channel,ncol=4,xgrid=xgrid,ygrid=ygrid,labels=False,minmax=minmax,box=QAC.iarray(box),plot='M100_weights.png')
        os.chdir('..')

if QAC.select(6,select,"M100_niter.png"):        
    # make M100final; open M100qac/test6a_5/M100_niter.png
    if QAC.exists('test6a_5'):
        os.chdir('test6a_5')
        n1 = ['clean3_0.61']
        m1 = ['int%s.image', 'tpint%s.image', 'tpint%s.residual', 'tpint%s.tweak.image']
        i1 = [1,2,3,4,5]
        channel = 35    # central
        channel = 45    # north arc
        channel = 25    # south arc
        images = []
        for i in i1:
            for m in m1:
                mmm = m % QAC.label(i)
                if mmm.find('residual') == -1:
                    mmm = mmm + '.pbcor'
                images.append('%s/%s' % (n1[0],mmm))
        xgrid = ['int', 'tpint', 'residual', 'tweak']
        ygrid = ['1k','3k','10k','100k','300k']
        minmax = [-0.15, 0.15]
        minmax = [-0.05, 0.05]
        qac_plot_grid(images,channel,ncol=4,xgrid=xgrid,ygrid=ygrid,labels=False,minmax=minmax,box=QAC.iarray(box),plot='M100_niter.png')
        os.chdir('..')

if QAC.select(7,select,"better comparisons on same grid"):        
    # better comparison on same spatial grid, the casaguide keeps the combine on the big grid. we also add the sdint, and when tp2vis is ready, that too
    im0  = 'M100_TP_CO_cube.regrid.subim.mom0'
    im1  = 'M100_Feather_CO.image.mom0.pbcor'
    im2  = 'M100_combine_CO_cube.image.mom0.pbcor'    # needs box
    im1v = 'M100_Feather_CO.image.mom1'
    im2v = 'M100_combine_CO_cube.image.mom1'         # needs box
    minmax1 = [0.0, 10.0]
    minmax2 = [0.0, 50.0]
    qac_plot(im0,                                     plot='M100_TP.mom0.png')    
    qac_plot(im1, range=minmax1,                      plot='M100_feather.mom0.png')
    qac_plot(im2, range=minmax1, box=QAC.iarray(box), plot='M100_combine.mom0.png')
    # sdint
    chan_rms = [0,8,62,69]
    rms1      = 0.011
    # qac_mom('M100sdint_7.joint.cube.image', chan_rms, rms=rms2)       - needs a new rms
    qac_mom('M100sdint_12.joint.cube.image', chan_rms, rms=rms1)
    #
    im3  = 'M100sdint_7.joint.cube.image.mom0'
    im4  = 'M100sdint_12.joint.cube.image.mom0'
    im4v = 'M100sdint_12.joint.cube.image.mom1'
    # qac_plot(im3, range=minmax2, box=QAC.iarray(box), plot='M100_sdint_7.mom0.png')   - needs a new rms
    qac_plot(im4, range=minmax1, box=QAC.iarray(box), plot='M100_sdint_12.mom0.png')

    # velocity fields
    minmax2 = [1400,1745]    # the full spectral range
    minmax2 = [1440,1695]    # the galaxy range
    qac_plot(im1v, range=minmax2,                      plot='M100_feather.mom1.png')    
    qac_plot(im2v, range=minmax2, box=QAC.iarray(box), plot='M100_combine.mom1.png')
    qac_plot(im4v, range=minmax2, box=QAC.iarray(box), plot='M100_sdint.mom1.png')    
    

if QAC.select(8,select,"tp2vis flux vs. niter M100_flux_niter.png "):        
    # tp2vis flux as function of niter for a few weights 
    data = []
    do_box1 = True

    # (box; _8)
    data0 = []
    data0.append(0.18)
    if do_box1:
        data0.append((0, [0.0,                 0.69069289908853526, 7.0445373956769428, 0.0, 1233.2964119680692, 1404.1389226551587, 0, 0]))
        data0.append((1,[67.549319753423333, 329.13769715125238, 330.03394369662487, 69.869173774495721, 1461.7287003026006, 1622.9835573199737, 4490.4631195904631, 5068.9796896283315]))
        data0.append((10,[183.60104722948745, 917.5493314723733, 963.00072264745882, 197.92762706801295, 1892.3216386077345, 2078.6017151066071, 4051.7690416359064, 4547.8673890529817]))
        data0.append((30,[205.59680126048625, 1025.9519102339518, 1078.5805834175244, 237.31611787574366, 2019.6764649396957, 2214.1855722374594, 3981.1592366697741, 4446.6054392054775]))
        data0.append((100,[246.07167254609521, 1219.2556737138473, 1302.9865180017471, 431.33667713851901, 2648.1349144413903, 2912.3136451938035, 3767.6033148205315, 4191.7484094832116]))
        data0.append((300,[243.92841600797328, 1208.7783932253055, 1278.8313984809452, 458.61424574242869, 2734.1371047614812, 2982.5608609107435, 3746.1962853018772, 4100.9616509371326]))
    else:
        data0.append((0, [0.0, -0.038297581834341447, 1.2242853025649814, 0.0, 1043.1725438455428, 1120.876482014816,0,0]))
        data0.append((1,[67.030729785561562, 336.11393760931469, 346.28738195504587, 69.311512798070908, 1280.535364760877, 1363.8503122949878, 3824.176203635011, 4113.6380864082512]))
        data0.append((10,[173.57975618215278, 851.51873792681101, 885.893010365995, 186.82226391322911, 1658.4133647906083, 1756.7423922479345, 3395.3674589263546, 3627.5037170377377]))
        data0.append((30,[192.81406448082998, 949.18292057673239, 989.31891013609231, 221.35052382247522, 1773.5300335921563, 1878.3248513514359, 3347.9749364537952, 3572.5506065985765]))
        data0.append((100,[219.49922603252344, 1112.0733408492422, 1159.6488533322131, 376.44856606243411, 2310.6031570592818, 2443.3963152843417, 3269.8975256000763, 3477.8761517951316]))
        data0.append((300,[220.37329601700912, 1104.4628472421518, 1152.0910272020278, 403.96391585901074, 2398.3367641275859, 2533.7153842433768, 3266.7867505152662, 3473.6850884844303]))
    data.append(data0)
        
    # box _6
    data1 = []
    data1.append(0.25)
    if do_box1:
        data1.append((0,   [0.0,                0.69069289908853526, 7.0445373956769428, 0.0,              1708.6252157811412, 1942.671266258154,  0,                  0]))
        data1.append((1,[67.549319753423333, 329.13769715125238, 330.03394369662487, 70.77634771168232, 1896.5321870112789, 2119.3352585749144, 4311.1245322001068, 4869.7784662443564]))
        data1.append((10,[183.60104722948745, 917.5493314723733, 963.00072264745882, 200.55549032753333, 2247.014792986437, 2485.0880206385582, 3986.9754992006729, 4476.763490314338]))
        data1.append((30,[205.59680126048625, 1025.9519102339518, 1078.5805834175244, 246.5625622458756, 2365.7439318259508, 2610.0037926807595, 3921.7938194236258, 4386.0935048420833]))
        data1.append((100,[246.07167254609521, 1219.2556737138473, 1302.9865180017471, 468.27220697456505, 2932.862997962744, 3231.4449826958212, 3717.8230128450632, 4119.835313155012]))
        data1.append((300,[243.92841600797328, 1208.7783932253055, 1278.8313984809452, 499.64624189459937, 3023.235317878612, 3314.2778384792487, 3722.3648689352071, 4104.9023796488409]))
    else:
        data1.append((0,[0.0, -0.038297581834341447, 1.2242853025649814, 0.0, 1445.4984411595058, 1552.5725581575098,0,0]))
        data1.append((1,[67.030729785561562, 336.11393760931469, 346.28738195504587, 70.192708736285567, 1642.7552872391043, 1754.0107953313861, 3665.119251406813, 3938.2974288195455]))
        data1.append((10,[173.57975618215278, 851.51873792681101, 885.893010365995, 189.22188530676067, 1950.4799189452544, 2071.8855667121061, 3357.7544514760048, 3588.1879756674439]))
        data1.append((30,[192.81406448082998, 949.18292057673239, 989.31891013609231, 229.70064438832924, 2058.8039673502331, 2185.4490258988399, 3311.9102478561563, 3534.1447751230412]))
        data1.append((100,[219.49922603252344, 1112.0733408492422, 1159.6488533322131, 407.3894325006986, 2554.2513744543739, 2704.6463311621023, 3232.1094029543769, 3433.9799978887436]))
        data1.append((300,[220.37329601700912, 1104.4628472421518, 1152.0910272020278, 440.41637931164951, 2643.0138601364501, 2795.7585555981173, 3231.5090664936274, 3432.2378646735465]))

        
    data.append(data1)

    # box _6
    data2 = []
    data2.append(0.40)
    if do_box1:
        data2.append((0,  [0.0,                0.69069289908853526, 7.0445373956769428, 0.0,                2719.687810756986, 3087.749396071923, 0, 0]))
        data2.append((1,  [67.549319753423333, 329.13769715125238, 330.03394369662487, 72.743410345166922, 2817.3260300035431, 3170.1661175871182, 4146.4670023243962, 4685.6821099856534]))
        data2.append((10,  [183.60104722948745, 917.5493314723733, 963.00072264745882, 202.70333690242842, 2986.1881102402499, 3333.4119425288577, 3931.1919972860292, 4416.5090810657885]))
        data2.append((30,  [205.59680126048625, 1025.9519102339518, 1078.5805834175244, 267.014651005622, 3059.8612023050546, 3402.1437799769656, 3859.6658368444682, 4316.6347602559599]))
        data2.append((100,  [246.07167254609521, 1219.2556737138473, 1302.9865180017471, 515.18583698745351, 3340.6295604918191, 3688.3177769677882, 3678.271310193963, 4068.0407457055426]))
        data2.append((300, [243.92841600797328, 1208.7783932253055, 1278.8313984809452, 557.40592814209231, 3416.5423175451374, 3771.7195566517407, 3695.1600302533343, 4093.3588876767126]))
    else:
        data2.append((0,  [0.0, -0.038297581834341447, 1.2242853025649814, 0.0, 2301.339866645365, 2470.686255015165,0,0]))
        data2.append((1,  [67.030729785561562, 336.11393760931469, 346.28738195504587, 72.10475599206984, 2409.5626815765113, 2579.8862585166958, 3519.6727950639338, 3777.7613508570989]))
        data2.append((10, [173.57975618215278, 851.51873792681101, 885.893010365995, 191.19576603500172, 2556.9205152762406, 2725.999931738168, 3324.7130942828785, 3553.4382549905445]))
        data2.append((30, [192.81406448082998, 949.18292057673239, 989.31891013609231, 247.70078978640959, 2630.3867901462449, 2800.4725754358369, 3276.703086617184, 3496.1385728850801]))
        data2.append((100,[219.49922603252344, 1112.0733408492422, 1159.6488533322131, 446.53941891214345, 2900.5562096498052, 3074.4789981172539, 3192.3421890812137, 3387.1014837564335]))
        data2.append((300,[220.37329601700912, 1104.4628472421518, 1152.0910272020278, 489.73093435325791, 2965.0433674789947, 3140.0651264342687, 3194.4039872245626, 3387.7724002500863]))
    data.append(data2)    

    # box _5
    data3 = []
    data3.append(0.61)
    if do_box1:
        data3.append((0,  [0.0,                0.69069289908853526, 7.0445373956769428, 0.0,               4118.1842584617889, 4670.6618351443885,  0,                 0]))
        data3.append((1,  [67.549319753423333, 329.13769715125238, 330.03394369662487, 75.097607307136059, 4082.625038443839, 4613.9238235719668, 4060.0681476754989, 4588.190699817028]))
        data3.append((10,  [183.60104722948745, 917.5493314723733, 963.00072264745882, 207.66671728342772, 3995.8465274868063, 4490.4987728331098, 3893.196495290289,   4372.8158111696084]))
        data3.append((30,  [205.59680126048625, 1025.9519102339518, 1078.5805834175244, 280.40720982197672, 3935.4342553809333, 4403.9308073378979, 3826.0928290771494, 4278.7595772800669]))
        data3.append((100,  [246.07167254609521, 1219.2556737138473, 1302.9865180017471, 548.54510666429996, 3698.9768314474418, 4077.8831124559192, 3645.4630125113376, 4018.7234519358758]))
        data3.append((300,  [243.92841600797328, 1208.7783932253055, 1278.8313984809452, 594.84484219591968, 3683.9969765420756, 4047.9371091586268, 3647.7651383714056, 4007.6402197904526]))
    else:
        data3.append((0,  [0.0, -0.038297581834341447, 1.2242853025649814, 0.0, 3485.2745996249769, 3740.3034589888262,0,0]))
        data3.append((1,  [67.030729785561562, 336.11393760931469, 346.28738195504587, 74.340407798066735, 3462.1380176197113, 3713.2241515014412, 3443.3324213841106, 3692.9441005241383]))
        data3.append((10, [173.57975618215278, 851.51873792681101, 885.893010365995, 195.81382716167718, 3385.4839064948364, 3618.8582707356873, 3301.894454038676, 3528.787987644821]))
        data3.append((30, [192.81406448082998, 949.18292057673239, 989.31891013609231, 259.78732012538239, 3346.708023564574, 3570.8779058961613, 3258.2322221819391, 3475.6821907364306]))
        data3.append((100,[219.49922603252344, 1112.0733408492422, 1159.6488533322131, 474.75316428265069, 3214.5234392710645, 3406.6730727632648, 3167.8343945121273, 3357.0048715245694]))
        data3.append((300,[220.37329601700912, 1104.4628472421518, 1152.0910272020278, 521.71984523128049, 3214.8024854230771, 3405.3893680761034, 3183.7939572095106, 3372.0955273772483]))
                      
    # testing the better tclean (box)  _9
    if False:
        data3 = []
        data3.append(0.61)
        data3.append((0,  [0.0,                 0.69069289908853526, 7.0445373956769428, 0.0,              4118.1842584617889, 4670.6618351443885, 0, 0]))
        data3.append((1,  [67.549319753423333, 329.13769715125238, 330.03394369662487, 75.097607307136059, 4082.625038443839, 4613.9238235719668, 4060.0681476754989, 4588.190699817028]))
        data3.append((10, [183.85870719142258, 917.68653677068903, 961.98122936770642, 207.90568770514801, 3995.6482148114064, 4490.1155902113633, 3894.0928412013664, 4373.6832481988167]))
        data3.append((30, [205.77796576567926, 1025.3555461563892, 1076.3527160363631, 280.41517391940579, 3937.0850658903328, 4405.7459789488739, 3829.8798736543372, 4283.0151240110799]))
        data3.append((100,[247.98066672834102, 1242.7052236373304, 1322.0264121343048, 492.59753824223299, 3779.1632415099589, 4188.1619618638024, 3713.6551205074634, 4113.4624909463491]))
        data3.append((300,[247.98066672834102, 1242.7052236373304, 1322.0264121343048, 492.59753824223299, 3779.1632415099589, 4188.1619618638024, 3713.6551205074634, 4113.4624909463491]))

    data.append(data3)
    

    # box _7
    data4 = []
    data4.append(1.0)
    if do_box1:
        data4.append((0,  [0.0,                 0.69069289908853526, 7.0445373956769428, 0.0,              6663.7951437358752, 7549.0958141233459, 0, 0]))
        data4.append((1,  [67.549319753423333, 329.13769715125238, 330.03394369662487, 80.200590550899506, 6358.64720382826, 7209.2763661616627, 3989.6236788469664, 4506.3057953302996]))
        data4.append((10, [183.60104722948745, 917.5493314723733, 963.00072264745882, 199.85963830025867, 5855.6298006472161, 6622.9682488301614, 3873.2658828493609, 4350.9133028193482]))
        data4.append((30, [205.59680126048625, 1025.9519102339518, 1078.5805834175244, 305.54776356508955, 5384.9149855448713, 6056.4140452965275, 3788.257506826807, 4229.8841215361763]))
        data4.append((100,[246.07167254609521, 1219.2556737138473, 1302.9865180017471, 622.93938792886729, 3984.4353783458614, 4373.6760819364508, 3620.045652236041, 3971.1606282645357]))
        data4.append((300,[243.92841600797328, 1208.7783932253055, 1278.8313984809452, 625.43513297669324, 3978.3742781413148, 4368.6535960531037, 3622.2712431350892, 3976.3167300055088]))
    else:
        data4.append((0,  [0.0, -0.038297581834341447, 1.2242853025649814, 0.0, 5640.7483161237396, 6050.3807547169827,0,0]))
        data4.append((1,  [67.030729785561562, 336.11393760931469, 346.28738195504587, 79.208705764263868, 5353.0901061455861, 5748.2004079484668, 3381.9164184520919, 3623.9339711968209]))
        data4.append((10, [173.57975618215278, 851.51873792681101, 885.893010365995, 188.8292862791568, 4910.1378886858374, 5261.2710643914215, 3290.6099285984974, 3516.7879353905223]))
        data4.append((30, [192.81406448082998, 949.18292057673239, 989.31891013609231, 281.76977715268731, 4530.5647381579138, 4840.1269849423779, 3237.3317109400532, 3450.8076810238194]))
        data4.append((100,[219.49922603252344, 1112.0733408492422, 1159.6488533322131, 548.33864640893262, 3478.7847006795973, 3682.1066440716863, 3169.8176285891991, 3352.953754267261]))
        data4.append((300,[220.37329601700912, 1104.4628472421518, 1152.0910272020278, 549.58631599209093, 3472.2946935622908, 3674.9758640611703, 3169.1736883822523, 3352.188794215529]))
    data.append(data4)
    


    nwt = len(data)          # weight values
    nit = len(data[0])-1     # iter values
    nmp = len(data[0][1][1]) # map values   tpint in [5], tweak in [7]

    print(nwt,nit,nmp)

    wt = []
    for i in range(nwt):
        wt.append(data[i][0])
    print("Wt values:",wt)

    # DM
    flux_tp = []
    flux_dm = []
    flux_cm2 = []    
    flux_tm2 = []    
    flux_cm4 = []    
    flux_tm4 = []    
    flux_cm6 = []    
    flux_tm6 = []    
    for i in range(nwt):
        if do_box1:
            flux_tp.append(3118)
        else:
            flux_tp.append(2569)
        flux_dm.append(data[i][1][1][5])
        flux_cm2.append(data[i][2][1][5])
        flux_tm2.append(data[i][2][1][7])                
        flux_cm4.append(data[i][4][1][5])
        flux_tm4.append(data[i][4][1][7])                
        flux_cm6.append(data[i][6][1][5])
        flux_tm6.append(data[i][6][1][7])                
    print('DM: ',flux_dm)


    pl.figure()
    pl.plot(wt,flux_tp,'-',c='black',linewidth=2, label='TP')    
    pl.plot(wt,flux_dm,'o-',c='c',label='DM')
    pl.plot(wt,flux_cm2,'o-', c='r',label='1k')
    pl.plot(wt,flux_tm2,'o--',c='r') #,label='TM1')
    pl.plot(wt,flux_cm4,'o-', c='g',label='30k')
    pl.plot(wt,flux_tm4,'o--',c='g') #,label='TM30')
    pl.plot(wt,flux_cm6,'o-', c='b',label='300k')
    pl.plot(wt,flux_tm6,'o--',c='b') #,label='TM300')
    pl.xlim([0.1,1.1])
    pl.title('TPINT (solid) and TWEAK (dashed) for different niter values')
    pl.xlabel('wtfac (rms=0.13 at 1.0, beammatch at 0.18)')
    pl.ylabel('M100 Flux (Jy.km/s) in casaguide box')
    pl.legend(loc='best')
    pl.savefig('M100_flux_niter.png')
    pl.show()


    # single case convergence comparing INT, TPINT, MODEL, TWEAK?
    # we have this data structure:
    #     [wtfac, (n1, [...]), (n2, [...]), ...]
    d = data4    # wtfac=1
    d = data3    # wtfac=0.61
    d = data2    # wtfac=0.4
    d = data1    # wtfac=0.25
    d = data0    # wtfac=0.18
    wtfac = d[0]
    niter=[]
    f0=[]   # TP
    f1=[]   # int
    f2=[]   # tpint-model
    f3=[]   # tpint
    f4=[]   # tweak
    dv = 5.0    # channel separation in km/s for model flux
    for n in range(1,len(d)):
        f = d[n][1]
        print('niter',d[n][0],f)
        niter.append(d[n][0])
        if do_box1:
            f0.append(3118)
        else:
            f0.append(2569)
        f1.append(f[2])
        f2.append(f[3]*dv)
        f3.append(f[5])
        f4.append(f[7])
        
    pl.figure()
    pl.plot(niter,f0,'-',c='black',linewidth=2, label='TP')    
    pl.plot(niter,f1,'o-',c='c',label='INT')
    pl.plot(niter,f2,'o--',c='g',label='TPINT-model')
    pl.plot(niter,f3,'o-',c='g',label='TPINT')
    pl.plot(niter,f4,'o-',c='b',label='TWEAK')
    pl.title('Flux convergence for wtfac=%g' % wtfac)
    pl.xlabel('Niter/1000')
    pl.ylabel('M100 Flux (Jy.km/s) in casaguide box')
    pl.legend(loc='best')
    pl.savefig('M100_flux_niter2.png')
    pl.show()


if QAC.select(9,select,"test6a_5/clean3_0.61/  plot7a,b,c,d"):
    if QAC.exists('test6a_5/clean3_0.61/'):
        os.chdir('test6a_5/clean3_0.61/')
        plot7('.',2, 15, range=[-0.05,0.05],residual=True,box=QAC.iarray(box),plot='plot7a.png')
        plot7('.',3, 15, range=[-0.05,0.05],residual=True,box=QAC.iarray(box),plot='plot7b.png')
        plot7('.',4, 15, range=[-0.05,0.05],residual=True,box=QAC.iarray(box),plot='plot7c.png')
        plot7('.',5, 15, range=[-0.05,0.05],residual=True,box=QAC.iarray(box),plot='plot7d.png')
        os.chdir('..')

if QAC.select(10,select,"plot flux(box-size) for TP data"):
    tpim1 = 'M100_TP_CO_cube.regrid'
    tpim2 = 'M100_TP_CO_cube.regrid.mom0'
    nsigma = 2
    qac_mom(tpim1,[0,9,60,69],rms=0.13, momfac = [nsigma, 5, 5])
    #qac_mom(tpim1,[0,9,60,69])
    box  = box1
    if QAC.exists(tpim1):
        b  = list(range(-50,50,5))
        f1 = np.zeros(len(b))
        f2 = np.zeros(len(b))
        bl = QAC.iarray(box)
        for i in range(len(b)):
            b1 = '%d,%d,%d,%d' % (bl[0]-b[i],bl[1]-b[i],bl[2]+b[i],bl[3]+b[i])
            f1[i] = imstat(tpim1, box=b1)['flux'][0]
            f2[i] = imstat(tpim2, box=b1)['flux'][0]
            print(b[i],b1,f1[i],f2[i])
        f3 = f2 * 0 + 3118
        f4 = f2 * 0 + 2972   # error: 319
        #
        plt.figure()
        plt.plot(b,f1,'-',label='flux in cube')
        plt.plot(b,f2,'-',label='flux in mom0 w/ %g sigma cut' % nsigma)
        plt.plot(b,f3,'--',label='ALMA')
        plt.plot(b,f4,'--',label='BIMASONG (+/- 319)')
        plt.plot([-35,-35],[2400,2800],'--',label='box2 (roughly)')
        plt.xlabel('Box size difference from box1 (arcsec)')    # this assumes pixel=1"
        plt.ylabel('Flux (Jy.km/s)')
        plt.title('TP Flux as function of box size (box1=%s)' % box1)
        plt.legend(loc='best')
        plt.savefig('M100_TP_boxflux.png')
        plt.show()
            


