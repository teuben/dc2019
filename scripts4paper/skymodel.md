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

We can consider the following files:

## TP images
                                                                 res    MRS
      tp[0] = skymodel-b.fits     jy/pixel                       0.05   205"
      tp[1] = sky.otf             jy/beam_TP  (via imsmooth)    50.6
      tp[2] = sky.map             jy/pixel    (immath rescaled)
      tp[3] = sky.*.dirtymap      jy/beam_TP  (via tclean(tpms))

## TPMS pseudo visibilities from tp2vis()

      tpms[0] = tp2vis(tp[0], deconv=False)
      tpms[1] = tp2vis(tp[1], deconv=True)

## MS from simobserve()
                                                                 res    MRS
      ms[0] = sky.aca.cycle6.ms   (via simobserve())            10.9"   58.0"
      ms[1] = sky.alma.6.1.ms     (via simobserve())             2.93   24.8
      ms[2] = sky.alma.6.2.ms     (via simobserve())             2.00   19.7
      ms[3] = sky.alma.6.3.ms     (via simobserve())             1.23   14.1
      ms[4] = sky.alma.6.4.ms     (via simobserve())             0.798   9.74
      ms[5] = sky.alma.6.5.ms     (via simobserve())             0.474   5.83

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
