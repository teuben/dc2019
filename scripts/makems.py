#   in CASA execute this with execfile('makems.py')
#
#   In the current version this will take ~11hr CPU and take 234GB of diskspace
#   (231GB are in trash, which you can remove afterwards)
#   Normally you will not need to run this (except if you want to experiment
#   with using different array combinations), but can just take the output MS:
#   
#   simdata_aca.i.ms  simdata_alma.cycle4.2.ms  simdata_alma.cycle4.3.ms  simdata_alma.tp.ms
#
#   Original author:     Jin Koda            24-jul-2019
#   Adapted for DC2019   Peter Teuben
#



import numpy as np
import os
import glob
import pyfits
import shutil

# Input data


infits          = 'skymodel_16k.fits'


# Other params

#antennalists    = ["aca.i.cfg",
#		   "alma.cycle4.4.cfg",
#		   "alma.cycle4.3.cfg",
#		   "alma.cycle4.2.cfg",
#		   "alma.cycle4.1.cfg"]
antennalists    = ["aca.i.cfg",
		   "alma.cycle4.3.cfg",
		   "alma.cycle4.2.cfg"]

beamTP = 56.69569
cellTP = 5.62

if not os.path.exists('trash'): os.mkdir('trash')

# Simobserve

default('simobserve')

skymodel        = infits
project         = 'mkptg'

indirection     = 'J2000 12h00m00 -35d00m00'
incell          = '0.015arcsec'
mapsize         = ['2.5arcmin','2.5arcmin']
maptype         = 'hexagonal'
incenter        = '115GHz'
inwidth         = '2GHz'
image,head      = pyfits.getdata(skymodel,0,header=True)
inbright        = str(image.max()) + 'Jy/pixel'
setpointings    = True
integration     = '10s'
graphics        = 'none'
obsmode         = 'int'
totaltime       = '1000s'
thermalnoise    = ""
pointingspacing = '0.4arcmin'
antennalist     = "aca.i.cfg"

simobserve()


# Split .ptg

ptgfile          = 'mosaic.ptg'
simobservedimage = 'mosaic.image'
shutil.copy2(project+'/'+project+'.'+antennalist[:-4]+'.ptg.txt',ptgfile)
shutil.copytree(project+'/'+project+'.'+antennalist[:-4]+'.skymodel',simobservedimage)

shutil.move(project,'trash/')

f     = open(ptgfile,'r')
lines = f.readlines()
f.close()
lines = lines[1:]

ptgs=[]
for ii in range(len(lines)):
    ptg='mosaic_%003d.ptg' % (ii)
    ptgs.append(ptg)
    f = open(ptg,'w')
    f.write(lines[ii])
    f.close()

print ptgs

# Run simobserve

setpointings = False
integration  = '10s'
obsmode      = 'int'
totaltime    = '600s'
hourangle    = 'transit'

projects=[]

for ptg in ptgs:    
    ptgfile = ptg
    project = ptg[:-4]
    projects.append(project)
    for antennalist in antennalists:
        print "Working on (%s, %s)" % (ptg, antennalist)
        simobserve()


# Concat

vislist=[]
for antennalist in antennalists:
    config   = antennalist[:-4]
    outname  = 'simdata_' + config + '.ms'
    vis      = []
    for project in projects:
        vis.append(project+'/'+project+'.'+antennalist[:-4]+'.ms')
    print vis
    concat(vis=vis,concatvis=outname,respectname=True)
    vislist.append(outname)


# Clean up
for project in projects:
    shutil.move(project,'trash/')


# For TP2VIS

bmaj='%farcsec' % (beamTP)
bmin='%farcsec' % (beamTP)
bpa ='0deg'

print "Smooth image with TP beam:", bmaj, bmin, bpa

smofile='mosaic.image.smo'
imsmooth(imagename=simobservedimage,outfile=smofile,kernel='gauss', major=bmaj, minor=bmin, pa=bpa)

cell = np.abs(imhead(simobservedimage,mode='list')['cdelt1'])*180.*3600./np.pi
nbin = long(cellTP/cell)

print "Rebin image (cell, cellTP, nbin):", cell, cellTP, nbin
regfile='mosaic_TP.image'
imrebin(smofile,regfile,factor=[nbin,nbin])

print "Running TP2VIS"
execfile('tp2vis.py')
infile  = regfile
outfile = 'simdata_alma.tp.ms'
ptgfile = 'mosaic.ptg'
tp2vis(infile,outfile,ptgfile,nvgrp=5,rms=1.0,winpix=3)


vislist.append(outfile)


# Time offsets

print "Time offsets for: ", vislist

for iv in range(len(vislist)):
    msname = vislist[iv]
    tb.open(msname,nomodify=False)
    time0 = tb.getcol("TIME")
    time1 = tb.getcol("TIME_CENTROID")
    if (iv == 0): t0 = time0[0]
    time0 = [t0 + 24.*60.*60.*iv + 1.*ii for ii in range(len(time0))]
    time1 = time0
    tb.putcol('TIME',time0)
    tb.putcol('TIME_CENTROID',time1)
    tb.close()

