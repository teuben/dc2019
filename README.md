# *Improving Image Fidelity on Astronomical Data: Radio Interferometer and Single-Dish Data Combination* (DC2019)

This was the material we used for the
[DC2019](https://www.lorentzcenter.nl/lc/web/2019/1179/info.php3?wsid=1179&venue=Oort)
workshop. We planned to have all scripts, code, documentation, and presentations here,
but our data are typically large and we will supply URLs from where you can download them
from. Some scripts were taking from other projects, and may not be maintained here so well.

## Combination Techniques

We will probably try out a few techniques:

   * [feather](https://casa.nrao.edu/casadocs/casa-5.4.1/image-combination/feather) [talk by Ginsburg](https://keflavich.github.io/talks/FeatheringPresentation/FeatheringPresentation.slides.html?transition=fast); see also the [uvcombine](https://github.com/radio-astro-tools/uvcombine/) package
   * [tp2vis](https://github.com/tp2vis/distribute) [talk by Teuben]
   * [hybrid](https://sites.google.com/site/jenskauffmann/research-notes/adding-zero-spa) [talk by Kauffmann]
   * [sdint](https://github.com/urvashirau/WidebandSDINT) [talk by Rau]
   * ...

## Software needed

Since we are going to be CASA based this week, we only support Linux and Mac.
WSL on Window10 is currently too slow to be useful (but hasn't been tested).

   * CASA: https://casa.nrao.edu/casa_obtaining.shtml. The current release is 5.5, but 5.6 was just released. We have helper scripts
     in [contrib](contrib). 
      * [https://casa.nrao.edu/casadocs/casa-5.6.0/introduction/release-notes-560](5.6.0 Release notes)
      * [https://casa.nrao.edu/casadocs/casa-5.6.0/introduction/release-notes-560[(5.5.0 Release notes)
      * [CASA 6](https://science.nrao.edu/enews/casa_008/) can also be installed via pip wheels. We also have a helper script.
   * QAC (this will also install TP2VIS, SD2VIS, SDINT and AU)
   * TP2VIS (comes with QAC)
   * SD2VIS (optional, can come with QAC)
   * AU (comes with QAC)
   * WidebandSDINT (comes with QAC) - as of July 2020 CASA 5.7 has this included as sdintimaging()
   * 

and recommended software

   * DS9: http://ds9.si.edu/site/Home.html (the XPA tools can also be very useful)
   * vanilla python3 via miniconda or anaconda (an install script is available in dc2019, but you may also be able to install modules
     in CASA's python)
   * a spectral cube fits viewer (ds9, carta, casaviewer, QFitsView, glue). See also https://fits.gsfc.nasa.gov/fits_viewer.html

## Data needed

see [README_DC2018_data](data/README_DC2019_data) for more details

We should have a USB and portable HDD during the meeting for copying large datasets, but
we strongly recommend you come prepared with the data loaded on your laptop. We hope to have an estimate for the minimum amount
of space you will need for the experiments, and/or bring your own spare external HDD. It will probably be closer to 100GB than 10GB.

## Installation

See the [INSTALL](INSTALL) file for some current guidelines.
