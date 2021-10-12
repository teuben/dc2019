"""
Script to use the datacomb module

by L. Moser-Fischer, Oct 2020

Based on the work at the Workshop
"Improving Image Fidelity on Astronomical Data", 
Lorentz Center, Leiden, August 2019, 
and subsequent follow-up work. 

Run under CASA 6. (CASA5 no longer supported)

Typical use in CASA6:
     execfile("DC_script.py")

"""

#  no not modify this file, instead copy a template from DC_pars_*.py to DC_pars.py and edit that

execfile("DC_pars.py", globals())          # user modifiable parameters (templates exist)

execfile("DC_run.py",  globals())          # call the datacomb routines


