# Scripts for the Paper

These should be the steps that allow you to reproduce the
figures in the paper:

0. Ensure your CASA has astropy installed
1. Gather the data (see ../data/README_DC2019_data)
2. Run configure to be able to run the casa based scripts
3. Run DC_script.py to run through your selected data set
4. Run IQA_script.py create our standard assessment tests
   (this might go into DC_scripts.py ?)
   
## 0. astropy  (et al.)

In case your CASA does not have astropy, which you can test by trying

      casa -c "import astropy"
	  
	  
you will need to install it.  Since casa has it's own python, you can
install it using **pip3** from the casa prompt (it's cumbersome to
try this from the unix command line):

	  CASA <1>:    !pip3 install astropy

If this results in some kind of permission related problem, you will need to
ask the owner of CASA to do this. Just to be clear, we are using only python3 now,
hence CASA 6.2 and above.

**TBD** Unclear at this stage if/how a user based install will work, but
we do need to provide a solution here.

## 1. Data

## 2. Configure

In order to configure your casa environment for these script, one
suggested solution is the use of the included **configure** script. By
default it will expect your data to be locally present, but the
command

        ./configure --help

will remind you what to configure.  It will report something like

        execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py")

which you will need to add to your scripts, or better yet, addd this to
your ~/.casa/init.py (CASA5) or ~/.casa/startup.py (CASA6).

NOTE:  MAC users may need to install the needed command **realpath** via "brew install coreutils"

## 

This is a discussion how the DC2019 data should be circulated, and
easily match a CASA tasks API for the different combination techniques
discussed in the paper

## 3. DC_script.py

There is currently in [DC_script](DC_script.md)

## 4. IQA_scripts.py

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
        - Line data (from workshop) here: ftp://ftp.astro.umd.edu/pub/teuben/tp2vis/Lup3mms_12CO_tp_7m_12m_nchan10.tgz
        - Images (preliminary combination): https://astrocloud.nrao.edu/s/Np7STzGMMY9fCWz
        - Adele's script here: https://github.com/teuben/dc2019/blob/master/scripts/datacomb2019_outflowsWG.py
   * HI (line)
   * N346(line)
   * skymodel (cont)
        - Script for imaging the individual simulated datasets by Dirk Petry using the hogbom deconvolver https://github.com/teuben/dc2019/blob/master/scripts4paper/scriptForImaging.py
   * ...

The final data will NOT be in github, we will use the UMD ftp server for this. Contact peter to provide
a link so we can make it available to others. Currently this is http://ftp.astro.umd.edu/pub/teuben/tp2vis
but that name will change.

## Assessment

Once we have a uniform way to combine data across methods and data, the
assessment scripts should be able to compare this matrix.
