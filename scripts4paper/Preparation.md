Astropy, analysis utils
What need to do before running everything for the first time
Alternative name (Executing Data Combination)




## astropy  (et al.)

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
	  
to your personal CASA setup (e.g. via ~/.casa/config.py), but making sure there
is no version skew between CASA's python and the one astropy is expecting.

      CASA <1>:    !pip3 install --user astropy

## analysisUtilities

The https://casaguides.nrao.edu/index.php/Analysis_Utilities gives instructions
how to get and install the Analysis Utilities.  Here's our suggested example of 
installing it:

      cd ~/.casa
	  wget ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
	  tar xf analysis_scripts.tar
	  
and add the following lines to your **~/.casa/config.py** script:

      import sys
	  sys.path.append(os.environ['HOME'] + '/.casa/analysis_scripts')
	  import analysisUtils as au
	  import analysisUtils as aU
	  
TBD about the casing.





## Configure

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










## Preparing (new in May 2021)

First an outline of how to use the scripts in this directory and configure local paths:

1) Before using these scripts, you will first need to configure to set the script, data and working directories
that the scripts will use on your local machine, as opposed to the current defaults.
To do this, you need to execute the **configure** script from the scripts4paper directory to set the directories (a) in which you would like to save the output products (--with-s4p-work) and (b) where the data you want to combine is located (--with-s4p-data). For example,

      ./configure  --with-s4p-work=tmp  --with-s4p-data=../data

will place your working files in a tmp directory (which will be created for you) in your current directory and set **../data** to be the
directory where all the input data are located (at least for the DC2019 project). Use the --help argument to find out
what other options might be useful for you. What is listed here are the defaults.

2) The second step will be to pick a parameter file template and change any input parameters for your specific case. First, choose a parameter file from the several templates that are available, for example for the GMC dataset

       cp  DC_pars_GMC.py  DC_pars.py
	   
Then you can change various parameters (see also USER INPUTS below)  in this **DC_pars.py** for your specific case.

3) Set up your CASA environment by executing **DC_locals.py** in your CASA session,

       execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py")

It is best to place your version of this line in your **~/.casa/config.py** file so that this is
automatically done for each CASA session. But see also an alternative approach in the next section.

4) Lastly to do the data combination, from your CASA session exectute **DC_script.py** (which simply calls DC_pars and DC_run):

       execfile("DC_script.py")

which will do the whole data combination as specified by the many USER INPUTS in your **DC_pars.py**



## Alternative Script

If you prefer to be in many directories, and work from those, first configure for a dummy **/tmp** 

	./configure  --with-s4p-data=../data  --with-s4p-work=/tmp
	
and in each the directories you want to work can create a script
**DC_script.py** that reads something like the following:

	execfile("/home/teuben/dc2019/scripts4paper/DC_locals.py",globals())
	execfile("DC_pars.py", globals()) 
	execfile("/home/teuben/dc2019/scripts4paper/DC_run.py",globals())
	
in those directories you can use

	execfile("DC_script.py")
	
Just make sure not to use the **_s4p_work** variable, but define the **pathtoimage** directory as a local folder, e.g. **./**	
