# Bloopers and Lessons Learned

In preparation and parallel to an appendix we list here
some mistakes we (and you could) make and hopefully
help you identifying a wrong path. This, as well as some
useful CASA shortcuts you may not have seen before.

Some of the issues we ran into you can find on https://github.com/teuben/dc2019/issues

## Notation

Perhaps it is useful to write functional forms of the CASA procedures. First
define a few names for the data objects we use:

      vis   = the visibilities
      sd    = single dish (SD,  but also called total power (TP))
      tpms  = pseudo visibilities representing the single dish (via tp2vis)

      im    = CASA's (noise-flat) .image file
      pb    = CASA's PB (im/pb is CASA's .image.pbcor file)
      psf   = CASA's PSF
      model = CASA's clean components
      resid = CASA's residual

with these, we can write out data combination procedures as follows:

      (im,pb,psf,model) = tclean(vis)
      f1 = feather(im, sd*pb) / pb     # feather the right way
      f2 = feather(im/pb, sd)          # feather the wrong way
      tpms = tp2vis(sd)
      (im,pb,psf,model) = tclean(vis+tpms)



## Polka Dot pattern

If your image seems to show a polka dot pattern, this can happen
on tclean with the weight of the total power visibilities too
high.  There are several ways to try and combat this:

1. bring the weight of the TPMS down
2. use multi-scale clean
3. use a smaller cycleniter to more often do a major cycle
4. use a more interactive clean

Under full disclosure, I have not tried all but the first option

## Cheat Maps

For models we have the Jy/pixel map, we can run **tclean** on visibilities, with
**niter=0** and **startmodel=skymodel-b.fits**.
In a way this would also confirm that the simulator
works. The resulting difference between
a properly smoothed skymodel and the **.image.pbcor** map shows interesting
striped patterns that correllate with the pointing centers. The
RMS in the difference map for our default sky4 script is about 25-50 mJy/beam.
Since these are from noiseless simulations, this should also tell us what
the **threshold=** should be in tclean.  Perhaps surprising,
there was no indication that using more
configurations (which ought to give more UV points) would give better RMS. In
fact, TPINT was worse than INT. I don't understand this yet.


## Primary Beam

When and where should the primary beam correction be applied? Users
will normally get a  *noise-flat* **.image** and *flux-flat*
**.image.pbcor**
file, but especially in cases like feather and ssc, one has to be careful
when and where the PB is applied. If using TP data as a start model, you should think about applying the interferometeric (mosaic) PB to it first.

## Total Power (Single Dish) Map

A TP map can be made in two ways

1. An OTF style map, based on smoothing the skymodel with the
appropriate beam (57" or whatever), but of course the question is ,
what is this beam?

2. Use the simobserve() and friends. In **simalma** it was found that 
it introduced an extra factor of 0.96 to the real TP beam apart from the
flux scaling (kernel beam/real beam) - this factor is not included in
the **simanalyze** code.  The comments in **simalma** say that the simulated
beam deviates from the real (diffraction) beam so that it needs this
correction.


## Too many open files

Can happen if you have large mosaics (e.g. our LMC).  I had this in sky4f, using cfg=[0,1,2,3,4,5]
Was ok with 0:4   Something like the shell command

       ulimit -Sn 4096

might be needed. On my machine, the default was 1024.  You can also do this from the python shell,
e.g.

       nofiles = 8000
       import resource
       soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
       resource.setrlimit(resource.RLIMIT_NOFILE, (nofiles, hard))
       print("Changing max open files from %d to %d" % (soft,nofiles))


## region= and  box=

Due to curved wcs .... not exactly same flux....   See comments and examples in skymodel.md,
but write this up for the final paper here.

## execfile is evil

Execfile is evil. python code should ideally use **import**, not **execfile**.  The kludge to
tell users to add **globals()** as a second argument does not work if "A" uses "B" and "B"
uses "A". Multiple passes are needed, or the correct order of loading can help in some cases
too.

The conclusion is really: use **import**

## Mosaic vs. Single Pointing

The tclean ...=mosaic option in data that has one pointing silently has devastating effects.

## CASA performance tips:

1. If not enough memory, the chanchunks= can be used to deal with smaller chunks of the cube
in memory. We don't have statistics of the overhead penalty (yet).

2. Is there a penalty for niter=100000 vs. niter=range(0,100000,10000) ?  Yes, it could be,
since this triggers an extra major cycle, which for large MS files can add an extra I/O
component to your script.

3. Does tclean scale linearly with the number of channels?

4. Modern laptops can sometimes be faster than your desktop, but once you count in the
   GHz drop in parallel tclean you may loose that again.




## CASA bugs

Yes, sometimes we do run into CASA bugs as well. This is 
of course a moving target, and we'll try and list a few here.

1. If you want to bring the TP and INT data into the same spectral
frame, mstransform() is useful for the INT data, but it cannot reverse
the spectral axis.  In particular the M100 example exposed this is
others ways, for example a first or last channel that was blanked in one
or more of the data to be combined, perhaps related to ephemeris and a
correct RESTFREQ.  It was thus important not to use a commonbeam.

2. The requirement of having to use **concat()** in simulations vs. real obs.
Not well described what the cause is.

3. That feather bug

4. not a bug, but be careful with weight and older data. Melissa will have
a reminder of this as well somewhere in the paper.

5. edge channel:   in combinations some programs need to have their spectral
axes on the same frame of reference. This can magically result in a first or
last channel that is not combined properly.  Actually, we never tested if
channel I and I+1 are thus combined.
