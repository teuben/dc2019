combo steps provided
user gives clean and naming and combination parameter inputs
level of flexibility
Assessment





It should be noted that this version will only support CASA 6.


## DC_run overview

The **DC_run.py** combines your interferometric and single dish (SD)/total power (TP) data.
It uses the **datacomb.py**, **tp2vis.py**, and  **IQA_script.py** 
module. The DC_run's goal is to provide a homogeneous 
input to all combination methods (e.g. clean parameters), a homogeneous output 
style, and a quality analysis.

It offers several different actions to be selected via the python 'thesteps' list set in **DC_pars.py**

| step | purpose |
| ------ | ------ |
| 0 | Concat   (can be skipped if data are already in one ms) |
| 1 | Prepare the SD-image and create masks |
| 2 | Clean for Feather/Faridani |
| 3 | Feather |
| 4 | Faridani short spacings combination (SSC) |
| 5 | Hybrid (startmodel clean + Feather) |
| 6 | SDINT |
| 7 | TP2VIS |
| 8 | Assessment of the combination results |




The naming scheme of the output images is the following

      imname = imbase + cleansetup + combisetup

- imbase     - a basename you define
- cleansetup - defined by your tclean parameter choice
- combisetup - defined by your combination method and parameter choice

Example:

      skymodel-c_120L.mfs_INTpar_HB_SD-AM_nIA_n100.feather_f1.0.image.pbcor.fits
      skymodel-c_120L.mfs_INTpar_HB_SD-AM_nIA_n100.hybrid_f1.0.image.pbcor.fits
      skymodel-c_120L.mfs_INTpar_HB_SD-AM_nIA_n100.hybrid_f.image.pbcor.fits
      skymodel-c_120L.mfs_INTpar_HB_SD-AM_nIA_n100.SSC_f1.0.image.pbcor.fits
      skymodel-c_120L.mfs_INTpar_HB_SD-AM_nIA_n100.tclean.image.pbcor.fits

      <-  imbase ->   <-----   cleansetup -------> <-- combisetup ------------->
		  
		  
* Q1:   why f1.0 and f  <--- hybrid_f is an intermediate product (before feather)
* Q2:   need a function to reverse engineer this name  (par1,par2,....) = decode(filename)
		  

Various **USER INPUTS**, which you should all find in **DC_pars.py**, 
are described in 
[DC_pars](https://github.com/teuben/dc2019/blob/master/scripts4paper/DC_pars.md). 
Details on the work-flow of core-script **DC_run.py** are given in
[DC_run](https://github.com/teuben/dc2019/blob/master/scripts4paper/DC_run.md). 



## Tips and tricks
* Start with few **nit** (clean-interations in **DC_pars**-file) for quick look at what the products look like
* Run step 0 only once per dataset
* Only run step 1 the first time, then in following runs, only rerun step 1 for changes in the spectral or the masking setup
* Play with all other steps
* For running step 8 alone: activate combination steps of interest (2-7) and use dryrun=True (no active combination - just load products from previous runs)

NEW:
* If you just want the feedback on the rms and threshold that DC_run has derived from your DC_pars_* input, set ``thesteps`` to any step except from step 8 and ``dryrun = True``
* In theory: Thanks to full paths the script can be executed in any arbitrary folder. Having several CASA instances started in the same folder makes them interfere with each other intermediate products (e.g. erase each other's *temp*-folders) leading to crashes. Therefore, execute each script in the corresponding output folder to stay safe.
* Check path names in your DC_locals.py and DC_pars_*.py: A '/' too few or too many might be the reason for trouble.
* In case of a poor PSF (blotchy sidelobes, often for 7m snapshot data)
      * automatically generated masks might let CLEAN diverge
      * create interactive user mask by executing step 2 in ``interactive='IA'`` - mode and rename the resulting <tclean-product>.mask to another name, so that it does not get erased the next time step 2 is executed.
      * execute DC_run from now on with ``masking = 'UM'`` and ``interactive = 'nIA'`` 
        (NOT YET IMPLEMENTED!: and use few 100 of cycleniter. Faint emission might require cycleniter of few tens only!)
* Unknown issue: We had hick-ups with data concatenated in another CASA version that DC_run was executed in. We recommend that you re-do the concatenation in DC-run, if the original data sets are accessible to you. 
* Restarting CASA and or using a new shell can sometimes solve weird processing crashes.
      
      

## Flexibility





## Assessment
