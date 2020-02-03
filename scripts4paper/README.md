# Scripts for the Paper

Here we gather (now in a more organized way) the scripts for the paper.


## 

This is a discussion how the DC2019 data should be circulated, and
easily match a CASA tasks API for the different combination techniques
discussed in the paper


## Methods teams

Each method team should provide the way how the data teams should be calling that method:

   * feather - 
   * tp2vis - experimenting with CASA 6
   * sdint - upcoming in CASA 5.7
   * faridani (?) - is also in QAC
   * hybrid (?) - not really easily available

## Data teams

The data will be prepared in a form ready for the different methods API's:

   * M100 (line)
   * Lupus (line)
   * HI (line)
   * N346(line)
   * skymodel (cont)
   * ...

The final data will NOT be in github, we will use the UMD ftp server for this. Contact peter to provide
a link so we can make it available to others. Currently this is http://ftp.astro.umd.edu/pub/teuben/tp2vis
but that name will change.

## Assessment

Once we have a uniform way to combine data across methods and data, the
assessment scripts should be able to compare this matrix.
