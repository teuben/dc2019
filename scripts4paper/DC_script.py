"""
Script to use the datacomb module

by L. Moser-Fischer, Oct 2020

Based on the work at the Workshop
"Improving Image Fidelity on Astronomical Data", 
Lorentz Center, Leiden, August 2019, 
and subsequent follow-up work. 

Run under CASA 6.

"""



#thesteps=[0,1,2,3,4,5,6]
thesteps=[5]



import os 
import sys 
#import glob

sys.path.append('/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/dc2019/scripts4paper/')               # path to the folder with datacomb.py and ssc_DC.py

pythonversion = sys.version[0]


if pythonversion=='3':
    from casatasks import version as CASAvers
    if CASAvers()[0]>=6 and CASAvers()[1]>=1:
        #print('Executed in CASA ' +'.'.join(map(str, CASAvers())))    
        #if 'casatasks' in locals():
        import datacomb as dc
        #import ssc_DC_2 as ssc     # need to import casatasks therein!
        from casatasks import concat
        from casatasks import casalog
        from importlib import reload  
         
        #reload(ssc)
        reload(dc)
    else:
        print('###################################################')
        print('Your CASA version does not support sdintimaging.')
        print('Please use at least CASA 5.7.0 or 6.1.x')
        print('Aborting script ...')
        print('###################################################')
        sys.exit()


elif pythonversion=='2':
    import casadef
    if casadef.casa_version == '5.7.0':
        #print('Executed in CASA ' +casadef.casa_version)
        execfile('/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/dc2019/scripts4paper/datacomb.py', globals())               # path to the folder swith datacomb.py and ssc_DC.py
        #execfile('/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/dc2019/scripts4paper/ssc_DC_2.py', globals())               # path to the folder swith datacomb.py and ssc_DC.py
    else:
        print('###################################################')
        print('Your CASA version does not support sdintimaging.')
        print('Please use at least CASA 5.7.0 or 6.1.x')
        print('Aborting script ...')
        print('###################################################')
        sys.exit()




# path to input and outputs
pathtoconcat = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/ToshiSim/gmcSkymodel_120L/gmc_120L/'   # path to the folder with the files to be concatenated
#pathtoconcat = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/ToshiSim/skymodel-c.sim/skymodel-c_120L/'   # path to the folder with the files to be concatenated
pathtoimage  = '/vol/arc3/data1/arc2_data/moser/DataComb/DCSlack/DC_Ly_tests/'                          # path to the folder where to put the combination and image results


### delete garbage from aboprted script ###
os.system('rm -rf '+pathtoimage + 'TempLattice*')


# setup for concat 
#thevis = [pathtoconcat + 'skymodel-c_120L.alma.cycle6.4.2018-10-02.ms']#,
thevis = [pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-02.ms']#,
          #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-02.ms',
          #pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-03.ms',
          #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-03.ms',
          #pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-04.ms',
          #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-04.ms',
          #pathtoconcat + 'gmc_120L.alma.cycle6.4.2018-10-05.ms',
          #pathtoconcat + 'gmc_120L.alma.cycle6.1.2018-10-05.ms',
          #pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-20.ms',
          #pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-21.ms',
          #pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-22.ms',
          #pathtoconcat + 'gmc_120L.aca.cycle6.2018-10-23.ms']

weightscale = [1.]#, 1., 1., 1., 1., 1., 1., 1.,
               #0.116, 0.116, 0.116, 0.116]

concatms     = pathtoimage + 'skymodel-b_120L.alma.all_int-weighted.ms'       # path and name of concatenated file
#concatms     = pathtoimage + 'skymodel-c_120L.alma.all_int-weighted.ms'       # path and name of concatenated file




############# input to combination methods ###########

vis       = concatms 
sdimage_input  = pathtoconcat + 'gmc_120L.sd.image'
#sdimage_input   = pathtoconcat + 'skymodel-c_120L.sd.image'
imbase    = pathtoimage + 'skymodel-b_120L'            # path + image base name
#imbase    = pathtoimage + 'skymodel-c_120L'            # path + image base name

sdimage = sdimage_input



    ### ### tclean specific 
    ### startmodel='',  # ---> sdimage in WSM
    ### 
    ### ### WSM specific
    ### sdimage,  ### startmodel 
    ### 
    ### ### SDint specific
    ### sdimage, 
    ### jointname, ### = imname 




############ names and parameters that should be noted in the file name

# structure could be something like:
#    imname = imbase + cleansetup + combisetup 
#
# e.g. cleansetup = '.mfs.n1e2.hogbom.manual'
# e.g. cleansetup = '.cube.n1e9.MS.AM'

mode   = 'mfs'    # 'mfs' or 'cube'
mscale = 'HB'     # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT by default!)) 
masking  = 'SD-AM'   # 'UM' (user mask), 'SD-AM' (SD+AM mask)), 'AM' ('auto-multithresh') or 'PB' (primary beam)
inter = 'nIA'     # interactive ('IA') or non-interactive ('nIA')
nit = 1        # max = 9.9 * 10**9 

#cleansetup = "."+ mode +"."+ mscale +"."+ inter + (".n%.1e").replace("+","")  %(nit)
cleansetup = '.'+ mscale +'_'+ masking +'_'+ inter +'_'+ str(nit)

#cleansetup = '.'+ mscale +'_'+ masking + '_n%.1e' %(nit)
#cleansetup = cleansetup.replace("+0","")

                     
                       
### general tclean parameters:

general_tclean_param = dict(#overwrite  = overwrite,
                           spw         = '0', 
                           field       = '0~68', 
                           specmode    = mode,      # ! change in variable above dict !        
                           imsize      = [1120], 
                           cell        = '0.21arcsec',    # arcsec
                           phasecenter = 'J2000 12:00:00 -35.00.00.0000',             
                           start       = 0, 
                           width       = 1, 
                           nchan       = -1, 
                           restfreq    = '',
                           threshold   = '0.021Jy',        # SDINT: None 
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


### SDint specific parameters:

sdint_tclean_param = dict(sdpsf   = '',
                         #sdgain  = 5,     # own factor! see below!
                         dishdia = 12.0)
                       
                       
                       
                         
                         
### naming scheme specific inputs:
if inter == 'IA':
    general_tclean_param['interactive'] = True    
elif inter == 'nIA':
    general_tclean_param['interactive'] = False    
                             
if masking == 'UM':
    general_tclean_param['usemask']     = 'user'
if masking == 'SD-AM': 
    if not os.path.exists(imbase + 'SD-AM.mask'):
        thesteps.append(1)      
        thesteps.sort()           # force execution of SDint mask creation (Step 1)
    general_tclean_param['usemask']     = 'user'   
if masking == 'PB':
    general_tclean_param['usemask']     = 'pb'
if masking == 'AM':
    general_tclean_param['usemask']     = 'auto-multithresh'    

if mscale == 'HB':
    general_tclean_param['multiscale'] = False
if mscale == 'MS':
    general_tclean_param['multiscale'] = True      # automated scale choice dependant on maxscale




# feather parameters:
sdfac = [1.0]

# Faridani parameters:
SSCfac = [1.0]

# Hybrid feather paramteters:
sdfac_h = [1.0]

# SDINT parameters:
sdg = [1.0]

## TP2VIS parameters:
#tweak = [1.0]



### output of combination methods 

tcleansetup  = '.tclean'
feathersetup = '.feather_f' #+ str(sdfac)
SSCsetup     = '.SSC_f'     #+ str(SSCfac)
hybridsetup  = '.hybrid_f'  #+ str(sdfac_h)
sdintsetup   = '.sdint_g'   #+ str(sdg)
#TP2VISsetup  = '.TP2VIS_t'  #+ str(tweak)

### need to modify datacomb.py because of its current output:
# current output: imnametclean  = imbase + cleansetup + '.TCLEAN.image '
# current output: imnamefeather = imbase + cleansetup + '.image'
# current output: imnameSSC     = imbase + cleansetup + '_ssc_f%sTP%s%s.image'   % (f,label,niter_label)
# current output: imnamehybrid  = imbase + cleansetup + '.combined.image'               
# current output: imnamesdint   = imbase + cleansetup + '.joint.multiterm.image.tt0' or '.joint.cube.image'


####### collect file names for assessment ######

dryrun = False    # False to execute combination, True to gather filenames only

tcleanims  = []
featherims = []
SSCims     = []
hybridims  = []
sdintims   = []
#TP2VISims  = []


# methods for combining agg. bandwidth image with TP image - cube not yet tested/provided

#### thesteps = []   # define at beginning or outside this script

step_title = {0: 'Concat',
              1: 'Prepare the SD-image',
              2: 'Clean for Feather/Faridani',
              3: 'Feather', 
              4: 'Faridani short spacings combination (SSC)',
              5: 'Hybrid (startmodel clean + Feather)',
              6: 'SDINT'#,
              #7: 'TP2VIS'
              }

        
    
mystep = 0    ###################----- CONCAT -----####################
if(mystep in thesteps):
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
           


mystep = 1    ############# ----- PREPARE SD-IMAGE -----###############
if(mystep in thesteps):
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')    
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')
  
  
    # axis reordering
    sdreordered = imbase +'.SD_ro.image'
    reorder_axes(sdimage_input, sdreordered)
    
    # read SD image frequency setup as input for tclean    
    cube_dict = get_SD_cube_params(sdcube = sdreordered) #out: {'nchan':nchan, 'start':start, 'width':width}
    #print(cube_dict)

    imname = imbase + cleansetup
    threshmask = imbase + '.RMS'

    thresh = derive_threshold(vis, imname, threshmask,
                     phasecenter=general_tclean_param['phasecenter'], 
                     spw=        general_tclean_param['spw'], 
                     field=      general_tclean_param['field'], 
                     imsize=     general_tclean_param['imsize'], 
                     cell=       general_tclean_param['cell'],
                     specmode=general_tclean_param['specmode'],
                     start = general_tclean_param['start'],
                     width = general_tclean_param['width'],
                     nchan = general_tclean_param['nchan'],
                     restfreq = general_tclean_param['restfreq'],
                     overwrite=False,
                     smoothing = 5, 
                     RMSfactor = 0.5)
                     
                     

    ##### add to sdmask function 
    #     # regrid SD image frequency axis to tclean 
    #     #    for cube mask needed !!!
    #     print('Regridding lowres image...')
    #     imregrid(imagename=lowres,
    #                      template=highres,
    #                      axes=[0,1,2,3],
    #                      output='lowres.regrid')    
    
    
       
    # make SD+AM mask (currently:  cont mode only)
    

    SDint_mask_root = imbase
    sdmasklev = 0.3
    
    SDint_mask = make_SDint_mask(vis, sdreordered, imname, 
                                 sdmasklev, 
                                 SDint_mask_root, 
                                 phasecenter=general_tclean_param['phasecenter'], 
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

    combined_mask = SDint_mask_root + '.SD-AM-RMS.mask'
    immath(imagename=[SDint_mask, threshmask+'.mask'],
           expr='iif((IM0+IM1)>'+str(0)+',1,0)',
           outfile=combined_mask)    



    # 
    #if masking == 'SD-AM': 
    #    general_tclean_param['mask']  = SDint_mask   


           

mystep = 2    ############----- CLEAN FOR FEATHER/SSC -----############
if(mystep in thesteps):
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
        general_tclean_param['mask']  = threshmask+'.mask'


    ### for CASA 5.7:
    z = general_tclean_param.copy()   
    #z.update(special_tclean_param)


    if dryrun == True:
        pass
    else:
        os.system('rm -rf '+imname+'*')
        if pythonversion=='3':
            dc.runtclean(vis, imname, startmodel='', 
                    **z)
                    #**general_tclean_param, **special_tclean_param)   # in CASA 6.x
        else:
            runtclean(vis, imname, startmodel='', **z)    # in CASA 5.7
        
        #dc.runtclean(vis, imname, startmodel='',spw='', field='', specmode='mfs', 
        #            imsize=[], cell='', phasecenter='',
        #            start=0, width=1, nchan=-1, restfreq=None,
        #            threshold='', niter=0, usemask='auto-multithresh' ,
        #            sidelobethreshold=2.0, noisethreshold=4.25, lownoisethreshold=1.5, 
        #            minbeamfrac=0.3, growiterations=75, negativethreshold=0.0,
        #            mask='', pbmask=0.4, interactive=True, 
        #            multiscale=False, maxscale=0.)

        #os.system('for f in '+imbase+cleansetup+'.TCLEAN*; \
         #          do mv "$f" "${f/.TCLEAN./.}" \
          #         done')   # rename output to our convention 
        #os.system('for f in '+imbase+cleansetup+'.TCLEAN*; do mv "$f" "$(echo $f | sed 's/^.TCLEAN././g')"; done')
        
        #oldnames=glob.glob(imname+'.TCLEAN*')
        #for nam in oldnames:
        #    os.system('mv '+nam+' '+nam.replace('.TCLEAN',''))
        #
        ##os.system('rename "s/.TCLEAN//g" '+imname+'.TCLEAN*')


    tcleanims.append(imname)



mystep = 3    ###################----- FEATHER -----###################
if(mystep in thesteps):
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
        
        #os.system('rm -rf '+pathtoimage+'lowres*')
        #os.system('rm -rf '+imname+'.image.pbcor.fits')
                
        if dryrun == True:
            pass
        else:
            if pythonversion=='3':
                dc.runfeather(intimage, intpb, sdimage, sdfactor = sdfac[i],
                          featherim = imname)
            else:
                runfeather(intimage, intpb, sdimage, sdfactor = sdfac[i],
                          featherim = imname)
                                      
            #dc.runfeather(intimage,intpb, sdimage, featherim='featherim')

        featherims.append(imname)




mystep = 4    ################----- FARIDANI SSC -----#################
if(mystep in thesteps):
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')

    for i in range(0,len(sdfac)):
        imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
        
        if dryrun == True:
            pass
        else:
            os.system('rm -rf '+imname+'*')

            if pythonversion=='3':
                dc.ssc(highres=imbase+cleansetup+tcleansetup+'.image', 
                    lowres=sdimage, pb=imbase+cleansetup+tcleansetup+'.pb',
                    sdfactor = SSCfac[i], combined=imname) 
            else:
                ssc(highres=imbase+cleansetup+tcleansetup+'.image', 
                    lowres=sdimage, pb=imbase+cleansetup+tcleansetup+'.pb',
                    sdfactor = SSCfac[i], combined=imname) 
                    
                    
            #ssc(pathtoimage,highres=imbase+cleansetup+tcleansetup+'.image.pbcor', 
            #    lowres=sdimage, f = SSCfac[i]) 

            #os.system('for file in '+imbase+cleansetup+'_ssc_f'+str(SSCfac[i])+'TP* \
            #           do mv "$file" "${file//_ssc_f'+str(SSCfac[i])+'TP/'+SSCsetup + str(SSCfac[i])+'}" \
            #           done')   # rename output to our convention 

            #os.system('rename "s/'+tcleansetup+'_ssc_f'+str(SSCfac[i])+'TP/'+SSCsetup + str(SSCfac[i])+'/g" '+imbase+cleansetup+tcleansetup+'_ssc_f'+str(SSCfac[i])+'TP*')

        SSCims.append(imname)





mystep = 5    ###################----- HYBRID -----####################
if(mystep in thesteps):
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')


    if masking == 'SD-AM': 
        general_tclean_param['mask']  = combined_mask


    ### for CASA 5.7:
    z = general_tclean_param.copy()   
    #z.update(special_tclean_param)




    for i in range(0,len(sdfac_h)):
        imname = imbase + cleansetup + hybridsetup #+ str(sdfac_h[i]) 

        #os.system('rm -rf '+pathtoimage+'lowres*')
        #os.system('rm -rf '+imname+'.image.pbcor.fits')
        
        if dryrun == True:
            pass
        else:
            os.system('rm -rf '+imname+'.*')
            #os.system('rm -rf '+imname.replace('_f'+str(sdfac_h[i]),'')+'.*') 
            # delete tclean files ending on 'hybrid.*'  (dot '.' is important!)

            
            if pythonversion=='3':
                dc.runWSM(vis, sdimage, imname, sdfactorh = sdfac_h[i],
                      **z)
                      #**general_tclean_param, **special_tclean_param)
            else:
                runWSM(vis, sdimage, imname, sdfactorh = sdfac_h[i],
                      **z)
            
            #dc.runWSM(vis, sdimage, imname, spw='', field='', specmode='mfs', 
            #            imsize=[], cell='', phasecenter='',
            #            start=0, width=1, nchan=-1, restfreq=None,
            #            threshold='',niter=0,usemask='auto-multithresh' ,
            #            sidelobethreshold=2.0,noisethreshold=4.25,lownoisethreshold=1.5, 
            #            minbeamfrac=0.3,growiterations=75,negativethreshold=0.0,
            #            mask='', pbmask=0.4,interactive=True, 
            #            multiscale=False, maxscale=0.)


            #os.system('for file in '+imbase+cleansetup+'.combined* \
            #           do mv "$file" "${file//.combined/'+hybridsetup + str(sdfac_h[i])+'}" \
            #           done')   # rename output to our convention 
            
            
            #oldnames=glob.glob(imname+'.TCLEAN*')
            #for nam in oldnames:
            #    os.system('mv '+nam+' '+nam.replace('_f'+str(sdfac_h[i])+'.TCLEAN',''))
            #oldnames=glob.glob(imname+'.combined*')
            #for nam in oldnames:
            #    os.system('mv '+nam+' '+nam.replace('.combined',''))
            
            ####os.system('rename "s/.combined//g" '+imname+'.combined*')
            
        hybridims.append(imname)


mystep = 6    ####################----- SDINT -----####################
if(mystep in thesteps):
    casalog.post('### ','INFO')
    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
    casalog.post('### ','INFO')
    print(' ')
    print('### ')
    print('Step ', mystep, step_title[mystep])
    print('### ')
    print(' ')
    
    
    
    if masking == 'SD-AM': 
        general_tclean_param['mask']  = combined_mask




    ### for CASA 5.7:
    z = general_tclean_param.copy()   
    z.update(sdint_tclean_param)
    #z.update(special_tclean_param)


    
    for i in range(0,len(sdg)) :
        jointname = imbase + cleansetup + sdintsetup + str(sdg[i]) 
        
        if dryrun == True:
            pass
        else:
            os.system('rm -rf '+jointname+'*')
            
            if pythonversion=='3':
                dc.runsdintimg(vis, sdimage, jointname, sdgain = sdg[0],
                   **z)
                   #**general_tclean_param, **sdint_tclean_param)
            else:
                runsdintimg(vis, sdimage, jointname, sdgain = sdg[0],
                   **z)
                   
                   
                                           
            #dc.runsdintimg(vis, sdimage, jointname, spw='', field='', specmode='mfs', sdpsf='',
            #            threshold=None, sdgain=5, imsize=[], cell='', phasecenter='', dishdia=12.0,
            #            start=0, width=1, nchan=-1, restfreq=None, interactive=True, 
            #            multiscale=False, maxscale=0.)                

            #os.system('for file in '+imbase+cleansetup+'.combined* \
            #           do mv "$file" "${file//.combined/'+hybridsetup + str(sdfac_h[i])+'}" \
            #           done')   # rename output to our convention 

            #os.system('rename "s/.joint.multiterm//g" '+jointname+'.joint.multiterm.*')
            #os.system('rename "s/.tt0//g" '+jointname+'.*.tt0*')
            #os.system('rename "s/.joint.cube//g" '+jointname+'.joint.cube.*')

        sdintims.append(jointname)                
                
                
#mystep = 7    ###################----- TP2VIS -----####################
#if(mystep in thesteps):
#    casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
#    print('Step ', mystep, step_title[mystep])




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






#
#
#sdint default
#
#
#    +usedata                 = 'sdint'                 # Output image type(int, sd, sdint)
#    +   sdimage              = ''                      # Input single dish image
#    +   sdpsf                = ''                      # Input single dish PSF image
#    +   sdgain               = 1.0                     # A factor or gain to adjust single dish flux scale
#    +   dishdia              = 100.0                   # Effective dish diameter
#    +vis                     = ''                      # Name of input visibility file(s)
#selectdata              = True                    # Enable data selection parameters
#   field                = ''                      # field(s) to select
#       +spw                  = ''                      # spw(s)/channels to select
#   timerange            = ''                      # Range of time to select from data
#   uvrange              = ''                      # Select data within uvrange
#   antenna              = ''                      # Select data based on antenna/baseline
#   scan                 = ''                      # Scan number range
#   observation          = ''                      # Observation ID range
#   intent               = ''                      # Scan Intent(s)
#datacolumn              = 'corrected'             # Data column to image(data,corrected)
#    +imagename               = ''                      # Pre-name of output images
#    +imsize                  = []                      # Number of pixels
#    +cell                    = []                      # Cell size
#    +phasecenter             = ''                      # Phase center of the image
#stokes                  = 'I'                     # Stokes Planes to make
#projection              = 'SIN'                   # Coordinate projection
#startmodel              = ''                      # Name of starting model image
#    +specmode                = 'mfs'                   # Spectral definition mode (mfs,cube,cubedata, cubesource)
#    +   reffreq              = ''                      # Reference frequency
#nchan                   = -1                      # Number of channels in the output image
#start                   = ''                      # First channel (e.g. start=3,start='1.1GHz',start='15343km/s')
#width                   = ''                      # Channel width (e.g. width=2,width='0.1MHz',width='10km/s')
#outframe                = 'LSRK'                  # Spectral reference frame in which to interpret 'start' and 'width'
#veltype                 = 'radio'                 # Velocity type (radio, z, ratio, beta, gamma, optical)
#restfreq                = []                      # List of rest frequencies
#interpolation           = 'linear'                # Spectral interpolation (nearest,linear,cubic)
#chanchunks              = 1                       # Number of channel chunks
#perchanweightdensity    = True                    # whether to calculate weight density per channel in Briggs style
#                                                  # weighting or not
#gridder                 = 'standard'              # Gridding options (standard, wproject, widefield, mosaic, awproject)
#   vptable              = ''                      # Name of Voltage Pattern table
#   pblimit              = 0.2                     # PB gain level at which to cut off normalizations
#deconvolver             = 'hogbom'                # Minor cycle algorithm
#                                                  # (hogbom,clark,multiscale,mtmfs,mem,clarkstokes)
#restoration             = True                    # Do restoration steps (or not)
#   restoringbeam        = []                      # Restoring beam shape to use. Default is the PSF main lobe
#   pbcor                = False                   # Apply PB correction on the output restored image
#    +weighting               = 'natural'               # Weighting scheme (natural,uniform,briggs, briggsabs[experimental])
#   uvtaper              = []                      # uv-taper on outer baselines in uv-plane
#niter                   = 0                       # Maximum number of iterations
#usemask                 = 'user'                  # Type of mask(s) for deconvolution: user, pb, or auto-multithresh
#   mask                 = ''                      # Mask (a list of image name(s) or region file(s) or region string(s)
#                                                  # )
#   pbmask               = 0.0                     # primary beam mask
#fastnoise               = True                    # True: use the faster (old) noise calculation. False: use the new
#                                                  # improved noise calculations
#restart                 = True                    # True : Re-use existing images. False : Increment imagename
#savemodel               = 'none'                  # Options to save model visibilities (none, virtual, modelcolumn)
#calcres                 = True                    # Calculate initial residual image
#calcpsf                 = True                    # Calculate PSF
#parallel                = False                   # Run major cycles in parallel
#
#
#
#runsdintimg(
#vis, 
#sdimage, 
#jointname, 
#spw='', 
#field='', 
#specmode='mfs', 
#sdpsf='',
#threshold=None, 
#sdgain=5, 
#imsize=[], 
#cell='', 
#phasecenter='', 
#dishdia=12.0,
#start=0, 
#width=1, 
#nchan=-1, 
#restfreq=None, 
#interactive=True, 
#multiscale=False, 
#maxscale=0.)
#                
#                
#       sdintimaging( ^vis=myvis,
#                     ^sdimage=mysdimage,
#                     ^sdpsf=mysdpsf,
#                     ^dishdia=dishdia,
#                     ^sdgain=sdgain,
#                     usedata='sdint',
#                     ^imagename=jointname,
#                     ^imsize=imsize,
#                     ^cell=cell,
#                     ^phasecenter=phasecenter,
#                     weighting='briggs',
#                     robust = 0.5,
#                     ^specmode=specmode,
#                     gridder=mygridder,
#                     pblimit=0.2,                #default
#                     pbcor=True,
#                     interpolation='linear',    #default
#                     wprojplanes=1,             # default & irrelevant
#                     ^deconvolver=mydeconvolver,
#                     scales=myscales,
#                     nterms=1,                  # for mtmfs
#                     niter=10000000,
#                     ^spw=spw,
#                     ^start=start,
#                     ^width=width,
#                     ^nchan = numchan, 
#                     ^field = field,
#                     ^threshold=threshold,
#                     ^restfreq=therf,
#                     perchanweightdensity=False,
#                     ^*#interactive=True,
#                     *#cycleniter=100,
#                     *#usemask='pb',
#                     #pbmask=0.4,
#                 )
#
#        sdintimaging(vis=myvis,
#                     sdimage=mysdimage,
#                     sdpsf=mysdpsf,
#                     dishdia=dishdia,
#                     sdgain=sdgain,
#                     usedata='sdint',
#                     *#imagename=jointname,
#                     imsize=imsize,
#                     cell=cell,
#                     phasecenter=phasecenter,
#                     weighting='briggs',
#                     robust = 0.5,
#                     specmode=specmode,
#                     *#gridder=mygridder, # mosaic
#                     pblimit=0.2, 
#                     pbcor=True,
#                     interpolation='linear',
#                     wprojplanes=1,
#                     deconvolver=mydeconvolver,
#                     scales=myscales,
#                     nterms=1,
#                     niter=10000000,
#                     spw=spw,
#                     start=start,
#                     width=width,
#                     nchan = numchan, 
#                     field = field,
#                     threshold=threshold,
#                     restfreq=therf,
#                     perchanweightdensity=False,
#                     *#interactive=False,
#                     *#cycleniter = 100000, 
#                     #cyclefactor=2.0,           # = 1.0 default
#                     *#usemask='auto-multithresh',
#                     #sidelobethreshold=2.0,
#                     #noisethreshold=4.25,
#                     #lownoisethreshold=1.5, 
#                     #minbeamfrac=0.3,
#                     #growiterations=75,
#                     #negativethreshold=0.0
#                 )
#
#
#
#
#    tclean(^vis = myvis,
#         ^*#imagename = imname+'.TCLEAN',
#         ^#startmodel = startmodel,
#         ^field = field,
#         #intent = 'OBSERVE_TARGET#ON_SOURCE',
#         ^phasecenter = phasecenter,
#         #stokes = 'I',                  # default
#         spw = spw,
#         #outframe = 'LSRK',             # DEFAULT
#         ^specmode = specmode,
#         nterms = 1,
#         ^imsize = imsize,
#         ^cell = cell,
#         deconvolver = mydeconvolver,
#         scales = myscales,
#         ^*#niter = niter,
#         *#cycleniter = niter,
#         *#cyclefactor=2.0,
#         weighting = 'briggs',
#         robust = 0.5,
#         *#gridder = 'mosaic',
#         pbcor = True,
#         ^threshold = threshold,
#         ^*#interactive = interactive,
#         ++++# Masking Parameters below this line 
#         ++++# --> Should be updated depending on dataset
#         ^*#usemask=mymask,
#         *#sidelobethreshold=sidelobethreshold,
#         *#noisethreshold=noisethreshold,
#         *#lownoisethreshold=lownoisethreshold, 
#         *#minbeamfrac=minbeamfrac,
#         *#growiterations=growiterations,
#         *#negativethreshold=negativethreshold,
#         ^mask=mask,
#         ^*#pbmask=pbmask,
#         verbose=True
#         )
#                ^start=0, width=1, nchan=-1, restfreq=None,
#                ^multiscale=False, maxscale=0.):
#
#
#
