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




## Flexibility





## Assessment
