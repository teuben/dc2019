# Testing several TCLEAN techniques

Here we describe variations of TCLEAN on the same skymodel
simulated mosaic map.

## Test multi-scale

### Imaging script

The script is found here: [scriptForImaging_modular_v2.py](https://github.com/teuben/dc2019/blob/master/scripts4paper/scriptForImaging_modular_v2.py)

Int, WSM, WSM+feather | mask | multiscale  | flux | min | max |
:---------------------|:----------------------:|:----------------------:|:---------------------:|:---------------------:|:--------------------:
Int | pb| false|1233.9|-1.007|3.347
Int | pb| true|1992.6|-0.604|2.785
Int | auto | false|2029.5|-0.908|2.808
Int| auto|true|1733.7|-1.198|2.664
WSM| pb| false|9288.4|-0.522|3.300
WSM+feather |pb|false|7912.8|-0.562|3.311
WSM| pb|true|9702.4|-0.492|3.307
WSM+feather| pb|true|7919.0|-0.523|3.306
WSM| auto|false|10219.6|-0.378|3.390
WSM+feather| auto|false|7839.9|-0.581|3.334
WSM |auto|true|9739.2|-0.557|3.197
WSM+feather| auto|true|7839.4|-0.549|3.175

mask | no multiscale  | multiscale
:--------------------:|:---------------------:|:---------------------:
pbmask | ![pbmask multiscale
false](https://github.com/adeleplunkett/myimages/blob/master/modbcompare/skymodel_b.WSM.int_pb.TCLEAN.pbcor.fits.cmr.rainforest.png)|![pbmask
multiscale true](https://github.com/adeleplunkett/myimages/blob/master/modbcompare/skymodel_b.WSM.int_pb_multi.TCLEAN.pbcor.fits.cmr.rainforest.png)
automask |![automask multiscale
false](https://github.com/adeleplunkett/myimages/blob/master/modbcompare/skymodel_b.WSM.int_auto.TCLEAN.pbcor.fits.cmr.rainforest.png)|![automask
multiscale
true](https://github.com/adeleplunkett/myimages/blob/master/modbcompare/skymodel_b.WSM.int_auto_multi.TCLEAN.pbcor.fits.cmr.rainforest.png)

pbmask  | auto-mask
:---------------------:|:---------------------:
![TCLEAN with startmodel](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.pb.TCLEAN.pbcor.fits.cmr.rainforest.png)|![FEATHER](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.pb.combined.image.pbcor.fits.cmr.rainforest.png)
![TCLEAN with startmodel](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.auto.TCLEAN.pbcor.fits.cmr.rainforest.png)|![FEATHER](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.auto.combined.image.pbcor.fits.cmr.rainforest.png)

## Previous TCLEAN tests without multi-scale

### Imaging script

The script is found here: [scriptForImaging_tcleanTest.py](https://github.com/teuben/dc2019/blob/master/scripts4paper/scriptForImaging_tcleanTest.py)

### (1) ``Simple''

No interaction is needed, and mask is drawn based on a pb level of 0.3.

TCLEAN parameters:

      threshold = '38mJy' or '11mJy'
      niter = 1000000, cycleniter = 100000, cyclefactor=2.0,
      usemask = 'pb', pbmask=0.3
      interactive = False

Files: 
- gmc_120L.inter.simple.image11mJy.feather*.fits
- gmc_120L.inter.simple.image38mJy.feather*.fits
- inter_simple_thresh11mJy/gmc_120L.inter.simple.*
- inter_simple_thresh38mJy/gmc_120L.inter.simple.*

threshold=11mJy | threshold=38mJy
:---------------------:|:---------------------:
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean_feather/gmc_120L.inter.simple.image11mJy.feather.pbcor.fits.cmr.rainforest.png)|![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean_feather/gmc_120L.inter.simple.image38mJy.feather.pbcor.fits.cmr.rainforest.png)
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
- gmc_120L.inter.interactive.image11mJy.feather*.fits
- gmc_120L.inter.interactive.image38mJy.feather*.fits
- inter_interact_thresh11mJy/gmc_120L.inter.interactive.*
- inter_interact_thresh38mJy/gmc_120L.inter.interactive.*

threshold=11mJy | threshold=38mJy
:---------------------:|:---------------------:
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean_feather/gmc_120L.inter.interactive.image11mJy.feather.pbcor.fits.cmr.rainforest.png)| ![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean_feather/gmc_120L.inter.interactive.image38mJy.feather.pbcor.fits.cmr.rainforest.png)
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.interactive.thresh11mJy.pbcor.png)| ![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.interactive.thresh38mJy.pbcor.png)

### (3) ``Automasking'' 

Following the [CASA Automasking Guide](https://casaguides.nrao.edu/index.php/Automasking_Guide).  Our maximum
baseline was <300m, so I used the following suggested parameters.

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
- gmc_120L.inter.auto.image11mJy.feather*.fits
- gmc_120L.inter.auto.image38mJy.feather*.fits
- inter_auto_thresh11mJy/gmc_120L.inter.auto.*
- inter_auto_thresh38mJy/gmc_120L.inter.auto.*

threshold=11mJy | threshold=38mJy
:---------------------:|:---------------------:
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean_feather/gmc_120L.inter.auto.image11mJy.feather.pbcor.fits.cmr.rainforest.png)|![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean_feather/gmc_120L.inter.auto.image38mJy.feather.pbcor.fits.cmr.rainforest.png)
![threshold=11mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.auto.thresh11mJy.pbcor.png)|![threshold=38mJy](https://github.com/adeleplunkett/myimages/blob/master/tclean/gmc_120L.inter.auto.thresh38mJy.pbcor.png)

### (4) Simple (pbmask) versus ``Automasking'' when using startmodel

Something interesting happens when using TCLEAN with
startmodel='singledish.jyPerPix', and then feathering.  The TCLEAN
apparently over-estimates the flux, and then FEATHER brings the flux
back down.

In the following table, I show the flux in a large region of the map
(box='300,300,820,820'), and around the point source in the south (box
= '552,315,568,330').  While the auto-masking version seems to 'lose' flux in
the feather step, more flux is still recovered compared with the
pbmask method in the larger region.  Less flux is recovered around the
point source.  (Note: needs to be compared with 'True' flux.)

|  | flux | min | max |
:---------------------|:---------------------:|:---------------------:|:--------------------:
Larger region: | | | |
pbmask, TCLEAN | 3730.39 | -0.0036 | 3.26
pbmask, Feather | 3759.05 | -0.0092 | 3.31
auto-mask, TCLEAN | 4690.32|  -0.0030 | 3.46
auto-mask, Feather | 3894.03 | -0.089 | 3.36
Point source: | | | |
pbmask, TCLEAN | 2.71  | 0.12 | 1.36 
pbmask, Feather | 2.15  | 0.050  | 1.29
auto-mask, TCLEAN | 3.04 |0.16 | 1.41
auto-mask, Feather | 2.07| 0.043| 1.28

pbmask  | auto-mask
:---------------------:|:---------------------:
![TCLEAN with startmodel](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.pb.TCLEAN.pbcor.fits.cmr.rainforest.png)|![FEATHER](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.pb.combined.image.pbcor.fits.cmr.rainforest.png)
![TCLEAN with startmodel](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.auto.TCLEAN.pbcor.fits.cmr.rainforest.png)|![FEATHER](https://github.com/adeleplunkett/myimages/blob/master/startmodel/gmc_120L.WSM.auto.combined.image.pbcor.fits.cmr.rainforest.png)


## Files
### Feathered images are uploaded [here](https://drive.google.com/file/d/1ALiCJk_UgTaAyaApiBohUnVvl6K4c2OL/view?usp=sharing)

Files in testtclean_featherfits.tgz:
- gmc_120L.inter.auto.image11mJy.feather.fits
- gmc_120L.inter.auto.image11mJy.feather.pbcor.fits
- gmc_120L.inter.auto.image38mJy.feather.fits
- gmc_120L.inter.auto.image38mJy.feather.pbcor.fits
- gmc_120L.inter.interactive.image11mJy.feather.fits
- gmc_120L.inter.interactive.image11mJy.feather.pbcor.fits
- gmc_120L.inter.interactive.image38mJy.feather.fits
- gmc_120L.inter.interactive.image38mJy.feather.pbcor.fits
- gmc_120L.inter.simple.image11mJy.feather.fits
- gmc_120L.inter.simple.image11mJy.feather.pbcor.fits
- gmc_120L.inter.simple.image38mJy.feather.fits
- gmc_120L.inter.simple.image38mJy.feather.pbcor.fits


### Interferometry only images are uploaded [here](https://drive.google.com/file/d/1hh5yNOr5-UUdzCh4ygwdacohI5VYYx-I/view?usp=sharing)

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

### Images to test the startmodel with auto-masking versus pbmask are uploaded [here](https://drive.google.com/file/d/1DhYLYWlQMJQ3hilCFkfrmLdEvBXjCYAL/view?usp=sharing)

Files in startmodel_testmasks.tgz:
- pbthresh39mJy/gmc_120L.WSM.pb.combined.image.pbcor.fits (--> pbmask,
feather image)
- pbthresh39mJy/gmc_120L.WSM.pb.TCLEAN.pbcor.fits (--> pbmask,
tclean image)
- autothresh39mJy/gmc_120L.WSM.auto.combined.image.pbcor.fits (--> automask,
feather image)
- autothresh39mJy/gmc_120L.WSM.auto.TCLEAN.pbcor.fits (--> automask,
tclean image)
