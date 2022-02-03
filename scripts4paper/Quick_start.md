How to execute/run DC_script and get images.
What you go to, to get started quickly. For first time and for future runs.
This will be to run with one of the DC_pars templates.



## Example DC_pars_XXX.py scripts

* M100 - the casaguide example
* (M100trim - the casaguide example - rebinned for smaller data size and faster processing)
* GMC-b - the skymodel b
* GMC-c - the skymodel c
* pointGauss  - point source and a Gaussian



## Execute as e.g.

	execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py",globals())
	execfile("/home/teuben/dc2019/scripts4paper/DC_pars_M100.py", globals()) 
	execfile("/home/teuben/dc2019/scripts4paper/DC_run.py",globals())




## suggestions

* start with few **nit** (clean-interations in **DC_pars**-file) for quick look at what the products look like
* step 0 once 
* step 1 run first time, then only for changes in the spectral or the masking setup
* play with all other steps
* step 8 alone: activate combination steps of interest (2-7) and use dryrun=True (no active combination - just load products from previous runs)
