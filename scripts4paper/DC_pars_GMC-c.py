#
#   GMC template for setting up a DC_script.py
#
#   Input are:     skymodel-c_120L.alma.cycle6.4.2018-10-02.ms
#                  (optionally more, there are 12 (8*12m + 4*7m) in this skymodel-c_120L)
#                  skymodel-c_120L.sd.image

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
#thesteps=[6]

######## collect only the product name (i.e. run assessment on already existing combination products)?          
dryrun = False    # False to execute combination, True to gather filenames only
 

#  you can use _s4p_data if you want to use the configure'd setup,
#  but feel free to override
#  _s4p_data :  for read-only data
#  _s4p_work :  for reading/writing

pathtoconcat = _s4p_data + '/skymodel-c.sim/skymodel-c_120L/'
pathtoimage  = _s4p_work + '/GMC-c/'



# setup for concat (the optional step 0)

a12m=[pathtoconcat + 'skymodel-c_120L.alma.cycle6.4.2018-10-02.ms',
      pathtoconcat + 'skymodel-c_120L.alma.cycle6.1.2018-10-02.ms',
      pathtoconcat + 'skymodel-c_120L.alma.cycle6.4.2018-10-03.ms',
      pathtoconcat + 'skymodel-c_120L.alma.cycle6.1.2018-10-03.ms',
      pathtoconcat + 'skymodel-c_120L.alma.cycle6.4.2018-10-04.ms',
      pathtoconcat + 'skymodel-c_120L.alma.cycle6.1.2018-10-04.ms',
      pathtoconcat + 'skymodel-c_120L.alma.cycle6.4.2018-10-05.ms',
      pathtoconcat + 'skymodel-c_120L.alma.cycle6.1.2018-10-05.ms'
      ]
      
weight12m = [1., 1., 1., 1., 1., 1., 1., 1.]
        
a7m =[pathtoconcat + 'skymodel-c_120L.aca.cycle6.2018-10-20.ms',
      pathtoconcat + 'skymodel-c_120L.aca.cycle6.2018-10-21.ms',
      pathtoconcat + 'skymodel-c_120L.aca.cycle6.2018-10-22.ms',
      pathtoconcat + 'skymodel-c_120L.aca.cycle6.2018-10-23.ms'
      ]

weight7m = [0.116, 0.116, 0.116, 0.116]  # weigthing for SIMULATED data !



skymodel=a12m[0].replace('.ms','.skymodel')    # model used for simulating the observation, expected to be CASA-imported



#  the concatenated MS 
concatms     = pathtoimage + 'skymodel-c_120L.alma.all_int-weighted.ms'


############# input to combination methods ###########

vis             = ''                                         # set to '' is concatms is to be used, else define your own ms-file
sdimage_input   = pathtoconcat + 'skymodel-c_120L.sd.image'
imbase          = pathtoimage + 'skymodel-c_120L'            # path + image base name
sdbase          = pathtoimage + 'skymodel-c_120L'            # path + sd image base name


# TP2VIS related:
TPpointingTemplate        = a12m[0]
listobsOutput             = imbase+'.12m.log'
TPpointinglist            = imbase+'.12m.ptg'
TPpointinglistAlternative = 'user-defined.ptg' 

TPnoiseRegion             = '980,980,1010,1010'  # in unregridded SD image (i.e. sdreordered = sdbase +'.SD_ro.image')
TPnoiseChannels           = '2~5'              # in unregridded and un-cut SD cube (i.e. sdreordered = sdbase +'.SD_ro.image')!



mode      = 'mfs'      # 'mfs' or 'cube'
mscale    = 'HB'       # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
masking   = 'SD-AM'    # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
inter     = 'nIA'      # interactive ('IA') or non-interactive ('nIA')
nit       = 0#1000000          # max = 9.9 * 10**9 

specsetup =  'INTpar'  # 'SDpar' (use SD cube's spectral setup) or 'INTpar' (user defined cube setup)

# if "SDpar", want to use just a channel-cut-out of the SD image? , 
# else set to None (None automatically for 'INTpar'

startchan = 30  #None  # start-value of the SD image channel range you want to cut out 
endchan   = 39  #None  #   end-value of the SD image channel range you want to cut out

# resulting name part looks like
# cleansetup = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter +'_n'+ str(nit)


smoothing  = 5.     # smoothing of the threshold mask (by 'smoothing x beam')
RMSfactor  = 0.5   # continuum rms level (not noise from emission-free regions but entire image)
cube_rms   = 3.     # cube noise (true noise) x this factor
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
t_maxscale    = 10.              # recommendations/explanations 
t_mask        = '' 
t_pbmask      = 0.4
sidelobethreshold = 2.0 
noisethreshold    = 4.25 
lownoisethreshold = 1.5               
minbeamfrac       = 0.3 
growiterations    = 75 
negativethreshold = 0.0 
 

########## sdint parameters 

sdpsf   = ''
dishdia = 12.0
        
          
########### SD factors for all methods:                       
               
sdfac   = [1.0]          # feather parameter
SSCfac  = [1.0]          # Faridani parameter
sdfac_h = [1.0]          # Hybrid feather paramteter
sdg     = [1.0]          # SDINT parameter
TPfac   = [1.0]          # TP2VIS parameter
          

          

