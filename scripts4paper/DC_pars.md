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

NEW: You should make sure that you input data contains solely the science observation on the target (i.e. intent = '*TARGET*') and no data for other observing intents. This is especially relevant for the combination of 12m data in TP2VIS-mode.

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
In ``mode='mfs'``  , ``specsetup`` is set to ``nt1`` meaning the number of Taylor terms for mtmfs-clean. An mfs-clean corresponds then to a mtmfs-clean with nterms=1. Currently, mfs is the only continuum mode offered and ``nt1`` is only inserted for the name without any effect on the tclean parameters.
Any accidental channel setup is ignored in this mode.
      
      
### multiscale
The parameter ``mscale`` allows to choose multiscale (``MS`` - for extended and complex structures) imaging instead of simple Hogbom (``HB`` - for compact sources) clean. 

      mscale    = 'MS'       # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
      t_maxscale    = -1 

The ``t_maxscale``-parameter can be used to give the ``mscale = 'MS'``-mode a maximum size scale (expected unit: arcsec), up to which the multiscale-shapes (paraboloids) are generated. For a beam size of e.g. 1 arcsec and a maxscale of e.g. 10 arcsec (t_maxscale=10.), 
DC_run.py will create shapes of size 0 (point source), 1 arcsec, 3 arcsec, and 9 arcsec. With ``t_maxscale = -1``, the script will determine a maxscale from the largest angular scales covered by the (concatenated) interferometric data.



### user interaction and iterations and threshold
With the parameter ``inter`` the user can choose between interactive (``IA``) and non-interactive (``nIA``) clean. The number of clean iterations to be executed is set under ``nit``. With ``t_cycleniter`` the number of minor cycle iterations before a major cycle is triggered can be restricted. For the default value of -1, CASA determines the cycleniter which is usually sufficient. The case of a poor PSF can require cycleniter of e.g. a few 10s (low SNR) to ~ 1000 (high SNR) to avoid the divergence of the clean process. The clean threshold ``t_threshold`` steers the depth of the clean, i.e. tclean stops at this peak flux level in the residual image.

      inter       = 'nIA'      # interactive ('IA') or non-interactive ('nIA')
      nit         = 1000000    #      
      t_cycleniter= -1         # number of minor cycle iterations before major cycle is triggered. default: -1 (CASA determined - usually sufficient), poor PSF: few 10s (low SNR) to ~ 1000 (high SNR)
      t_threshold = ''         # e.g. '0.1mJy', can be left blank -> DC_run will estimate from SD-INT-AM mask for all other masking modes, too


### masking
With the parameter ``masking`` the user can define the masking mode, i.e.
* loading a user defined mask file (``UM``, CASA-native subparameter ``t_mask``) 
* let tclean iteratively find and add clean mask regions (``AM`` - 'auto-multithreshold' in tclean, CASA-native subparameters ``t_sidelobethreshold, t_noisethreshold, t_lownoisethreshold, t_minbeamfrac, t_growiterations, t_negativethreshold``), 
* use the primary beam as a mask (``PB``, CASA-native subparameter ``t_pbmask`` for fluxlevel). 
* adjust a threshold-based mask from the interferometric and/or the SD-image (``SD-INT-AM``, subparameters ``smoothing, RMSfactor, cube_rms, cont_chans, sdmasklev, tclean_SDAMmask, hybrid_SDAMmask, sdint_SDAMmask, TP2VIS_SDAMmask``, see section below)

      masking              = 'SD-INT-AM'    # 'UM' (user mask), 'SD-INT-AM' (SD+INT+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
       t_mask              = '' 
       t_pbmask            = 0.4
       t_sidelobethreshold = 2.0 
       t_noisethreshold    = 4.25 
       t_lownoisethreshold = 1.5               
       t_minbeamfrac       = 0.3 
       t_growiterations    = 75 
       t_negativethreshold = 0.0 

In most cases, ``masking = 'AM'`` with its subparameters set to default (as above) is the best choice, but tends to fail for extremely extended emission.

NEW I.E. SHIFTED: The ``UM``- and the ``SD-INT-AM``-mode are designed such that a user-defined fraction of the tclean iterations 

       fniteronusermask = 0.3   # valid between 0.0 an 1.0
       
is spent on the provided mask. Once the stopping-threshold or interation limit ``fniteronusermask``*``nit`` is reached, tclean is restarted in ``AM``-mode and continues cleaning also on regions outside the providedmask until the threshold or the (1-``fniteronusermask``)*``nit`` is reached. 
With n ``fniteronusermask`` = 0.0, DC_run loads the provided mask with one iteration and then moves over to the ``AM``-mode. An ``fniteronusermask`` = 1.0 makes DC_run work solely on the provided mask for all iterations. Both extremes can give insufficient cleaning results, therefore a flexible mixture of the two modes is introduced by the 
``fniteronusermask``-parameter.
       
       

#### SD-INT-AM mask fine-tuning (step 1)

In cases of widespread extended emission (i.e. almost entire image), the cleaning process in ``PB`` or ``AM``-mode can diverge and lead to an insufficient image resoration.
With the ``SD-INT-AM`` mask the bulk of the prominent emission can be extracted so that the cleaning process can be handed over to a auto-multithreshold clean (might need to adjust ``AM``-subparameters) to deal with the residual emission.

Generating a common mask from an interferometric and/or SD image mask at an user defined threshold (``masking  = 'SD-INT-AM'``) requires additional input:

       theoreticalRMS = False  # use the theoretical RMS from the template image's 'sumwt', instead of measuring the RMS in a threshregion and cont_chans range of a template image
       smoothing    = 5    # smoothing of the threshold mask (by 'smoothing x beam')
       threshregion = '150,200,150,200'  # emission free region in template continuum or cube image
       RMSfactor    = 0.5  # continuum rms level (if threshregion not defined: noise  is not from emission-free regions but entire image)
       cube_rms     = 3    # cube noise (true noise) x this factor
       cont_chans   = ''   # line free channels for cube rms estimation, e.g. '2~5' 
       sdmasklev    = 0.3  # image peak x this factor = threshold for SD mask

For an interferometric image based mask, a dirty image of the ``vis`` with the basic clean parameters defining the image shape is created. 


In order to setup the parameters above it is best to execute step 1 once - SD_INT_AM parameters are irrelevant at this moment. 
This step regrids the SD and creates a dirty image of the ``vis`` with the basic clean parameters defining the image shape. Inspect dirty image and SD image 

      imnameth      = imbase + '.'+mode +'_'+ specsetup +'_template.image'
      sdreordered_cut = sdbase +potential-channel-cut-out+'.SD_ro.image' # SDpar case 
         or 
      sdroregrid      = sdbase +'.SD_ro-rg_'+specsetup+'.image'          # INTpar case

and find a suitable emission free region (continuum) or channel range (cube) in e.g. the CASA viewer (setting a box/region in the image in the CASA viewer gives you the rms therein in the region panel of the viewer). Define these in the ``threshregion`` and ``cont_chans``, respectively. Sometimes, there are no fully emission-free channels on a cube, so that one needs to select a range of the weakest emission channels and a region that is emission-free for all these selected channels. For fully emission-free channels, set ``threshregion = ''``.
Then, play with the image contours and their flux levels to find a good cut-off threshold for creating the clean mask. This flux value of the interferometric image is parametrised in DC_run.py as ``RMSfactor`` * RMS measured in the user defined threshregion in the continuum image or as ``cube_rms`` * RMS measured in the user defined cont_chans (and threshregion, if needed) in the cube image. If the image contains no reliably emission-free region, you can either use the entire image ``threshregion = ''`` and note that the measured RMS is not the true RMS of the image, or use the theoretical RMS defined by the uv-coverage by setting ``theoreticalRMS = True``. This RMS is derived from the '*.sumwt'-image generated during imaging and can be understood as a lower limit of the RMS. The RMS in the actual image is often higher due to e.g. an imperfect calibration.


The resulting threshold-clipped mask is smoothed by the ``smoothing``-factor times the interferometric beam.

The flux threshold for a single dish image based mask is given by the ``sdmasklevel`` times the SD image peak flux.

NEW: Having the parameters set, a second execution of step 1 is not necessary, because the threshold and masks are recalculated for any changes in the mask fine-tuning parameters at the beginning of each DC_run execution. In fact, when step 2 (ordinary tclean) has been executed, the tclean-product will be used as a templete for threshold and mask generation instead - under the assumption that the strongest sidelobes have been removed by cleaning and therefore yielding a more accurate representation of the actual brightness distribution. If the clean in step 2 diverged, delete the corresponding image product so that DC_run will use the dirty image from step 1 as a template.

Nevertheless, the updated *pars*-file needs to be executed before DC_run, else your new SD_INT_AM parameter are not implemented.

Whenever the interferometric masks is created, DC_run gives feedback in the terminal about the measured RMS and the applied threshold that is used for the mask - and for cleaning if specified ``t_threshold`` is not specified.

If the user does not specify a clean threshold ``t_threshold`` steering the depth of the clean, DC_run will take the threshold derived from the interferometric ``SD-INT-AM`` mask - independent from the masking-mode that has been specified. 
This implies that the  the parameters above are not only relevant for creating the SD-INT-AM mask, but also for auto-determining a reasonable clean threshold for DC_run in general.

Nonetheless, you can set up a ``t_threshold`` that is different from the threshold the interferometric mask is based on, e.g. clean deeper that the level of the mask has been defined for. 










#### SD-INT-AM masks for all methods using tclean etc (steps 2, 5 - 7)
For ``masking = 'SD-INT-AM'`` a mask is made from the threshold-clipped interferometric, from the ``sdmasklev``- clipped SD image and from the combination of both masks. The user can choose which one to use, i.e.
the options are: 'SD', 'INT', 'combined'

       tclean_SDAMmask = 'INT'  
       hybrid_SDAMmask = 'INT'     
       sdint_SDAMmask  = 'INT'     
       TP2VIS_SDAMmask = 'INT'


       



### Setup of the base name extension describing the basic clean properties 

We can generate a meaningful base name extension to attach to the imbase, reflecting the relevant clean properties. Currently, the extension name is defined by ``mode``, ``mscale``, ``masking``, ``inter``, ``nit``, and ``specsetup``, e.g.:

      mode      = 'mfs'      # 'mfs' or 'cube'
      mscale    = 'MS'       # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
      masking   = 'SD-INT-AM'    # 'UM' (user mask), 'SD-INT-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
      inter     = 'nIA'      # interactive ('IA') or non-interactive ('nIA')
      nit       = 1000000    #      
      specsetup =  'INTpar'  # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup)

DC_run uses an extension-definition of

      cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)

which gives us 

       cleansetup = '.mfs_INTpar_HB_SD-INT-AM_nIA_n0'


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
  
An alternative pointing list can be derived from e.g. a simulation (simobserve) or a setup (ALMA OT) of 12m observation with the same/similar map size and position. 
For transforming the SD image into visibilities, TP2VIS needs the rms in the SD images 
for setting the weights. Therefore, one has to specify a range of emission-free pixels 
in a continuum SD image, or a range of emission-free channels in the SD cube.

      TPnoiseRegion   = '10,30,10,30'  # emission free box in unregridded continuum SD image!
      TPnoiseChannels = '2~5'          # emission free channels in unregridded and un-cut SD cube!
      
These values can be determined from the step 1 - product ``sdreordered`` or ``sdreordered_cut``.    


## Assessment related (step 8)

In the case of an image cube, specify the line-emission channels that should be considered for moment maps as well as which channel to pick to run the single channel assessment on,

       momchans = ''      # channels to compute moment maps (integrated intensity, etc., e.g. '2~5') 
       mapchan = None     # cube channel (integer) of interest to use for assessment in step 8


If present, we can specify a ``skymodel``-image to compare our results to. In our examples of simulated data, we use the skymodel located in the same folder as one of the simulated data sets in pathtoconcat.

      skymodel = a12m[0].replace('.ms','.skymodel')    # model path/name used for simulating the observation, else set to ''
      
The skymodel image is expected to be CASA-imported!
To exclude low flux values from the assessment, you can set a threshold below which the data is masked. Option 'None' will use the rms derived by the CLEAN threshold and masking routine, 'clean-thresh' the CLEANing threshold used, and a number(float) will be the cut-off threshold in Jy/beam

      assessment_thresh = 0.01        # default: None, option: None, 'clean-thresh', or flux value(float, translated units: Jy/bm), 
                                       # threshold mask to exclude low SNR pixels, if None, use rms measurement from threshold_mask for tclean (see SD-INT-AM)
                                       # also used as lower flux limit for moment 0 map creation



