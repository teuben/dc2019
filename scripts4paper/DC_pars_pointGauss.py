#
#   GMC template for setting up a DC_script.py
#
#   Input are:     pointSrcGauss_3L.alma.cycle6.1.2018-10-02.ms
#                  (optionally more, there are 12 (2*12m + 1*7m) in this pointSrcGauss_3L)
#                  pointSrcGauss_3L.sd.image

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

#thesteps=[0,1,2,3,4,5,6,7,8]
thesteps=[1,5]

######## collect only the product name (i.e. run assessment on already existing combination products)?          
dryrun = False    # False to execute combination, True to gather filenames only
 

#  you can use _s4p_data if you want to use the configure'd setup,
#  but feel free to override
#  _s4p_data :  for read-only data
#  _s4p_work :  for reading/writing

pathtoconcat = _s4p_data + '/pointSrc.sim/pointSrcGauss_3L/'
pathtoimage  = _s4p_work + '/pointGauss/'



# setup for concat (the optional step 0)

a12m=[pathtoconcat + 'pointSrcGauss_3L.alma.cycle6.1.2018-10-02.ms',
      pathtoconcat + 'pointSrcGauss_3L.alma.cycle6.4.2018-10-02.ms'
      ]
   
weight12m = [1., 1.]
  
      
a7m =[pathtoconcat + 'pointSrcGauss_3L.aca.cycle6.2018-10-05.ms'
      ]

weight7m = [0.116]  # weigthing for SIMULATED data !



skymodel=a12m[0].replace('.ms','.skymodel')    # model used for simulating the observation, expected to be CASA-imported



#  the concatenated MS 
concatms     = pathtoimage + 'pointGauss.alma.all_int-weighted.ms'       # path and name of concatenated file



############# input to combination methods ###########

vis            = ''                                    # set to '' if concatms is to be used, else define your own ms-file
sdimage_input  = pathtoconcat + 'pointSrcGauss_3L.sd.image'
imbase         = pathtoimage + 'pointGauss'            # path + image base name
sdbase         = pathtoimage + 'pointGauss'            # path + sd image base name


# TP2VIS related:
TPpointingTemplate        = a12m[0]
listobsOutput             = imbase+'.12m.log'
TPpointinglist            = imbase+'.12m.ptg'
TPpointinglistAlternative = 'user-defined.ptg' 

TPnoiseRegion             = '150,200,150,200'  # in unregridded SD image (i.e. sdreordered = sdbase +'.SD_ro.image')
TPnoiseChannels           = '2~5'              # in unregridded and un-cut SD cube (i.e. sdreordered = sdbase +'.SD_ro.image')!



mode      = 'mfs'      # 'mfs' or 'cube'
mscale    = 'MS'       # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
masking   = 'SD-AM'    # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
inter     = 'nIA'      # interactive ('IA') or non-interactive ('nIA')
nit       = 10#1000000          # max = 9.9 * 10**9 

specsetup =  'INTpar'  # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup)

# if "SDpar", want to use just a channel-cut-out of the SD image? , 
# else set to None (None automatically for 'INTpar'

startchan = 30  #None  # start-value of the SD image channel range you want to cut out 
endchan   = 39  #None  #   end-value of the SD image channel range you want to cut out

# resulting name part looks like
# cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)


smoothing  = 5     # smoothing of the threshold mask (by 'smoothing x beam')
RMSfactor  = 0.5   # continuum rms level (not noise from emission-free regions but entire image)
cube_rms   = 3     # cube noise (true noise) x this factor
cont_chans = ''    # line free channels for cube rms estimation
sdmasklev  = 0.3   # maximum x this factor = threshold for SD mask


momchans = ''      # channels to compute moment maps (integrated intensity, etc.) 

                     
########## general tclean parameters


t_spw         = '0' 
t_field       = '0~68' 
t_imsize      = [1120] 
t_cell        = '0.21arcsec'    # arcsec
t_phasecenter = 'J2000 12:00:00 -35.00.00.0000'            
t_start       = 0 
t_width       = 1 
t_nchan       = -1 
t_restfreq    = ''
t_threshold   = ''               # SDINT: None 
t_maxscale    = -1 #10.              # recommendations/explanations 
t_mask        = '' 
t_pbmask      = 0.4
t_sidelobethreshold = 2.0 
t_noisethreshold    = 4.25 
t_lownoisethreshold = 1.5               
t_minbeamfrac       = 0.3 
t_growiterations    = 75 
t_negativethreshold = 0.0 
 

########## sdint parameters 

sdpsf   = ''
dishdia = 12.0
                 

########### SD-AM masks for all methods using tclean etc.:                       

# options: 'SD', 'INT', 'combined'

tclean_SDAMmask = 'INT'  
hybrid_SDAMmask = 'SD'     
sdint_SDAMmask  = 'INT'     
TP2VIS_SDAMmask = 'INT'     


########### SD factors for all methods:                       
               
sdfac   = [1.0]          # feather parameter
SSCfac  = [1.0]          # Faridani parameter
sdfac_h = [1.0]          # Hybrid feather paramteter
sdg     = [1.0]          # SDINT parameter
TPfac   = [1.0]          # TP2VIS parameter
          

          

