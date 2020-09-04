# DATACOMB

The **datacomb** module will be combining all methods in
a uniform way, and organize input and output data in a
standard way (the *file manifest*). Your scripts would start
with

      import datacomb as dc

From the first example Dirk presented, I'd like to take one
step up to try and simplify its usage. I try to explain this
below.

## Input files:  VIS and SD

Input will be one or more visibility files (in MS format), thus

      vis = 'vis1.ms'

or

      vis = ['vis1.ms', 'vis2.ms', 'vis3.ms']

are allowed where visibilities are needed. These could be from the
simulator, or from real observations. We will not place any
conditions on how they are obtained.

The single dish (SD) map can be provided in either Jy/beam or Jy/pixel
(e.g. for models), as long as the header makes this clear.

      sd = 'sd0.fits'
or
      sd = 'sd1.im'


The input files should be considered read-only.   If for some reason,
a new weight would need to be applied between arrays, copies should be
made and weights applied to the copies.

We probably should say something about keeping a commmon frame in the
spectral dimension for both the VIS and SD. There have been a few
CASA bugs that we don't like to discuss here, and so lets assume those
are all taken care of.


## Output Files

Per experiment, should we not keep everything in a single directory,
or some pre-agreed hierarchy? For those having used **qac_ssc**, the
first parameter is used for this. If you want it in the current
directory, you can always set

      project = '.'

and get all your files locally. But this could quickly become very messy.
There is also an example in **qac_fits()**,
which controls the assessment box and resolution, so the QA team
could take advantage of this. This is especially useful where the file
manifest can be adhered to, even if the user does their own experiments.
In QAC this could look as follows:

      qac_fits('clean3/skymodel_3.smooth.image',   'export/sky_model_box1.fits', box=box1, smooth=2)
      qac_fits('clean3/tpint_3.tweak.image.pbcor', 'export/sky_tweak_box1.fits', box=box1, smooth=2)
      qac_fits('clean6/macint.image.pbcor',        'export/sky_mac_box1.fits',   box=box1, smooth=2)

where certain experiments in the clean3 and clean6 directories were
done, but the export directory assembles the correct filenames, all in
fits format. This is useful because the QA team may use advanced
python modules which might not work or be compatible with the CASA
python.

## Parameters

There are quite a few common parameters (tclean parameters, sdgain, sdfactor, tp2vis_weight etc.etc.)
that can/should be shared between the methods. Should they be stored in parameter/pickle file, so
an experiment uses the same gridding, and an experiment can be continued (e.g. more clean iterations)

How about experiments where one loops over a certain parameter? These could be done in
directories with an index in the name, each directory have the same kind of manifest
of files (like the imagename= argument in tclean/sdintimaging)



## Methods

Using just CASA will allow the user to create files with almost arbitrary filenames
in arbitrary directories. We would like to organize this a bit, and setting a manifest
of the filenames to make it straightforward for the QA team to investigate a particular
experiment, and/or baseline this on another experiment.

      dc.sdint()
      dc.feather()
      dc.tp2vis()
      dc.tclean()
      dc.ssc()
      dc.mac()

Apart from some parameter that we control (e.g. imsize, cell etc.), users can still set their own by
using python's **kwargs mechanism.


## Method Examples

Loosely taken from [skymodel.md](skymodel.md) we have the following combination

1. tclean(vis) -> int, psf

2. feather(int, sd) -> feather

3. ssc(int, sd) -> ssc

4. tp2vis(sd) -> tpms

   tclean(vis+tpms) -> tpint

5. sdint(vis,sd,psf) -> sdint

6. tclean(vis, startmodel=sd/nppb) -> int1, model1, beam1

   feather((model1-sd/nppb)xbeam, sd) -> feather2
   
   tclean(vis, startmodel=feather2/nppb2) -> int3
   
Here 6. is Kauffmann's Model Assistent Clean, of which there can be
a few variations.    The **dc.mac()** method should probably
have descriptive options how to run it. Method 1. is needed to
create files (e.g. psf, beam) needed for other methods.
