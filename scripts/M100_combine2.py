#  Use the new CASA5 QAC bench data to run the M100 combination
#
#  curl http://admit.astro.umd.edu/~teuben/QAC/qac_bench5.tar.gz | tar zxf -
#
import os

pdir = 'M100qac'

ms1 = '../M100_aver_12.ms'
ms2 = '../M100_aver_7.ms'
tp1 = '../M100_TP_CO_cube.bl.image'


# QAC: start with a clean 'pdir' and do all the work inside
qac_begin(pdir)
qac_project(pdir)
os.chdir(pdir)

# Assert files exist
print("If you do not have the 3 QAC benchmark files, issue")
print("curl http://admit.astro.umd.edu/~teuben/QAC/qac_bench5.tar.gz | tar zxf -")
QAC.assertf(ms1)
QAC.assertf(ms2)
QAC.assertf(tp1)



# sanity
qac_stats(ms1)
qac_stats(ms2)
qac_stats(tp1)

#
listobs(ms1,listfile=ms1 + '.listobs',overwrite=True)
listobs(ms2,listfile=ms2 + '.listobs',overwrite=True)


#
os.system('rm -rf *m_mosaic.png')
au.plotmosaic(ms1,sourceid='0',doplot=True,figfile='12m_mosaic.png')
au.plotmosaic(ms2,sourceid='0',doplot=True,figfile='7m_mosaic.png')

#
plotms(vis=ms1,yaxis='wt',xaxis='uvdist',spw='0:200',coloraxis='spw',plotfile='12m_WT.png',showgui=True,overwrite=True)
plotms(vis=ms2,yaxis='wt',xaxis='uvdist',spw='0~1:200',coloraxis='spw',plotfile='7m_WT.png',showgui=True,overwrite=True)

ms3 = 'M100_combine_CO.ms'

# Concat and scale weights
os.system('rm -rf %s' % ms3)
if True:
    concat(vis=[ms1,ms2], concatvis=ms3)
else:
    concat(vis=[ms2], concatvis=ms3)    

# In CASA
plotms(vis=ms3,yaxis='wt',xaxis='uvdist',spw='0~2:200',coloraxis='spw',plotfile='combine_CO_WT.png',showgui=True,overwrite=True)

plotms(vis=ms3,yaxis='amp',xaxis='uvdist',spw='', avgscan=True,
       avgchannel='5000', coloraxis='spw',plotfile='M100_combine_uvdist.png',showgui=True,overwrite=True)

plotms(vis=ms3,yaxis='amp',xaxis='velocity',spw='', avgtime='1e8',avgscan=True,coloraxis='spw',avgchannel='5',
       transform=True,freqframe='LSRK',restfreq='115.271201800GHz', plotfile='M100_combine_vel.png',showgui=True,overwrite=True)

### Define clean parameters
vis      = ms3          
prename  = 'M100_combine_CO_cube'     # or replace .ms by _cube   # 'M100_combine_CO.ms'
imsize   = 800
cell     = '0.5arcsec'
minpb    = 0.2
restfreq = '115.271201800GHz'         # ? should be '115.271202GHz' to match the QAC benchmark data
outframe = 'LSRK'
spw      = ''
width    = '5km/s'
start    = '1400km/s'
nchan    = 70
robust   = 0.5
phasecenter = 'J2000 12h22m54.9 +15d49m15'

### Setup stopping criteria with multiplier for rms.
stop        = 3.

### Make initial dirty image
os.system('rm -rf '+prename+'_dirty.*')
tclean(vis=vis,
    imagename=prename + '_dirty',
    gridder='mosaic',
    deconvolver='hogbom',
    pbmask=minpb,
    imsize=imsize,
    cell=cell,
    spw=spw,
    weighting='briggs',
    robust=robust,
    phasecenter=phasecenter,
    specmode='cube',
    width=width,
    start=start,
    nchan=nchan,
    restfreq=restfreq,
    outframe=outframe,
    veltype='radio',
    restoringbeam='common',
    mask='',
    niter=0,
    interactive=False)


### Find the peak in the dirty cube.
myimage = prename+'_dirty.image'
bigstat = imstat(imagename=myimage)
peak    = bigstat['max'][0]
print 'peak (Jy/beam) in cube = '+str(peak)

# find the RMS of a line free channel (should be around 0.011
chanstat = imstat(imagename=myimage,chans='4')
rms1     = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2     = chanstat['rms'][0]
rms      = 0.5*(rms1+rms2)        

print 'rms (Jy/beam) in a channel = '+str(rms)


sidelobethresh = 2.0
noisethresh    = 4.25
minbeamfrac    = 0.3
lownoisethresh = 1.5
negativethresh = 0.0

os.system('rm -rf ' + prename + '.*')
tclean(vis=vis,
    imagename=prename,
    gridder='mosaic',
    deconvolver='hogbom',
    pbmask=minpb,
    imsize=imsize,
    cell=cell,
    spw=spw,
    weighting='briggs',
    robust=robust,
    phasecenter=phasecenter,
    specmode='cube',
    width=width,
    start=start,
    nchan=nchan,
    restfreq=restfreq,
    outframe=outframe,
    veltype='radio',
    restoringbeam='common',
    mosweight=True,
    niter=10000,
    usemask='auto-multithresh',
    threshold=str(stop*rms)+'Jy/beam',
    sidelobethreshold=sidelobethresh,
    noisethreshold=noisethresh,
    lownoisethreshold=lownoisethresh, 
    minbeamfrac=minbeamfrac,
    growiterations=75,
    negativethreshold=negativethresh,
    interactive=False,
    pbcor=True)

#
# viewer('M100_combine_CO_cube.image',gui=True)

myimage  = 'M100_combine_CO_cube.image'
chanstat = imstat(imagename=myimage,chans='4')
rms1     = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2     = chanstat['rms'][0]
rms      = 0.5*(rms1+rms2)
print 'rms in a channel = '+str(rms)


os.system('rm -rf M100_combine_CO_cube.image.mom0')
immoments(imagename = 'M100_combine_CO_cube.image',
         moments = [0],
         axis = 'spectral',chans = '9~61',
         mask='M100_combine_CO_cube.pb>0.3',
         includepix = [rms*2,100.],
         outfile = 'M100_combine_CO_cube.image.mom0')

os.system('rm -rf M100_combine_CO_cube.image.mom1')
immoments(imagename = 'M100_combine_CO_cube.image',
         moments = [1],
         axis = 'spectral',chans = '9~61',
         mask='M100_combine_CO_cube.pb>0.3',
         includepix = [rms*5.5,100.],
         outfile = 'M100_combine_CO_cube.image.mom1')

os.system('rm -rf M100_combine_CO_cube.image.mom*.png')
imview (raster=[{'file': 'M100_combine_CO_cube.image.mom0',
                 'range': [-0.3,25.],'scaling': -1.3,'colorwedge': True}],
         zoom={'blc': [190,150],'trc': [650,610]},
         out='M100_combine_CO_cube.image.mom0.png')

imview (raster=[{'file': 'M100_combine_CO_cube.image.mom1',
                 'range': [1440,1695],'colorwedge': True}],
         zoom={'blc': [190,150],'trc': [650,610]}, 
         out='M100_combine_CO_cube.image.mom1.png')


os.system('rm -rf M100_combine_CO_cube.pb.1ch')
imsubimage(imagename='M100_combine_CO_cube.pb',
           outfile='M100_combine_CO_cube.pb.1ch',
           chans='35')

os.system('rm -rf M100_combine_CO_cube.image.mom0.pbcor')
impbcor(imagename='M100_combine_CO_cube.image.mom0',
    pbimage='M100_combine_CO_cube.pb.1ch',
    outfile='M100_combine_CO_cube.image.mom0.pbcor')

# 
imview (raster=[{'file': 'M100_combine_CO_cube.image.mom0',
                 'range': [-0.3,25.],'scaling': -1.3},
                {'file': 'M100_combine_CO_cube.image.mom0.pbcor',
                 'range': [-0.3,25.],'scaling': -1.3}],
         zoom={'blc': [190,150],'trc': [650,610]})


os.system('rm -rf M100_combine_CO_cube.image.mom0.pbcor.png')
imview (raster=[{'file': 'M100_combine_CO_cube.image.mom0.pbcor',
                 'range': [-0.3,25.],'scaling': -1.3,'colorwedge': True}],
         zoom={'blc': [190,150],'trc': [650,610]},
         out='M100_combine_CO_cube.image.mom0.pbcor.png')

qac_fits('M100_combine_CO_cube.image')
qac_fits('M100_combine_CO_cube.pb')
qac_fits('M100_combine_CO_cube.image.mom0')
qac_fits('M100_combine_CO_cube.image.mom0.pbcor')
qac_fits('M100_combine_CO_cube.image.mom1')



imhead(tp1,                         mode='get',hdkey='restfreq')
imhead('M100_combine_CO_cube.image',mode='get',hdkey='restfreq')

imregrid(imagename=tp1,
         template='M100_combine_CO_cube.image',
         axes=[0, 1],
         output='M100_TP_CO_cube.regrid',
         overwrite=True)

imsubimage(imagename='M100_TP_CO_cube.regrid',
           outfile='M100_TP_CO_cube.regrid.subim',
           box='219,148,612,579',
           overwrite=True)

imsubimage(imagename='M100_combine_CO_cube.image',
           outfile='M100_combine_CO_cube.image.subim',
           box='219,148,612,579',
           overwrite=True)

imsubimage(imagename='M100_combine_CO_cube.pb',
           outfile='M100_combine_CO_cube.pb.subim',
           box='219,148,612,579',
           overwrite=True)

os.system('rm -rf M100_TP_CO_cube.regrid.subim.depb')
immath(imagename=['M100_TP_CO_cube.regrid.subim',
                  'M100_combine_CO_cube.pb.subim'],
       expr='IM0*IM1',
       outfile='M100_TP_CO_cube.regrid.subim.depb')

os.system('rm -rf M100_Feather_CO.image')
feather(imagename='M100_Feather_CO.image',
        highres='M100_combine_CO_cube.image.subim',
        lowres='M100_TP_CO_cube.regrid.subim.depb')

# Make Moment Maps of the Feathered Images

myimage  = 'M100_TP_CO_cube.regrid.subim'
chanstat = imstat(imagename=myimage,chans='4')
rms1     = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2     = chanstat['rms'][0]
rms      = 0.5*(rms1+rms2)  

os.system('rm -rf M100_TP_CO_cube.regrid.subim.mom0')
immoments(imagename='M100_TP_CO_cube.regrid.subim',
         moments=[0],
         axis='spectral',
         chans='10~61',
         includepix=[rms*2., 50],
         outfile='M100_TP_CO_cube.regrid.subim.mom0')
 
os.system('rm -rf M100_TP_CO_cube.regrid.subim.mom1')
immoments(imagename='M100_TP_CO_cube.regrid.subim',
         moments=[1],
         axis='spectral',
         chans='10~61',
         includepix=[rms*5.5, 50],
         outfile='M100_TP_CO_cube.regrid.subim.mom1')


os.system('rm -rf M100_TP_CO_cube.regrid.subim.mom*.png')
imview(raster=[{'file': 'M100_TP_CO_cube.regrid.subim.mom0',
                'range': [0., 1080.],
                'scaling': -1.3,
                'colorwedge': True}],
       out='M100_TP_CO_cube.regrid.subim.mom0.png')
 
imview(raster=[{'file': 'M100_TP_CO_cube.regrid.subim.mom1',
                'range': [1440, 1695],
                'colorwedge': True}], 
       out='M100_TP_CO_cube.regrid.subim.mom1.png')




myimage  = 'M100_Feather_CO.image'
chanstat = imstat(imagename=myimage,chans='4')
rms1     = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2     = chanstat['rms'][0]
rms      = 0.5*(rms1+rms2)  


os.system('rm -rf M100_Feather_CO.image.mom0')
immoments(imagename='M100_Feather_CO.image',
         moments=[0],
         axis='spectral',
         chans='10~61',
         includepix=[rms*2., 50],
         outfile='M100_Feather_CO.image.mom0')
 
os.system('rm -rf M100_Feather_CO.image.mom1')
immoments(imagename='M100_Feather_CO.image',
         moments=[1],
         axis='spectral',
         chans='10~61',
         includepix=[rms*5.5, 50],
         outfile='M100_Feather_CO.image.mom1')

os.system('rm -rf M100_Feather_CO.image.mom*.png')
imview(raster=[{'file': 'M100_Feather_CO.image.mom0',
                'range': [-0.3, 25.],
                'scaling': -1.3,
                'colorwedge': True}],
       out='M100_Feather_CO.image.mom0.png')
 
imview(raster=[{'file': 'M100_Feather_CO.image.mom1',
                'range': [1440, 1695],
                'colorwedge': True}], 
       out='M100_Feather_CO.image.mom1.png')



os.system('rm -rf M100_Feather_CO.image.pbcor')
immath(imagename=['M100_Feather_CO.image',
                  'M100_combine_CO_cube.pb.subim'],
       expr='IM0/IM1',
       outfile='M100_Feather_CO.image.pbcor')


os.system('rm -rf M100_combine_CO_cube.pb.1ch.subim')
imsubimage(imagename='M100_combine_CO_cube.pb.subim',
           outfile='M100_combine_CO_cube.pb.1ch.subim',
           chans='35')

os.system('rm -rf M100_Feather_CO.image.mom0.pbcor')
immath(imagename=['M100_Feather_CO.image.mom0',
                  'M100_combine_CO_cube.pb.1ch.subim'],
        expr='IM0/IM1',
        outfile='M100_Feather_CO.image.mom0.pbcor')

os.system('rm -rf M100_Feather_CO.image.mom0.pbcor.png')
imview(raster=[{'file': 'M100_Feather_CO.image.mom0.pbcor',
                'range': [-0.3, 25.],
                'scaling': -1.3,
                'colorwedge': True}],
       out='M100_Feather_CO.image.mom0.pbcor.png')

imstat('M100_combine_CO_cube.image.subim')


f1=imstat('M100_TP_CO_cube.regrid.subim.depb')['flux']
f2=imstat('M100_Feather_CO.image')['flux']
f3=imstat('M100_Feather_CO.image.pbcor')['flux']

print("%g %g %g" % (f1,f2,f3))

qac_end()

# full:

# 5.4 => 2822.29454956  2822.29259255  3055.66039175
# 5.5 => 2825.9993648   2825.99752571  3054.25147157
# 5.6 => 2826.22910583  2826.22718072  3050.38152141

# benchmark 5km/s

# 5.6    2852.29        2853.72        3084.51

#  (2972 +/- 319 Jy km/s from the BIMA SONG; Helfer et al. 2003).
