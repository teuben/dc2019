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
#print(sdroregrid)

imnamethSD      = imbase + cleansetup_nonit +'_template'   # dirty image for thershold and mask generation
threshmask      = imbase + '.'+specsetup+ '_RMS'           # thresold mask name
SDint_mask_root = sdbase + '.'+specsetup+ '_SD-AM'         # SD+AM mask name
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
    cta.casalog.post('### ','INFO')
    cta.casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    cta.casalog.post('### ','INFO')
    print(' ')    
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('  vis:',thevis)
    print('  concatvis:',concatms)
    print('### ')
    print(' ')

    for i in range(0,len(thevis)):
        dc.check_CASAcal(thevis[i])
        #dc.visHistory(thevis[i], origin='applycal', search='version',includeVis=False)


    if dryrun == True:
        pass
    else:    
        if thevis ==[]:
            pass
        else:   
            os.system('rm -rf '+concatms)
            
            concat(vis = thevis, concatvis = concatms, visweightscale = weightscale)
           


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
                                     **mask_tclean_param) 
                         
        general_tclean_param['threshold']  = str(thresh)+'Jy'   
        print('Set the tclean-threshold to ', general_tclean_param['threshold'])

                         
        
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
                                        **mask_tclean_param) 
        
        cta.immath(imagename=[SDint_mask_root+'.mask', threshmask+'.mask'],
                   expr='iif((IM0+IM1)>'+str(0)+',1,0)',
                   outfile=combined_mask)    


           

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
        os.system('rm -rf '+imname+'*')
        dc.runtclean(vis, imname, startmodel='', 
                     **z)
        #**general_tclean_param, **special_tclean_param)   # in CASA 6.x

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
            os.system('rm -rf '+imname+'.*')
            #os.system('rm -rf '+imname.replace('_f'+str(sdfac_h[i]),'')+'.*') 
            # delete tclean files ending on 'hybrid.*'  (dot '.' is important!)

            
            dc.runWSM(vis, sdimage, imname, sdfactorh = sdfac_h[i],
                      **z)
           
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
            os.system('rm -rf '+jointname+'*')
            
            dc.runsdintimg(vis, sdimage, jointname, sdgain = sdg[0],
                           **z)

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
            dc.ms_ptg(TPpointingTemplate, outfile=TPpointinglist, uniq=True)
            #dc.listobs_ptg(TPpointingTemplate, listobsOutput, TPpointinglist)
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
            dc.runtclean_TP2VIS_INT(TPresult, TPfac[i], vis, imname,
                                    RMSfactor=RMSfactor, cube_rms=cube_rms, cont_chans = cont_chans, **z)   # in CASA 6.x
        
        TP2VISims.append(imname+'.image')
    


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

    os.system('rm -rf ' + sdroregrid + '.fits')
    exportfits(imagename=sdroregrid, fitsimage=sdroregrid + '.fits', dropdeg=True)
    
    allcombims = tcleanims  + featherims + SSCims     + hybridims  + sdintims  # + TP2VISims
    print(allcombims)



    allcombims = [a.replace('.image','.image.pbcor') for a in allcombims]
    allcombimsfits = [a.replace('.image.pbcor','.image.pbcor.fits') for a in allcombims]



    # make comparison plots
    
    #### imbase         = pathtoimage + 'skymodel-b_120L
    sourcename = imbase.replace(pathtoimage,'')
    # cleansetup
    assessment='assessment_'+sourcename+cleansetup
    os.system('mkdir '+assessment) 


    #labelnames
    allcombi = [a.replace(pathtoimage+sourcename+cleansetup+'.','').replace('.image.pbcor','') for a in allcombims]

    # make Apar and fidelity images

    iqa.get_IQA(ref_image = sdroregrid, target_image=allcombims)
    
    
    
     


    if mode=='cube':   ###### Compare*cubes has problems! #####
        #xvalues, yvalues = iqa.plot_Apar(target_image[j]+"_convo2ref_Apar.fits",Nplots,j,str(target_image[j]))
        #
        iqa.Compare_Apar_cubes(ref_image = sdroregrid, 
                               target_image=allcombims,
                               save=True,
                               plotname=assessment+'/Apar_channels_'+sourcename+cleansetup,
                               labelname=allcombi, 
                               titlename='Accuracy Parameter of cube: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.','')
                               )
        iqa.Compare_Fidelity_cubes(ref_image = sdroregrid, 
                               target_image=allcombims,
                               save=True,
                               plotname=assessment+'/Fidelity_channels_'+sourcename+cleansetup,
                               labelname=allcombi, 
                               titlename='Fidelity of cube: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.','')
                               )      
            
    #    for i in range(0,len(allcombims)):
    #        os.system('rm -rf ' + allcombims[i]+'.mom0')
    #        immoments(imagename=allcombims[i],
    #                   moments=[0],                                           
    #                   chans='',                                         
    #                   outfile=allcombims[i]+'.mom0')
    #        os.system('rm -rf ' + allcombims[i]+'.mom0.fits')
    #        exportfits(imagename=allcombims[i]+'.mom0', fitsimage=allcombims[i]+'.mom0.fits', dropdeg=True)
    #        mapchan=general_tclean_param['nchan']/2.
    #        iqa.show_Apar_map(    sdroregrid,allcombims[i],
    #                              #pathtoimage, 
    #                              channel=mapchan, 
    #                              save=True, 
    #                              plotname=assessment+'/Accuracy_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor','')+'_channel', #expecting only one file name entry per combi-method
    #                              labelname=allcombi[i],
    #                              titlename='Accuracy map in channel '+str(mapchan)+' for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
    #       
    #        iqa.show_Fidelity_map(sdroregrid,
    #                              allcombims[i],
    #                              pathtoimage, 
    #                              channel=mapchan, 
    #                              save=True, 
    #                              plotname=assessment+'/Fidelity_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor','')+'_channel', #expecting only one file name entry per combi-method
    #                              labelname=allcombi[i],
    #                              titlename='Fidelity map in channel '+str(mapchan)+' for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
    #   
    #    os.system('rm -rf ' + sdroregrid+'.mom0')               
    #    immoments(imagename=sdroregrid,
    #               moments=[0],                                           
    #               chans='',                                         
    #               outfile=sdroregrid+'.mom0')
    #    
    #   
    #    
    #    
    #    # use mom0-maps as input for the cont-defined Apar/fidelity functions
    #    allcombims = [a.replace('.image.pbcor', '.image.pbcor.mom0') for a in allcombims]
    #    allcombimsfits = [a.replace('.image.pbcor.mom0','.image.pbcor.mom0.fits') for a in allcombims]
    #
    #    sdroregrid = sdroregrid+'.mom0'
    #    os.system('rm -rf ' + sdroregrid + '.fits')
    #    exportfits(imagename=sdroregrid, fitsimage=sdroregrid + '.fits', dropdeg=True)
    #
    #    iqa.get_IQA(ref_image = sdroregrid, target_image=allcombims)
    # 
    #
    #
    #
    #  
    #          
    #
    #
    ## all Apar and fidelity plots
    #iqa.Compare_Apar(ref_image = sdroregrid, 
    #                 target_image=allcombims, 
    #                 #pathnametodrop = pathtoimage,
    #                 save=True, 
    #                 plotname=assessment+'/AparALL_'+sourcename+cleansetup,
    #                 labelname=allcombi, 
    #                 titlename='Accuracy Parameter: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))
    #iqa.Compare_Fidelity(ref_image = sdroregrid, 
    #                 target_image=allcombims,
    #                 #pathnametodrop = pathtoimage,
    #                 save=True, 
    #                 plotname=assessment+'/FidelityALL_'+sourcename+cleansetup,
    #                 labelname=allcombi, 
    #                 titlename='Fidelity: comparison for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
    #for i in range(0,len(allcombims)):
    #    # Apar and fidelity vs signal plots
    #    iqa.Compare_Apar_signal(ref_image = sdroregrid, 
    #                             target_image=[allcombims[i]],
    #                             #pathnametodrop = pathtoimage,
    #                             save=True,
    #                             noise=0.0, 
    #                             plotname=assessment+'/Apar_signal_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
    #                             labelname=[allcombi[i]],
    #                             titlename='Accuracy vs. Signal for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
    #    iqa.Compare_Fidelity_signal(ref_image = sdroregrid, 
    #                             target_image=[allcombims[i]],
    #                             pathnametodrop = pathtoimage,
    #                             save=True,
    #                             noise=0.0, 
    #                             plotname=assessment+'/Fidelity_signal_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
    #                             labelname=[allcombi[i]],
    #                             titlename='Fidelity vs. Signal for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                                    
    #    # Apar and fidelity image plots
    #    iqa.show_Apar_map(    sdroregrid,allcombims[i],
    #                          #pathtoimage, 
    #                          channel=0, 
    #                          save=True, 
    #                          plotname=assessment+'/Accuracy_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
    #                          labelname=allcombi[i],
    #                          titlename='Accuracy map for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
    #
    #    iqa.show_Fidelity_map(sdroregrid,
    #                          allcombims[i],
    #                          pathtoimage, 
    #                          channel=0, 
    #                          save=True, 
    #                          plotname=assessment+'/Fidelity_map_'+allcombims[i].replace(pathtoimage,'').replace('.image.pbcor',''), #expecting only one file name entry per combi-method
    #                          labelname=allcombi[i],
    #                          titlename='Fidelity map for \ntarget: '+allcombims[i].replace(pathtoimage,'')+' and \nreference: '+sdroregrid.replace(pathtoimage,''))                                    
    #
    #
    #
    #
    #iqa.genmultisps(allcombimsfits, save=True, 
    #               plotname=assessment+'/Power_spectra_'+sourcename+cleansetup,
    #               labelname=allcombi,
    #               titlename='Power spectra for \nsource: '+sourcename+' and \nclean setup: '+cleansetup.replace('.',''))                         
    #
    #
    
    #################### NOT YET WORKING !!! problems #######
    #
    #iqa.get_aperture(allcombimsfits,position=(1,1),Nbeams=10)
    #
    ##### !!!needs SD-fitsfile ----> to create in step 1 !!!!
  
  
  







# delete tclean TempLattices

os.system('rm -rf '+pathtoimage + 'TempLattice*')


end = time.time()
diff = round(end - start)
print('')
print('')
print('---------------------------- WE ARE DONE! -----------------------------')
print('')
print('Execution of DC_run.py took:', diff, 'seconds =', round(diff/60.0, 2), 'minutes =', round(diff/60.0/60.0, 2), 'hours')







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




