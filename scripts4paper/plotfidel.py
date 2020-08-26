sys.path.append('.') # to pick up IQA_scripts

def plotfidel(target, reference, smooth='2.0arcsec'):
    """
    Obtain Fidelity comparison between 2 images
       A. Hacar, D. Petry - Aug 2020

       reference - fits image
       target - fits image
       smooth - Recomended (circularize the beam of your reference with a small convolution)

    """
    import IQA_scripts as iqa

    importfits(fitsimage=reference, imagename="myreference",overwrite=True) 
    importfits(fitsimage=target, imagename="mytarget",overwrite=True)
    # Convolve the reference (the target will be convolved and regridded later)
    imsmooth(imagename= 'myreference',
             outfile= 'ref_conv',
             kernel='gauss',
             major=smooth,
             minor=smooth,
             pa='0deg',
             targetres=True) # Mask reference
    
    thereference = "ref_conv" # Drop axis
    iqa.drop_axis(thereference)
    iqa.drop_axis(target)# Mask reference
    os.system("rm -rf *_masked")
    iqa.mask_image(thereference+"_subimage",threshold=0.0,relative=False)
    iqa.CASA2fits(thereference+"_subimage_masked")# get IQA's long process if these are cubes (do it once for all targets)
    iqa.get_IQA(ref_image = thereference+"_subimage_masked", target_image=target+"_subimage")# Get Fidelity map
    iqa.show_Fidelity_map(ref_image = thereference+"_subimage_masked", target_image=target+"_subimage")

    return
