# Testing several TCLEAN techniques

Here we describe three variations of TCLEAN on the same skymodel
simulated mosaic map.

## Imaging script

The script is found here: scriptForImaging_tcleanTest.py

Three variations are:

(1) ``Simple'', where no interaction is needed, and mask is drawn
based on a pb level of 0.3.

      threshold = '38mJy' or '11mJy'
      niter = 1000000, cycleniter = 100000, cyclefactor=2.0,
      usemask = 'pb', pbmask=0.3
      interactive = False

Files: 
- inter_simple_thresh11mJy/gmc_120L.inter.simple.*
- inter_simple_thresh38mJy/gmc_120L.inter.simple.*

(2) ``Interactive'', following Dirk's description, in which one
interactively lowers the cyclethreshold until meeting the threshold.
I used (interactively) cyclethreshold = [1.9Jy, 1.0Jy, 0.6Jy, 0.4Jy, 0.2Jy, 0.1Jy,
0.06Jy, 0.04Jy, 0.02Jy, 0.011Jy].]

      threshold = '38mJy' or '11mJy'
      niter = 1000000, cycleniter = 100000
      usemask = 'pb', pbmask=0.3
      interactive = False      

Files:
- inter_interact_thresh11mJy/gmc_120L.inter.interactive.*
- inter_interact_thresh38mJy/gmc_120L.inter.interactive.*

(3) ``Automasking,'' following
https://casaguides.nrao.edu/index.php/Automasking_Guide.  Our maximum
baseline was <300m, so I used the following suggested parameters:

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
