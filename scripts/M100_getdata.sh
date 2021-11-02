#  see also https://casaguides.nrao.edu/index.php?title=M100_Band3

wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz
wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz
wget https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages_5.1.tgz

tar xvfz M100_Band3_12m_CalibratedData.tgz
tar xvfz M100_Band3_7m_CalibratedData.tgz
tar xvfz M100_Band3_ACA_ReferenceImages_5.1.tgz

mv M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms   .
mv M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms     .
mv M100_Band3_ACA_ReferenceImages_5.1/M100_TP_CO_cube.spw3.image.bl .

