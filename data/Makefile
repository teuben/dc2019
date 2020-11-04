#
# Explanations of the datasets are given in README_DC2019_data
# these are some convenient shortcuts to get you going a little quicker

#            wget, wgetc, ncftpget, curl, ....
WGET = wget

URL1 = http://www.astro.umd.edu
URL2 = http://admit.astro.umd.edu
URL3 = http://ftp.astro.umd.edu

ALL = m100 tp2vis qac M51

help:
	@echo Help is in the Makefile and much more in README_DC2019_data

all:	$(ALL)

# the big bulky 25GB, you should not need it, use M100
M100_raw:
	$(WGET) https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz
	$(WGET) https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz
	$(WGET) https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages_5.1.tgz

# this creates:  M100_aver_12.ms  M100_aver_7.ms  M100_TP_CO_cube.bl.image
M100: qac_bench5.tar.gz

qac_bench5.tar.gz:
	$(WGET) $(URL1)/~teuben/QAC/qac_bench5.tar.gz
	tar zxf qac_bench5.tar.gz

skymodel-b.fits:
	$(WGET) $(URL1)/~teuben/QAC/skymodel-b.fits

skymodel-c.fits:
	$(WGET) $(URL1)/~teuben/QAC/skymodel-c.fits

skymodel-b.sim.tar:
	$(WGET) $(URL3)/pub/teuben/DC2019/skymodel-b.sim.tar

skymodel-c.sim.tar:
	$(WGET) $(URL3)/pub/teuben/DC2019/skymodel-c.sim.tar



#
tp2vis:
	$(WGET) $(URL1)/~teuben/QAC/skymodel.fits    
	$(WGET) $(URL1)/~teuben/QAC/skymodel.ptg

qac:  M100

M51:    M51ha.fits

M51ha.fits:
	$(WGET) https://casaguides.nrao.edu/images/3/3f/M51ha.fits.txt -O M51ha.fits


