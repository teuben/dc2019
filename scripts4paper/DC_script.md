# DC_script

The **DC_script** uses the **datacomb** module to conviniently combine 
your data. The DC_script's goal is to provide a homogeneous input to all 
combination methods (e.g. clean parameters) and a homogeneous output 
style.

It offers 6 different actions to be selected via the 'thesteps' variable:

      0: 'Concat',
      1: 'Prepare the SD-image',
      2: 'Clean for Feather/Faridani'
      3: 'Feather', 
      4: 'Faridani short spacings combination (SSC)',
      5: 'Hybrid (startmodel clean + Feather)',
      6: 'SDINT',
      7: 'TP2VIS'

The naming scheme of the output images is the following

      imname = imbase + cleansetup + combisetup

- imbase     - a basename you define
- cleansetup - defined by your tclean parameter choice
- combisetup - defined by your combination method and parameter choice



## USER INPUTS: Paths to the input and output files and for concatenation of several ms - data sets

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

      
   
## USER INPUTS: files and names used by the combination methods 
      
      vis       = concatms 
      sdimage   = pathtoconcat + 'gmc_120L.sd.image'
      imbase    = pathtoimage + 'skymodel-b_120L'        # path + image base name


##  USER INPUTS: setup of the clean parameters

With this section, we set up the clean parameters common for all tclean 
instances used in the combination methods including SDINT.

       general_tclean_param  - present in all methods
       sdint_tclean_param    - only given in runsdintimg

Furthermore, we can generate a meaningful file name "infix" to attach 
to the imbase, reflecting the relevant clean properties (you define). 
Currently, mode, mscale, inter, and nit define the infix name: e.g.

       mode   = 'mfs'    # 'mfs' or 'cube'
       mscale = 'HB'     # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT!)) 
       masking  = 'SD-AM'   # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
       inter  = 'AM'     # 'man' (manual), 'AM' ('auto-multithresh') or 'PB' (primary beam - not yet implemented)
       nit = 0           # max = 9.9 * 10**9 

       cleansetup = '.'+ mscale +'_'+ masking +'_'+ inter +'_'+ str(nit)

gives us 
 
       cleansetup = '.HB_AM_nIA_n1000'

Further parameters like usemask, interactive, and multiscale depend on 
the choice of the masking, inter, and mscale. 
This infix-definition could be made more flexible.
Maybe introduce a loop over some clean parameters like niter.



##  USER INPUTS: SD scaling in combination

Here we can list multiple scaling factors per scaling parameter 
(e.g sdfac=[0.8, 1.0, 1.2] for feather) for the corresponding 
combination method to iterate over. Default could be 1.0 for all.



## suffix for combination method

Here, we define the suffix for each method. The scaling factor iterator 
will be added in the corresponding combination loop.



## dryrun and combi name list

This section initiates lists in which the names of the combined images 
are dropped. This can be used for the assessment task to select the wanted 
products. In case the user wants to redefine the selection within this 
module, he can use dryrun=True: It generates the filennames with the wanted 
iterators and cleanname without executing the combination method.



## execution steps/methods

### step 0: concat

If you want to combine several interferometric datasets specify 
'thevis', 'weighscale', 'concatms' and add 0 to your 'thestep'-list 



### step 1: SD image and tclean preparation
1) the axes of the SD image are sorted according to the tclean 
output standard order (reorder_axes). 
2) the channel setup of the reordered SD cube is read out (get_SD_cube_params). 
If wanted, the results are used as inputs for all following tcleans etc (need to implement!).
3) a dirty image from the concatvis is created and the RMS of the entire image obtained. 
This is used to define a threshold and from this a clean mask (derive_threshold).
4) the dirty image is used as template to regrid the reordered SD image (imregrid).
5) a mask from the reordered-regridded SD image is created and combined 
with auto-masking results in tclean (make_SDint_mask).
6) combine theshold and SD mask, because the theshold mask may 
contain more/different emission peaks than auto-masking (immath).


### tclean only

       imname = imbase + cleansetup + tcleansetup
       e.g.     skymodel-b_120L.HB_AM_n0.0e0.tclean


### feather

      imname = imbase + cleansetup + feathersetup + str(sdfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.feather_f1.0


### SSC

      imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.SSC_f1.0


### hybrid

      imname = imbase + cleansetup + hybridsetup + str(sdfac_h[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.hybrid_f1.0


### SDINT 

      jointname = imbase + cleansetup + sdintsetup + str(sdg[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.sdint_g1.0


### TP2VIS
not yet activated.


## after combination loops
delete the nasty TempLattices







