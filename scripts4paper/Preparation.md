# Necessary Preparation to Run Data Combination
Follow these instructions to get your environment setup to run data combination (`DC_script.py`). Theoretically you will only have to do these things once. First you will ensure that you have the required software and packages (CASA, astropy, analysisUtils) then configure your CASA environment.

## Step 1: Requirements
* CASA 6
* astropy within your CASA installation
* analysisUtils

### astropy
You can test if your CASA installation has astropy by
```bash
casa -c "import astropy"
```
If this does not work, you will need to manually install it.  Since CASA has it's own python, you can
install it using `pip3` from the CASA prompt (it's cumbersome to try this from the unix command line):
```plain
CASA <1>: !pip3 install astropy
```
If this results in some kind of permission related problem, you will need to ask the owner of CASA to do this. Just to be clear, we are using only python3 now, hence CASA 6. 

**TBD** Unclear at this stage if/how a user based install will work, but we do need to provide a solution here. Another suggested solution is to add some kind of
```plain
sys.path.append(pathtoastropy)
```
to your personal CASA setup (e.g. via `~/.casa/config.py`), but making sure there is no version skew between CASA's python and the one astropy is expecting.
```plain
CASA <1>: !pip3 install --user astropy
```
### analysisUtils
This [CASA Guide](https://casaguides.nrao.edu/index.php/Analysis_Utilities) gives instructions on how to download and install analysisUtils. Here's our suggested example of installing it:
```bash
cd ~/.casa
wget ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
tar -xf analysis_scripts.tar
```
Then add the following lines to your `~/.casa/config.py` script:
```plain
import sys
sys.path.append(os.environ['HOME'] + '/.casa/analysis_scripts')
import analysisUtils as au
import analysisUtils as aU
```
TBD: casing

## Step 2: Configure
Before running `DC_script.py`, you will first need configure your CASA environment to set the script, data, and working directories that the scripts will use on your local machine, as opposed to the current defaults (it will expect your data to be locally present). One suggested solution is the use of the included `configure`, you need to execute the `configure` script from the `scripts4paper` directory to set the directories
(a) in which you would like to save the output products (`--with-s4p-work`) and
(b) where the data you want to combine is located (`--with-s4p-data`).
We recommend putting all datasets in one directory and all output files and images in another then you only have to run `configure` once. For example, let's say you plan to work with the M100 and GMC-c example datasets. You could have one directory for the input data `/users/user/datacomb/data/` where you will have a M100 directory and a GMC-c directory. And another for output files and images, `/users/user/datacomb/output/` where you will have a M100 folder and a GMC-c folder.

Then your configure statement would be
```bash
./configure --with-s4p-work=/users/user/datacomb/output --with-s4p-data=/users/user/datacomb/data
```

will place your working files in `/users/user/datacomb/output/` and set `/users/user/datacomb/data/` to be the
directory where all the input data are located (at least for the DC2019 project). Use the --help argument to find out
what other options might be useful for you.

`configure` will produce a file called `DC_locals.py` in the directory that you run `configure` in - this should be the directory where `DC_script.py` is. 


NOTE:  MAC users may need to install the needed command `realpath` via "brew install coreutils" for configure to work.

## Step 3: (Optional but Recommended) Permanently Set Up Your CASA Environment
We recommend to place your version of this the following line in your `~/.casa/config.py` file so that this is
automatically done for each CASA session.

```python
execfile("/users/user/dc2019/scripts4paper/DC_locals.py")
```

where the path should be the path to where `DC_locals.py` is on your machine.