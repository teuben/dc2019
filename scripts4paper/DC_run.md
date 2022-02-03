explain DC_run (header and step details)











	



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










