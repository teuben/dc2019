# This is a script to make fidelity vs model flux plot
# Make sure that you have model and output image with the same beam size! 

import matplotlib.pyplot as plt
import glob

project = 'm51c'

execfile('%s.param.py'%project)

### Plotting results
os.chdir(project)

if len(config) == 1:
    fidFile = '%s.%s.feather.fidelity'%(project,config[0])
    outFile = '%s.%s.feather.image'%(project,config[0])
    pbFile = '%s.%s.flux'%(project,config[0])
else:
    concatvis = project+'.concat'
    fidFile = '%s.feather.fidelity'%concatvis
    outFile = '%s.feather.image'%concatvis
    pbFile = '%s.flux'%concatvis

isThere = glob.glob(fidFile)
if not isThere:
    concatvis = project+'.concat'
    fidFile = '%s.feather.fidelity'%concatvis
    outFile = '%s.feather.image'%concatvis
    pbFile = '%s.flux'%concatvis
    

## To identify input image
inFiles = glob.glob('%s.*.regrid.conv'%project)
inFile = ''
outbeam = imhead(fidFile)['restoringbeam']
for f in inFiles:
    inbeam = imhead(f)['restoringbeam']
    if inbeam == outbeam:
        inFile = f
if not inFile:
    "####  No beam-matched image found... "
    sys.exit()
    
imsize = imhead(fidFile)['shape']    
box = '0,0,%s,%s'%(str(imsize[0]-1),str(imsize[1]-1))

fidData = imval( fidFile, box=box)['data']
imgData = imval( inFile, box=box)['data']
pbData = imval( pbFile, box=box)['data']

# RMS estimate with simple sigma clipping 
niter = 5
data = imgData
# Initialize 
rms = 0
med = np.max(data)
for i in range(niter):
    nonzero = data > 1e-33
    noise = data < (med+3*rms)
    med = np.median( data[nonzero*noise] )
    rms = np.std( data[nonzero*noise])


 ## linear fit
maxSN = np.max(imgData)/rms
good = (imgData > (med+maxSN*rms/4))
xx = imgData[good]
yy = fidData[good]
coeff = np.polyfit(xx, yy, 1)
print coeff


# Plotting     
doPlot = 1
if doPlot:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(project)
    ax.set_xlabel("Flux [Jy/pix]")
    ax.set_ylabel("Fidelity")

    signal = (imgData > (med+3*rms)) * (pbData > 0.2)
    noise =  (imgData < (med+3*rms)) * (pbData > 0.2)
    ax.plot(imgData[signal] ,fidData[signal],".")

    xline = [0,np.max(imgData)*1.1]
    yline = [coeff[1], xline[1]*coeff[0]+coeff[1]]

    plt.ylim(0,250)
#    ax.plot(xline, yline)
        
    plt.show()
    plt.savefig("%s.fidelity-flux.png"%project)


os.chdir('../')
