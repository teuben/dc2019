#  https://casaguides.nrao.edu/index.php/M100_Band3_Combine_5.4
#
#  The original M100 data, as described on the casaguide, are rather big.
#  During various workshops we trim these down to a more manageable 70 channel 5km/s data set
#  But you can edit this file to trim it down even more.


#    wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz
#    wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz
#    wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages_4.3.tgz
#
#    tar xvfz M100_Band3_12m_CalibratedData.tgz
#    tar xvfz M100_Band3_7m_CalibratedData.tgz
#    tar xvfz M100_Band3_ACA_ReferenceImages_4.3.tgz
#
#    mv M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms .
#    mv M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms .
#    mv M100_Band3_ACA_ReferenceImages/M100_TP_CO_cube.bl.image .


#   we start with this
ms1 = 'M100_Band3_12m_CalibratedData.ms'
ms2 = 'M100_Band3_7m_CalibratedData.ms'
tp1 = 'M100_TP_CO_cube.spw3.image.bl'

#   this is the spectral axis we want, given in the LSRK frame
line = {"restfreq":'115.271202GHz','start':'1400km/s', 'width':'5km/s','nchan':70}

#   and want these datasets

ms1q = 'M100_aver_12.ms'
ms2q = 'M100_aver_7.ms'
tp1q = 'M100_TP_CO_cube.bl.image'

#   to add to the challenge, the TP map has the highest frequency first, the MS files are lowest frequency first
#   generally tclean, if used with specmode='cube', does not like to combine these.


if True:
    split(vis='M100_Band3_12m_CalibratedData.ms',outputvis='M100_12m_CO.ms',spw='0',field='M100',datacolumn='data',keepflags=False)
    split(vis='M100_Band3_7m_CalibratedData.ms',outputvis='M100_7m_CO.ms',spw='3,5',field='M100',datacolumn='data',keepflags=False)

imtrans('M100_TP_CO_cube.bl.image','M100_TP_CO_cube.blr.image','012-3')
