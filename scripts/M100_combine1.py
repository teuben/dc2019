# Script taken from:   https://casaguides.nrao.edu/index.php/M100_Band3_Combine_5.4
#
# this whole script can be re-run, as it deletes data that are in the way.
# it should take about 30 minutes to complete.
# and needs about 42 GB of data. Produces all the plots that are on the casaguide page,
# and more.
#
#  Example to get the 3 needed datasets exposed here, YMMV:
#
#     tar zxf ../data/M100_Band3_12m_CalibratedData.tgz
#     mv M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms .
#     tar zxf ../data/M100_Band3_7m_CalibratedData.tgz
#     mv M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms .
#     tar zxf ../data/M100_Band3_ACA_ReferenceImages_5.1.tgz
#     mv M100_Band3_ACA_ReferenceImages_5.1/M100_TP_CO_cube.spw3.image.bl .
#


#
os.system('rm -rf M100_*m.ms.listobs')
listobs('M100_Band3_12m_CalibratedData.ms',listfile='M100_12m.ms.listobs')
listobs('M100_Band3_7m_CalibratedData.ms',listfile='M100_7m.ms.listobs')


#
os.system('rm -rf M100_12m_CO.ms')
split(vis='M100_Band3_12m_CalibratedData.ms',
      outputvis='M100_12m_CO.ms',spw='0',field='M100',
      datacolumn='data',keepflags=False)
os.system('rm -rf M100_7m_CO.ms')
split(vis='M100_Band3_7m_CalibratedData.ms',
      outputvis='M100_7m_CO.ms',spw='3,5',field='M100',
      datacolumn='data',keepflags=False)

#
os.system('rm -rf *m_mosaic.png')
au.plotmosaic('M100_12m_CO.ms',sourceid='0',doplot=True,figfile='12m_mosaic.png')
au.plotmosaic('M100_7m_CO.ms',sourceid='0',doplot=True,figfile='7m_mosaic.png')

#
os.system('rm -rf 7m_WT.png 12m_WT.png')
plotms(vis='M100_12m_CO.ms',yaxis='wt',xaxis='uvdist',spw='0:200',
       coloraxis='spw',plotfile='12m_WT.png',showgui=True)
#
plotms(vis='M100_7m_CO.ms',yaxis='wt',xaxis='uvdist',spw='0~1:200',
       coloraxis='spw',plotfile='7m_WT.png',showgui=True)

# Concat and scale weights
os.system('rm -rf M100_combine_CO.ms')
concat(vis=['M100_12m_CO.ms','M100_7m_CO.ms'],
       concatvis='M100_combine_CO.ms')

# In CASA
os.system('rm -rf combine_CO_WT.png')
plotms(vis='M100_combine_CO.ms',yaxis='wt',xaxis='uvdist',spw='0~2:200',
       coloraxis='spw',plotfile='combine_CO_WT.png',showgui=True)

os.system('rm -rf M100_combine_uvdist.png')
plotms(vis='M100_combine_CO.ms',yaxis='amp',xaxis='uvdist',spw='', avgscan=True,
       avgchannel='5000', coloraxis='spw',plotfile='M100_combine_uvdist.png',showgui=True)


os.system('rm -rf M100_combine_vel.png')
plotms(vis='M100_combine_CO.ms',yaxis='amp',xaxis='velocity',spw='', avgtime='1e8',avgscan=True,coloraxis='spw',avgchannel='5',
       transform=True,freqframe='LSRK',restfreq='115.271201800GHz', plotfile='M100_combine_vel.png',showgui=True)

### Define clean parameters
vis='M100_combine_CO.ms'
prename='M100_combine_CO_cube'
imsize=800
cell='0.5arcsec'
minpb=0.2
restfreq='115.271201800GHz'
outframe='LSRK'
spw='0~2'
width='5km/s'
start='1400km/s'
nchan=70
robust=0.5
phasecenter='J2000 12h22m54.9 +15d49m15'

### Setup stopping criteria with multiplier for rms.
stop=3.

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
myimage=prename+'_dirty.image'
bigstat=imstat(imagename=myimage)
peak= bigstat['max'][0]
print 'peak (Jy/beam) in cube = '+str(peak)

# find the RMS of a line free channel (should be around 0.011
chanstat=imstat(imagename=myimage,chans='4')
rms1= chanstat['rms'][0]
chanstat=imstat(imagename=myimage,chans='66')
rms2= chanstat['rms'][0]
rms=0.5*(rms1+rms2)        

print 'rms (Jy/beam) in a channel = '+str(rms)


sidelobethresh = 2.0
noisethresh = 4.25
minbeamfrac = 0.3
lownoisethresh= 1.5
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

myimage='M100_combine_CO_cube.image'
chanstat=imstat(imagename=myimage,chans='4')
rms1= chanstat['rms'][0]
chanstat=imstat(imagename=myimage,chans='66')
rms2= chanstat['rms'][0]
rms=0.5*(rms1+rms2)
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

os.system('rm -rf *.fits')
exportfits(imagename='M100_combine_CO_cube.image',fitsimage='M100_combine_CO_cube.image.fits')

exportfits(imagename='M100_combine_CO_cube.pb',fitsimage='M100_combine_CO_cube.pb.fits')

exportfits(imagename='M100_combine_CO_cube.image.mom0',fitsimage='M100_combine_CO_cube.image.mom0.fits')

exportfits(imagename='M100_combine_CO_cube.image.mom0.pbcor',fitsimage='M100_combine_CO_cube.image.mom0.pbcor.fits')

exportfits(imagename='M100_combine_CO_cube.image.mom1',fitsimage='M100_combine_CO_cube.image.mom1.fits')





imhead('M100_TP_CO_cube.spw3.image.bl',mode='get',hdkey='restfreq')
imhead('M100_combine_CO_cube.image',mode='get',hdkey='restfreq')

os.system('rm -rf M100_TP_CO_cube.regrid')
imregrid(imagename='M100_TP_CO_cube.spw3.image.bl',
         template='M100_combine_CO_cube.image',
         axes=[0, 1],
         output='M100_TP_CO_cube.regrid')


os.system('rm -rf M100_TP_CO_cube.regrid.subim')
imsubimage(imagename='M100_TP_CO_cube.regrid',
           outfile='M100_TP_CO_cube.regrid.subim',
           box='219,148,612,579')
os.system('rm -rf M100_combine_CO_cube.image.subim')
imsubimage(imagename='M100_combine_CO_cube.image',
           outfile='M100_combine_CO_cube.image.subim',
           box='219,148,612,579')



os.system('rm -rf M100_combine_CO_cube.pb.subim')
imsubimage(imagename='M100_combine_CO_cube.pb',
           outfile='M100_combine_CO_cube.pb.subim',
           box='219,148,612,579')


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

myimage = 'M100_TP_CO_cube.regrid.subim'
chanstat = imstat(imagename=myimage,chans='4')
rms1 = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2 = chanstat['rms'][0]
rms = 0.5*(rms1+rms2)  

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




myimage = 'M100_Feather_CO.image'
chanstat = imstat(imagename=myimage,chans='4')
rms1 = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2 = chanstat['rms'][0]
rms = 0.5*(rms1+rms2)  


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


imstat('M100_TP_CO_cube.regrid.subim.depb')['flux']
imstat('M100_Feather_CO.image')['flux']
imstat('M100_Feather_CO.image.pbcor')['flux']

# 5.4 => 2822.29454956  2822.29259255  3055.66039175
# 5.5 => 2825.9993648   2825.99752571  3054.25147157
# 5.6 => 2826.22910583  2826.22718072  3050.38152141
