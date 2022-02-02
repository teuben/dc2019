# ALMA Data Reduction Script
# ScriptForImaging.py by Dirk Petry, Aug 2020
# Adapted for running modular versions of combination by Adele Plunkett, Sep 2020
# Run with CASA 6

##---------------------------------------------------------
## Additional libraries and imports

import os
import importlib.util
import sys

file_path = '/lustre/cv/users/aplunket/Combo/DC2020/Scripts/datacomb.py'
module_name = 'datacomb'
spec = importlib.util.spec_from_file_location(module_name,file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

from datacomb import runtclean, runWSM
from casatasks import concat


##----------------------------------------------------------
## (0) Set up files

whichmodel = 'c' ## ['b','c']
doconcat = False  #True if you need to concat the ms files; false if you already have the concatenated ms
doimage = True #True if you want to do the image combination
dotclean = False #True if you want to do the interferometry-only TCLEAN (no startmodel).  Most likely as a test.

## skymodel-b
if whichmodel == 'b':
    WorkingDir = '/lustre/cv/users/aplunket/Combo/DC2020/ModbComp/'# --> Directory where you want to work
    DataDir = '/lustre/cv/users/aplunket/Combo/DC2020/Data/SimObsB/skymodel-b.sim/skymodel-b_120L/' # 
    IntDir = '/lustre/cv/users/aplunket/Combo/DC2020/Tcleanb/'
    Int_vis = IntDir+'skymodel-b.alma.all_int-weighted0.116.ms/' # --> interferometry visibilities (measurement set)
    TP_image = DataDir+'skymodel-b_120L.sd.image' # --> Total power image, should be in *.image format
    myroot = 'skymodel_b.WSM' # --> Root name for your images

    if doconcat:
        os.chdir(IntDir)
        thevis = [DataDir+'skymodel-b_120L.alma.cycle6.4.2018-10-02.ms',
            DataDir+'skymodel-b_120L.alma.cycle6.1.2018-10-02.ms',
            DataDir+'skymodel-b_120L.alma.cycle6.4.2018-10-03.ms',
            DataDir+'skymodel-b_120L.alma.cycle6.1.2018-10-03.ms',
            DataDir+'skymodel-b_120L.alma.cycle6.4.2018-10-04.ms',
            DataDir+'skymodel-b_120L.alma.cycle6.1.2018-10-04.ms',
            DataDir+'skymodel-b_120L.alma.cycle6.4.2018-10-05.ms',
            DataDir+'skymodel-b_120L.alma.cycle6.1.2018-10-05.ms',
            DataDir+'skymodel-b_120L.aca.cycle6.2018-10-20.ms',
            DataDir+'skymodel-b_120L.aca.cycle6.2018-10-21.ms',
            DataDir+'skymodel-b_120L.aca.cycle6.2018-10-22.ms',
            DataDir+'skymodel-b_120L.aca.cycle6.2018-10-23.ms']
        weightscale = [1., 1., 1., 1., 1., 1., 1., 1.,
                 0.116, 0.116, 0.116, 0.116]

        concat(vis=thevis, 
               concatvis=Int_vis,
               visweightscale = weightscale)


## skymodel-c

if whichmodel == 'c':
    WorkingDir = '/lustre/cv/users/aplunket/Combo/DC2020/ModcComp/'# --> Directory where you want to work
    DataDir = '/lustre/cv/users/aplunket/Combo/DC2020/Data/SimObsC/skymodel-c.sim/skymodel-c_120L/' # 
    IntDir = '/lustre/cv/users/aplunket/Combo/DC2020/Tcleanc/'
    Int_vis = IntDir+'skymodel-c.alma.all_int-weighted0.116.ms/' # --> interferometry visibilities (measurement set)
    TP_image = DataDir+'skymodel-c_120L.sd.image' # --> Total power image, should be in *.image format
    myroot = 'skymodel_c.WSM' # --> Root name for your images

    if doconcat:
        os.chdir(IntDir)
        thevis = [DataDir+'skymodel-c_120L.alma.cycle6.4.2018-10-02.ms',
            DataDir+'skymodel-c_120L.alma.cycle6.1.2018-10-02.ms',
            DataDir+'skymodel-c_120L.alma.cycle6.4.2018-10-03.ms',
            DataDir+'skymodel-c_120L.alma.cycle6.1.2018-10-03.ms',
            DataDir+'skymodel-c_120L.alma.cycle6.4.2018-10-04.ms',
            DataDir+'skymodel-c_120L.alma.cycle6.1.2018-10-04.ms',
            DataDir+'skymodel-c_120L.alma.cycle6.4.2018-10-05.ms',
            DataDir+'skymodel-c_120L.alma.cycle6.1.2018-10-05.ms',
            DataDir+'skymodel-c_120L.aca.cycle6.2018-10-20.ms',
            DataDir+'skymodel-c_120L.aca.cycle6.2018-10-21.ms',
            DataDir+'skymodel-c_120L.aca.cycle6.2018-10-22.ms',
            DataDir+'skymodel-c_120L.aca.cycle6.2018-10-23.ms']
        weightscale = [1., 1., 1., 1., 1., 1., 1., 1.,
                 0.116, 0.116, 0.116, 0.116]

        concat(vis=thevis, 
               concatvis=Int_vis,
               visweightscale = weightscale)



os.chdir(WorkingDir)

##----------------------------------------------------------
## (1) Set up parameters

cellsize = '0.21arcsec'
imsize =  [1120,1120]
phasecenter = 'J2000 12:00:00 -35.00.00.0000'
spw = '0'
field = '0~68'
if whichmodel == 'b': 
    threshold = '39mJy'
    noisethresh=4.25 #default: 4.25
    sidelobethresh=2.0 #default: 2.0
if whichmodel == 'c': 
    threshold = '10mJy' ## meets threshold in PB map
    noisethresh=1.5 #default: 4.25
    sidelobethresh=1.25 #default: 2.0
niter=1000000

## Test tclean of interferometry data, using runtclean method
if dotclean:
    print('## pb mask, no multiscale')
    runtclean(Int_vis,imname=myroot+'.int_pb',phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'pb',pbmask=0.5,
                interactive=True,
                multiscale=False)
    print('## pb mask, multiscale')
    runtclean(Int_vis,imname=myroot+'.int_pb_multi',phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'pb',pbmask=0.5,
                interactive=True,
                multiscale=True,maxscale=10.)
    print('## auto-mask, no multiscale')
    runtclean(Int_vis,imname=myroot+'.int_auto',phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'auto-multithresh',
                noisethreshold=noisethresh,sidelobethreshold=sidelobethresh,
                interactive=True,
                multiscale=False)
    print('## auto-mask, multiscale')
    runtclean(Int_vis,imname=myroot+'.int_auto_multi',phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'auto-multithresh',
                noisethreshold=noisethresh,sidelobethreshold=sidelobethresh,
                interactive=True,
                multiscale=True,maxscale=10.)

## Run tclean with startmodel and feather together, using the runWSM method
## Test with automask and pb mask
if doimage:
    if whichmodel == 'b':
        ## pb-mask, no multiscale
        runWSM(Int_vis,TP_image, 
                myroot+'pb', phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'pb',pbmask=0.5,
                interactive=True,
                multiscale=False)
        os.system('rm -rf lowres.*')
        ## pb-mask, multiscale
        runWSM(Int_vis,TP_image, 
                myroot+'pb_multi', phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'pb',pbmask=0.5,
                interactive=True,
                multiscale=True,maxscale=10)
        os.system('rm -rf lowres.*')
        ## auto-mask, no multiscale
        runWSM(Int_vis,TP_image, 
                myroot+'auto', phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'auto-multithresh',
                noisethreshold=noisethresh,sidelobethreshold=sidelobethresh,
                interactive=True,
                multiscale=False)
        os.system('rm -rf lowres.*')
        ## auto-mask, multiscale
        runWSM(Int_vis,TP_image, 
                myroot+'auto_multi', phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'auto-multithresh',
                noisethreshold=noisethresh,sidelobethreshold=sidelobethresh,
                interactive=True,
                multiscale=True,maxscale=10)
        os.system('rm -rf lowres.*')
    if whichmodel == 'c':
        ## pb-mask, no multiscale
        print('## pb mask, no multiscale')
        runWSM(Int_vis,TP_image, 
                myroot+'pb', phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'pb',pbmask=0.5,
                interactive=True,
                multiscale=False)
        os.system('rm -rf lowres.*')
        ## pb-mask, multiscale
        print('## pb mask, multiscale')
        runWSM(Int_vis,TP_image, 
                myroot+'pb_multi', phasecenter=phasecenter, 
                spw='0', field=field, imsize=imsize, cell=cellsize,
                threshold=threshold, niter=niter,
                usemask = 'pb',pbmask=0.5,
                interactive=True,
                multiscale=True,maxscale=10)
        os.system('rm -rf lowres.*')
 

