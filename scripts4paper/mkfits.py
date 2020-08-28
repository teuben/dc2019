import glob

imname = 'pointSrcGauss' # 

fluxPt = 1. 
fluxGauss = 100.
gaussFWHM = '10arcsec'

direction = "J2000 12h00m00.0s -35d00m0.0s"


### Point source setting 
os.system('rm -rf point.cl')
cl.done()

cl.addcomponent(dir=direction, flux=fluxGauss, fluxunit='Jy',freq='115.0GHz', shape="Gaussian", majoraxis=gaussFWHM,minoraxis=gaussFWHM, positionangle='0deg')
cl.addcomponent(dir=direction, flux=fluxPt, fluxunit='Jy', freq='115.0GHz', shape="point")

ia.fromshape("%s.im"%imname,[4096,4096,1,1],overwrite=True)
cs=ia.coordsys()
cs.setunits(['rad','rad','','Hz'])
cell_rad=qa.convert(qa.quantity("0.05arcsec"),"rad")['value']
cs.setincrement([-cell_rad,cell_rad],'direction')
cs.setreferencevalue([qa.convert("12h",'rad')['value'],
                      qa.convert("-35deg",'rad')['value']],type="direction")
cs.setreferencevalue("115GHz",'spectral')
cs.setincrement('2GHz','spectral')
ia.setcoordsys(cs.torecord())
ia.setbrightnessunit("Jy/pixel")
ia.modify(cl.torecord(),subtract=False)

os.system('rm -rf %s.fits'%imname)
exportfits(imagename='%s.im'%imname,fitsimage='%s.fits'%imname,
                overwrite=True)
cl.done()


# Smoothing with a gaussian kernel
mybeam = {'major': '0.5arcsec', 'minor': '0.5arcsec', 'pa': '0deg'}
model = '%s.fits' %imname
outfile = '%s_05sec.image'% imname
os.system('rm -rf '+outfile)
imsmooth( imagename=model, kernel='gauss', beam=mybeam, outfile=outfile)


# Export fits 
outfits = outfile.replace('.image','.fits')
os.system('rm -rf '+outfits)
exportfits(imagename=outfile, fitsimage=outfits)
