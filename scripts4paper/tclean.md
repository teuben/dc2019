# Testing several TCLEAN techniques

Here we describe three variations of TCLEAN on the same skymodel
simulated mosaic map.

## Imaging script

The script is found here: scriptForImaging_tcleanTest.py

Three TCLEAN variations in the script are:

### (1) ``Simple''

No interaction is needed, and mask is drawn based on a pb level of 0.3.

TCLEAN parameters:

      threshold = '38mJy' or '11mJy'
      niter = 1000000, cycleniter = 100000, cyclefactor=2.0,
      usemask = 'pb', pbmask=0.3
      interactive = False

Files: 
- inter_simple_thresh11mJy/gmc_120L.inter.simple.*
- inter_simple_thresh38mJy/gmc_120L.inter.simple.*

threshold=11mJy | threshold=38mJy
:---------------------:|:---------------------:
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.simple.thresh11mJy.pbcor.png)|![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.simple.thresh38mJy.pbcor.png)

### (2) ``Interactive''

Following Dirk's description, in which one interactively lowers the cyclethreshold until meeting the threshold.
I used (interactively) cyclethreshold = [1.9Jy, 1.0Jy, 0.6Jy, 0.4Jy, 0.2Jy, 0.1Jy,
0.06Jy, 0.04Jy, 0.02Jy, 0.011Jy].

TCLEAN parameters:

      threshold = '38mJy' or '11mJy'
      niter = 1000000, cycleniter = 100000
      usemask = 'pb', pbmask=0.3
      interactive = False      

Files:
- inter_interact_thresh11mJy/gmc_120L.inter.interactive.*
- inter_interact_thresh38mJy/gmc_120L.inter.interactive.*

threshold=11mJy | threshold=38mJy
:---------------------:|:---------------------:
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.interactive.thresh11mJy.pbcor.png)| ![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.interactive.thresh38mJy.pbcor.png)

### (3) ``Automasking'' 

Following the [CASA Automasking Guide](https://casaguides.nrao.edu/index.php/Automasking_Guide).  Our maximum
baseline was <300m, so I used the following suggested parameters:

TCLEAN parameters:

      threshold = '38mJy' or '11mJy'
      niter = 1000000, cycleniter = 100000, cyclefactor=2.0,
      usemask='auto-multithresh',
      sidelobethreshold=2.0,
      noisethreshold=4.25,
      lownoisethreshold=1.5, 
      minbeamfrac=0.3,
      growiterations=75,
      negativethreshold=0.0,

Files:
- inter_auto_thresh11mJy/gmc_120L.inter.auto.*
- inter_auto_thresh38mJy/gmc_120L.inter.auto.*

threshold=11mJy | threshold=38mJy
:---------------------:|:---------------------:
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.auto.thresh11mJy.pbcor.png)|![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.auto.thresh38mJy.pbcor.png)

## Files

Images are uploaded [here](https://drive.google.com/file/d/1hh5yNOr5-UUdzCh4ygwdacohI5VYYx-I/view?usp=sharing)

Files in testtcleanfits.tgz:
- inter_auto_thresh11mJy/gmc_120L.inter.auto.image.fits
- inter_auto_thresh11mJy/gmc_120L.inter.auto.pbcor.fits
- inter_auto_thresh11mJy/gmc_120L.inter.auto.pb.fits
- inter_auto_thresh38mJy/gmc_120L.inter.auto.image.fits
- inter_auto_thresh38mJy/gmc_120L.inter.auto.pbcor.fits
- inter_auto_thresh38mJy/gmc_120L.inter.auto.pb.fits
- inter_interact_thresh11mJy/gmc_120L.inter.interactive.image.fits
- inter_interact_thresh11mJy/gmc_120L.inter.interactive.pbcor.fits
- inter_interact_thresh11mJy/gmc_120L.inter.interactive.pb.fits
- inter_interact_thresh38mJy/gmc_120L.inter.interactive.image.fits
- inter_interact_thresh38mJy/gmc_120L.inter.interactive.pbcor.fits
- inter_interact_thresh38mJy/gmc_120L.inter.interactive.pb.fits
- inter_simple_thresh11mJy/gmc_120L.inter.simple.image.fits
- inter_simple_thresh11mJy/gmc_120L.inter.simple.pbcor.fits
- inter_simple_thresh11mJy/gmc_120L.inter.simple.pb.fits
- inter_simple_thresh38mJy/gmc_120L.inter.simple.image.fits
- inter_simple_thresh38mJy/gmc_120L.inter.simple.pbcor.fits
- inter_simple_thresh38mJy/gmc_120L.inter.simple.pb.fits
