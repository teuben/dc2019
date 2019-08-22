#  some final analysis / plotting after all the M100_combine* scripts have been run.

pdir = 'M100qac'

tpim  = '../M100_TP_CO_cube.bl.image'
ms07  = '../M100_aver_7.ms'
ms12  = '../M100_aver_12.ms'

os.chdir(pdir)

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

    f4a =  imstat('M100sdint_7.joint.cube.image/',         axes=[0,1])['flux']
    f4b =  imstat('M100sdint_7.sd.cube.image/',            axes=[0,1])['flux']

    f5a =  imstat('M100sdint_12.joint.cube.image/',        axes=[0,1])['flux']
    f5b =  imstat('M100sdint_12.sd.cube.image/',           axes=[0,1])['flux']

    f6a =  imstat('M100_Feather_CO.image.pbcor',           axes=[0,1])['flux'][::-1]
    f6b =  imstat('../M100/M100_Feather_CO.image.pbcor',   axes=[0,1])['flux'][::-1]

    f7a =  imstat('test6/clean3/tpint.image.pbcor',        axes=[0,1])['flux']
    f7b =  imstat('test6/clean3/tpint_3.image.pbcor',      axes=[0,1])['flux']
    f7c =  imstat('test6/clean4/tpint.image.pbcor',        axes=[0,1])['flux']    # crazy high
    f7d =  imstat('test6/clean6/tpint.image.pbcor',        axes=[0,1])['flux']    # beam match
    f7e =  imstat('test6/clean6/tpint_2.tweak.image',      axes=[0,1])['flux']    #

    label = []
    label.append("TP")                    # f0a
    label.append("TP vis deconv=True")     # f2a
    label.append("TP deconvolver")       # f2b
    label.append("TP model")              # f3a
    plot2a([f0a,f2a,f2b,f3a],'Flux Comparison M100','flux-cmp1.png', dv=5, label=label)

    label = []
    label.append("TP")                    # f0a
    label.append("TP vis deconv=True")     # f2a
    label.append("SDINT 7m")
    label.append("SDINT 7m SD")
    label.append("SDINT 7+12m")
    label.append("SDINT 7+12m SD")
    
    plot2a([f0a,f2a,f4a,f4b,f5a,f5b],'Flux Comparison M100','flux-cmp2.png', dv=5, label=label)

    label = []
    label.append("TP")                    # f0a
    label.append("TP vis deconv=True")     # f2a
    label.append("Feather")               # f6a
    label.append("SDINT")                 # f5a
    label.append("tp2vis")               # f7a
    
    plot2a([f0a,f2a,f6a,f5a,f7e],'Flux Comparison M100','flux-cmp3.png', dv=5, label=label)

    label = []
    label.append("TP")                    # f0a
    label.append("Feather")               # f6a
    label.append("Feather-full")          # f6b
    
    plot2a([f0a,f6a,f6b],'Flux Comparison M100','flux-cmp4.png', dv=5, label=label)
