#  DC_pars_M100trim.py:    parameters for a trimmed matching channels M100
#
#  to work with, and edit parameters here, copy this script to DC_pars.py to be used by your DC_script.py

#  Data and procedure are described here:
#        https://casaguides.nrao.edu/index.php?title=M100_Band3_Combine_5.4
#  except we already prepared all the data to be in 71 matching channels. 
#
#  This assumes you have run M100_trimdata5.py, which is a smaller 2GB dataset with
#  calibrated data and 71 channels already lined up between 12m, 7m and TP
#      M100_aver_12.ms
#      M100_aver_7.ms
#      M100_TP_CO_cube.bl.image

step_title = {0: 'Concat',
              1: 'Prepare the SD-image',
              2: 'Clean for Feather/Faridani',
              3: 'Feather', 
              4: 'Faridani short spacings combination (SSC)',
              5: 'Hybrid (startmodel clean + Feather)',
              6: 'SDINT',
              7: 'TP2VIS'
              }

#thesteps=[0,1,2,3,4,5,6,7]
thesteps=[3]

import os 
import sys 


# this script assumes the DC_locals.py has been execfiled'd - see the README.md how to do this

pathtoconcat = _s4p_data + '../scripts/'
pathtoimage  = _s4p_work + '/'


############ USER INPUT needed - beginning ##############


# to quote the casaguide, "In order to run this guide you will need the following three files:"
_7ms  = 'M100_aver_7.ms'
_12ms = 'M100_aver_12.ms'
_sdim = 'M100_TP_CO_cube.bl.image'


### delete garbage from aboprted script ###
os.system('rm -rf '+pathtoimage + 'TempLattice*')


# setup for concat (the optional step 0)

thevis = [pathtoconcat + _12ms]


a12m = thevis

weightscale = [1.0]

concatms     = pathtoimage + 'M100-B3.alma.all_int-weighted.ms' 




############# input to combination methods ###########

vis            = concatms
sdimage_input  = pathtoconcat + _sdim
imbase         = pathtoimage + 'M100-B3'            # path + image base name
sdbase         = pathtoimage + 'M100-B3'            # path + sd image base name


# TP2VIS related:
TPpointingTemplate = a12m[0]
listobsOutput      = imbase+'.12m.log'
TPpointinglist     = imbase+'.12m.ptg'
TPpointinglistAlternative = 'user-defined.ptg' 

TPnoiseRegion   = '150,200,150,200'  # in unregridded SD image (i.e. sdreordered = sdbase +'.SD_ro.image')
TPnoiseChannels = '2~5'        # in unregridded and un-cut SD cube (i.e. sdreordered = sdbase +'.SD_ro.image')!



######## names and parameters that should be noted in the file name ######

# structure could be something like:
#    imname = imbase + cleansetup + combisetup 

mode   = 'mfs'        # 'mfs' or 'cube'
mscale = 'HB'         # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
masking  = 'SD-AM'    # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
inter = 'nIA'         # interactive ('IA') or non-interactive ('nIA')
nit = 100               # max = 9.9 * 10**9 

specsetup =  'INTpar' # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup)
######### if "SDpar", want to use just a channel-cut-out of the SD image? , 
# else set to None (None automatically for 'INTpar'
startchan = 30  #None  # start-value of the SD image channel range you want to cut out 
endchan   = 39  #None  #   end-value of the SD image channel range you want to cut out




# resulting name part looks like
# cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)


######### specific inputs for masking  = 'SD-AM', else ignore

smoothing = 5    # smoothing of the threshold mask (by 'smoothing x beam')
RMSfactor = 0.5  # continuum rms level (not noise from emission-free regions but entire image)
cube_rms = 3     # cube noise (true noise) x this factor
cont_chans =''   # line free channels for cube rms estimation
sdmasklev = 0.3  # maximum x this factor = threshold for SD mask




                      
########## general tclean parameters

# M100                           
general_tclean_param = dict(#overwrite  = overwrite,
                           spw         = '', #'0~2', #'0', 
                           field       = '', #'0~68', 
                           specmode    = mode,      # ! change in variable above dict !        
                           imsize      = 560, #800, #[1120], 
                           cell        = '0.5arcsec', #'0.21arcsec',    # arcsec
                           phasecenter = 'J2000 12h22m54.9 +15d49m15', #'J2000 12:00:00 -35.00.00.0000',             
                           start       = '1550km/s', #'1400km/s', #0, 
                           width       = '5km/s', #1, 
                           nchan       = 10, #70, #-1, 
                           restfreq    = '115.271202GHz', #'',
                           threshold   = '',        # SDINT: None 
                           maxscale    = 10.,              # recommendations/explanations 
                           niter      = nit,               # ! change in variable above dict !
                           mask        = '', 
                           pbmask      = 0.4,
                           #usemask           = 'auto-multithresh',    # couple to interactive!              
                           sidelobethreshold = 2.0, 
                           noisethreshold    = 4.25, 
                           lownoisethreshold = 1.5,               
                           minbeamfrac       = 0.3, 
                           growiterations    = 75, 
                           negativethreshold = 0.0)#, 
                           #sdmasklev=0.3)   # need to overthink here                            


########### SDint specific parameters:

sdint_tclean_param = dict(sdpsf   = '',
                         #sdgain  = 5,     # own factor! see below!
                         dishdia = 12.0)
          
          
          
########### SD factors for all methods:                       
                       
# feather parameters:
sdfac   = [1.0]

# Faridani parameters:
SSCfac  = [1.0]

# Hybrid feather parameters:
sdfac_h = [1.0]

# SDINT parameters:
sdg     = [1.0]

## TP2VIS parameters:
TPfac   = [1.0] 

         
          
######## collect only the product name?          
dryrun = False    # False to execute combination, True to gather filenames only
          
          
          
          
############### USER INPUT - end ##################          
