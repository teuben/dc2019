explain DC_run (header and step details)

# DC-run


## automated setup of the header


### load modules

### Tidy up TempLattices from previous runs

os.system('rm -rf '+pathtoimage + 'TempLattice*')

Switch this off, if you run multiple casa instances/DC_runs in the same work folder !  Else you delete files from another working process



### prepare concatfiles

### filecheck and preparation on vis

### setup general and SD tcleanparameters from DC_pars*

### translate mode, inter, mscale into tclean params






#### naming scheme specific inputs

Translate the abbreviated clean properties used in the user clean setup 
into real tclean parameters. Define the filename-'infix':

       cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)


#### suffix for combination method (called via combisetup later)

Here, we define the suffix for each method. The scaling factor iterator 
will be added in the corresponding combination loop.


#### intermediate products name for step 1 = gather information 

In this section, intermediate file names such as for the
axis-reordered SD image, the optional channel-range-cut-out of an SD cube, and
regridded SD image are defined.

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

### suffix generation for step 8
Merge stepnumber the the assesment is based on to add them to the 
assements file names.


### execution steps/methods

#### step 0: concat (optional)

If you want to combine several interferometric datasets specify 
'thevis', 'weightscale', 'concatms' and add 0 to your 'thestep'-list 

--- Slides ---

Purpose:
combine several interferometric datasets (ALMA 12m and 7m)
For this, specify in *_pars_*-file:
* pathtoconcat
* ‘a12m’
* ‘a7m’ 
* ‘weight12m’,
* ‘weight7m ‘
* 'concatms' 
* add 0 to your 'thesteps'-list

what it does:
* checks CASA version of calibration of the input ms-files
* warnings for simulated data and calibrations prior CASA 4.3 - user has to correct/adjust weights
* executes CASA task ‘concat’

run ONCE to create concatenated ms-file, if not yet available

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

--- Slides ---

Purpose:
put input data to shape (reorder, regrid) desired by combination methods, and prepare masking and thresholds for 'SD-AM' mode
For this, specify in *_pars_*-file:
* (pathtoconcat)
* sdimage_input
* mode     
* masking
* general_tclean_param
* specsetup
* startchan
* endchan   
* smoothing
* RMSfactor
* cube_rms  
* cont_chans
* sdmasklev


what it does:
* reorder_axes: reorder SD image axes to standard   
* channel_cutout: if specmode='SDpar' and start and end channel defined: trim SD cube to these channels
* get_SD_cube_params: if specmode='SDpar', get SD channel setup and use as inputs for all following tcleans etc.
* derive_threshold: make dirty image from the concatms, get RMS, use it as threshold and make clean mask from it
* regrid_SD: regrid reordered SD image to dirty image 
* make_SDint_mask: make mask from the reordered-regridded SD image (and automask-AM)
* combine threshold and SD(-AM) mask

effects:
* if general_tclean_param['threshold'] == '':
  * use threshold from derive_threshold
  * retrieve/modify it and its mask each DC_run without new dirty image
* if masking == 'SD-AM':
  * use threshold(RMS) or SD(-AM) + threshold(RMS) mask


run this step ONCE for a new (spec-)mode and spectral setup (specsetup, startchan, endchan, nchan, width, start) or for a change of the SD mask level
full flexibitiy for combination parameters from here on (aka. everything is at hand for playing around)



#### step 2: tclean only

       imname = imbase + cleansetup + tcleansetup
	   e.g. skymodel-b_120L.HB_AM_n0.0e0.tclean


--- Slides ---

Purpose:
create (deconvolved) INT image from the concatms data
For this, specify in *_pars_*-file:
* mode     
* mscale   
* masking  
* inter    
* nit      
* specsetup
* general_tclean_param

what it does:
* runtclean
  * executes CASA task ‘tclean’ and ‘exportfits’


#### step 3: feather

Requires restoringbeam='common'! perplanebeam-problems

      imname = imbase + cleansetup + feathersetup + str(sdfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.feather_f1.0


--- Slides ---

Purpose:
combine INT image with SD image
For this, specify in *_pars_*-file:
* mode     
* mscale   
* masking  
* inter    
* nit      
* specsetup
* sdfac

what it does:
* runfeather
  * immath: SD.image * INT.pb
  * feather: SD.image.pbskewed and INT.image
  * immath: pbcorr feathered image
  * exportfits



#### step 4: SSC

      imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.SSC_f1.0


--- Slides ---

Purpose:
combine INT image with SD image following S. Faridani
(https://bitbucket.org/snippets/faridani/pRX6)
For this, specify in *_pars_*-file:
* mode     
* mscale   
* masking  
* inter    
* nit      
* specsetup
* SSCfac

what it does:
* ssc
  * immath: SD.image * INT.pb
  * imsmooth: INT.image to SD.beam
  * immath: SD.image.INTpb - INT.image.SDbeam = SD-INT.diff
  * weight = INTbeam/SDbeam
  * immath: INT.image + SD-INT.diff * weight = SSC.image
  * immath: pbcorr SSC image
  * exportfits


#### step 5: hybrid

      imname = imbase + cleansetup + hybridsetup + str(sdfac_h[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.hybrid_f1.0


--- Slides ---

Purpose:
create (deconvolved) INT image from the concatms data using SD image as startmodel, then feather INT and SD image
For this, specify in *_pars_*-file:
* mode     
* mscale   
* masking  
* inter    
* nit      
* specsetup
* general_tclean_param
* sdfac_h

what it does:
* runWSM
  * prepare SD image for startmodel use
  * runtclean with SD image as startmodel
  * runfeather


#### step 6: SDINT 

      jointname = imbase + cleansetup + sdintsetup + str(sdg[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.sdint_g1.0


--- Slides ---

Purpose:
create (deconvolved) SD+INT image from the concatms data with tclean working on feathered image
For this, specify in *_pars_*-file:
* mode     
* mscale   
* masking  
* inter    
* nit      
* specsetup
* general_tclean_param
* sdint_tclean_param
* sdg

what it does:
* runsdintimg
  * image preparation (perplanebeams in SD image)
  * sdintimaging


#### step 7: TP2VIS

      imname = imbase + cleansetup + TP2VISsetup + str(TPfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.TP2VIS_t1.0
    

--- Slides ---
  
Purpose:
create SD visibilities from SD image, combine SD and INT visibilities and create deconvolved image from it.
For this, specify in *_pars_*-file:
* mode     
* mscale   
* masking  
* inter    
* nit      
* specsetup
* general_tclean_param
* TPfac
* TPpointingTemplate       
* listobsOutput            
* TPpointinglist           
* TPpointinglistAlternative
* TPnoiseRegion            
* TPnoiseChannels         

what it does:
* get pointings: user specified or listobs_ptg on 12m ms-file
* create_TP2VIS_ms
  * imstat: get noise
  * TP2VIS: transform SD image into SD.ms
* transform_INT_to_SD_freq_spec
  * get_SD_cube_params: get frequnecy range of SD.image
  * mstransform: tranform INT.ms to SD reference frame
* runtclean_TP2VIS_INT
  * concat: INT.ms + SD.ms
  * runtclean: on combined *.ms
  * tp2vistweak: correct for dirty/clean beam mismatch

      
#### step 8: assessment

    

--- Slides ---
  
  
Purpose:
analyze combination results
For this, specify in *_pars_*-file:
* momchans
* skymodel     

what it does:
* residual maps + tclean masks, stopping criteria NUMBERS, and thresholds
* Combined image vs. SD image (and model image, if skymodel from simulation is given)
  * Compare_Apar/Fidelity_(cubes)
  * show_Apar/Fidelity_map
  * Compare_Apar/Fidelity_signal
  * genmultisps: power spectra of images and apar images
  








