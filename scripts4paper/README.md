# Scripts for the Paper

These should be the steps that allow you to reproduce the
figures in the paper:

1. Ensure your CASA has **astropy** installed
2. Ensure the **analysisUtilities** are installed for your CASA
3. Gather the data (see ../data/README_DC2019_data)
4. Run configure to be able to run the CASA based scripts
5. Execfile DC_script.py to run through your selected data set
6. Execfile IQA_script.py create our standard assessment tests
   (this might go into DC_scripts.py ?)
   
## 1. astropy  (et al.)

In case your CASA does not have astropy, which you can test by trying

      casa -c "import astropy"
	  
	  
you will need to install it.  Since CASA has it's own python, you can
install it using **pip3** from the CASA prompt (it's cumbersome to
try this from the unix command line):

	  CASA <1>:    !pip3 install astropy

If this results in some kind of permission related problem, you will need to
ask the owner of CASA to do this. Just to be clear, we are using only python3 now,
hence CASA 6. (TBD on exactly what CASA version we require, but this is a moving
target).

**TBD** Unclear at this stage if/how a user based install will work, but
we do need to provide a solution here. Another suggested solution is to add
some kind of

      sys.path.append(pathtoastropy) 
	  
to your personal CASA setup (e.g. via ~/.casa/startup.py), but making sure there
is no version skew between CASA's python and the one astropy is expecting.

      CASA <1>:    !pip3 install --user astropy

## 2. analysisUtilities

The https://casaguides.nrao.edu/index.php/Analysis_Utilities gives instructions
how to get and install the Analysis Utilities.  Here's our suggested example of 
installing it:

      cd ~/.casa
	  wget ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
	  tar xf analysis_scripts.tar
	  
and add the following lines to your **~/.casa/startup.py** script:

      import sys
	  sys.path.append(os.environ['HOME'] + '/.casa/analysis_scripts')
	  import analysisUtils as au
	  import analysisUtils as aU
	  
TBD about the casing.

## 3. Data

Details are in [../data/README_DC2019_data](../data/README_DC2019_data)

This suggests that the data is present in **../data**, physically or via
a symlink.

## 4. Configure

In order to configure your CASA environment for these script, one
suggested solution is the use of the included **configure** script. By
default it will expect your data to be locally present, but the
(shell) command

        ./configure --help

will remind you what to configure.  It will report something like

        execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py")

which you will need to add to your scripts, or better yet, add this to
your **~/.casa/startup.py** file.

NOTE:  MAC users may need to install the needed command **realpath** 
via "brew install coreutils" for configure to work.

## 

This is a discussion how the DC2019 data should be circulated, and
easily match a CASA tasks API for the different combination techniques
discussed in the paper

## 5. DC_script.py

There is currently described in more detail in [DC_script](DC_script.md)

## 6. IQA_script.py

TBD 


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
a link so we can make it available to others. Currently this is https://ftp.astro.umd.edu/pub/teuben/tp2vis
but that name may change.

## Assessment

Once we have a uniform way to combine data across methods and data, the
assessment scripts should be able to compare this matrix.
