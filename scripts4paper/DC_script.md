# DC_script

It should be noted that this version will only support CASA 6.


## Preparing (new in May 2021)

First an outline of how to use the scripts in this directory and configure local paths:

1) Before using these scripts, you will first need to configure to set the script, data and working directories
that the scripts will use on your local machine, as opposed to the current defaults.
To do this, you need to execute the **configure** script from the scripts4paper directory to set the directories (a) in which you would like to save the output products (--with-s4p-work) and (b) where the data you want to combine is located (--with-s4p-data). For example,

      ./configure  --with-s4p-work=tmp  --with-s4p-data=../data

will place your working files in a tmp directory (which will be created for you) in your current directory and set **../data** to be the
directory where all the input data are located (at least for the DC2019 project). Use the --help argument to find out
what other options might be useful for you. What is listed here are the defaults.

2) The second step will be to pick a parameter file template and change any input parameters for your specific case. First, choose a parameter file from the several templates that are available, for example for the GMC dataset

       cp  DC_pars_GMC.py  DC_pars.py
	   
Then you can change various parameters (see also USER INPUTS below)  in this **DC_pars.py** for your specific case.

3) Set up your CASA environment by executing **DC_locals.py** in your CASA session,

       execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py")

It is best to place your version of this line in your **~/.casa/config.py** file so that this is
automatically done for each CASA session. But see also an alternative approach in the next section.

4) Lastly to do the data combination, from your CASA session exectute **DC_script.py** (which simply calls DC_pars and DC_run):

       execfile("DC_script.py")

which will do the whole data combination as specified by the many USER INPUTS in your **DC_pars.py**



## Alternative Script

If you prefer to be in many directories, and work from those, first configure for a dummy **/tmp** 

	./configure  --with-s4p-data=../data  --with-s4p-work=/tmp
	
and in each the directories you want to work can create a script
**DC_script.py** that reads something like the following:

	execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py",globals())
	execfile("DC_pars.py", globals()) 
	execfile("/home/teuben/dc2019/scripts4paper/DC_run.py",globals())
	
in those directories you can use

	execfile("DC_script.py")
	
Just make sure not to use the **_s4p_work** variable, but define the **pathtoimage** directory as a local folder, e.g. **./**	



## Example DC_pars_XXX.py scripts

* M100 - the casaguide example
* GMC-b - the skymodel b
* GMC-c - the skymodel c
* pointGauss  - point source and a Gaussian

	

## DC_run overview

The **DC_run.py** is called by the DC_script to combine your data.
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





### automated setup of the header

#### naming scheme specific inputs

Translate the abbreviated clean properties used in the user clean setup 
into real tclean parameters. Define the filename-'infix':

       cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)


#### suffix for combination method (called via combisetup later)

Here, we define the suffix for each method. The scaling factor iterator 
will be added in the corresponding combination loop.


#### intermediate products name for step 1 = gather information 

In this section, intermediate file names such as for the
axis-reordered, the potential channel-range-cut-out of an SD cube, and
regridded SD images are defined.

The chosen mask setup is translated into CASA parameters and the
several mask names (threshold based, SD-AM based and combined) are
defined and forwarded to the different combination methods.  File
existence checks initiate the execution of 'step 1', if one of the
here defined files does not exist and step 1 is not yet included in
the list of execution steps.

The choice of the 'specsetup'-parameter sets the tclean parameters
'start', 'width', and 'nchans' either to the spectral setup of the SD
image (specsetup == 'SDpar') or to the user defined spectral setup
(specsetup == 'INTpar').  

The SDimage used in the combination methods is the
axis-reordered-(channel-cut-out-)only-image or the
axis-reordered-(channel-cut-out-)regridded-image, respectively.  If no
threshold is given and a threshold-based mask exists from previous
runs, the threshold used therein is retreived from it again, else step
1 is enforced.


#### combi name list

This section initiates lists in which the names of the combined images 
are dropped. This can be used for the assessment task to select the wanted 
products. In case the user wants to redefine the selection within this 
module, he can use dryrun=True (see above).


#### before DC_run loops

delete the forgotten TempLattices to clean up



### execution steps/methods

#### step 0: concat (optional)

If you want to combine several interferometric datasets specify 
'thevis', 'weightscale', 'concatms' and add 0 to your 'thestep'-list 


#### step 1: SD image and tclean/mask preparation

1) the axes of the SD image are sorted according to the tclean 
   output standard order (reorder_axes).

2) if in specmode='SDpar' and start and end channel are defined, 
   the SD cube is trimmed to these channels (exclusively; channel_cutout).

3) the channel setup of the reordered (channel-cut-out0) SD cube is read out (get_SD_cube_params). 
   If wanted, the results are used as inputs for all following tcleans etc.

4) a dirty image from the concatvis is created and the RMS of the entire image obtained. 
   This is used to define a threshold and from this a clean mask (derive_threshold).

5) the dirty image is used as template to regrid the reordered SD image (imregrid).

6) a mask from the reordered-regridded SD image is created and combined 
   with auto-masking results in tclean (make_SDint_mask).

7) combine theshold and SD mask, because the theshold mask may 
   contain more/different emission peaks than auto-masking (immath).


#### step 2: tclean only

       imname = imbase + cleansetup + tcleansetup
	   e.g. skymodel-b_120L.HB_AM_n0.0e0.tclean


#### step 3: feather

Requires restoringbeam='common'! perplanebeam-problems

      imname = imbase + cleansetup + feathersetup + str(sdfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.feather_f1.0


#### step 4: SSC

      imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.SSC_f1.0


#### step 5: hybrid

      imname = imbase + cleansetup + hybridsetup + str(sdfac_h[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.hybrid_f1.0


#### step 6: SDINT 

      jointname = imbase + cleansetup + sdintsetup + str(sdg[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.sdint_g1.0


#### step 7: TP2VIS

      imname = imbase + cleansetup + TP2VISsetup + str(TPfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.TP2VIS_t1.0
      
      
#### step 8: assessment










