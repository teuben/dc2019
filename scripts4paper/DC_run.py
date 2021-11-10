# do not modify the parameters in this script, instead use DC_pars.py
# See DC_script.py for an example how to use this script

# After DC_pars.py defines the parameters this script works in two steps:
#   - set up the filenames for a convention we use in the DC project
#   - provide a number of snippets of code (currently 8) that can all
#     or individually be selected to run. It uses routines from
#     datacomb.py and standard CASA6 routines.


step_title = {0: 'Concat (optional)',
              1: 'Prepare the SD-image',
              2: 'Clean for Feather/Faridani',
              3: 'Feather', 
              4: 'Faridani short spacings combination (SSC)',
              5: 'Hybrid (startmodel clean + Feather)',
              6: 'SDINT',
              7: 'TP2VIS',
              8: 'Assessment'
              }

# thesteps need to be set in DC_pars.py
# thesteps=[0,1,2,3,4,5,6,7]

import os 
import sys 
from importlib import reload  
import datacomb as dc
#   we do a reload here, because we often edit this in the same casa session
reload(dc)

import IQA_script as iqa
reload(iqa)

import casatasks as cta

import time
start = time.time()

### switch this off, if you run multiple casa instances/DC_runs in the same work folder !
#          
#  ### delete garbage from aboprted script ###
#  os.system('rm -rf '+pathtoimage + 'TempLattice*')
#  
####### else switch on #######


### naming scheme specific inputs:
if mode == 'mfs':
    specsetup =  'INTpar'  # no other mode possible 

if inter == 'IA':
    general_tclean_param['interactive'] = 1     # use 1 instead of True to get tclean feedback dictionary !
elif inter == 'nIA':
    general_tclean_param['interactive'] = 0     # use 0 instead of False to get tclean feedback dictionary !  
 
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
#print(sdroregrid)

imnamethSD      = imbase + '.'+mode +'_'+ specsetup +'_template'   # dirty image for thershold and mask generation
threshmask      = imbase + '.'+mode +'_'+ specsetup+ '_RMS'           # thresold mask name
SDint_mask_root = sdbase + '.'+mode +'_'+ specsetup+ '_SD-AM'         # SD+AM mask name
combined_mask   = SDint_mask_root + '-RMS.mask'            # SD+AM+threshold mask name





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
    general_tclean_param['usemask']     = 'auto-multithresh'   
    general_tclean_param['loadmask']    = True   
    
    #general_tclean_param['mask']        = imbase + 'SD-AM.mask' 


# masks per combination method
tclean_mask = threshmask+'.mask'    # 

#hybrid_mask = combined_mask         # 
#sdint_mask  = combined_mask         # 
#TP2VIS_mask = combined_mask         # 

hybrid_mask = threshmask+'.mask'    #
sdint_mask  = threshmask+'.mask'    #
TP2VIS_mask = threshmask+'.mask'    #



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
    if dryrun==True:
        pass 
    elif 0 in thesteps:
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


# step numbers for filename suffix 
thesteps2 = map(str, thesteps)    
stepsjoin=''.join(thesteps2)
steps=stepsjoin.replace('0','').replace('1','').replace('8','')
steplist='_s'+steps       # for assessment (step 8)
steplist2='_s'+stepsjoin  # for runtime measurement 









# methods for combining agg. bandwidth image with TP image - cube not yet tested/provided



    
mystep = 0    ###################----- CONCAT -----####################
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
    print(' ')    
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('  vis:')
    print(*thevis, sep = "\n")
    print('  concatvis:')
    print(concatms)
    print('### ')
    print(' ')


    if dryrun == True:
        pass
    else:   
        if thevis ==[]:
            pass
        else:   
            for i in range(0,len(thevis)):
                dc.check_CASAcal(thevis[i])    
            
            print(' ')         
            print('Starting CONCAT')         

            os.system('rm -rf '+concatms)
            
            cta.concat(vis = thevis, concatvis = concatms, visweightscale = weightscale)
            print('--- Done! ---')         


mystep = 1    ############# ----- PREPARE SD-IMAGE and MASKS-----###############
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
    print(' ')    
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')

    if dryrun == True:
        pass
    else:    

        # axis reordering       
        print(' ')         
        print('Reorder SD image axes')                          
        dc.reorder_axes(sdimage_input, sdreordered)
        print('--- Axis reorder done! --- ')         
        
        # make a channel-cut-out from the SD image?
        if sdreordered!=sdreordered_cut:
            print(' ')         
            print('Make a channel-cut-out from the SD image from channel', startchan, 'to', endchan)  
            dc.channel_cutout(sdreordered, sdreordered_cut, startchan = startchan,
                              endchan = endchan)
            print('--- Channel-cut-out done! --- ')         

        
        # read SD image frequency setup as input for tclean    
        if specsetup == 'SDpar':
            print(' ')         
            print('Read SD image frequency setup as input for tclean')              
            cube_dict = dc.get_SD_cube_params(sdcube = sdreordered_cut) #out: {'nchan':nchan, 'start':start, 'width':width}
            general_tclean_param['start'] = cube_dict['start']  
            general_tclean_param['width'] = cube_dict['width']
            general_tclean_param['nchan'] = cube_dict['nchan']
            sdimage = sdreordered_cut  # for SD cube params used   
            print('--- Tclean frequency setup done! --- ')         

        
        
        # derive a simple threshold and make a mask from it 
        print(' ')         
        print('Derive a simple threshold from concatms dirty image and make a mask from it')                                  
        thresh = dc.derive_threshold(vis, imnamethSD , threshmask,
                                     overwrite=True,
                                     smoothing = smoothing,
                                     RMSfactor = RMSfactor,
                                     cube_rms   = cube_rms,    
                                     cont_chans = cont_chans, 
                                     **mask_tclean_param) 
                                     
        if general_tclean_param['threshold'] == '':
            general_tclean_param['threshold']  = str(thresh)+'Jy'   
            print('Set the tclean-threshold to ', general_tclean_param['threshold'])
        print('--- Threshold and mask done! --- ')         
                                     
                         

                         
        
        # regrid SD image frequency axis to tclean (requires derive_threshold to be run)    
        if specsetup == 'SDpar':
            sdimage = sdreordered_cut  # for SD cube params used
        else:
            print('')
            print('Regrid SD image')
            os.system('rm -rf '+sdroregrid)
            dc.regrid_SD(sdreordered_cut, sdroregrid, imnamethSD+'.image')
            sdimage = sdroregrid  # for INT cube params used
            print('--- Regridding done! --- ')     
            # just for testing - if it fails then the common beam in regridSD didn't work 
            hdr = imhead(sdimage,mode='summary')
            beam_major = hdr['restoringbeam']['major']    
        
           
        # make SD+AM mask (requires regridding to be run; currently)
        print(' ')         
        print('Make single dish (SD) + automasking (AM) mask')                                          
        SDint_mask = dc.make_SDint_mask(vis, sdimage, imnamethSD, 
                                        sdmasklev, 
                                        SDint_mask_root,
                                        **mask_tclean_param) 
        print('--- SD+AM mask done! --- ')         


        cta.immath(imagename=[SDint_mask_root+'.mask', threshmask+'.mask'],
                   expr='iif((IM0+IM1)>'+str(0)+',1,0)',
                   outfile=combined_mask)    
                   
                   # ! terminal complains about bunit issues !
        print('Combined SD+AM and threshold mask')                                          

           

mystep = 2    ############----- CLEAN FOR FEATHER/SSC -----############
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
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
        #os.system('rm -rf '+imname+'*')
        dc.runtclean(vis, imname, startmodel='', 
                     **z)
        #**general_tclean_param, **special_tclean_param)   # in CASA 6.x
        #if masking == 'SD-AM':
        #    z['continueclean'] = True 
        #    z['usemask'] = 'auto-multithresh' 
        #    dc.runtclean(vis, imname, startmodel='', 
        #             **z)

    tcleanims.append(imname+'.image')



mystep = 3    ###################----- FEATHER -----###################
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')

    #intimage = imbase + cleansetup + '.tclean.image'
    #intpb    = imbase + cleansetup + '.tclean.pb'

    intimage = imbase + cleansetup + tcleansetup + '.image'
    intpb    = imbase + cleansetup + tcleansetup + '.pb'
    
    for i in range(0,len(sdfac)):
        
        imname = imbase + cleansetup + feathersetup + str(sdfac[i]) 
        
             
        if dryrun == True:
            pass
        else:
            dc.runfeather(intimage, intpb, sdimage, sdfactor = sdfac[i],
                          featherim = imname)

        featherims.append(imname+'.image')




mystep = 4    ################----- FARIDANI SSC -----#################
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')

    intimage = imbase + cleansetup + tcleansetup + '.image'
    intpb    = imbase + cleansetup + tcleansetup + '.pb'

    for i in range(0,len(SSCfac)):
        imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
        
        if dryrun == True:
            pass
        else:
            os.system('rm -rf '+imname+'*')

            dc.ssc(highres=intimage, lowres=sdimage, pb=intpb,
                   sdfactor = SSCfac[i], combined=imname) 
                   
        SSCims.append(imname+'.image')





mystep = 5    ###################----- HYBRID -----####################
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
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
            #os.system('rm -rf '+imname+'.*')
            #os.system('rm -rf '+imname.replace('_f'+str(sdfac_h[i]),'')+'.*') 
            # delete tclean files ending on 'hybrid.*'  (dot '.' is important!)

            
            dc.runWSM(vis, sdimage, imname, sdfactorh = sdfac_h[i],
                      **z)
            #if masking == 'SD-AM':
            #    z['continueclean'] = True 
            #    z['usemask'] = 'auto-multithresh' 
            #    dc.runWSM(vis, sdimage, imname, sdfactorh = sdfac_h[i], doautomask = True
            #          **z)
                                
        hybridims.append(imname+str(sdfac_h[i])+'.image')


mystep = 6    ####################----- SDINT -----####################
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
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
            #os.system('rm -rf '+jointname+'*')
            
            dc.runsdintimg(vis, sdimage, jointname, sdgain = sdg[0],
                           **z)
            #if masking == 'SD-AM':
            #    z['renameexport'] = False 
            #    dc.runsdintimg(vis, sdimage, jointname, sdgain = sdg[0], 
            #               **z)
            #    z['renameexport'] = True  
            #    z['continueclean'] = True 
            #    z['usemask'] = 'auto-multithresh' 
            #    dc.runsdintimg(vis, sdimage, jointname, sdgain = sdg[0],
            #               **z)
            #else:
            #    dc.runsdintimg(vis, sdimage, jointname, sdgain = sdg[0], 
            #               **z)


                      
        sdintims.append(jointname+'.image')                
                
                
mystep = 7    ###################----- TP2VIS -----####################
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')



    # inputs: concatms, sdreordered, a12m[0]
    # get 12m pointings to simulate TP observation as interferometric
        
    # if a12m[0] exists:        

    if dryrun == True:
        pass
    else:    
        if a12m!=[]:    # if 12m-data exists ...
            #dc.ms_ptg(TPpointingTemplate, outfile=TPpointinglist, uniq=True)
            dc.listobs_ptg(TPpointingTemplate, listobsOutput, TPpointinglist)
        else:
            TPpointinglist = TPpointinglistAlternative    
    

    imTP = sdreordered
    TPresult= sdreordered.replace('.image','.ms')
    imname1 = imbase + cleansetup + TP2VISsetup  # first plot
      
      
    if dryrun == True:
        pass
    else:    
        dc.create_TP2VIS_ms(imTP=imTP, TPresult=TPresult,
            TPpointinglist=TPpointinglist, mode=mode,  
            vis=vis, imname=imname1, TPnoiseRegion=TPnoiseRegion, 
            TPnoiseChannels=TPnoiseChannels)  # in CASA 6.x

    if masking == 'SD-AM': 
        general_tclean_param['mask']  = TP2VIS_mask



    # tclean segmentation fault -
    # maybe due to different numbers of spw in INT and SD ms-files
    # we can expect TP.ms to have only one spw
    # put relevant INT data range (i.e SD range) on one spw

    transvis = vis+'_LSRK' #'_1spw'


    if dryrun == True:
        pass
    else:
        dc.transform_INT_to_SD_freq_spec(TPresult, imTP, vis, 
            transvis, datacolumn='DATA', outframe='LSRK')  # in CASA 6.x


    ### for CASA 5.7:
    z = general_tclean_param.copy()   
    #z.update(sdint_tclean_param)
    #z.update(special_tclean_param)
    
    for i in range(0,len(TPfac)) :
        imname = imbase + cleansetup + TP2VISsetup + str(TPfac[i]) #+ '_CD'     #don't remember the reason for this "CD" ending
        
        vis=transvis #!
        
        if dryrun == True:
            pass
        else:
            #if masking == 'SD-AM':
            #    dc.runtclean_TP2VIS_INT(TPresult, TPfac[i], vis, imname,
            #                        RMSfactor=RMSfactor, cube_rms=cube_rms, 
            #                        cont_chans = cont_chans, doautomask = True, **z) 
            #else:
            dc.runtclean_TP2VIS_INT(TPresult, TPfac[i], vis, imname,
                                    RMSfactor=RMSfactor, cube_rms=cube_rms, 
                                    cont_chans = cont_chans, **z)   # in CASA 6.x
 
        TP2VISims.append(imname+'.tweak.image')
        


mystep = 8    ###################----- ASSESSMENT -----####################
if mystep in thesteps:
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')



    
    #### imbase         = pathtoimage + 'skymodel-b_120L
    sourcename = imbase.replace(pathtoimage,'')
    # folder to put the assessment images to 
    assessment=pathtoimage + 'assessment_'+sourcename+cleansetup
    os.system('mkdir '+assessment) 


    ########## list residuals, threshold and stopping criteria ############

    tcleanres = []
    hybridres = []
    sdintres  = []
    TP2VISres = []
    
    if (2 in thesteps) or (3 in thesteps) or (4 in thesteps): # and (tcleanres != []): 
        tcleanres = [imbase + cleansetup + tcleansetup + '.image']
    if 5 in thesteps: hybridres = [imbase + cleansetup + hybridsetup + '.image']
    if 6 in thesteps: sdintres  = sdintims                                    
    if 7 in thesteps: TP2VISres = TP2VISims                                   

    allcombires=tcleanres + hybridres + sdintres + TP2VISres

    allcombires = [a.replace('.tweak','') for a in allcombires]
    allcombires = [a.replace('.image','.residual') for a in allcombires]
    allcombimask = [a.replace('.residual','.mask') for a in allcombires]
    allcombitxt = [a.replace('.residual', '') for a in allcombires]
    #print(allcombimask)
    #print(allcombires[0])

    print(' ')
    print(' ')
    print('Showing residual maps and tclean masks, stopping criteria, and thresholds for ')
    print(*allcombires, sep = "\n")
    print(' ')

    stop_crit=[]
    cleanthresh=[]
    cleaniterdone = []

    for i in range(0, len(allcombitxt)):
        os.system('rm -rf ' + allcombires[i] + '.fits')
        os.system('rm -rf ' + allcombimask[i] + '.fits')
        cta.exportfits(imagename=allcombires[i], fitsimage=allcombires[i] + '.fits', dropdeg=True)
        cta.exportfits(imagename=allcombimask[i], fitsimage=allcombimask[i] + '.fits', dropdeg=True)
        tcleanresults = dc.file_to_pydict2(allcombitxt[i])
        dc.pydict_to_file(tcleanresults, allcombitxt[i])       # export to human readable format 
        #print(tcleanresults['threshold'])
        stop_crit.append(tcleanresults['stopcode'])
        cleanthresh.append(tcleanresults['threshold'])
        cleaniterdone.append(tcleanresults['iterdone'])

    #allcombiresfits = [a.replace('.residual','.residual.fits') for a in allcombires]
    #allcombimaskfits = [a.replace('.mask','.mask.fits') for a in allcombimask]

    #labelnames
    allcombireslabel = [a.replace(pathtoimage+sourcename+cleansetup+'.','') for a in allcombitxt]

    mapchan=int(general_tclean_param['nchan']/2.)
    iqa.show_residual_maps(allcombires, allcombimask,
                          channel=mapchan, 
                          save=True, 
                          plotname=assessment+'/Residual_maps_'+sourcename+cleansetup+steplist, 
                          labelname=allcombireslabel,
                          titlename='Residual maps in channel '+str(mapchan)+' from the tclean instances used by the chosen \n  combination methods for '+sourcename+cleansetup,
                          stop_crit=stop_crit,
                          cleanthresh=cleanthresh,
                          cleaniterdone=cleaniterdone)                                    





    
    ########## Assessment with respect to SD image ############
    
    os.system('rm -rf ' + sdroregrid + '.fits')
    cta.exportfits(imagename=sdroregrid, fitsimage=sdroregrid + '.fits', dropdeg=True)
    
    allcombims0 = tcleanims  + featherims + SSCims     + hybridims  + sdintims  + TP2VISims
    #print(allcombims)
    print(' ')
    print(' ')
    print('Running assessment with respect to SD image on ')
    print(*allcombims0, sep = "\n")
    print(' ')
    
    
    allcombims = [a.replace('.image','.image.pbcor') for a in allcombims0]
    allcombimsfits = [a.replace('.image.pbcor','.image.pbcor.fits') for a in allcombims]
    
    # make comparison plots
    
    #labelnames
    allcombi = [a.replace(pathtoimage+sourcename+cleansetup+'.','').replace('.image.pbcor','') for a in allcombims]
    
    # make Apar and fidelity images
    
    iqa.get_IQA(ref_image = sdroregrid, target_image=allcombims)
    
    
    
     
    
    
    if mode=='cube':   
        iqa.Compare_Apar_cubes(ref_image = sdroregrid, 
                               target_image=allcombims,
                               save=True,
                               plotname=assessment+'/SD_Apar_channels_'+sourcename+cleansetup+steplist,
                               labelname=allcombi, 
                               titlename='Accuracy Parameter of cube: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.','')
                               )
        iqa.Compare_Fidelity_cubes(ref_image = sdroregrid, 
                               target_image=allcombims,
                               save=True,
                               plotname=assessment+'/SD_Fidelity_channels_'+sourcename+cleansetup+steplist,
                               labelname=allcombi, 
                               titlename='Fidelity of cube: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.','')
                               )      
            
        for i in range(0,len(allcombims)):
            os.system('rm -rf ' + allcombims[i]+'.mom0')
            cta.immoments(imagename=allcombims[i],
                       moments=[0],                                           
                       chans=momchans,                                         
                       outfile=allcombims[i]+'.mom0')
            os.system('rm -rf ' + allcombims[i]+'.mom0.fits')
            cta.exportfits(imagename=allcombims[i]+'.mom0', fitsimage=allcombims[i]+'.mom0.fits', dropdeg=True)
            mapchan=general_tclean_param['nchan']/2.
            iqa.show_Apar_map(    sdroregrid,allcombims[i],
                                  channel=mapchan, 
                                  save=True, 
                                  plotname=assessment+'/SD_Accuracy_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor','')+'_channel', #expecting only one file name entry per combi-method
                                  labelname=allcombi[i],
                                  titlename='Accuracy map in channel '+str(mapchan)+' for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
           
            iqa.show_Fidelity_map(sdroregrid,
                                  allcombims[i],
                                  channel=mapchan, 
                                  save=True, 
                                  plotname=assessment+'/SD_Fidelity_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor','')+'_channel', #expecting only one file name entry per combi-method
                                  labelname=allcombi[i],
                                  titlename='Fidelity map in channel '+str(mapchan)+' for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
       
        os.system('rm -rf ' + sdroregrid+'.mom0')               
        cta.immoments(imagename=sdroregrid,
                   moments=[0],                                           
                   chans=momchans,                                         
                   outfile=sdroregrid+'.mom0')
        
       
        
        
        # use mom0-maps as input for the cont-defined Apar/fidelity functions
        allcombims = [a.replace('.image.pbcor', '.image.pbcor.mom0') for a in allcombims]
        allcombimsfits = [a.replace('.image.pbcor.mom0','.image.pbcor.mom0.fits') for a in allcombims]
    
        sdroregrid = sdroregrid+'.mom0'
        os.system('rm -rf ' + sdroregrid + '.fits')
        cta.exportfits(imagename=sdroregrid, fitsimage=sdroregrid + '.fits', dropdeg=True)
    
        iqa.get_IQA(ref_image = sdroregrid, target_image=allcombims)
     
    
    
    
      
              
    
    
    # all Apar and fidelity plots
    iqa.Compare_Apar(ref_image = sdroregrid, 
                     target_image=allcombims, 
                     save=True, 
                     plotname=assessment+'/SD_AparALL_'+sourcename+cleansetup+steplist,
                     labelname=allcombi, 
                     titlename='Accuracy Parameter: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))
    iqa.Compare_Fidelity(ref_image = sdroregrid, 
                     target_image=allcombims,
                     save=True, 
                     plotname=assessment+'/SD_FidelityALL_'+sourcename+cleansetup+steplist,
                     labelname=allcombi, 
                     titlename='Fidelity: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
    for i in range(0,len(allcombims)):
        # Apar and fidelity vs signal plots
        iqa.Compare_Apar_signal(ref_image = sdroregrid, 
                                 target_image=[allcombims[i]],
                                 save=True,
                                 noise=0.0, 
                                 plotname=assessment+'/SD_Apar_signal_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                                 labelname=[allcombi[i]],
                                 titlename='Accuracy vs. Signal for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
        iqa.Compare_Fidelity_signal(ref_image = sdroregrid, 
                                 target_image=[allcombims[i]],
                                 save=True,
                                 noise=0.0, 
                                 plotname=assessment+'/SD_Fidelity_signal_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                                 labelname=[allcombi[i]],
                                 titlename='Fidelity vs. Signal for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                                    
        # Apar and fidelity image plots
        iqa.show_Apar_map(    sdroregrid,allcombims[i],
                              channel=0, 
                              save=True, 
                              plotname=assessment+'/SD_Accuracy_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                              labelname=allcombi[i],
                              titlename='Accuracy map for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
    
        iqa.show_Fidelity_map(sdroregrid,
                              allcombims[i],
                              channel=0, 
                              save=True, 
                              plotname=assessment+'/SD_Fidelity_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                              labelname=allcombi[i],
                              titlename='Fidelity map for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
  
    
    
    allcombimsfits.append(sdroregrid + '.fits')
    allcombi.append('single dish')
         
    iqa.genmultisps(allcombimsfits, save=True, 
                   plotname=assessment+'/SD_Power_spectra_'+sourcename+cleansetup+steplist,
                   labelname=allcombi,
                   titlename='Power spectra for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
    
    
    
    allcombimsfits_conv = [a.replace('pbcor.fits','pbcor_convo2ref.fits') for a in allcombimsfits]
    allcombimsfits_conv = [a.replace('pbcor.mom0.fits','pbcor.mom0_convo2ref.fits') for a in allcombimsfits]
         
    iqa.genmultisps(allcombimsfits_conv, save=True, 
                   plotname=assessment+'/SD_Power_spectra_convo2ref_'+sourcename+cleansetup+steplist,
                   labelname=allcombi,
                   titlename='Power spectra (convolved to SD) for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         

    allcombimsfits_conv_Apar = [a.replace('_convo2ref.fits','_convo2ref_Apar.fits') for a in allcombimsfits_conv]

    iqa.genmultisps(allcombimsfits_conv_Apar, save=True, 
                   plotname=assessment+'/SD_Power_spectra_convo2ref_Apar_'+sourcename+cleansetup+steplist,
                   labelname=allcombi,
                   titlename='Apar power spectra (convolved to SD) for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
    
    
    
    #################### NOT YET WORKING !!! problems #######
    #
    #iqa.get_aperture(allcombimsfits,position=(1,1),Nbeams=10)
    #
    ##### !!!needs SD-fitsfile ----> to create in step 1 !!!!
    
    
    
    
    
    
    if skymodel!='':
    
        ########## Assessment with respect to SKYMODEL image ############
        
        #os.system('rm -rf ' + sdroregrid + '.fits')
        #cta.exportfits(imagename=sdroregrid, fitsimage=sdroregrid + '.fits', dropdeg=True)
        
        if mode=='cube':   
            allcombims0 = tcleanims  + featherims + SSCims     + hybridims  + sdintims  + TP2VISims   # need to fix TP2VIS for cont images without emission-free region first 
        else:
			print('Skip TP2VIS results in this selection - most likely no good result in mfs-mode')
            allcombims0 = tcleanims  + featherims + SSCims     + hybridims  + sdintims  #+ TP2VISims   # need to fix TP2VIS for cont images without emission-free region first 
        #print(allcombims)
        print(' ')
        print(' ')
        print('Running assessment with respect to the SKYMODEL on ')
        print(*allcombims0, sep = "\n")
        print(' ')
    
        
        allcombims = [a.replace('.image','.image.pbcor') for a in allcombims0]
        allcombimsfits = [a.replace('.image.pbcor','.image.pbcor.fits') for a in allcombims]
        
        
        
        # make comparison plots
        
        #### imbase         = pathtoimage + 'skymodel-b_120L
        #sourcename = imbase.replace(pathtoimage,'')
        # folder to put the assessment images to 
        #assessment=pathtoimage + 'assessment_'+sourcename+cleansetup
        #os.system('mkdir '+assessment) 
        
        
        #labelnames
        allcombi = [a.replace(pathtoimage+sourcename+cleansetup+'.','').replace('.image.pbcor','') for a in allcombims]
        
        
        ## step numbers 
        #thesteps2 = map(str, thesteps)    
        #stepsjoin=''.join(thesteps2)
        #steps=stepsjoin.replace('0','').replace('1','').replace('8','')
        #steplist='_s'+steps
        
        
        # get largest beam axes present in the input images and smooth model image to them
        
        BeamMaj=[]
        BeamMin=[]
        BeamPA =[]
        
        # expects common beam and not perplanebeam @cube!
         
        for j in range(0,len(allcombims)): 
            BeamMaj.append(cta.imhead(allcombims[j], mode='get', hdkey='bmaj')['value'])
            BeamMin.append(cta.imhead(allcombims[j], mode='get', hdkey='bmin')['value'])
            BeamPA.append(cta.imhead(allcombims[j], mode='get', hdkey='bpa' )['value'])
    
        print(BeamMaj)
        print(BeamMin) 
        print(BeamPA )
        
        skymodelreg=imbase +'.skymodel.regrid'
        os.system('rm -rf '+skymodelreg)
        dc.regrid_SD(skymodel, skymodelreg, allcombims[0])
            
        skymodelconv=imbase +'.skymodel.regrid.conv'
        os.system('rm -rf '+skymodelconv+'*')
        
        import numpy as np  
            
        cta.imsmooth(imagename = skymodelreg,
                     kernel    = 'gauss',               
                     targetres = False,                                                             
                     major     = str(max(np.array(BeamMaj))*1.1)+'arcsec', 
                     minor     = str(max(np.array(BeamMin))*1.1)+'arcsec',    
                     pa        = str(np.mean(np.array(BeamPA)))+'deg',                                       
                     outfile   = skymodelconv,            
                     overwrite = True)    
        # have to add 10% in size (factor 1.1), else imsmooth in get_IQA might fail for largest beam size in image set                                              
        
        
        
        os.system('rm -rf ' + skymodelconv + '.fits')
        cta.exportfits(imagename=skymodelconv, fitsimage=skymodelconv + '.fits', dropdeg=True)
                
        
        # make Apar and fidelity images
        
        iqa.get_IQA(ref_image = skymodelconv, target_image=allcombims)
        
        
        
         
        
        
        if mode=='cube':   
            iqa.Compare_Apar_cubes(ref_image = skymodelconv, 
                                   target_image=allcombims,
                                   save=True,
                                   plotname=assessment+'/Model_Apar_channels_'+sourcename+cleansetup+steplist,
                                   labelname=allcombi, 
                                   titlename='Accuracy Parameter of cube: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.','')
                                   )
            iqa.Compare_Fidelity_cubes(ref_image = skymodelconv, 
                                   target_image=allcombims,
                                   save=True,
                                   plotname=assessment+'/Model_Fidelity_channels_'+sourcename+cleansetup+steplist,
                                   labelname=allcombi, 
                                   titlename='Fidelity of cube: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.','')
                                   )      
                
            for i in range(0,len(allcombims)):
                #os.system('rm -rf ' + allcombims[i]+'.mom0')
                #cta.immoments(imagename=allcombims[i],
                #           moments=[0],                                           
                #           chans=momchans,                                         
                #           outfile=allcombims[i]+'.mom0')
                #os.system('rm -rf ' + allcombims[i]+'.mom0.fits')
                #cta.exportfits(imagename=allcombims[i]+'.mom0', fitsimage=allcombims[i]+'.mom0.fits', dropdeg=True)
                mapchan=general_tclean_param['nchan']/2.
                iqa.show_Apar_map(    skymodelconv,allcombims[i],
                                      channel=mapchan, 
                                      save=True, 
                                      plotname=assessment+'/Model_Accuracy_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor','')+'_channel', #expecting only one file name entry per combi-method
                                      labelname=allcombi[i],
                                      titlename='Accuracy map in channel '+str(mapchan)+' for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
               
                iqa.show_Fidelity_map(skymodelconv,
                                      allcombims[i],
                                      channel=mapchan, 
                                      save=True, 
                                      plotname=assessment+'/Model_Fidelity_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor','')+'_channel', #expecting only one file name entry per combi-method
                                      labelname=allcombi[i],
                                      titlename='Fidelity map in channel '+str(mapchan)+' for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
           
            os.system('rm -rf ' + skymodelconv+'.mom0')               
            cta.immoments(imagename=skymodelconv,
                       moments=[0],                                           
                       chans=momchans,                                         
                       outfile=skymodelconv+'.mom0')
            
           
            
            
            # use mom0-maps as input for the cont-defined Apar/fidelity functions
            allcombims = [a.replace('.image.pbcor', '.image.pbcor.mom0') for a in allcombims]
            allcombimsfits = [a.replace('.image.pbcor.mom0','.image.pbcor.mom0.fits') for a in allcombims]
        
            skymodelconv = skymodelconv+'.mom0'
            os.system('rm -rf ' + skymodelconv + '.fits')
            cta.exportfits(imagename=skymodelconv, fitsimage=skymodelconv + '.fits', dropdeg=True)
        
            iqa.get_IQA(ref_image = skymodelconv, target_image=allcombims)
         
        
        
        
          
                  
        
        
        # all Apar and fidelity plots
        iqa.Compare_Apar(ref_image = skymodelconv, 
                         target_image=allcombims, 
                         save=True, 
                         plotname=assessment+'/Model_AparALL_'+sourcename+cleansetup+steplist,
                         labelname=allcombi, 
                         titlename='Accuracy Parameter: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))
        iqa.Compare_Fidelity(ref_image = skymodelconv, 
                         target_image=allcombims,
                         save=True, 
                         plotname=assessment+'/Model_FidelityALL_'+sourcename+cleansetup+steplist,
                         labelname=allcombi, 
                         titlename='Fidelity: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
        for i in range(0,len(allcombims)):
            # Apar and fidelity vs signal plots
            iqa.Compare_Apar_signal(ref_image = skymodelconv, 
                                     target_image=[allcombims[i]],
                                     save=True,
                                     noise=0.0, 
                                     plotname=assessment+'/Model_Apar_signal_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                                     labelname=[allcombi[i]],
                                     titlename='Accuracy vs. Signal for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
            iqa.Compare_Fidelity_signal(ref_image = skymodelconv, 
                                     target_image=[allcombims[i]],
                                     save=True,
                                     noise=0.0, 
                                     plotname=assessment+'/Model_Fidelity_signal_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                                     labelname=[allcombi[i]],
                                     titlename='Fidelity vs. Signal for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                                    
            # Apar and fidelity image plots
            iqa.show_Apar_map(    skymodelconv,
                                  allcombims[i],
                                  channel=0, 
                                  save=True, 
                                  plotname=assessment+'/Model_Accuracy_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                                  labelname=allcombi[i],
                                  titlename='Accuracy map for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
        
            iqa.show_Fidelity_map(skymodelconv,
                                  allcombims[i],
                                  channel=0, 
                                  save=True, 
                                  plotname=assessment+'/Model_Fidelity_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
                                  labelname=allcombi[i],
                                  titlename='Fidelity map for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
        
        
        
        allcombimsfits.append(skymodelconv + '.fits')
        allcombi.append('model')
        
        iqa.genmultisps(allcombimsfits, save=True, 
                       plotname=assessment+'/Model_Power_spectra_'+sourcename+cleansetup+steplist,
                       labelname=allcombi,
                       titlename='Power spectra for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
            
        allcombimsfits_conv = [a.replace('pbcor.fits','pbcor_convo2ref.fits') for a in allcombimsfits]
        allcombimsfits_conv = [a.replace('pbcor.mom0.fits','pbcor.mom0_convo2ref.fits') for a in allcombimsfits]
         

        iqa.genmultisps(allcombimsfits_conv, save=True, 
                       plotname=assessment+'/Model_Power_spectra_convo2ref_'+sourcename+cleansetup+steplist,
                       labelname=allcombi,
                       titlename='Power spectra (convolved to model) for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
        
        allcombimsfits_conv_Apar = [a.replace('_convo2ref.fits','_convo2ref_Apar.fits') for a in allcombimsfits_conv]

        iqa.genmultisps(allcombimsfits_conv_Apar, save=True, 
                       plotname=assessment+'/Model_Power_spectra_convo2ref_Apar_'+sourcename+cleansetup+steplist,
                       labelname=allcombi,
                       titlename='Apar power spectra (convolved to model) for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
        



        #################### NOT YET WORKING !!! problems #######
        #
        #iqa.get_aperture(allcombimsfits,position=(1,1),Nbeams=10)
        #
        ##### !!!needs SD-fitsfile ----> to create in step 1 !!!!
        
        
    
    
    
    
    
    
    




# delete tclean TempLattices

os.system('rm -rf '+pathtoimage + 'TempLattice*')


end = time.time()
diff = round(end - start)


filename0 = imbase + cleansetup +'._Runtime_' + steplist2

if dryrun==False:
    filename = filename0
if dryrun==True:
    filename = filename0+'_assessment'

os.system('rm -rf '+filename+'.txt')
string1 = 'Execution of steps '+str(thesteps)[1:-1]+' of DC_run.py with dryrun='+str(dryrun)+' took:'
string2 = str(diff) + ' seconds = ' + str(round(diff/60.0, 2)) + ' minutes = ' + str(round(diff/60.0/60.0, 2)) + ' hours'
f = open(filename+'.txt','w')
f.write(string1)
f.write('\n'+string2)
f.close()

print('')
print('')
print('---------------------------- WE ARE DONE! -----------------------------')
print('')
print(string1)
print(string2)





### SDINT Traditional OUTPUTS

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



