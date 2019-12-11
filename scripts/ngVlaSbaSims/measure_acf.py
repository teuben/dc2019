
from taskinit import *

# casa -c measure_acf.py runs the "main" routine at the end
#   you can also use the function measure_acf_mc() within CASA 
#   directly.

def measure_acf_mc(inimg,thetamin=0,thetamax=100,niter=10000):
"""
Monte carlo estimate of the angular correlation function of an input CASA image
(niter per angular bin). thetamin and thetamax are in pixels. 
Returns the ACF and corresponding angule values (again in pixels).

v1 dec2019 brian mason (nrao)
"""
    # read an image
    ia=iatool()
    ia.open(inimg)
    # convert it to a numpy array
    imvals=np.squeeze(ia.getchunk())

    print imvals.shape

    nvals = thetamax-thetamin+1
    acf = np.zeros(nvals)
    theta = np.arange(nvals) + thetamin

    # filter out NaNs for calculating mean and SD
    imvals2 = imvals[~np.isnan(imvals)]
    pix_mean = imvals2.mean()
    pix_sd = np.std(imvals2)

    print pix_mean, pix_sd

    # loop over theta (distance) values
    for i in range(nvals):
        # set i_min, i_max
        imin = theta[i]+1
        imax = imvals.shape[0]-theta[i]-1
        jmin = theta[i]+1
        jmax = imvals.shape[1]-theta[i]-1
        #print i,theta[i],imin,imax,jmin,jmax
        # draw niter random samples of i,j,theta
        ivals = np.array(np.round(np.random.uniform(imin,imax,niter)),dtype=np.int)
        jvals = np.array(np.round(np.random.uniform(jmin,jmax,niter)),dtype=np.int)
        phivals = np.random.uniform(0,2*3.14159265358979,niter)
        # calculate i and j for the other pixel
        i2 = ivals + np.array(np.round(theta[i] * np.cos(phivals)),dtype=np.int)
        j2 = jvals + np.array(np.round(theta[i] * np.sin(phivals)),dtype=np.int)
        #print ivals.shape,jvals.shape,i2.shape,j2.shape
        # filter out NaNs (mask hits) - 
        these_values = (imvals[ivals,jvals] - pix_mean)*(imvals[i2,j2] - pix_mean)
        these_values = these_values[~np.isnan(these_values)]
        this_niter = np.prod(these_values.shape)
        acf[i] = np.sum(these_values ) / (this_niter * pix_sd**2)

    return acf,theta

if __name__ == "__main__":

    # parameters appropriate for ngVLA/SBA simulations
    #  (pixel sizes in arcseconds)
    core_pix = 0.25
    sba_pix = 1.25
    tp_pix = 4.3
    sky_pix = 0.216

    # input image 
    skymod = "ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.skymodel.flat"
    # input image (smoothed to SBA res.)
    sba_skymod = 'sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.skymodel.TMP.smo.TMP.regrid'

    # TP: sd_30dor_new/sd...sf7.tp.fixed
    tp_image = "sd_30dor_new/sd_30dor_new.ngvla-sd_loc.sd.sf7.tp.fixed"

    # core: autoDev2.final 
    core_image = "ngvla_30dor/ngvla_30dor.ngvla-core-revC_loc.autoDev2.final.image"

    # joint: joint_30dor.ngvla.revC_new.autoDev5
    joint_image = "joint_30dor.ngvla.revC_new.autoDev5.image"
    joint_sdmod_image = "joint_30dor.ngvla.revC_new.sdmod.autoDev5.image"
    joint_sdmod_feath_image = "joint_30dor.ngvla.revC_new.sdmod.autoDev5.image.feather.pbcor"

    # SBA: autoDev5.final.image
    sba_image = "sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.image"

    # SBAfeathered:
    sba_feath_image = "sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.image.feather.pbcor"
    # SBAsdmod: autoDev5.final.sdmod
    sba_sdmod_image = "sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.sdmod.image"
    # SBAsdmodFeathered: autoDev5.final.sdmod.feather.pbcor
    sba_sdmod_feath_image = "sba_30dor_new/sba_30dor_new.ngvla-sba-revC_loc.autoDev5.final.sdmod.image.feather.pbcor"

    acf_sky,theta_sky = measure_acf_mc(skymod,thetamax=417)
    acf_sba_sky,theta_sba_sky = measure_acf_mc(sba_skymod,thetamax=75)
    acf_tp, theta_tp = measure_acf_mc(tp_image,thetamax=21)
 
    acf_core, theta_core = measure_acf_mc(core_image,thetamax=360)
    acf_joint, theta_joint = measure_acf_mc(joint_image,thetamax=360)
    acf_joint_sdmod, theta_joint_sdmod = measure_acf_mc(joint_sdmod_image,thetamax=360)
    acf_joint_sdmod_feath, theta_joint_sdmod_feath = measure_acf_mc(joint_sdmod_feath_image,thetamax=360)

    acf_sba, theta_sba = measure_acf_mc(sba_image,thetamax=75)
    acf_sba_feath, theta_sba_feath = measure_acf_mc(sba_feath_image,thetamax=75)
    acf_sba_sdmod, theta_sba_sdmod = measure_acf_mc(sba_sdmod_image,thetamax=75)
    acf_sba_sdmod_feath, theta_sba_sdmod_feath = measure_acf_mc(sba_sdmod_feath_image,thetamax=75)


    acf_core, theta_core = measure_acf_mc(core_image,thetamax=360)

    # ngVLA Core and ngVLA SBA 
    #  beam FWHM and LAS, in arcsec.
    #  LAS is lambda/b_min, so is the absolute
    #  upper limit on LAS not the actual practical LAS.
    bm_core = 1.78
    bm_sba = 11.3
    las_core = 19.0
    las_sba = 55.0

    pl.xlabel('arcseconds')
    pl.ylabel('angular correl. fcn.')
    pl.plot(theta_sky*sky_pix,acf_sky,label='sky')
    pl.plot(theta_sba_sky*sba_pix,acf_sba_sky,label='sky(lowres)')
    pl.plot(theta_tp*tp_pix,acf_tp,label='TP')
    pl.plot(theta_core*core_pix,acf_core,label='core')
    pl.plot(theta_sba*sba_pix, acf_sba,label='sba')
    pl.legend()
    pl.plot([bm_core,bm_core],[0,1.4],'b:')
    pl.plot([bm_sba,bm_sba],[0,1.4],'r:')
    pl.plot([las_core,las_core],[0,1.4],'b-.')
    pl.plot([las_sba,las_sba],[0,1.4],'r-.')
    pl.text(0,-0.05,'core bm',color='b')
    pl.text(10,-0.15,'SBA bm',color='r')
    pl.text(20,-0.05,'core LAS',color='b')
    pl.text(55,-0.15,'SBA LAS',color='r')
    pl.savefig('acf_fig1.png')

    pl.close()

    pl.xlabel('arcseconds')
    pl.ylabel('angular correl. fcn.')
    pl.plot(theta_sky*sky_pix,acf_sky,label='sky')
    pl.plot(theta_sba*sba_pix, acf_sba,label='sba')
    pl.plot(theta_sba_sdmod*sba_pix, acf_sba_sdmod,label='sba-SDmod')
    pl.plot(theta_sba_sdmod_feath*sba_pix, acf_sba_sdmod_feath,label='sba-SDmod-feather')
    pl.legend()
    pl.plot([bm_sba,bm_sba],[0,1.4],'r:')
    pl.plot([las_sba,las_sba],[0,1.4],'r-.')
    pl.text(10,-0.15,'SBA bm',color='r')
    pl.text(55,-0.15,'SBA LAS',color='r')
    pl.savefig('acf_fig2.png')

    pl.close()

    pl.xlabel('arcseconds')
    pl.ylabel('angular correl. fcn.')
    pl.plot(theta_sky*sky_pix,acf_sky,label='sky')
    pl.plot(theta_joint*core_pix,acf_joint,label='Joint(core+SBA)')
    pl.plot(theta_joint_sdmod*core_pix,acf_joint_sdmod,label='Joint-SDmod')
    pl.plot(theta_joint_sdmod_feath*core_pix,acf_joint_sdmod_feath,label='Joint-SDmod-feather')
    pl.legend()
    pl.plot([bm_core,bm_core],[0,1.4],'b:')
    pl.plot([las_core,las_core],[0,1.4],'b-.')
    pl.text(0,-0.05,'core bm',color='b')
    pl.text(20,-0.05,'core LAS',color='b')
    pl.savefig('acf_fig2b.png')


