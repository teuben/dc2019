# various python and casa things
#

# the ones likely we use at DC2019
ALL = uvcombine turbustat QAC WidebandSDINT

help:
	@echo Sorry, No help, read the Makefile

all: $(ALL)

#           Only make this when you have the right python
uvcombine:
	git clone https://github.com/keflavich/uvcombine
	(cd uvcombine; python setup.py install)
	pip install image_registration radio_beam reproject spectral_cube

turbustat:
	pip install turbostat

QAC:
	git clone https://github.com/teuben/QAC/

analysis_scripts.tar:
	wget ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar


#       rubbl has some new CASA based tools and interfaces via rust
peel:
	git clone https://github.com/pkgw/rubbl-rxpackage
	git clone https://github.com/pkgw/rubbl

#       See also: https://www.rust-lang.org/tools/install
rust:
	curl https://sh.rustup.rs -sSf | sh

sd2018:
	git clone https://github.com/teuben/sd2018

rica:
	git clone https://gitlab.com/mileslucas/rica

WidebandSDINT:
	git clone https://github.com/urvashirau/WidebandSDINT


#     http://montage.ipac.caltech.edu/
montage: Montage
	(cd Montage; make clean all)

Montage:
	git clone https://github.com/Caltech-IPAC/Montage
