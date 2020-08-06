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

# This picks up both noisy and noiseless MS 
    visTP = glob.glob("%s/%s.aca.tp.*-??.sd.ms"%(project,project))
    vis7  = glob.glob("%s/%s.%s.*-??.ms"%(project,project,acaconfig))
    visINT = []
    for item in config:
        visList = glob.glob("%s/%s.%s.*-??.ms"%(project,project,item))
        visINT[len(visINT):len(visINT)]=visList    
else:
    visTP = glob.glob("%s/2018*/%s.aca.tp.*.noisy.sd.ms"%(project,project))
    vis7  = glob.glob("%s/2018*/%s.%s.*.noisy.ms"%(project,project,acaconfig))

    visINT = []
    for item in config:
        visList = glob.glob("%s/2018*/%s.%s.*.noisy.ms"%(project,project,item))
        visINT[len(visINT):len(visINT)]=visList

## Weight control 
wtINT = [] # weight for concat
for i in range(len(visINT)):
    wtINT.append(1)
        
visINT[len(visINT):len(visINT)]= vis7
for i in range(len(vis7)):
    wtINT.append(0.193) # for ACA 7m
    

# Concat and scale weights
concatvis = '%s/%s.concat' %(project,project)
os.system('rm -rf '+concatvis+'.ms')
concat(vis= visINT, 
       concatvis=concatvis+'.ms'
       ,visweightscale= wtINT)

concatvisTP = '%s/%s.concat.sd' %(project,project)
os.system('rm -rf '+concatvisTP+'.ms')
concat(vis= visTP, 
       concatvis=concatvisTP+'.ms')


os.system('rm -rf '+project+'/'+project+'*image*')

############################################ 

simanalyze( 
    project            =  project,
    vis                =  concatvisTP+'.ms', 
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

