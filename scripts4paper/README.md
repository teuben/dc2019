Explain each file. If you want to get an image go to quick_start.md, if you want to understand the steps go to Overview.md, if you are more advanced and want to start playing with the parameters to hone in your data combination go to DC_pars?
General overview.md
X Preparation.md (only once)
Quick_start.md
DC_pars.md – link to Template_pars.py and explain
DC_run.md










# Scripts for the Paper

These should be the steps that allow you to reproduce the
figures in the paper:

1. Ensure your CASA has **astropy** installed
2. Ensure the **analysisUtilities** are installed for your CASA
3. Run configure to be able to run the CASA based scripts
4. Gather the data (see ../data/README_DC2019_data)
5. Execfile DC_script.py to run through your selected data set


   
## 1. - 3. Preparations
Details are given in [Preparation](https://github.com/teuben/dc2019/blob/master/scripts4paper/Preparation.md)
You have to make these adjustments just once.


## 4. Data

Details are in [../data/README_DC2019_data](../data/README_DC2019_data)

This suggests that the data is present in **../data**, physically or via
a symlink.


## 5. DC_script.py, DC_run.py, and IQA_script.py

At each start of a CASA instance you have to call the **DC_locals.py** once to set up your source and destination folders, e.g.

    execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py",globals())

**DC_script.py** is a wrapper that calls the **DC_pars**-file you defined in there and then the combination program **DC_run.py**.

Alternatively, you can call

	execfile("/home/teuben/dc2019/scripts4paper/DC_pars_M100.py", globals()) 
	execfile("/home/teuben/dc2019/scripts4paper/DC_run.py",globals())

An overview of the capabilities of **DC_run.py** is given in [Overview](Overview.md) 
and in more detail in [DC_run](DC_run.md).
A quick start guide is given in	[Quick_start](Quick_start.md).

**DC_run.py** uses the python module **datacomb.py** for preparation and combination 
of the data and the python module **IQA_script.py** for the assessment of the combination products. 
Both modules can be used as a stand-alone.









## whaaat is this about ???

This is a discussion how the DC2019 data should be circulated, and
easily match a CASA tasks API for the different combination techniques
discussed in the paper




## Methods teams

Each method team should provide the way how the data teams should be calling that method:

   * feather - 
   * tp2vis - experimenting with CASA 6
   * sdint - upcoming in CASA 5.7
   * faridani (?) - is also in QAC
   * hybrid (?) - not really easily available, but a promising option

## Data teams

The data will be prepared in a form ready for the different methods API's:

   * M100 (line)
   * Lupus (line)
        - Line data (from workshop) here: https://ftp.astro.umd.edu/pub/teuben/tp2vis/Lup3mms_12CO_tp_7m_12m_nchan10.tgz
        - Images (preliminary combination): https://astrocloud.nrao.edu/s/Np7STzGMMY9fCWz
        - Adele's script here: https://github.com/teuben/dc2019/blob/master/scripts/datacomb2019_outflowsWG.py
   * HI (line)
   * N346(line)
   * skymodel (cont)
        - Script for imaging the individual simulated datasets by Dirk Petry using the hogbom deconvolver https://github.com/teuben/dc2019/blob/master/scripts4paper/scriptForImaging.py
   * ...

The final data will NOT be in github, we will use the UMD ftp server for this. Contact peter to provide
a link so we can make it available to others. Currently this is 
https://ftp.astro.umd.edu/pub/teuben/DC2019/scripts4paper/
but that name may change.


