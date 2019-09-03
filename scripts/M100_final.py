#  some final analysis / plotting after all the M100_combine* scripts have been run.

pdir = 'M100qac'

tpim  = '../M100_TP_CO_cube.bl.image'
ms07  = '../M100_aver_7.ms'
ms12  = '../M100_aver_12.ms'

box1  = '219,148,612,579'     # casaguide box in their 800x800 image
box   = box1

os.chdir(pdir)

if True:
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
    
    f7a =  imstat('test6/clean3/tpint.image.pbcor',        axes=[0,1])['flux']
    f7b =  imstat('test6/clean3/tpint_3.image.pbcor',      axes=[0,1])['flux']
    f7c =  imstat('test6/clean4/tpint.image.pbcor',        axes=[0,1])['flux']    # crazy high
    f7d =  imstat('test6/clean6/tpint.image.pbcor',        axes=[0,1])['flux']    # beam match
    f7e =  imstat('test6/clean6/tpint_2.tweak.image',      axes=[0,1])['flux']    #

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
    label.append("TP")                    # f0a
    label.append("Feather")               # f6a
    label.append("SDINT")                 # f5a
    label.append("tp2vis")                # f7e
    
    plot2a([f0a,f6a,f5a,f7e],'Flux Comparison M100','flux-cmp3.png', dv=5, label=label)

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


if True:
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

if True:
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

if True:
    # save some fits cubes for other analysis
    qac_fits(tpim,                                    'cube0.fits')
    qac_fits('test6/tp0/clean0/dirtymap.image.pbcor', 'cube1.fits')
    qac_fits('M100_combine_CO_cube.image.pbcor',      'cube2.fits')
    qac_fits('M100_Feather_CO.image.pbcor',           'cube3.fits')
    qac_fits('M100sdint_7.joint.cube.image',          'cube4.fits')
    qac_fits('M100sdint_12.joint.cube.image',         'cube5.fits')
    qac_fits('test6/clean1/tpint.image.pbcor',        'cube6.fits')
    qac_fits('test6/clean6/tpint_2.image.pbcor',      'cube7.fits')
    qac_fits('test6/clean6/tpint_2.tweak.image',      'cube8.fits')
