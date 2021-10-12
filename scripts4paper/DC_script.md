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

It is best to place your version of this line in your **~/.casa/startup.py** file so that this is
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
	execfile("/home/teuben/dc2019/scripts4paper/DC_runs.py",globals())
	
in those directories you can use

	execfile("DC_script.py")
	
Just make sure not to use the **_s4p_work** variable, but define the **pathtoimage** directory as a local folder, e.g. **./**	

## Example DC_pars_XXX.py scripts

* M100 - the casaguide example
* GMC-b - the skymodel b
* GMC-c - the skymodel c
* pointGauss  - point source and a Gaussian

	

## DC_script overview

The **DC_script.py** uses the **datacomb.py**, **tp2vis.py**, and  **IQA_script.py** 
module to combine 
your data. The DC_script's goal is to provide a homogeneous input to all 
combination methods (e.g. clean parameters), a homogeneous output 
style, and a quality analysis.

It offers several different actions to be selected via the python 'thesteps' list set in **DC_pars.py**

      0: Concat   [can be skipped if data are already in one ms]
      1: Prepare the SD-image and create masks
      2: Clean for Feather/Faridani
      3: Feather
      4: Faridani short spacings combination (SSC)
      5: Hybrid (startmodel clean + Feather)
      6: SDINT
      7: TP2VIS
      8: Assessment of the combination results




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
		  
		  
* Q1:   why f1.0 and f1  <--- hybrid_f is an intermediate product (before feather)
* Q2:   need a function to reverse engineer this name  (par1,par2,....) = decode(filename)
		  

Various **USER INPUTS** are described below, which you should all find in **DC_pars.py**



## intermission: DC_pars* overview


#### USER INPUTS: Paths to the input and output files and for concatenation of several ms - data sets

      pathtoconcat = 'path-to-ms-datasets-(array-configs)-and-SD-image-to-combine'   
      # path to the folder with the files to be concatenated
      
      pathtoimage  = 'path-to-your-products'                         
      # path to the folder where to put the combination and image results
      
      concatms     = pathtoimage + 'skymodel-b_120L.alma.all_int-weighted.ms'       
      # path and name of concatenated file (e.g. blabla.ms)

The list of files to concatenate is defined in this section, too, 
as well as the visweighting.

If you don't need/want to concatenate data, give the name and path 
of the file or a list of files you want to image directly to concatms 
and skip thesteps=[0].

      
   
#### USER INPUTS: files and names used by the combination methods 
      
      vis       = concatms 
      sdimage   = pathtoconcat + 'gmc_120L.sd.image'
      imbase    = pathtoimage + 'skymodel-b_120L'            # path + image base name
      sdbase    = pathtoimage + 'skymodel-b_120L_TP'         # path + sd image base name


#### USER INPUTS:  TP2VIS related setup

TPpointingTemplate is an ALMA 12m dataset used in the combination, listobsOutput 
holds the information that listobs produces, TPpointinglist contains the antenna 
pointings read out from the listobsOutput. If these are not provided the user can 
use his own pointing list. 

      TPpointingTemplate        = a12m[0]        
      listobsOutput             = imbase+'.12m.log'
      TPpointinglist            = imbase+'.12m.ptg'
      TPpointinglistAlternative = 'user-defined.ptg'   
 
For transforming the SD image into visibilities, TP2VIS needs the rms in the SD images 
for setting the weights. Therefore, one has to specify a range of emission-free pixels 
in a continuum SD image, or a range of emission-free channels in the SD cube.

      TPnoiseRegion   = '10,30,10,30'  # emission free box in unregridded continuum SD image!
      TPnoiseChannels = '2~5'          # emission free channels in unregridded and un-cut SD cube!


####  USER INPUTS: setup of the clean parameters

With this section, we set up the clean parameters common for all tclean 
instances used in the combination methods including SDINT.

       general_tclean_param  - present in all methods
       sdint_tclean_param    - only given in runsdintimg

Before setting the parameters included above, we can generate a meaningful 
file name "infix" to attach 
to the imbase, reflecting the relevant clean properties (you define). 
Currently, mode, mscale, masking, inter, nit, and specsetup define the 
infix name: e.g.

       mode      = 'mfs'      # 'mfs' or 'cube'
       mscale    = 'HB'       # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT!)) 
       masking   = 'SD-AM'    # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
       inter     = 'nIA'      # interactive ('IA') or non-interactive ('nIA')
       nit       = 0          # max = 9.9 * 10**9 
       specsetup = 'INTpar'   # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup, only option for 'mfs')



Using an infix-definition of

       cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)

gives us 
 
       cleansetup = '.mfs_INTpar_HB_SD-AM_nIA_n0'


This infix-definition could be made more flexible.
Maybe introduce a loop over some clean parameters like niter.


For "SDpar" we can also define a channel-cut-out from the SD image to 
reduce channel range translated into the combined product. If specsetup = 'INTpar', 
the cut-out-channel inputs are ignored.

       startchan = 30  #None  # start-value of the SD image channel range you want to cut out 
       endchan   = 39  #None  #   end-value of the SD image channel range you want to cut out

Generating a common mask from an SD image mask and an auto-multithreshold mask
or user defined threshold (masking  = 'SD-AM'), requires additional input:

       smoothing  = 5    # smoothing of the threshold mask (by 'smoothing x beam')
       RMSfactor  = 0.5  # continuum rms level (not noise from emission-free regions but entire image)
       cube_rms   = 3    # cube noise (true noise) x this factor
       cont_chans = ''   # line free channels for cube rms estimation
       sdmasklev  = 0.3  # image peak x this factor = threshold for SD mask



The parameters defined above define some of the clean parameters common for all tclean 
instances used in the combination methods including SDINT. Further parameters that can 
be set by the user are spw, field, imsize, cell, phasecenter, start, width, nchan, 
restfreq, threshold, maxscale, mask, pbmask, and the automasking parameters
sidelobethreshold, noisethreshold, lownoisethreshold, minbeamfrac, growiterations,
and negativethreshold.
For SDINT, the user can specify the parameters sdpsf and dishdia in addition. 
       
      general_tclean_param = dict(#overwrite  = overwrite,
                                 spw         = '0', 
                                 field       = '0~68', 
                                 specmode    = mode,            # ! change in mode-variable above dict !        
                                 imsize      = [1120], 
                                 cell        = '0.21arcsec',    
                                 phasecenter = 'J2000 12:00:00 -35.00.00.0000',             
                                 start       = 0, 
                                 width       = 1, 
                                 nchan       = -1, 
                                 restfreq    = '',
                                 threshold   = '',              
                                 maxscale    = 10.,              
                                 niter      = nit,               # ! change in nit-variable above dict !
                                 mask        = '', 
                                 pbmask      = 0.4,
                                 #usemask           = 'auto-multithresh',    # defined via masking-variable!              
                                 sidelobethreshold = 2.0, 
                                 noisethreshold    = 4.25, 
                                 lownoisethreshold = 1.5,               
                                 minbeamfrac       = 0.3, 
                                 growiterations    = 75, 
                                 negativethreshold = 0.0) 
      
      sdint_tclean_param = dict(sdpsf   = '',
                               dishdia = 12.0)
      




####  USER INPUTS: SD scaling in combination

Here, we can list multiple scaling factors per scaling parameter 
(e.g sdfac=[0.8, 1.0, 1.2] for feather) for the corresponding 
combination method to iterate over. Default could be 1.0 for all.


####  USER INPUTS: dryrun

       dryrun=True

It generates the filenames with the wanted iterators and cleannames
without executing the combination method (time saving).








## resume: DC_script overview


## automated setup: naming scheme specific inputs

Translate the abbreviated clean properties used in the user clean setup 
into real tclean parameters. Define the filename-'infix':

       cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)


## automated setup: suffix for combination method (called via combisetup later)

Here, we define the suffix for each method. The scaling factor iterator 
will be added in the corresponding combination loop.


## automated setup: intermediate products name for step 1 = gather information 

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



## automated setup: combi name list

This section initiates lists in which the names of the combined images 
are dropped. This can be used for the assessment task to select the wanted 
products. In case the user wants to redefine the selection within this 
module, he can use dryrun=True (see above).



## execution steps/methods

### step 0: concat (optional)

If you want to combine several interferometric datasets specify 
'thevis', 'weightscale', 'concatms' and add 0 to your 'thestep'-list 


### step 1: SD image and tclean/mask preparation

1) the axes of the SD image are sorted according to the tclean 
   output standard order (reorder_axes).

2) if in specmode='SDpar' and start and end channel are defined, 
   the SD cube is trimmed to these channels (exclusively; channel_cutout).

3) the channel setup of the reordered (channel-cut-out0) SD cube is read out (get_SD_cube_params). 
   If wanted, the results are used as inputs for all following tcleans etc (need to implement!).

4) a dirty image from the concatvis is created and the RMS of the entire image obtained. 
   This is used to define a threshold and from this a clean mask (derive_threshold).

5) the dirty image is used as template to regrid the reordered SD image (imregrid).

6) a mask from the reordered-regridded SD image is created and combined 
   with auto-masking results in tclean (make_SDint_mask).

7) combine theshold and SD mask, because the theshold mask may 
   contain more/different emission peaks than auto-masking (immath).


### step 2: tclean only

       imname = imbase + cleansetup + tcleansetup
	   e.g. skymodel-b_120L.HB_AM_n0.0e0.tclean


### step 3: feather

Requires restoringbeam='common'! perplanebeam-problems

      imname = imbase + cleansetup + feathersetup + str(sdfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.feather_f1.0


### step 4: SSC

      imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.SSC_f1.0


### step 5: hybrid

      imname = imbase + cleansetup + hybridsetup + str(sdfac_h[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.hybrid_f1.0


### step 6: SDINT 

      jointname = imbase + cleansetup + sdintsetup + str(sdg[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.sdint_g1.0


### step 7: TP2VIS

      imname = imbase + cleansetup + TP2VISsetup + str(TPfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.TP2VIS_t1.0


## after combination loops

delete the nasty TempLattices (this is a CASA bug and should be reported that somebody
is not cleaning up)







