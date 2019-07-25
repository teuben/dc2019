# *Improving Image Fidelity on Astronomical Data: Radio Interferometer and Single-Dish Data Combination* (DC2019)

This is the material for the
[DC2019](https://www.lorentzcenter.nl/lc/web/2019/1179/info.php3?wsid=1179&venue=Oort)
workshop. We plan to have all scripts, code, documentation, and presentations here,
but our data are typically large and we will supply URLs from where you can download them
from.

## Combination Techniques

We will probably try out a few techniques:

   * [feather](https://casa.nrao.edu/casadocs/casa-5.4.1/image-combination/feather) [talk by Ginsburg]
   * [tp2vis](https://github.com/tp2vis/distribute) [talk by Teuben]
   * [hybrid](https://sites.google.com/site/jenskauffmann/research-notes/adding-zero-spa) [talk by Kauffmann]
   * ...

## Software needed

Since we are going to be CASA based this week, we only support Linux and Mac.
WSL on Window10 is currently too slow to be useful (but hasn't been tested).

   * CASA: https://casa.nrao.edu/casa_obtaining.shtml. The current release is 5.5.0. We 
   * QAC (this will also install TP2VIS, SD2VIS, and AU)
   * TP2VIS (comes with QAC)
   * SD2VIS (optional, can come with QAC)
   * AU (comes with QAC)

and recommended software

   * DS9: http://ds9.si.edu/site/Home.html (the XPA tools can also be very useful)
   * vanilla python3 (or 2) via miniconda or anaconda (an install script is available here)
   * a spectral cube fits viewer (ds9, carta, casaviewer, QFitsView). See also https://fits.gsfc.nasa.gov/fits_viewer.html

## Data needed

see [README_DC2018_data](data/README_DC2019_data) for more details

We should have a USB and portable HDD during the meeting for copying large datasets, but
we strongly recommend you come prepared with the data loaded on your laptop.

## Installation

See the [INSTALL](install) file for some current guidelines.
