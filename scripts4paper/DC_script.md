# DC_script

The **DC_script** uses the **datacomb** module to conviniently combine 
your data. The DC_script's goal is to provide a homogeneous input to all 
combination methods (e.g. clean parameters) and a homogeneous output 
style.

It offers 6 different actions to be selected via the 'thesteps' variable:

      0: 'Concat',
      1: 'Clean for Feather/Faridani'
      1: 'Feather', 
      2: 'Faridani short spacings combination (SSC)',
      3: 'Hybrid (startmodel clean + Feather)',
      4: 'SDINT',
      5: 'TP2VIS'

The naming scheme of the output images is the following

      imname = imbase + cleansetup + combisetup

imbase     - a basename you define
cleansetup - defined by your tclean parameter choice
combisetup - defined by your combination method and parameter choice



things to check:
- compare the tclean inputs
- sdint: switch interactive -->  parameter setup differs at interactive, 
usemask, cycleniter + additional paramterers not present in the 
corresponding other version



## Paths to the input and output files and for concatenation of several 
ms - data sets

      pathtoconcat = 'path-to-ms-datasets-(array-configs)-and-SD-image-to-combine'   
      # path to the folder with the files to be concatenated
      
      pathtoimage  = 'path-to-your-products'                         
      # path to the folder where to put the combination and image results
      
      concatms     = pathtoimage + 'skymodel-b_120L.alma.all_int-weighted.ms'       
      # path and name of concatenated file (e.g. blabla.ms)

The list of files to concatenate is defined in this section, too, 
as well as the visweighting.


## files and names used by the combination methods 
      
      vis       = concatms 
      sdimage   = pathtoconcat + 'gmc_120L.sd.image'
      imbase    = pathtoimage + 'skymodel-b_120L'        # path + image base name


## setup of the clean parameters

With this section, we set up the clean parameters common for all tclean 
instances used in the combination methods including SDINT.

       general_tclean_param  - present in all methods
       special_tclean_param  - only given in runtclean and runWSM
                                -> to be merged into general_tclean_param
       sdint_tclean_param    - only given in runsdintimg

For these, we have to discuss which parameters should be defined in the 
backgroud and which should be user defined
       
Furthermore, we can generate a meaningful file name "infix" to attach 
to the imbase, reflecting the relevant clean properties (you define). 
Currently, mode, mscale, inter, and nit define the infix name: e.g.

       mode   = 'mfs'    # 'mfs' or 'cube'
       mscale = 'HB'     # 'MS' (multiscale) or 'HB' (hogbom; MTMFS in SDINT!)) 
       inter  = 'AM'     # 'man' (manual), 'AM' ('auto-multithresh') or 'PB' (primary beam - not yet implemented)
       nit = 0           # max = 9.9 * 10**9 

       cleansetup = '.'+ mscale +'_'+ inter + '_n%.1e' %(nit)
       cleansetup = cleansetup.replace("+0","")

gives us 
 
       cleansetup = '.HB_AM_n0.0e0'

Further parameters like usemask, interactive, and multiscale depend on 
the choice of the mscale and inter. 
This infix-definition could be made more flexible.
Maybe introduce a loop over some clean parameters like niter.



## SD scaling in combination

Here we can list multiple scaling factors per scaling parameter 
(e.g sdfac=[0.8, 1.0, 1.2] for feather) for the corresponding 
combination method to iterate over. Default could be 1.0 for all.



## suffix for combination method

Here, we define the suffix for each method. The scaling factor iterator 
will be added in the corresponding combination loop.



## dryrun and combi name list

This section initiates lists in which the names of the combined images 
are dropped. This can be used for the assessment task to select the wanted 
products. In case the user wants to redefine the selection within this 
module, he can use dryrun=True: It generates the filennames with the wanted 
iterators and cleanname without executing the combination method.



## execution steps/methods

### concat
Straight forward

### tclean only
need to rename the products name after image creation 
-> need to adjust in datacomb.py

       imname = imbase + cleansetup + tcleansetup
       e.g.     skymodel-b_120L.HB_AM_n0.0e0.tclean


### feather
need to remove intermediate and final products before image creation, 
else function fails -> need to adjust in datacomb.py

      imname = imbase + cleansetup + feathersetup + str(sdfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.feather_f1.0


### SSC
not yet present as a module; need to do execfile('SSC_dc.py') 
-> need to import casatasks in SSC_dc.py and integrate it into the datacomb.py
need to rename the products name after image creation 
-> need to adjust in SSC_dc.py/datacomb.py

      imname = imbase + cleansetup + SSCsetup + str(SSCfac[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.SSC_f1.0


### hybrid
need to remove intermediate and final products before image creation, 
else feather function fails -> need to adjust in datacomb.py
need to rename the products name after image creation 
-> need to adjust in datacomb.py

      imname = imbase + cleansetup + hybridsetup + str(sdfac_h[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.hybrid_f1.0


### SDINT 
need to rename the products name after image creation 
-> need to adjust in datacomb.py

      jointname = imbase + cleansetup + sdintsetup + str(sdg[i]) 
      e.g.     skymodel-b_120L.HB_AM_n0.0e0.sdint_g1.0


### TP2VIS
not yet activated.


## after combination loops
delete the nasty TempLattices







