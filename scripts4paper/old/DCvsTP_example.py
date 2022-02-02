
# Load scripts
execfile("IQA_scripts.py")
execfile("genmultisps.py")

# Load images
def get_data():
	# Delete all previous images
	os.system('rm -rf *.image')
	
	# TP
	importfits(fitsimage='gmc_120L.sd.image.fits',imagename="TP.image",overwrite=True)
	os.system("rm -rf TP_crop")
	imsubimage(imagename="TP.image", outfile="TP_crop", region='box [ [ 200pix , 200pix] , [1000pix, 1000pix ] ]')
	imrebin(imagename="TP_crop", outfile="TP_final", factor=[20,20,1,1],overwrite=True)

	# IntAlone
	importfits(fitsimage='gmc_120L.alma.all_int-mfs.I.manual-weighted.pbcor.fits',imagename="IntAlone",overwrite=True)
	# SDint
	importfits(fitsimage='sdintimaging-gmc_120L-attempt1.fits',imagename="SDint",overwrite=True)
	# TP2vis
	importfits(fitsimage='sky_tpint_box1.fits',imagename="TP2vis",overwrite=True)
	# Feather
	importfits(fitsimage='gmc_120L_feather.image.fits',imagename="Feather",overwrite=True)
	# hybrid
	importfits(fitsimage='gmc_120L.hybrid.Feather.pbcor.fits',imagename="Hybrid",overwrite=True)	
	# Faridanis
	importfits(fitsimage='/gmc_120L_FaridaniComb_SDF_1.0.fits',imagename="Faridani",overwrite=True)
	

# get data
get_data()

reference = "TP_final"
targets = ["IntAlone","Faridani","Hybrid","Feather","SDint"]
# Mask reference
os.system("rm -rf *_masked")
mask_image(reference+"_subimage",threshold=0.0,relative=False)
CASA2fits(reference+"_subimage_masked")
# Drop axis
for i in targets:
	drop_axis(i)
# get IQA's long process if these are cubes (do it once for all targets)
get_IQA(ref_image = reference+"_subimage_masked",target_image=[str(x) + "_subimage" for x in targets])
# show All IQA's maps
for i in targets:
	show_Apar_map(ref_image = reference+"_subimage_masked",target_image=str(i)+"_subimage")
	plt.savefig("DCvsTP_"+str(i)+"_Apar_map.pdf")
	show_Fidelity_map(ref_image = reference+"_subimage_masked",target_image=str(i)+"_subimage")
	plt.savefig("DCvsTP_"+str(i)+"_Fidelity_map.pdf")

# Compare All results
Compare_Apar_continuum(ref_image = reference+"_subimage_masked",target_image=[str(x) + "_subimage" for x in targets])
plt.savefig("DCvsTP_All_Apar.pdf")

Compare_Fidelity_continuum(ref_image = reference+"_subimage_masked",target_image=[str(x) + "_subimage" for x in targets])
plt.savefig("DCvsTP_Fidelity_Apar.pdf")
