#

ALL = m100 tp2vis qac M51

help:
	@echo Help is in the Makefile

all:	$(ALL)

m100:
	wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz
	wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz
	wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages_5.1.tgz

tp2vis:
	wget http://admit.astro.umd.edu/~teuben/QAC/skymodel.fits    
	wget http://admit.astro.umd.edu/~teuben/QAC/skymodel.ptg

qac:
	wget http://admit.astro.umd.edu/~teuben/QAC/qac_bench5.tar.gz 


M51:    M51ha.fits

M51ha.fits:
	wget https://casaguides.nrao.edu/images/3/3f/M51ha.fits.txt -O M51ha.fits
