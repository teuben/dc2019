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

## Some examples

If you have not seen QAC in action, it's simply a wrapper around CASA, to abstract and
simplify some of it's operations. All function names start with **qac_**:

The most important one for the dc2019 is hte qac_fits(), which allow a selection of
a box= or region=, as well as setting a zoom= if we agree on this. It does not allow
for a regrid template, as we are supposed to use the 1120 x 0.21" maps for comparisons.
The assessment box is also defined in skymodel.md:

     qac_fits('clean3/skymodel_3.smooth.image', 'export/sky_model_box1.fits',   box=box1, stats=True)
     QAC_STATS: export/sky_model_box1.fits 0.8773450 1.3325265 -4.06316843e-07 7.75700092 6657.30589 1.0

the values listed are **mean,rms,min,max,flux,sratio (FluxP-FluxN)/(FluxP+FluxN).**
