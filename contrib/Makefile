# various python and casa things
#

ALL = uvcombine QAC

help:
	@echo Sorry, No help, read the Makefile

all: $(ALL)

#           Only make this when you have the right python
uvcombine:
	git clone https://github.com/keflavich/uvcombine
	(cd uvcombine; python setup.py install)
	pip install image_registration radio_beam reproject spectral_cube

QAC:
	git clone https://github.com/teuben/QAC/


#       rubbl has some new CASA based tools and interfaces via rust
peel:
	git clone https://github.com/pkgw/rubbl-rxpackage
	git clone https://github.com/pkgw/rubbl

#       See also: https://www.rust-lang.org/tools/install
rust:
	curl https://sh.rustup.rs -sSf | sh

sd2018:
	git clone https://github.com/teuben/sd2018
