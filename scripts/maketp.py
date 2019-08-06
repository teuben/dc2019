#   map TP autocorrelating on-the-fly mapping to a TP cube
#
#   in CASA execute this with execfile('maketp.py')
#   or you can run it from the terminal:
#         casa -c maketp.py
#   this script takes about 10'
#
#
#   Original author:     Thomas Stanke            6-aug-2019
#   Adapted for DC2019   Peter Teuben
#



import numpy as np
import os
import glob
import pyfits
import shutil

# 
# The command
#       tar xf region3by3-TP-leiden.tar
# will produce 8 MS_BL files, the calibrated single dish data in MS autocorrelation format.
#


msNames = ['uid___A002_Xd0dc33_X408.ms_bl',
           'uid___A002_Xd0e450_X2e32.ms_bl',
           'uid___A002_Xd21a3a_X2873.ms_bl',
           'uid___A002_Xd21a3a_X2d40.ms_bl',
           'uid___A002_Xd23397_Xc689.ms_bl',
           'uid___A002_Xd248b5_X2f67.ms_bl',
           'uid___A002_Xd257e5_Xa540.ms_bl',
           'uid___A002_Xd257e5_Xaf48.ms_bl',
           ]

#  takes about 10 mins
sdimaging(infiles = msNames,
          field = 'NGC_346_1',
          spw = '23',
          mode = 'frequency', nchan = 7, start = '230.405GHz', width = '3.333MHz', restfreq = '230.5380GHz',
          outframe = 'LSRK',
          gridfunction = 'SF',
          convsupport = 6,
          phasecenter = 'J2000 00:59:30 -72.10.30',
          imsize = [200],
          cell = '8arcsec',
          overwrite = True,
          outfile = 'all.cube.spw23-forLeiden.image')

