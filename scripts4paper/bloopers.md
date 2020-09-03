# Bloopers and Lessons Learned

In preparation and parallel to an appendix we list here
some mistakes we (and you could) make and hopefully
help you identifying a wrong path.

## meta code

Perhaps it is useful to write functional forms of the CASA procedures. First
define a few names for the data objects we use:

      vis   = the visibilities
      sd    = single dish
      tpms  = pseudo visibilities representing the single dish (tp2vis)

      im    = CASA's (noise-flat) .image file
      pb    = CASA's PB (im/pb is CASA's .image.pbcor file)
      psf   = CASA's PSF
      model = CASA's clean components

with these, we can write out data combination procedures as follows:

      (im,pb,psf,model) = clean(vis)
      f1 = feather(im, sd*pb) / pb     # feather the right way
      f2 = feather(im/pb, sd)          # feather the wrong way
      tpms = tp2vis(sd)
      (im,pb,psf,model) = clean(vis+tpms)



## polka dot pattern

If your image seems to show a polka dot pattern, this can happen
on tclean with the weight of the total power visibilities too
high.  There are several ways to try and combat this:

1. bring the weight of the TPMS down
2. use multi-scale clean
3. use a smaller cycleniter to more often do a major cycle
4. use a more interactive clean

Under full disclosure, I have not tried all but the first option

## Primary Beam

When and where should the primary beam correction be applied? Users
will normally get a  *noise-flat* **.image** and *flux-flat*
**.image.pbcor**
file, but especially in cases like feather and ssc, one has to be careful
when and where the PB is applied. 

## CASA bugs

Yes, sometimes we do run into CASA bugs as well. This is 
of course a moving target, and we'll try and list a few here.

1. If you want to bring the TP and INT data into the same spectral
frame, mstransform() is useful for the INT data, but it cannot reverse
the spectral axis.  In particular the M100 example exposed this is
others ways, for example a first or last channel that was blanked in one
or more of the data to be combined, perhaps related to ephemeris and a
correct RESTFREQ.  It was thus important not to use a commonbeam. 

