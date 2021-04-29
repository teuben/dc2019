"""
Script to use the datacomb module

by L. Moser-Fischer, Oct 2020

Based on the work at the Workshop
"Improving Image Fidelity on Astronomical Data", 
Lorentz Center, Leiden, August 2019, 
and subsequent follow-up work. 

Run under CASA 6. (does CASA 5 stil work?)

Typical use in CASA6:
     execfile("DC_script.py",globals())

"""

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
thesteps=[5]

print("STEPS:",thesteps)

import os 
import sys 
#import glob


from importlib import reload  
import datacomb as dc
reload(dc)
from casatasks import immath
from casatasks import casalog


#   Need to find a way to execfile yet another parameter file?

pathtoconcat = _s4p_data + '/skymodel-c.sim/skymodel-c_120L/'
pathtoimage  = _s4p_work + '/'


############ USER INPUT needed - beginning ##############


# path to input and outputs
#pathtoconcat = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/M100-data/'   # path to the folder with the files to be concatenated
#pathtoconcat = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/ToshiSim/gmcSkymodel_120L/gmc_120L/'   # path to the folder with the files to be concatenated
#pathtoconcat = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/ToshiSim/skymodel-c.sim/skymodel-c_120L/'   # path to the folder with the files to be concatenated
#pathtoimage  = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/DC_Ly_tests/'                          # path to the folder where to put the combination and image results


### delete garbage from aboprted script ###
os.system('rm -rf '+pathtoimage + 'TempLattice*')


# setup for concat 

#a12m=[#pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-02.ms',
      #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-02.ms',
      #pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-03.ms',
      #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-03.ms',
      #pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-04.ms',
      #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-04.ms',
      #pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-05.ms',
      #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-05.ms']
      
#a7m =[#pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-20.ms',
      #pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-21.ms',
      #pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-22.ms',
      #pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-23.ms']

#thevis = a12m
#thevis = thevis.extend(a7m)

#thevis = [pathtoconcat + 'M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms']#,

thevis = [pathtoconcat + 'skymodel-c_120L.alma.cycle6.4.2018-10-02.ms']
a12m = thevis


#weight12m = [1., 1., 1., 1., 1., 1., 1.]
#weight7m = [0.116, 0.116, 0.116, 0.116]
#
#weightscale = weight12m
#weightscale = weightscale.expand(weight7m)
#
weightscale = [1.]#, 1., 1., 1., 1., 1., 1., 1.,
               #0.116, 0.116, 0.116, 0.116]

#concatms     = pathtoimage + 'M100-B3.alma.all_int-weighted.ms'       # path and name of concatenated file
#concatms     = pathtoimage + 'skymodel-b_120L.alma.all_int-weighted.ms'       # path and name of concatenated file
concatms     = pathtoimage + 'skymodel-c_120L.alma.all_int-weighted.ms'       # path and name of concatenated file




############# input to combination methods ###########

vis       = concatms
#sdimage_input  = pathtoconcat + 'M100_Band3_ACA_ReferenceImages/M100_TP_CO_cube_1550-5.image'
#sdimage_input  = pathtoconcat + 'M100_Band3_ACA_ReferenceImages/M100_TP_CO_cube.bl.image'
#sdimage_input  = pathtoconcat + 'gmc_120L.sd.image'
sdimage_input   = pathtoconcat + 'skymodel-c_120L.sd.image'
#imbase    = pathtoimage + 'M100-B3'            # path + image base name
#imbase    = pathtoimage + 'skymodel-b_120L'            # path + image base name
imbase    = pathtoimage + 'skymodel-c_120L'            # path + image base name
#sdbase    = pathtoimage + 'M100-B3'            # path + sd image base name
sdbase    = pathtoimage + 'skymodel-c_120L.sd'            # path + sd image base name



# TP2VIS related:
TPpointingTemplate = a12m[0]
listobsOutput  = imbase+'.12m.log'
TPpointinglist = imbase+'.12m.ptg'
TPpointinglistAlternative = 'user-defined.ptg' 

TPnoiseRegion = '150,200,150,200'  # in unregridded SD image (i.e. sdreordered = sdbase +'.SD_ro.image')
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

# skymodel
general_tclean_param = dict(#overwrite  = overwrite,
                           spw         = '0', 
                           field       = '0~68', 
                           specmode    = mode,      # ! change in variable above dict !        
                           imsize      = [1120], 
                           cell        = '0.21arcsec',    # arcsec
                           phasecenter = 'J2000 12:00:00 -35.00.00.0000',             
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
 
## M100                           
#general_tclean_param = dict(#overwrite  = overwrite,
#                           spw         = '', #'0~2', #'0', 
#                           field       = '', #'0~68', 
#                           specmode    = mode,      # ! change in variable above dict !        
#                           imsize      = 560, #800, #[1120], 
#                           cell        = '0.5arcsec', #'0.21arcsec',    # arcsec
#                           phasecenter = 'J2000 12h22m54.9 +15d49m15', #'J2000 12:00:00 -35.00.00.0000',             
#                           start       = '1550km/s', #'1400km/s', #0, 
#                           width       = '5km/s', #1, 
#                           nchan       = 10, #70, #-1, 
#                           restfreq    = '115.271202GHz', #'',
#                           threshold   = '',        # SDINT: None 
#                           maxscale    = 10.,              # recommendations/explanations 
#                           niter      = nit,               # ! change in variable above dict !
#                           mask        = '', 
#                           pbmask      = 0.4,
#                           #usemask           = 'auto-multithresh',    # couple to interactive!              
#                           sidelobethreshold = 2.0, 
#                           noisethreshold    = 4.25, 
#                           lownoisethreshold = 1.5,               
#                           minbeamfrac       = 0.3, 
#                           growiterations    = 75, 
#                           negativethreshold = 0.0)#, 
#                           #sdmasklev=0.3)   # need to overthink here                            


########### SDint specific parameters:

sdint_tclean_param = dict(sdpsf   = '',
                         #sdgain  = 5,     # own factor! see below!
                         dishdia = 12.0)
          
          
          
########### SD factors for all methods:                       
                       
# feather parameters:
sdfac = [1.0]

# Faridani parameters:
SSCfac = [1.0]

# Hybrid feather paramteters:
sdfac_h = [1.0]

# SDINT parameters:
sdg = [1.0]

## TP2VIS parameters:
#TPfac = [1.0]        #M100
TPfac = [1000000.]     #sky-c

          
          
          
######## collect only the product name?          
dryrun = False    # False to execute combination, True to gather filenames only
          
          
          
          
          
############### USER INPUT - end ##################          
#### no user interaction needed from here-on ######  
          
                  
# -------------------------------------------------------------------#

          
          
                       
######## automatic setup of parameters and file existance checks ######                         
                         
                         
### naming scheme specific inputs:
if mode == 'mfs':
    specsetup =  'INTpar'  # no other mode possible 

if inter == 'IA':
    general_tclean_param['interactive'] = True    
elif inter == 'nIA':
    general_tclean_param['interactive'] = False   
 
if mscale == 'HB':
    general_tclean_param['multiscale'] = False
if mscale == 'MS':
    general_tclean_param['multiscale'] = True      # automated scale choice dependant on maxscale




############## naming convention ############
#
#    imname = imbase + cleansetup + combisetup 

cleansetup_nonit = '.'+ mode +'_'+ specsetup +'_'+ mscale +'_'+ masking +'_'+ inter
cleansetup = cleansetup_nonit +'_n'+ str(nit)

#cleansetup = '.'+ mscale +'_'+ masking + '_n%.1e' %(nit)
#cleansetup = cleansetup.replace("+0","")


### output of combination methods ('combisetup')

tcleansetup  = '.tclean'
feathersetup = '.feather_f' #+ str(sdfac)
SSCsetup     = '.SSC_f'     #+ str(SSCfac)
hybridsetup  = '.hybrid_f'  #+ str(sdfac_h)
sdintsetup   = '.sdint_g'   #+ str(sdg)
TP2VISsetup  = '.TP2VIS_t'  #+ str(TPfac)






##### intermediate products name for step 1 = gather information - no need to change!

# SD image: axis-reordering and regridding
sdreordered = sdbase +'.SD_ro.image'                 # SD image axis-reordering

if startchan!=None and endchan!=None and specsetup == 'SDpar':
    sdbase = sdbase + '_ch'+str(startchan)+'-'+str(endchan)

sdreordered_cut = sdbase +'.SD_ro.image'                 # SD image axis-reordering
#print('sdreordered_cut', sdreordered_cut)
sdroregrid = sdbase +'.SD_ro-rg_'+specsetup+'.image' # SD image regridding


imnamethSD  = imbase + cleansetup_nonit +'_template'      # dirty image for thershold and mask generation
threshmask = imbase + '.'+specsetup+ '_RMS'         # thresold mask name
SDint_mask_root = sdbase + '.'+specsetup+ '_SD-AM'  # SD+AM mask name
combined_mask = SDint_mask_root + '-RMS.mask'       # SD+AM+threshold mask name





if masking == 'PB':
    general_tclean_param['usemask']     = 'pb'
if masking == 'AM':
    general_tclean_param['usemask']     = 'auto-multithresh'                   
if masking == 'UM':
    general_tclean_param['usemask']     = 'user'
if masking == 'SD-AM': 
    if not os.path.exists(combined_mask) or not os.path.exists(threshmask+'.mask'):
        if 1 in thesteps:
            pass
        else:    
            thesteps.append(1)      
            thesteps.sort()           # force execution of SDint mask creation (Step 1)
            print('Need to execute step 1 to generate an image mask')
    general_tclean_param['usemask']     = 'user'   
    #general_tclean_param['mask']        = imbase + 'SD-AM.mask' 


# masks per combination method
tclean_mask = threshmask+'.mask'    # 
hybrid_mask = combined_mask         # 
sdint_mask  = combined_mask         # 
TP2VIS_mask = combined_mask         # 



if specsetup == 'SDpar':
    if not os.path.exists(sdreordered_cut):
        if 1 in thesteps:
            pass
        else:    
            thesteps.append(1)      
            thesteps.sort()           # force execution of SDint mask creation (Step 1)
            print('Need to execute step 1 to reorder image axes of the SD image')
    elif os.path.exists(sdreordered_cut):
        # read SD image frequency setup as input for tclean    
        cube_dict = dc.get_SD_cube_params(sdcube = sdreordered_cut) #out: {'nchan':nchan, 'start':start, 'width':width}
        general_tclean_param['start'] = cube_dict['start']  
        general_tclean_param['width'] = cube_dict['width']
        general_tclean_param['nchan'] = cube_dict['nchan']
        sdimage = sdreordered_cut  # for SD cube params used
elif specsetup == 'INTpar':
    if not os.path.exists(sdroregrid):
        if 1 in thesteps:
            pass
        else:    
            thesteps.append(1)      
            thesteps.sort()           # force execution of SDint mask creation (Step 1)
            print('Need to execute step 1 to regrid SD image')
    elif os.path.exists(sdroregrid):
        sdimage = sdroregrid  # for INT cube params used



# common tclean parameters needed for generating a simple dirty image in step 1

mask_tclean_param = dict(phasecenter=general_tclean_param['phasecenter'],
                         spw=        general_tclean_param['spw'], 
                         field=      general_tclean_param['field'], 
                         imsize=     general_tclean_param['imsize'], 
                         cell=       general_tclean_param['cell'],
                         specmode=general_tclean_param['specmode'],
                         start = general_tclean_param['start'],
                         width = general_tclean_param['width'],
                         nchan = general_tclean_param['nchan'],
                         restfreq = general_tclean_param['restfreq']
                         )


if general_tclean_param['threshold'] == '':
    if not os.path.exists(threshmask + '.mask') or not os.path.exists(imnamethSD + '.image'):
        if 1 in thesteps:
            pass
        else:    
            thesteps.append(1)      
            thesteps.sort()           # force execution of SDint mask creation (Step 1)
            print('Need to execute step 1 to estimate a thresold')
    else:
        thresh = dc.derive_threshold(vis, imnamethSD , threshmask,
                                     overwrite=False,   # False for read-only
                                     smoothing = smoothing,
                                     RMSfactor = RMSfactor,
                                     cube_rms   = cube_rms,    
                                     cont_chans = cont_chans,
                                     **mask_tclean_param
        )

        general_tclean_param['threshold']  = str(thresh)+'Jy'   
        

if not os.path.exists(vis):
    if 0 in thesteps:
        pass
    else:    
        thesteps.append(0)      
        thesteps.sort()           # force execution of SDint mask creation (Step 1)
        print('Need to execute step 0 to generate a concatenated ms')









####### collect file names for assessment ######

tcleanims  = []
featherims = []
SSCims     = []
hybridims  = []
sdintims   = []
TP2VISims  = []





# methods for combining agg. bandwidth image with TP image - cube not yet tested/provided



    
mystep = 0    ###################----- CONCAT -----####################
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')    
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')
    
    os.system('rm -rf '+concatms)

    concat(vis = thevis, concatvis = concatms, visweightscale = weightscale)
           


mystep = 1    ############# ----- PREPARE SD-IMAGE and MASKS-----###############
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')    
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')
  
  
    # axis reordering
    dc.reorder_axes(sdimage_input, sdreordered)

    # make a a channel-cut-out from the SD image?
    if sdreordered!=sdreordered_cut:
        dc.channel_cutout(sdreordered, sdreordered_cut, startchan = startchan,
                          endchan = endchan)

    # read SD image frequency setup as input for tclean    
    if specsetup == 'SDpar':
        cube_dict = dc.get_SD_cube_params(sdcube = sdreordered_cut) #out: {'nchan':nchan, 'start':start, 'width':width}
        general_tclean_param['start'] = cube_dict['start']  
        general_tclean_param['width'] = cube_dict['width']
        general_tclean_param['nchan'] = cube_dict['nchan']
        sdimage = sdreordered_cut  # for SD cube params used   



    # derive a simple threshold and make a mask from it 
    thresh = dc.derive_threshold(vis, imnamethSD , threshmask,
                                 overwrite=True,
                                 smoothing = smoothing,
                                 RMSfactor = RMSfactor,
                                 cube_rms   = cube_rms,    
                                 cont_chans = cont_chans, 
                                 **mask_tclean_param
    ) 
                     
    general_tclean_param['threshold']  = str(thresh)+'Jy'   
                     
    
    # regrid SD image frequency axis to tclean (requires derive_threshold to be run)    
    if specsetup == 'SDpar':
        sdimage = sdreordered_cut  # for SD cube params used
    else:
        print('')
        print('Regridding SD image...')
        os.system('rm -rf '+sdroregrid)
        dc.regrid_SD(sdreordered_cut, sdroregrid, imnamethSD+'.image')
        sdimage = sdroregrid  # for INT cube params used

    
       
    # make SD+AM mask (requires regridding to be run; currently)
    SDint_mask = dc.make_SDint_mask(vis, sdimage, imnamethSD, 
                                    sdmasklev, 
                                    SDint_mask_root,
                                    **mask_tclean_param
    ) 
    
    immath(imagename=[SDint_mask_root+'.mask', threshmask+'.mask'],
           expr='iif((IM0+IM1)>'+str(0)+',1,0)',
           outfile=combined_mask)    


           

mystep = 2    ############----- CLEAN FOR FEATHER/SSC -----############
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')
    

    imname = imbase + cleansetup + tcleansetup
    
    
    if masking == 'SD-AM': 
        general_tclean_param['mask']  = tclean_mask


    ### for CASA 5.7:
    z = general_tclean_param.copy()   


    if dryrun == True:
        pass
    else:
        os.system('rm -rf '+imname+'*')
        dc.runtclean(vis, imname, startmodel='', 
                     **z)
        #**general_tclean_param, **special_tclean_param)   # in CASA 6.x

    tcleanims.append(imname)



mystep = 3    ###################----- FEATHER -----###################
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')

    intimage = imbase + cleansetup + '.tclean.image'
    intpb    = imbase + cleansetup + '.tclean.pb'

    for i in range(0,len(sdfac)):
        
        imname = imbase + cleansetup + feathersetup + str(sdfac[i]) 
        
             
        if dryrun == True:
            pass
        else:
            dc.runfeather(intimage, intpb, sdimage, sdfactor = sdfac[i],
                          featherim = imname)

        featherims.append(imname)




mystep = 4    ################----- FARIDANI SSC -----#################
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')

    for i in range(0,len(SSCfac)):
        imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
        
        if dryrun == True:
            pass
        else:
            os.system('rm -rf '+imname+'*')

            dc.ssc(highres=imbase+cleansetup+tcleansetup+'.image', 
                   lowres=sdimage, pb=imbase+cleansetup+tcleansetup+'.pb',
                   sdfactor = SSCfac[i], combined=imname) 
                   
        SSCims.append(imname)





mystep = 5    ###################----- HYBRID -----####################
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')


    if masking == 'SD-AM': 
        general_tclean_param['mask']  = hybrid_mask


    ### for CASA 5.7:
    z = general_tclean_param.copy()   


    for i in range(0,len(sdfac_h)):
        imname = imbase + cleansetup + hybridsetup #+ str(sdfac_h[i]) 

        
        if dryrun == True:
            pass
        else:
            os.system('rm -rf '+imname+'.*')
            #os.system('rm -rf '+imname.replace('_f'+str(sdfac_h[i]),'')+'.*') 
            # delete tclean files ending on 'hybrid.*'  (dot '.' is important!)

            
            dc.runWSM(vis, sdimage, imname, sdfactorh = sdfac_h[i],
                      **z)
           
        hybridims.append(imname)


mystep = 6    ####################----- SDINT -----####################
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')
    
    
    
    if masking == 'SD-AM': 
        general_tclean_param['mask']  = sdint_mask




    ### for CASA 5.7:
    z = general_tclean_param.copy()   
    z.update(sdint_tclean_param)


    
    for i in range(0,len(sdg)) :
        jointname = imbase + cleansetup + sdintsetup + str(sdg[i]) 
        
        if dryrun == True:
            pass
        else:
            os.system('rm -rf '+jointname+'*')
            
            dc.runsdintimg(vis, sdimage, jointname, sdgain = sdg[0],
                           **z)

        sdintims.append(jointname)                
                
                
mystep = 7    ###################----- TP2VIS -----####################
if mystep in thesteps:
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')


    # inputs: concatms, sdreordered, a12m[0]
    # get 12m pointings to simulate TP observation as interferometric


    
    # if a12m[0] exists:        

    
    if a12m!=[]:    # if 12m-data exists ...
        dc.ms_ptg(TPpointingTemplate, outfile=TPpointinglist, uniq=True)
    else:
        TPpointinglist = TPpointinglistAlternative    
    

    imTP = sdreordered
    TPresult= sdreordered.replace('.image','.ms')
    imname1 = imbase + cleansetup + TP2VISsetup  # first plot
      
      
    # works!  
    #
    #    dc.create_TP2VIS_ms(imTP=imTP, TPresult=TPresult,
    #        TPpointinglist=TPpointinglist, mode='mfs',  
    #        vis=vis, imname=imname1, TPnoiseRegion=TPnoiseRegion)  # in CASA 6.x
          

    


    if masking == 'SD-AM': 
        general_tclean_param['mask']  = TP2VIS_mask



    # tclean segmentation fault -
    # maybe due to different numbers of spw in INT and SD ms-files
    # we can expect TP.ms to have only one spw
    # put relevant INT data range (i.e SD range) on one spw

    transvis = vis+'_LSRK' #'_1spw'

    # works!
    #    dc.transform_INT_to_SD_freq_spec(TPresult, imTP, vis, 
    #        transvis, datacolumn='DATA', outframe='LSRK')  # in CASA 6.x


    ### for CASA 5.7:
    z = general_tclean_param.copy()   
    #z.update(sdint_tclean_param)
    #z.update(special_tclean_param)
    
    for i in range(0,len(TPfac)) :
        imname = imbase + cleansetup + TP2VISsetup + str(TPfac[i]) + '_CD'
        
        vis=transvis #!
        
        if dryrun == True:
            pass
        else:
            dc.runtclean_TP2VIS_INT(TPresult, TPfac[i], vis, imname,
                                    RMSfactor=RMSfactor, cube_rms=cube_rms, cont_chans = cont_chans, **z)   # in CASA 6.x
        
        TP2VISims.append(imname)
    


# delete tclean TempLattices

os.system('rm -rf '+pathtoimage + 'TempLattice*')











### SDINT OUTPUTS

## MTMFS

#   *.int.cube.model/
#   *.int.cube.pb/
#   *.int.cube.psf/
#   *.int.cube.residual/
#   *.int.cube.sumwt/
#   *.int.cube.weight/
#   *.joint.cube.psf/
#   *.joint.cube.residual/
#   *.joint.multiterm.image.tt0/
#   *.joint.multiterm.image.tt0.pbcor/
#   *.joint.multiterm.image.tt0.pbcor.fits
#   *.joint.multiterm.mask/
#   *.joint.multiterm.model.tt0/
#   *.joint.multiterm.pb.tt0/
#   *.joint.multiterm.psf.tt0/
#   *.joint.multiterm.residual.tt0/
#   *.joint.multiterm.sumwt.tt0/
#   *.joint.multiterm.weight.tt0/
#   *.sd.cube.image/
#   *.sd.cube.psf/
#   *.sd.cube.residual/




