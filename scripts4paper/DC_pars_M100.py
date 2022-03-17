#  DC_pars_M100.py:    parameters for M100
#
#  to work with, and edit parameters here, copy this script to DC_pars.py to be used by your DC_script.py

#  Data and procedure are described here:
#        https://casaguides.nrao.edu/index.php?title=M100_Band3_Combine_5.4

step_title = {0: 'Concat',
              1: 'Prepare the SD-image',
              2: 'Clean for Feather/Faridani',
              3: 'Feather', 
              4: 'Faridani short spacings combination (SSC)',
              5: 'Hybrid (startmodel clean + Feather)',
              6: 'SDINT',
              7: 'TP2VIS',
              8: 'Assessment of the combination results'
              }

thesteps=[0,1,2,3,4,5,6,7,8]

#thesteps=[7]

dryrun = True    # False to execute combination, True to gather filenames only

 


## Paths to the input and output files

# this script assumes the DC_locals.py has been execfiled'd - see the README.md how to do this
#  you can use _s4p_data if you want to use the configure'd setup,
#  but feel free to override
#  _s4p_data :  for read-only data
#  _s4p_work :  for reading/writing

pathtoconcat = _s4p_data #+ '/M100/'
pathtoimage  = _s4p_work + '/M100/'

# to quote the casaguide, "In order to run this guide you will need the following three files:"
_7ms  = '/M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms'
_12ms = '/M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms'
_sdim = '/M100_Band3_ACA_ReferenceImages_5.1/M100_TP_CO_cube.spw3.image.bl'


# setup for concat (step 0)

a12m= [pathtoconcat + _12ms
      ]
a7m = [pathtoconcat + _7ms
      ]      
weight12m = [1.]
weight7m  = [1.]  # weigthing for REAL data !  If CASA calibration older than 4.3.0: weight: 0.193

concatms     = pathtoimage + 'M100-B3.alma.all_int-weighted.ms'  # path and name of concatenated file



## Files and base-names used by the combination methods (steps 1 - 8)

vis            = ''                                  # set to '' if concatms is to be used, else define your own ms-file
sdimage_input  = pathtoconcat + _sdim                #
imbase         = pathtoimage + 'M100-B3'  # path + image base name
sdbase         = pathtoimage + 'M100-B3'  # path + sd image base name



## Setup of the clean parameters (steps 1, 2, 5, 6, 7)

### general  - data selection and image parameters
						
t_spw         = '' 
t_field       = ''
t_imsize      = 560  
t_cell        = '0.5arcsec' 
t_phasecenter = 'J2000 12h22m54.9 +15d49m15'  	


### spectral mode - mfs -cube
				
mode       = 'cube'          # 'mfs' or 'cube'
specsetup  =  'INTpar'       # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup)
                             
t_start    = '1400km/s'      # e.g.,  0 (first chan),  '10km/s',  '10MHz'
t_width    = '5km/s'       # e.g.,  1 (one chan),  '-100km/s', '200GHz'
t_nchan    = 70              # e.g., -1 (all chans),        20 ,     100
t_restfreq = '115.271202GHz' # e.g., '234.567GHz'
                             			          
startchan  = 30      # None  # e.g., 30, start-value of the SD image channel range you want to cut out 
endchan    = 39      # None  # e.g., 39,   end-value of the SD image channel range you want to cut out
		
				      
### multiscale                

mscale     = 'HB'             # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
t_maxscale = -1               # for 'MS': number for largest scale size ('arcsec') expected in source


### user interaction and iterations and threshold

inter       = 'nIA'           # interactive ('IA') or non-interactive ('nIA')
nit         = 0 #10000000      # number of iterations
t_threshold = ''              # e.g. '0.1mJy', can be left blank -> DC_run will estimate from SD-INT-AM mask for all other masking modes, too


### masking

masking  = 'SD-INT-AM'        # 'UM' (user mask), 'SD-INT-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
t_mask              = ''      # specify for 'UM', mask name
t_pbmask            = 0.2     # specify for 'PM', cut-off level
t_sidelobethreshold = 2.0     # specify for 'AM', default: 2.0 
t_noisethreshold    = 4.25    # specify for 'AM', default: 4.25 
t_lownoisethreshold = 1.5     # specify for 'AM', default: 1.5             
t_minbeamfrac       = 0.3     # specify for 'AM', default: 0.3 
t_growiterations    = 75      # specify for 'AM', default: 75 
t_negativethreshold = 0.0     # specify for 'AM', default: 0.0 


#### SD-INT-AM mask fine-tuning (step 1)

smoothing    = 5.               # smoothing of the threshold mask (by 'smoothing x beam')
threshregion = ''               # emission free region in template continuum or channel image
RMSfactor    = 0.5              # continuum rms level (not noise from emission-free regions but entire image)
cube_rms     = 3.               # cube noise (true noise) x this factor
cont_chans   = '1~7,64~69'      # line free channels for cube rms estimation
sdmasklev    = 0.3              # maximum x this factor = threshold for SD mask
				              

#### SD-INT-AM masks for all methods using tclean etc (steps 2, 5 - 7)
# options: 'SD', 'INT', 'combined'

tclean_SDAMmask = 'INT'  
hybrid_SDAMmask = 'INT'     
sdint_SDAMmask  = 'INT'     
TP2VIS_SDAMmask = 'INT' 
fniteronusermask = 0.3


### SDINT options (step 6)

sdpsf   = ''
dishdia = 12.0


## SD factors for all methods (steps (3 - 7)
               
sdfac   = [1.0]               # feather parameter
SSCfac  = [1.0]               # Faridani parameter
sdfac_h = [1.0]               # Hybrid feather paramteter
sdg     = [1.0]               # SDINT parameter
TPfac   = [1.0]               # TP2VIS parameter


## TP2VIS related setup (step 7)

TPpointingTemplate        = a12m[0]
listobsOutput             = imbase+'.12m.log'
TPpointinglist            = imbase+'.12m.ptg'
Epoch                     = 'J2000'    # Epoch in listobs, e.g. 'J2000'

TPpointinglistAlternative = 'user-defined.ptg' 

TPnoiseRegion             = '150,200,150,200'  # in unregridded SD image (i.e. sdreordered = sdbase +'.SD_ro.image')
TPnoiseChannels           = '1~7'              # in unregridded and un-cut SD cube (i.e. sdreordered = sdbase +'.SD_ro.image')!

      
## Assessment related (step 8)

momchans = '8~63'             # line-free: '1~7,64~69'      # channels to compute moment maps (integrated intensity, etc.) 
mapchan  = None               # cube channel (integer) of interest to use for assessment in step 8. None = central channel
				              
skymodel = ''                 # model used for simulating the observation, expected to be CASA-imported


