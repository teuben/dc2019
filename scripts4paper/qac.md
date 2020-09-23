# QAC (Quick Array Combination) 

Here is a reminder for users of QAC, a CASA wrapper.

## Installing QAC

This is detailed within QAC, and note currently CASA6 is not yet supported. But here
is a quick summary:

Your **~/.casa/init.py** file will typically contain a line

      execfile(os.environ['HOME'] + '/.casa/QAC/casa.init.py')

and you will need a symlink of **~/casa/QAC** pointing to where QAC is
really located (the recommended procedure). For dc2019 this would
be in the **dc2019/contrib/QAC** directory:

      cd dc2010/contrib
      make QAC

will grab the latest version, but very likely will need a regular
"git pull" to get recent updates.

## Running QAC

If you have installed QAC, the **dc2019/contrib/QAC/test** directory
has a **Makefile** via which a number of tests can be run that are
also used in DC2019. Make sure you copies or symlinks to the datafiles
(e.g. **skymodel-b.fits**) in that directory

      cd dc2019/contrib/QAC/test
      ln -s ../../../data/skymodel-b.fits
      make sky4
      

## QAC filename conventions

The QAC
has a more rigorous convention
of the basenames of files, though the portion of the filename
after the first dot is often derived (via the **imagename=** keyword in
**tclean()** and **sdintimaging()**)
Scripts can freely pick directory names, though historically
they are export or cleanN, where N is some integer
depicting the kind of experiment (e.g. clean0 for imaging TPMS only)

Here is an example

    sky4a/
        sky4.py                              copy of the script used
        sky4a.log                            log file via Makefile
        export/                              export fits file for QA team
               sky_int_box1.fits
               sky_mac1_box1.fits
               sky_mac3_box1.fits
               ...
        clean0/                              mapping just the TPMS
               dirtymap.image
               dirtymap.image.pbcor
               dirtymap.psf
               dirtymap.pb
               dirtymap.model
               dirtymap.residual
               dirtymap.sumwt
               dirtymap.weight
        clean3/                              mapping TPMS + INT in various ways
	       int.image
	       tpint.image
	       sdint.image
	       feather.image
	       ssc.image
	       macint.image
	       ...

There are a number of cleanN variations possible, depending on how the combinations
are initialized (e.g. an OTF Jy/beam vs. Jy/pixel map for the TP). The **export/**
directory will contain agreed upon maps for the QA team.

## Running CASA: execfile vs. import

It is useful to consider the different approaches how CASA can be run. Traditionally
python2's **execfile()** has been used. In python3 this command does not exist anymore,
but was re-implemented for CASA6. The more pythonic way should be **import**, but
without some modifications to the code is not always possible.

But lets review the differences for tp2vis (ignoring the problem where
the file should be located in your filesystem):

      execfile("tp2vis")
      tp2vis('tp.im','tp.ms','12m.ptg',rms=0.67)

this has placed the tp2vis() function in global namespace, this approach is similar to

      from tp2vis import *

which is discouraged in python (imagine somebody else using that name).  The better
approach would be something like

       import tp2vis as t2v
       t2v.tp2vis('tp.im','tp.ms','12m.ptg',rms=0.67)

which also makes your code more readable (as in: identifying the origin of the routine).


Something more about that other problem where the file should live. Typically with **execfile()**
you will do something like (we do in QAC)

      import os
      execfile(os.environ['HOME'] + '/.casa/QAC/casa.init.py')

which of course is pretty horrible. The pythonic approach is an install step like

      python setup.py install
      
or

      pip install -e .

insode the QAC code tree.  This places the code "in the right place", and there are lots of other
advanced steps like virtualenv if you need more flexibility.



    



## Some examples

If you have not seen QAC in action, it's simply a wrapper around CASA, to abstract and
simplify some of it's operations. All function names start with **qac_**:

The most important one for the dc2019 is hte qac_fits(), which allow a selection of
a box= or region=, as well as setting a zoom= if we agree on this. It does not allow
for a regrid template, as we are supposed to use the 1120 x 0.21" maps for comparisons.
The assessment box is also defined in skymodel.md:

     qac_fits('clean3/skymodel_3.smooth.image', 'export/sky_model_box1.fits',   box=box1, stats=True)
     QAC_STATS: export/sky_model_box1.fits 0.8773450 1.3325265 -4.06316843e-07 7.75700092 6657.30589 1.0

the values listed are **mean,rms,min,max,flux,sratio (FluxP-FluxN)/(FluxP+FluxN).**       <div style="page-break-after: always"></div>


## sky4

The **sky4.py** script is currently the most complete version of
running a number of combinations on the skymodel. The only input needed
is the skymodel fits filename.  Without explaining and setting up too
many variables, this is the essence of the workflow:

      # niter needs to be a list in QAC, the first needs to be 0
      niter = [0, 10000]

      # create a pointing file based on the skymodel
      qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)

      # loop over some configurations to make a list of INTMS via simobserve (simalma)
      #           0:7m  1,2,3....:12m
      ms1={}
      for c in [0,1,4]:
           ms1[c] = qac_alma(pdir,model,imsize_m,pixel_m,cycle=7,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times)
      startmodel = ms1[cfg[0]].replace('.ms','.skymodel')	   
      intms = list(ms1.values())

      # create the TPMS
      tpms = qac_tp_vis(pdir,model,ptg,phasecenter=phasecenter,deconv=False,maxuv=maxuv,nvgrp=nvgrp,fix=0)

      # map the TPMS, if not to get the PSF for an input to sdintimager()
      qac_clean1(pdir+'/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter,
                 **tclean_args)

      # combination using TPMS, including the tweak (for this niter needs to be a list)
      qac_clean(pdir+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,
                do_int=True,do_concat=False, **tclean_args)
      qac_tweak(pdir+'/clean3','tpint',niter)

      # followup with other combinations in this "clean3" directory
      qac_feather(pdir+'/clean3', name="int")
      qac_ssc    (pdir+'/clean3', name="int")
      qac_smooth (pdir+'/clean3', startmodel, name="int")
      qac_smooth (pdir+'/clean3', startmodel, name="tpint")

      # Hybrid with perfect startmodel for cheating
      qac_clean(pdir+'/clean4',tpms,intms,imsize_s,pixel_s,niter=0,phasecenter=phasecenter,
                do_int=True,do_concat=False, startmodel=startmodel, **tclean_args)

      # Combination with sdintimaging() 
      qac_sd_int(pdir+'/clean5',sdimage,intms,sdpsf, imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,
                 **tclean_args)

      # Model Assisted Cleaning
      qac_mac(pdir+'/clean7',sdimage,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,
              **tclean_args)

      # export results into standard export names, only the assessment box is exported, and smoothed to 2"
      qac_fits('clean3/skymodel_3.smooth.image',  'export/sky_model_box1.fits',   box=box1, stats=True, smooth=2.0)
      qac_fits('clean3/int_3.image.pbcor',        'export/sky_int_box1.fits',     box=box1, stats=True, smooth=2.0)
      qac_fits('clean3/tpint_3.image.pbcor',      'export/sky_tpint_box1.fits',   box=box1, stats=True, smooth=2.0)
      qac_fits('clean3/tpint_3.tweak.image.pbcor','export/sky_tweak_box1.fits',   box=box1, stats=True, smooth=2.0)
      qac_fits('clean3/feather_3.image.pbcor',    'export/sky_feather_box1.fits', box=box1, stats=True, smooth=2.0)
      qac_fits('clean3/ssc_3.image',              'export/sky_ssc_box1.fits',     box=box1, stats=True, smooth=2.0)
      qac_fits('clean4/int.image.pbcor',          'export/sky_cheat1_box1.fits',  box=box1, stats=True, smooth=2.0)
      qac_fits('clean4/tpint.image.pbcor',        'export/sky_cheat2_box1.fits',  box=box1, stats=True, smooth=2.0)
      qac_fits('clean4/feather.image.pbcor',      'export/sky_cheat3_box1.fits',  box=box1, stats=True, smooth=2.0)
      qac_fits('clean4/ssc.image',                'export/sky_cheat4_box1.fits',  box=box1, stats=True, smooth=2.0)
      qac_fits('clean7/int1.image.pbcor',         'export/sky_mac1_box1.fits',    box=box1, stats=True, smooth=2.0)
      qac_fits('clean7/macint.image.pbcor',       'export/sky_mac3_box1.fits',    box=box1, stats=True, smooth=2.0)
