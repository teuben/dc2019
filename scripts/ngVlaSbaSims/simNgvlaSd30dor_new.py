 
in_map_center="J2000 08h37m27.2s 22d38m44.7s"
phase_center="J2000 08h37m27.2s 22d39m14.7s"

myproj="sd_30dor_new"
skmod="30dor-hires.fits"
#myproj="sba_ptsrc_new"
#skmod="ptsrc3500ctr.fits"

#
# 821 ptgs @ 5sec each = 4105s
#   --> 1235 @ 5sec = 6175s
mytotaltime="6175s"
my_cfg = "ngvla-sd_loc"
out_vis = myproj+'/'+myproj+'.'+my_cfg
real_cfg=my_cfg+'.cfg'

#
# 23 ptgs @ 100sec each = 2300sec ~ 1.3*1870s
#

# 
# OR
vp.reset()
# vp.loadtable() - old versions....
#


# 
# OR
#vp.reset()
# vp.loadtable() - old versions....
#vp.loadfromtable('sba_new.tab')
#

default("simobserve")
project            =  myproj
indirection=in_map_center
direction=phase_center
#direction=in_map_center
skymodel         =  skmod
#incell="1.0arcsec"
#inbright         = pkpixel
inbright="0.01Jy/pixel"
incenter="93.0GHz"
inwidth="100MHz"
# have simobserve calculate mosaic pointing locations:
setpointings       =  True
mapsize = "6.75arcmin"
hourangle = "transit"
integration        =  "5s"
obsmode            =  "int"
graphics           =  "both"
thermalnoise       = ""
refdate = "2017/12/01"
obsmode='sd'
sdantlist = real_cfg
#antennalist        =  real_cfg
totaltime          =  mytotaltime
thermalnoise       = ""
tau = 0.0
dryrun=False
#dryrun=True
simobserve() 

