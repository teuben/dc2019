* separate those that are critical for running the scripts and those that are for tweaking your images.
* What you need to run YOUR data through DC_script








# DC_pars*

## Select processing and combination steps to execute

The available execution steps are:

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

To select from these you give the ``thesteps``-parameter a list of the step numbers, e.g.

      thesteps=[0,1,2,3,4,5,6,7,8]       


## dryrun - parameter

To execute any combination step (0 to 7) you need

       dryrun=False
      
There might be cases in which you only want to gather all the filenames generated in a previously executed combination run, e.g. you only want to have an assessment of these products (step 8) or use them for your own routines. In this case, select all the combinations steps (for assessment set step 8, too) and parameters from the previous combination run, but set

       dryrun=True

It generates lists of filenames for each combination method with the wanted iterators and cleannames, but without executing the combination method itself (time saving).



## Paths to the input and output files

If you do not wish to concatenate data, because you already have your data concatenated or want to work on only one interferometric data set, then go to the next section.

It is helpful to use different folders for the input and output data. If you want to concatenate several ALMA 12m or 7m data sets, you can put them into the ``pathtoconcat``-folder

      pathtoconcat = 'path-to-input-data'  
      # path to the folder with the files to be concatenated and the input SD image

In our examples, this folder contains also the SD image!
The ``pathtoimage``-folder is the actual working folder and holds the processing, combination, and assessment products.

      pathtoimage = 'path-to-products'                         
      # path to the folder, where to put the combination and image results
 
 
## Setup for concatenation of several ms - data sets (step 0)
 
If you want to concatenate several ALMA data sets list the 12m data sets in ``a12m`` and ``a7m``, e.g.

      a12m = [pathtoconcat + 'name12m1.ms', pathtoconcat + 'name12m2.ms', ...]
      a7m  = [pathtoconcat + 'name7m1.ms',  pathtoconcat + 'name7m2.ms', ...]

and their corresponding data weights in the concatenation (visweight-parameter in concat) in ``weight12m`` and ``weight7m``, e.g.

      weight12m = [1.,1.,...]
      weight7m  = [1.,1.,...]

In most cases, the weights are 1.0, except for 7m data, that have been simulated (0.166 = (D_7m/D_12m)^4 *(t_int_7m/t_int_12m)) or that have been manually calibrated in a CASA version < 4.3.0. Follow the instructions on https://casaguides.nrao.edu/index.php/DataWeightsAndCombination to prepare your data and choose the weights correctly. 
The ``concatms``-parameter holds the file name of the concatenated data sets.

      concatms = pathtoimage + 'skymodel-b_120L.alma.all_int-weighted.ms'       
      # path and name of concatenated file (e.g. blabla.ms)




## Files and base-names used by the combination methods (steps 1 - 8)

      vis            = ''                                          # set to '' is concatms is to be used, else define your own ms-file
      sdimage_input  = pathtoconcat + 'skymodel-b_120L.sd.image'
      imbase         = pathtoimage  + 'skymodel-b_120L'            # path + image base name
      sdbase         = pathtoimage  + 'skymodel-b_120L'            # path + sd image base name
      
If you don't need/want to concatenate data, skip thesteps=[0] and give the ``vis`` the path/name of the file or a list of files you want to image. If you leave ``vis`` blank, it will use the ``concatms`` as input. The ``sdimage_input`` links to the input SD image. All image processing results are stored under file names starting with the base names ``imbase`` (interferometric and SD-combined) or ``sdbase`` (SD alone). If the sdbase-name should not reflect any important information, it can be the same as imbase - an ``.SD.`` extension is added to the sdbase-name automatically to differentiation.


## Setup of the clean parameters (steps 1, 2, 5, 6, 7)

The parameters in this section define the clean parameters common for all tclean instances used in the combination methods including SDINT and TP2VIS
All parameters starting with ``t_`` except from ``t_maxscale`` are set in the same way as for the stand-alone tclean-task (CASA-native).


### general  - data selection and image parameters

       t_spw         = '0' 
       t_field       = '0~68' 
       t_imsize      = [1120] 
       t_cell        = '0.21arcsec'   
       t_phasecenter = 'J2000 12:00:00 -35.00.00.0000'  
       
### spectral mode - mfs -cube
The parameter ``mode`` indicates whether to perform continuum (``mfs``) or line (``cube``) imaging. 

      mode      = 'mfs'      # 'mfs' or 'cube'

DC_run.py offers two ways to define the spectral setup of a cube under the paramter ``specsetup``. 
      
      specsetup =  'INTpar'  # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup)
      
Setting it to ``INTpar`` requires the definition the number of channels, start channel and channel width - the latter being at least as large as the SD image channel width or larger, 

       t_start       = 0 
       t_width       = 1 
       t_nchan       = -1 
       t_restfreq    = '' 

whereas setting it to ``SDpar`` automatically uses the channel setup of the SD image. In addition, for ``SDpar`` one can limit the channel range translated into the combined product by using only the channels between a ``startchan`` and ``endchan`` from the SD image, else they should be set to ``None``. 

       startchan = 30  #None  # start-value of the SD image channel range you want to cut out 
       endchan   = 39  #None  #   end-value of the SD image channel range you want to cut out

If specsetup = ``INTpar``, the cut-out-channel inputs are ignored.
In ``mode='mfs'``  , ``INTpar`` is set by default but without any effect.   

      
      
### multiscale
The parameter ``mscale`` allows to choose multiscale (``MS`` - for extended and complex structures) imaging instead of simple Hogbom (``HB`` - for compact sources) clean. 

      mscale    = 'MS'       # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
       t_maxscale    = -1 

The ``t_maxscale``-parameter can be used to give the ``mscale = 'MS'``-mode a maximum size scale (expected unit: arcsec), up to which the multiscale-shapes (paraboloids) are generated, e.g. for a beam size of 1 arcsec and a maxscale of 10 arcsec (t_maxscale=10.), 
DC_run.py will create shapes of size 0 (point source), 1 arcsec, 3 arcsec, and 9 arcsec. With ``t_maxscale = -1`` the script will determine a maxscale from the largest angular scales covered by the (concatenated) interferometric data.



### masking
With the parameter ``masking`` the user can define the masking mode, i.e.
* loading a user defined mask file (``UM``, CASA-native subparameter ``t_mask``) 
* let tclean iteratively find and add clean mask regions (``AM`` - 'auto-multithreshold' in tclean, CASA-native subparameters ``t_sidelobethreshold, t_noisethreshold, t_lownoisethreshold, t_minbeamfrac, t_growiterations, t_negativethreshold``), 
* use the primary beam as a mask (``PB``, CASA-native subparameter ``t_pbmask`` for fluxlevel). 
* adjust a threshold-based mask from the interferometric and/or the SD-image (``SD-AM``, subparameters ``smoothing, RMSfactor, cube_rms, cont_chans, sdmasklev, tclean_SDAMmask, hybrid_SDAMmask, sdint_SDAMmask, TP2VIS_SDAMmask``, see section below)

      masking   = 'SD-AM'    # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
       t_mask        = '' 
       t_pbmask      = 0.4
       t_sidelobethreshold = 2.0 
       t_noisethreshold    = 4.25 
       t_lownoisethreshold = 1.5               
       t_minbeamfrac       = 0.3 
       t_growiterations    = 75 
       t_negativethreshold = 0.0 

In most cases, ``masking = 'AM'`` with its subparameters set to default (as above) is the best choice, but tends to fail for extremely extended emission.


#### SD-AM mask fine-tuning (step 1)

In cases of widespread extended emission (i.e. almost entire image), the cleaning process in ``PB`` or ``AM``-mode can diverge and lead to an insufficient image resoration.
With the ``SD-AM`` mask the bulk of the prominent emission can be extracted so that the cleaning process can be handed over to a auto-multithreshold clean to deal with the residual emission.

Generating a common mask from an interferometric and/or SD image mask at an user defined threshold (``masking  = 'SD-AM'``), requires additional input:

       smoothing  = 5    # smoothing of the threshold mask (by 'smoothing x beam')
       RMSfactor  = 0.5  # continuum rms level (not noise from emission-free regions but entire image)
       cube_rms   = 3    # cube noise (true noise) x this factor
       cont_chans = ''   # line free channels for cube rms estimation, e.g. '2~5' 
       sdmasklev  = 0.3  # image peak x this factor = threshold for SD mask

For an interferometric image based mask, a dirty image of the ``vis`` with the basic clean parameters defining the image shape is created.
In the case of continuum data, the ``RMSfactor`` is multiplied with the rms of the entire continuum image - irregardless of the emission present (i.e. it is not the true rms!). This product is used as a threshold for the mask. In the case of a cube, the true rms-noise can be computed from the line-free channels, that the user has to adjust under ``cont_chans``. This noise is multiplied with the with ``cube_rms`` and is used as a threshold of the cube-data. In both cases, the threshold mask is smoothed by the ``smoothing``-factor times the interferometric beam.
The threshold for a single dish image based mask is given by the ``sdmasklevel`` times the SD image peak flux.
If the user does not specify a clean threshold for tclean to stop
DC_run will take the threshold derived from the interferometric ``SD-AM`` mask - independent from the masking-mode that has been specified.
Once step 1 has been executed, the mask is recalculated for any changes in the mask fine-tuning parameters at the beginning of the DC_run.


#### SD-AM masks for all methods using tclean etc (steps 2, 5 - 7)
For ``masking = 'SD-AM'`` a mask is made from the threshold-clipped interferometric, from the ``sdmasklev``- clipped SD image and from the combination of both masks. The user can choose which one to use, i.e.
the options are: 'SD', 'INT', 'combined'

       tclean_SDAMmask = 'INT'  
       hybrid_SDAMmask = 'INT'     
       sdint_SDAMmask  = 'INT'     
       TP2VIS_SDAMmask = 'INT'
       

### user interaction and iterations and threshold
With the parameter ``inter`` the user can choose between interactive (``IA``) and non-interactive (``nIA``) clean. The number of clean iterations to be executed is set under ``nit``.


      inter     = 'nIA'      # interactive ('IA') or non-interactive ('nIA')
      nit       = 1000000    #      


### Setup of the base name extension describing the basic clean properties 

We can generate a meaningful base name extension to attach to the imbase, reflecting the relevant clean properties. Currently, the extension name is defined by ``mode``, ``mscale``, ``masking``, ``inter``, ``nit``, and ``specsetup``, e.g.:

      mode      = 'mfs'      # 'mfs' or 'cube'
      mscale    = 'MS'       # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
      masking   = 'SD-AM'    # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
      inter     = 'nIA'      # interactive ('IA') or non-interactive ('nIA')
      nit       = 1000000    #      
      specsetup =  'INTpar'  # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup)

DC_run uses an extension-definition of

      cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)

which gives us 

       cleansetup = '.mfs_INTpar_HB_SD-AM_nIA_n0'


### SDINT options (step 6)
For SDINT, the user can specify the parameters sdpsf and dishdia (as in sdintimaging-task) in addition. 

       sdpsf   = ''
       dishdia = 12.0


## SD factors for all methods (steps (3 - 7)

The SD data can be scaled/weighted by a factor (default: 1.0 for all).
Here, we can list multiple scaling factors per scaling parameter 
(e.g sdfac=[0.8, 1.0, 1.2] for feather) for the corresponding 
combination method to iterate over.

       sdfac   = [1.0]          # feather parameter
       SSCfac  = [1.0]          # Faridani parameter
       sdfac_h = [1.0]          # Hybrid feather paramteter
       sdg     = [1.0]          # SDINT parameter
       TPfac   = [1.0]          # TP2VIS parameter


## TP2VIS related setup (step 7)

``TPpointingTemplate`` is an ALMA 12m dataset, e.g. used in the combination, that covers the region of interest in the sky. It is used as a template for the 12m artificial SD  pointings for which TP2VIS generates mock-interferometric data. The meta-data including the antenna pointings is stored in the file ``listobsOutput`` by the *listobs*-task. ``TPpointinglist`` contains solely the antenna pointings read out from the ``listobsOutput``. 

      TPpointingTemplate        = a12m[0]        
      listobsOutput             = imbase+'.12m.log'
      TPpointinglist            = imbase+'.12m.ptg'
      TPpointinglistAlternative = 'user-defined.ptg' 
      
If a ``TPpointingTemplate`` cannot be provided the user can load his own pointing list under ``TPpointinglistAlternative`` with the content formatted like, e.g.

      J2000 11:59:53.753070 -35.01.15.95089
      J2000 11:59:53.753610 -35.00.50.63393
      J2000 11:59:53.754150 -35.00.25.31697
      ...
  
For transforming the SD image into visibilities, TP2VIS needs the rms in the SD images 
for setting the weights. Therefore, one has to specify a range of emission-free pixels 
in a continuum SD image, or a range of emission-free channels in the SD cube.

      TPnoiseRegion   = '10,30,10,30'  # emission free box in unregridded continuum SD image!
      TPnoiseChannels = '2~5'          # emission free channels in unregridded and un-cut SD cube!


## Assessment related (step 8)

In the case of an image cube, specify the line-emission channels that should be considered for moment maps,

       momchans = ''      # channels to compute moment maps (integrated intensity, etc., e.g. '2~5') 

If present, we can specify a ``skymodel``-image to compare our results to. In our examples of simulated data, we use the skymodel located in the same folder as one of the simulated data sets in pathtoconcat.

      skymodel = a12m[0].replace('.ms','.skymodel')    # model path/name used for simulating the observation, else set to ''
      
The skymodel image is expected to be CASA-imported!

