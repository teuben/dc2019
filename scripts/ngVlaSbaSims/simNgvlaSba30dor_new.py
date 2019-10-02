
#
# sep2019 bsm 
#  -fix vptable
#  -fix integration time ratio
#     

in_map_center="J2000 08h37m27.2s 22d38m44.7s"
phase_center="J2000 08h37m27.2s 22d39m14.7s"

myproj="sba_30dor_new"
skmod="30dor-hires.fits"


# core sim = 1870s
#   *2.2 = 4114sec (SBA total integ goal)
#   23 * 180s = 4140s -- 18x 10sec integs per ea of 23 ptgs
mytotaltime="4140s"
my_cfg = "ngvla-sba-revC_loc"
out_vis = myproj+'/'+myproj+'.'+my_cfg
real_cfg=my_cfg+'.cfg'

this_vp = 'sba_final.tab'
rmtables(this_vp)
# use this to set the beam properly
vp.reset()
vp.setpbairy(telescope='NGVLA',dishdiam=6.0,blockagediam=0.0,maxrad='8.5deg',reffreq='1.0GHz',dopb=True)
vp.saveastable(this_vp)
sba_table = vp.getuserdefault('NGVLA')
vp.setuserdefault(sba_table,'NGVLA','sbaNgvla')

# 
# OR load a pre-existing table-
#vp.reset()
# vp.loadtable() - old versions....
#vp.loadfromtable(this_vp)
#

default("simobserve")
project            =  myproj
indirection=in_map_center
direction=phase_center
skymodel         =  skmod
inbright="0.01Jy/pixel"
incenter="93.0GHz"
inwidth="100MHz"
# have simobserve calculate mosaic pointing locations:
setpointings       =  True
mapsize = "4.5arcmin"
hourangle = "transit"
integration        =  "10s"
obsmode            =  "int"
graphics           =  "both"
thermalnoise       = ""
refdate = "2017/12/03"
antennalist        =  real_cfg
totaltime          =  mytotaltime
simobserve() 

