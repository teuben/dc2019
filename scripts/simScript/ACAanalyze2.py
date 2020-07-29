import os
import glob 

##########################################
## You need to run ACASimulation.py first!! 
##########################################

#project = "m51c_330GHz_test"
#config = ["alma.cycle6.3" ]
#acaconfig = "aca.cycle6"

########################
### Simulation settings 
########################

cell = "0.2arcsec" 
imsize = [512,512] 


visTP = project+".aca.tp.sd.ms" 
vis7  = project+"."+acaconfig+".ms"
vis12 = [project+"."+item+".ms" for item in config]

visINT = [project+"."+item+".ms" for item in config]
visINT.append(vis7)

wtINT = [1 for i in range(len(config))]
wtINT.append(0.193) # for ACA 7m 
    
# Concat and scale weights
os.chdir(project)
concatvis = project+'.concat'
os.system('rm -rf '+concatvis+'.ms')
concat(vis= visINT, 
       concatvis=concatvis+'.ms',
       visweightscale= wtINT)
os.chdir('../')

os.system('rm -rf '+project+'/'+project+'*image*')

############################################

simanalyze( 
    project            =  project,
    vis                =  visTP+','+vis7, 
    imsize             =  imsize,
    cell               =  cell, 
    threshold          = '30mJy',
    niter              = 10000,
    pbcor              = True,
    analyze            = True,
    showuv             = True,
    showpsf            = False,
    showmodel          = True,
    showconvolved      = True,
    showclean          = True,
    showresidual       = False,
    showdifference     = True,
    verbose            = True,
    showfidelity       = True
)

simanalyze( 
    project            =  project,
    vis                =  ','.join(vis12),
    imsize             =  imsize,
    cell               =  cell,
    modelimage         =  project+'/'+project+".%s.image"%acaconfig,
    featherimage       =  project+'/'+project+".sd.image",
    weighting          = 'briggs',
    threshold          = '30mJy',
    niter              = 10000,
    pbcor              = True,
    analyze            = True,
    showuv             = True,
    showpsf            = False,
    showmodel          = True,
    showconvolved      = True,
    showclean          = True,
    showresidual       = False,
    showdifference     = True,
    verbose            = True,
    showfidelity       = True
)



#################### 

