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

cell = outcell
imsize = outImgSize

## Noisy Visibility setting
addNoise = noisy

if addNoise == False:
    visTP = project+".aca.tp.sd.ms" 
    vis7  = project+"."+acaconfig+".ms"

    visINT = [project+"."+item+".ms" for item in config] 
    visINT.append(vis7)
else:
    visTP = project+".aca.tp.noisy.sd.ms" 
    vis7  = project+"."+acaconfig+".noisy.ms"

    visINT = [project+"."+item+".noisy.ms" for item in config] 
    visINT.append(vis7)
    

    # Concat and scale weights
wtINT = [1 for i in range(len(config))]
wtINT.append(0.193) # for ACA 7m 

os.chdir(project)
concatvis = project+'.concat'
os.system('rm -rf '+concatvis+'.ms')
concat(vis= visINT, 
       concatvis=concatvis+'.ms'
       ,visweightscale= wtINT)
os.chdir('../')

os.system('rm -rf '+project+'/'+project+'*image*')

############################################ 

simanalyze( 
    project            =  project,
    vis                =  visTP, 
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
    vis                =  concatvis+'.ms', 
    imsize             =  imsize,
    cell               =  cell, 
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


######################################## 

