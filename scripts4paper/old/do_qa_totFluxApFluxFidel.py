"""
BSM 4 sept 2020
v1 of total flux, aperture photometry, and fractional flux-weighted fidelity QA script
   runs in one directory that should contain all the files to be assessed; a true modelfile;
   and fluxbox.reg region file

"""
import pickle
# dependencies: place combo_utils.py in your casa path (e.g. ~/casapy/ or the like)
#  https://github.com/teuben/dc2019/blob/master/scripts/ngVlaSbaSims/combo_utils.py
import combo_utils as combut

try:
    del files_to_assess
except:
    pass

########################################
# Set this! ->
# truth/reference file: **should be in Jy/pix**
modelfile = 'skymodel-b.fits'
# scripts also requires fluxbox.reg in the current working directory

# derive me instead but for now -
trueFlux = 6644.09

#mysteps = [4]
thesteps = []
step_title = {0: 'Import FITS files',
              1: 'total flux assessment',
              2: 'fidelity assessment',
              3: 'aperture flux assessment',
              4: 'summarize assessments'}

# used if no files_to_assess list is manually set below
file_regexp = "*fits"
#file_regexp = "*image"
#file_regexp = "*{totFlux,fid,apFlux}.pkl"
#file_regexp = "*totFlux.pkl"

#files_to_assess = glob.glob("*noRing.apFlux.pkl")+glob.glob("*totFlux.pkl")+glob.glob("*fid.pkl")

# list of FITS files to assess (requiring step 0, import)
#  or images to directly assess
#  or pickle files to summarize results of
#
#files_to_assess=['gmc_120L.alma.all_int-mfs.I.manual-weighted.pbcor.image',
#'gmc_120L.Feather_sdfactor1.2.pbcor.image',
#'gmc_120L.Feather_sd_1.2.image.image',
#'gmc_120L.Feather.pbcor.image',
#'gmc_120L_FaridaniComb_SDF_1.0.image',
#'gmc_120L.hybrid3.image.pbcor.image',
#'gmc_120L.hybrid.pbcor.image',
#'gmc_120L.hybrid.Feather.pbcor.image',
#'sky_tweak_box1.image',
#'sky_tpint_box1.image',
#'sky_mac_box1.image',
#'deepclean-sdgain1.joint.multiterm.pbcor.tt0.image',
#'deepclean-sdgain1.25.joint.multiterm.pbcor.tt0.image']
# files_to_assess = ['a.fits','b.fits']
#files_to_assess = ['gmc_120L.alma.all_int-mfs.I.manual-weighted.pbcor.image',
#'gmc_120L.Feather_sdfactor1.2.pbcor.image',
#'gmc_120L.Feather_sd_1.2.image.image',
#'gmc_120L.Feather.pbcor.image',
#'gmc_120L_FaridaniComb_SDF_1.0.image',
#'gmc_120L.hybrid3.image.pbcor.image',
#'gmc_120L.hybrid.pbcor.image',
#'gmc_120L.hybrid.Feather.pbcor.image',
#'sky_tweak_box1.image',
#'sky_tpint_box1.image',
#'sky_mac_box1.image',
#'deepclean-sdgain1.joint.multiterm.pbcor.tt0.image',
#'deepclean-sdgain1.25.joint.multiterm.pbcor.tt0.image']
#
#
# these are not at present used-
#tpobsfile = 'gmc_120L.sd.fits'
#pbfile = 'feather2/gmc_120L.alma.all_int-mfs.I.manual-weighted.pb.fits'
#
######## DO NOT EDIT BELOW HERE ##############
#
# builds or infers images_to_assess from files_to_assess
# makes or infers results_list
#

try:
    print("List of steps to be executed: ",mysteps)
    thesteps = mysteps
except:
    print("Global variable mysteps not set.")
if (thesteps==[]):
    thesteps = range(0,len(step_title))
    print("Executing all steps: ",thesteps)

# choose files
try:
    print(" Using file list files_to_assess = ")
    print(files_to_assess)
except:
    try:
        print("files_to_assess undefined, using file_regexp to match files")
        files_to_assess = glob.glob(file_regexp)
        if (len(files_to_assess) == 0):
            mystr = "Failed to match requested files "+file_regexp
            raise Exception(myster)
        print(" Assessing files from regular expression",file_regexp)
        print(files_to_assess)
    except:
        raise Exception("Must provide either files_to_assess or file_regexp")

# check that the file list and the requested steps are consistent
first_filename, first_file_ext = os.path.splitext(files_to_assess[0])
if ((first_file_ext == '.fits' or first_file_ext == '.FITS') and not(0 in thesteps)):
    raise Exception("File list contains FITS file but FITS import was not requested (step 0)")
if ((first_file_ext != '.fits' and first_file_ext != '.FITS') and (0 in thesteps)):
    raise Exception(" FITS import was requested but first file appears not to be a .fits or .FITS file")
if ((first_file_ext == '.pkl') and (thesteps != [4])):
    raise Exception("File list contains pickle file but steps other than result summary were requested")
if ((first_file_ext != '.pkl') and (thesteps == [4])):
    raise Exception("Summary requested but file contains non-pkl file")
    



###########

def do_fits_import(flnm,do_pbcor=False,pbfile='',overwrite=True):
    """
    import FITS to CASA image. 
    """
    flnm_noext,file_ext = os.path.splitext(flnm)
    outFile = flnm_noext + ".image"
    importfits(fitsimage=flnm,imagename=outFile,overwrite=overwrite)
    if (do_pbcor and len(pbfile) > 0):
        pbfile = flnm_noext+".pbcor"
        immath(imagename=[outFile,pbfile],outfile=outFile+".pbcor",expr='IM0/IM1',overwrite=True)  
        return pbfile
    else:
        return outFile

def do_total_flux(flnm,region):
    my_stats = imstat(flnm,region=region)    
    my_stats['metric'] = 'totalFlux'
    my_stats['inimg'] = flnm
    return my_stats

def do_fidelity(flnm,refimg):
    my_stats = combut.calc_fidelity(flnm,refimg)
    my_stats['metric'] = 'fidelity'
    my_stats['inimg'] = flnm
    my_stats['refimg'] = refimg
    return my_stats

def do_ap_flux(inimg,refimg,do_stats=True,clean_up=True,make_pickles=True,search_img=1,doAnnuli=True,tag=''):
    """
    Given input (Jy/bm) and reference (Jy/pix) images, compute aperture flux curves.
    return a dictionary with results (radius in arcsec; median fraction of flux recovered;
    MAD of fraction of flux recovered; list of peaks identified; input and ref image names)
    """
    inimg_jypix=inimg+'.TMP.jyPix'
    combut.jyBm2jyPix(inimg,inimg_jypix)
    inimg_jypix_regrid=inimg_jypix+'.TMP.regrid'
    imregrid(imagename=inimg_jypix,template=refimg,output=inimg_jypix_regrid,overwrite=True)
    r,f,ef,xx,yy,im =combut.compare_fluxes(inimg_jypix_regrid,refimg,thresh=5.0,maxrad=45,radstep=0.5,doAnnuli=doAnnuli,search_img=search_img)
    ap_flux = {'r':r,'f':f,'ef':ef,'xc':xx,'yc':yy,'inimg':inimg,'refimg':refimg,'metric':'apFlux'}
    if make_pickles:
        imdict = {'im':im,'inimg':inimg,'refimg':refimg,'xc':xx,'yc':yy}
        fh=open(inimg+tag+".apFlux.pkl","wb")
        pickle.dump(ap_flux,fh)
        fh.close()
        # these are quite big but useful for diagnostics and
        #  the odd pretty plot or two-
        #fh=open(inimg+tag+"images.pkl","wb")
        #pickle.dump(imdict,fh)
        #fh.close()
    if clean_up:
        rmtables(inimg_jypix)
        rmtables(inimg_jypix_regrid)
    return ap_flux

###########

# build these up as we go - 
# if a summary was requested, and no result-generating steps are included,
#  assume the file list contains result pickle files-
images_to_assess = []

# now import the model file if needed
if (2 in thesteps or 3 in thesteps):
    model_filename, model_file_ext = os.path.splitext(modelfile)
    if ( model_file_ext == ".fits" or model_file_ext == ".FITS"):
        print( " Importing model FITS file ",modelfile)
        print("  ***assumed to be in Jy/pix***")
        modelimage=do_fits_import(modelfile)
    else:
        print(" Using model image ",modelfile)
        print("  ***assumed to be in Jy/pix***")
        modelimage = modelfile

result_list = []
if ( 4 in thesteps and not(1 in thesteps or 2 in thesteps or 3 in thesteps)):
    for thisFile in files_to_assess:
        fh=open(thisFile,'rb')
        z=pickle.load(fh)
        fh.close()
        result_list.append(z)

# do import if needed
#  build list of image files
mystep = 0
casalog.post("Step "+str(mystep)+" "+step_title[mystep],'INFO')
if (mystep in thesteps):
    for thisFile in files_to_assess:
        thisImage = do_fits_import(thisFile)
        images_to_assess.append(thisImage)
else:
    images_to_assess = files_to_assess

mystep = 1 
casalog.post("Step "+str(mystep)+" "+step_title[mystep],'INFO')
if (mystep in thesteps):
    for thisImage in images_to_assess:
        thisResult = do_total_flux(thisImage,'fluxbox.reg')
        result_list.append(thisResult)
        fh=open(thisImage+".totFlux.pkl","wb")
        pickle.dump(thisResult,fh)
        fh.close()


# do fidelity assessment - save to pkl files
mystep = 2
casalog.post("Step "+str(mystep)+" "+step_title[mystep],'INFO')
if (mystep in thesteps):
    for thisImage in images_to_assess:
        thisResult = do_fidelity(thisImage,modelimage)
        result_list.append(thisResult)
        fh=open(thisImage+".fid.pkl","wb")
        pickle.dump(thisResult,fh)
        fh.close()


# do aperture flux assessment - save to pkl files
mystep = 3
casalog.post("Step "+str(mystep)+" "+step_title[mystep],'INFO')
if False:
    for thisImage in images_to_assess:
        thisResult=do_ap_flux(thisImage,modelimage,search_img=1,doAnnuli=False,tag='-noRing')
        result_list.append(thisResult)
        fh=open(thisImage+".apFlux.pkl","wb")
        pickle.dump(thisResult,fh)
        fh.close()
        
# summarize results
mystep = 4
casalog.post("Step "+str(mystep)+" "+step_title[mystep],'INFO')
if mystep in thesteps:
    print("========= Total Flux ==================")
    vlist = np.array([])
    flist=np.array([])
    for thisResult in result_list:
        if thisResult['metric'] == 'totalFlux':
            if 'flux' in thisResult.keys():
                totalFlux = thisResult['flux']
            else:
                totalFlux = thisResult['sum']
            vlist = np.append(totalFlux,vlist)
            flist=np.append(thisResult['inimg'],flist)
            #print(thisResult['inimg']," ",str(totalFlux))
    si = np.argsort(1.0-np.abs((vlist-trueFlux)/trueFlux))
    si =  si[::-1]
    vlist=vlist[si]
    flist=flist[si]
    for i in range(len(vlist)):
        print(flist[i]," ",vlist[i])
    print("========== Fidelity (F_3) =================")
    vlist=np.array([])
    flist=np.array([])
    for thisResult in result_list:
        if thisResult['metric'] == 'fidelity':
            vlist=np.append(thisResult['f3'],vlist)
            flist=np.append(thisResult['inimg'],flist)
            #print(thisResult['inimg']," ",str(thisResult['f3']))
    si = np.argsort(vlist)
    si =  si[::-1]
    vlist=vlist[si]
    flist=flist[si]
    for i in range(len(vlist)):
        print(flist[i]," ",vlist[i])
    print("========== Ap.Flux  =================")
    vlist=np.array([])
    vlist2=np.array([])
    flist=np.array([])
    for thisResult in result_list:
        if thisResult['metric'] == 'apFlux':
            r = thisResult['r']
            good_ind = np.argwhere(r < 60.0)
            f = thisResult['f'][good_ind]
            mean_f = np.mean(f)
            # RMS of (f-1)
            rms_f = (np.sum( (f-1)**2)/len(f))**0.5
            vlist=np.append(mean_f,vlist)
            vlist2=np.append(rms_f,vlist2)
            flist=np.append(thisResult['inimg'],flist)
            #print(thisResult['inimg']," ",str(mean_f)," ",str(rms_f))
    si = np.argsort(np.abs(1-vlist))
    #si =  si[::-1]
    vlist=vlist[si]
    flist=flist[si]
    vlist2=vlist2[si]
    for i in range(len(vlist)):
        print(flist[i]," ",vlist[i]," ",vlist2[i])
    si=np.argsort(vlist2)
    #si =  si[::-1]
    vlist2=vlist2[si]
    vlist=vlist[si]
    flist=flist[si]
    print(" -=-=-=- ")
    for i in range(len(vlist)):
        print(flist[i]," ",vlist[i]," ",vlist2[i])
    
