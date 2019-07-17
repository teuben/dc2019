# various python and casa things
#

ALL = uvcombine QAC

help:
	@echo Sorry, No help, read the Makefile

all: $(ALL)

uvcombine:
	git clone https://github.com/keflavich/uvcombine
	(cd uvcombine; python setup.py install)
	pip install image_registration radio_beam reproject spectral_cube

QAC:
	git clone https://github.com/teuben/QAC/
