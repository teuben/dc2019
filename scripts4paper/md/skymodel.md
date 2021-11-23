# skymodel

To run simulations and compare (lots of) maps, we need a scripting
environment (in my opinion casa is too low a level), and believe QAC
is one way to get you this. Each experiment should be in a directory
by itself, which also gives you the freedom to not mess with long
names underneath and have shorter filenames to deal with.

The description below is somewhat CASA centric, e.g. it excludes
MIRIAD's mosmem approach, or wsclean.

# Overview of Parameter Space

For the skymodel we have skymodel-b.fits, in Jy/pixel.  This image has
4096 x 0.05" pixels, which effectively limits which ALMA 12m configurations
we can use for the simulations.

We can consider the following files (numbers taken for 115GHz):

## TP images
                                                                 res    MRS
      tp[0] = skymodel-b.fits     jy/pixel                       0.05   205"
      tp[1] = sky.otf             jy/beam_TP  (via imsmooth)    50.6
      tp[2] = sky.map             jy/pixel    (immath rescaled)
      tp[3] = sky.*.dirtymap      jy/beam_TP  (via tclean(tpms))
      tp[4] = sky.*.sd            jy/beam_TP  (via simanalyze)

For these simulations we have the advantage of a Jy/pixel model, but for
real observations only the "otf" style map will be available.

## TPMS pseudo visibilities from tp2vis()

      tpms[0] = tp2vis(tp[0], deconv=False)
      tpms[1] = tp2vis(tp[1], deconv=True)

## MS from simobserve()
                                                                 res    MRS    Lmax
      ms[0] = sky.aca.cycle6.ms   (via simobserve())            10.9"   58.0"    45
      ms[1] = sky.alma.6.1.ms     (via simobserve())             2.93   24.8    161
      ms[2] = sky.alma.6.2.ms     (via simobserve())             2.00   19.7    312
      ms[3] = sky.alma.6.3.ms     (via simobserve())             1.23   14.1    500
      ms[4] = sky.alma.6.4.ms     (via simobserve())             0.798   9.74   784
      ms[5] = sky.alma.6.5.ms     (via simobserve())             0.474   5.83  1398
      ms[6] = sky.alma.6.6.ms     (via simobserve())             0.267   3.57  2516

  Of course it needs to be discussed which of this ms[] are to be used for
  the combination. Toshi was using [0,1,4] which have a nice staggering range
  of scales  from 0.8 - 58"
  The TP has a resolution of 50", so on paper this should recover all scales.

- rescaling the sky.otf to sky.map
  from h0=imstat('sky.otf') we get scaling factor **h0['sum'][0]/h0['flux'][0]**
  which is about 18156.6 for a 512 * 0.4" map
  and about 4539.2 for a 256 * 0.8" map
  This sky.map of course has the correct total flux, but is too smooth a solution
  as a Jy/pixel starmodel.

- we have at least three possible startmodels[] for hybrid combinations:

      a: None
      b: tp[0]
      c: tp[2]

- setting the various parameters to tclean/tp2vis/sdintimaging/feather/ssc are left
  out of this discussion here.

## Final Maps

Thus we have the following maps (and for each of these up to 3 different ones, 
depending on which startmodel can be used; we call them 'a', 'b' and 'c' ?)


      int1     = tclean(ms, startmodel)
      tpint1   = tclean(tpms[0] + ms, startmodel)
      tpint2   = tclean(tpms[1] + ms, startmodel)
      sdint1   = sdintimaging(tp[1], ms, startmodel)
      sdint2   = sdintimaging(tp[3], ms, startmodel)
      feather1 = feather(tp[1], int1)
      ssc1     = ssc(tp[1], int1)

This is a total of as many as 15 maps.

For example, Kaufman's hybrid would be "int1b", but if you don't have a perfect model,
you only have "int1c".


## Implementation

A series of scripts in dc2019/contrib/QAC/test/sky*.py implement this scheme. Currently
the first few are for testing, but sky4.py attempts to implement these, but finetuning
the parameters (e.g. tclean etc.) is still ongoing.


## Added Pointsources

We added two pointsource in skymodel-a.fits at (2048,1048) [0 based pixels], which is in
the south where the background is 0. The other source was placed on the "western" part of
the circular "SNR" type structure in the east part of the image, at (802,2205), again 0
based pixels.
                                                         peak             peak
 source 0-based pixel         RA              DEC        skymodel-a       skymodel-b
      A     2048 1048    12 00 00.0000    -35 00 50.000  0.1              0.00765315
      B      802 2205    12 00 05.0703    -34 59 52.140  0.130665         0.01

When convolved to a 2" beam, the flux is about

      A     ~1.6 Jy
      B     +6 Jy      (which includes a background)

## Flux
                                    whole map            region1
      Original skymodel.fits:      113100.527020  Jy
      Scaled +2pt skymodel-b.fits:   8659.028656  Jy        6644
      skymodel.otf                   7518                   6402
      gmc_120L.sd.image              7191                   6035
      gmc_2L.sd.image0.scaled        7879

There is an issue discussion this flux scaling issue of the SD vs. OTF:  https://github.com/teuben/dc2019/issues/14
possible related to a 4% re-scaling.

## Imaging

The following imaging parameters should make it possible to compare maps pixel by pixel
without the need for regridding:

      phasecenter  = 'J2000 180.0deg -35.0deg'
      imsize       = 1120
      cell         = '0.21arcsec'

this is for ALMA configurations 0 (ACA), 1 and 4, where the resulting beam is about 1.2 x 1.0".

For configuration (0,1,2) we use

      phasecenter  = 'J2000 180.0deg -35.0deg'
      imsize       = 256
      cell         = '0.8arcsec'

because the beam is about 3". These simulations run a lot faster.


For detailed comparisons we use a smaller box, excluding fairly obvious edge effects. Based on
the 1120 pixel we use a proposed

      box1     = '150,150,970,970'
                  (150,150,970,970)  674041   6657.3
               = '12:00:07.009, -35.01.26.087' to '11:59:52.995, -34.58.33.887'
      region1  = 'box[[12h00m07.009s,-35d01m26.082s],[11h59m52.990s,-34d58m33.946s]],coord=J2000'
                  (150,151,970,969)  672340   6648.2
      region2  = 'box[[12h00m07.009s,-35d01m26.090s],[11h59m52.990s,-34d58m33.850s]],coord=J2000'
                  (150,150,970,970)  673981   6656.5

      box10     = '500,500,3500,3500'
      region10  = 'box[[500pix,500pix],[3500pix,3500pix]]'
                  (500,500,3500,3500) 9006001 5590.1
      box11     = '326,326,3770,3770'
      		  11868025 6647.1
		 

But note in **imstat** this identical **box=** and **region=** do not give the same flux and pixel
count, presumably due to the curvature of the WCS.

Maps that are compared on a pixel by pixel basis, also need to be smoothed to the same beam.
The assessment methods team uses a 2" beam, and a certain physical area (maybe not quite box1).
To be confirmed.


