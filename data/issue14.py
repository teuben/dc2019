#  see also https://github.com/teuben/dc2019/issues/14

f0 = 'gmc_2L.sd.image.fits'
f0 = 'gmc_120L.sd.image.fits'                           # 6034.647 Jy
f1 = 'skymodel-b.fits'
beam = 55.0       # -26  to +83                           6417.9334
beam = 56.0       # -50  to +41 in 3 bands                6403.62898
beam = 56.7       # used in sky4.py -79 to +10            6393.446
beam = 57.06      # -80 to -12 in 3 horizontal bands      6388.154
beam = 58.0       # -120 to -40 in 3 horizontal bands     6374.1653

beam = 57.06




qac_import(f0,'otf0.im')

qac_import(f1,'otf1.im')
imsmooth(imagename='otf1.im',
             kernel='gauss',
             major='%sarcsec'%beam,
             minor='%sarcsec'%beam,
             pa='0deg',
             outfile='otf2.im',
             overwrite=True)

imregrid('otf2.im','otf0.im','otf3.im', overwrite=True)
qac_math('diff1','otf0.im','-','otf3.im')

print("beam=",beam)

region1  = 'box[[12h00m07.009s,-35d01m26.082s],[11h59m52.990s,-34d58m33.946s]],coord=J2000'
qac_stats('otf3.im')
qac_stats('otf3.im',region=region1)
qac_stats('otf0.im')
qac_stats('otf0.im',region=region1)


# imtrans('otf2.im','otf3.im',order='0132')
