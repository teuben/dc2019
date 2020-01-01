2oct2019 Brian Mason (NRAO)

Scripts to simulate and image ngVLA core + short baseline array (SBA)
observations of a 30 Dor-like target. Simulations are 93 GHz continuum
with the core tapered to ~2" FWHM.

Depends upon some functions combo_utils.py

 and the FITS image

30dor-hires.fits 
    which can be found at https://astrocloud.nrao.edu/s/ZPbz95tkTi4sSPr

Included here:

combo_utils.py - put this in your CASA path.
run_all - shell script to run simulations and imaging
ngvla-sd_loc.cfg  - 
ngvla-core-revC_loc.cfg 
ngvla-sba-revC_loc.cfg - TP, Core, and SBA config files. "_loc"
  ensures that CASA doesn't outwit you and include a version included
  in your CASA distribution
simNgvlaSba30dor_new.py 
simNgvlaCore30dor.py 
simNgvlaSd30dor_new.py  - simulation scripts
image_sba_30dor_new.py - image TP and SBA
image_joint_30dor_new.py - image ngVLA core, and SBA+core
