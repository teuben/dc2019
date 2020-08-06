# *2020 Follow-up: Improving Image Fidelity on Astronomical Data*

## AIM

This is a follow-up of the
[DC2019](https://www.lorentzcenter.nl/lc/web/2019/1179/info.php3?wsid=1179&venue=Oort)
workshop, and a sprint to make progress on the [Github](https://github.com/teuben/dc2019) page.
A lot of work has already been done, which should not be lost or forgotten, and some final coordination is needed to close out the [manuscript](https://www.overleaf.com/project/5d829641216025000191a049).

Specific goals are (to be discussed with team):
* Return to [manuscript](https://www.overleaf.com/project/5d829641216025000191a049) draft, **before July 29**
* Develop specific tasks for each team, **July 29-31** 
* Share data/scripts, and test methods, **July 31-August 24**
* Develop publicly sharable code, **before August 24**
* Final hack-a-thon, **August 24-28**
* Robust manuscript draft, **end of August**

## FORMAT

We will dedicate two ''work weeks'' on July 29-31; and again August 24-28.  In between, we will meet every Thursday (06/08/20, 13/08/20, 20/08/20).

*Our Zoom meetings will be held at UTC 11-13.*  These are mornings in the US (~7:00-9:00 EDT; 5:00 MT); afternoon in Europe (13:00-15:00); and night in Japan (20:00-22:00) and in Australia (21:00-23:00).  

*Zoom connection information in Slack channel #manuscript-leads*

#### WEEK 0 (Jul 29-31), *Work Week #1*: 

*Minutes/notes [here](https://docs.google.com/document/d/1E_PnQzwuBf5Fm1itBsQCfwFL0j3hWvCP9NvD3hRsvD4/edit?usp=sharing)*

* 29/07 Wednesday 11-12 UT: 
    * General opening discussion
    * Discuss methods; Each sub-team makes a 5 minute presentation (informal)
* 29/07 Wednesday 12:10-13 UT: 
    * Discuss datasets; Each sub-team makes a 5 minute presentation (informal)
    * Make a 3-day plan with action-items
* 30/07 Thursday 11-12 UT: 
    * Assessment methods (Alvaro)
* 30/07 Thursday 12:10-13 UT: 
    * Discussion on consistent imaging (TCLEAN/sdintimaging) techniques
    * Short updates from any team
* 31/07 Friday 11-12 UT: 
    * Select a color map for plots
    * Make a list of important output plots for manuscript
* 31/07 Friday 12:10-13 UT: 
    * Manuscript outline
    * Plan for August

#### WEEK 1 (Aug 3-7):  - see also:  https://github.com/teuben/dc2019/issues

*Updated minutes/notes [here](https://docs.google.com/document/d/1E_PnQzwuBf5Fm1itBsQCfwFL0j3hWvCP9NvD3hRsvD4/edit?usp=sharing)*

- [x]  Make the "sky model" with a few point sources.  Notify the group when it's ready. [[AI: Peter/Dirk ]] - **See: skymodel-b.fits on Slack**
- [x]  Determine common observing setup for the 12m/7m/TP simulated observations, and send feedback to Toshi about the simulated data setup. [[AI: Devaky]] - **Per pointing: 20min (12m); 1 hour (7m); 80 min (TP).  Total 12m observing time is ~17 hours. **
- [ ]  Generate the simulated observations of the skymodel-b (from Peter/Dirk) [[AI: Toshi/Yusuke]]
- [x]  Wednesday: Suggest colormap possibilities to vote. [[AI: All]] - **List [here](https://datacomb2019.slack.com/archives/CP6QCUPKQ/p1596583510149600)**
- [ ]  Friday: Vote on colormap for observational images.  [[AI: All]]
- [x]  Weekly meeting on Thursday @ UTC 11-12 (any additional discussion from 12-13).

#### WEEK 2 (Aug 10-14):

- [ ]  First half of week: Define the details of the TCLEAN method [[AI: Dirk]]
- [ ]  Run combinations on simulated observations [[AI: Methods teams]]
- [ ]  Provide scripts for combination methods.  [[AI: Methods teams]]
- [ ]  Weekly meeting on Thursday @ UTC 11-12 (any additional discussion from 12-13).

**Datasets needed for QA by Aug. 17**
For each DC method we need:
* Initial Skymodel
* TP map
* Final combined (TP+ACA+12m) map at it highest resolution
* Intermediate products (if created): i.e. TP+ACA only map
*Format: either FITS or CASA images*

#### WEEK 3 (Aug 17-21):

- [ ]  Assessment [[AI: Alvaro]]
- [ ]  Select a colormap for assessment plots [[AI: Alvaro]]
- [ ]  Run combination methods on observational datasets [[AI: Dataset teams]]
- [ ]  Weekly meeting on Thursday @ UTC 11-12 (any additional discussion from 12-13).

#### WEEK 4 (Aug 24-28), *Work Week #2*:

- [ ] Daily meetings @ UTC 11-13.


### Preferred communication: 
Via Slack, datacomb2019.slack.com

## PARTICIPANTS

All leaders of the sub-teams, and active members who are testing methods and developing the manuscript draft.  

* Nickolas Pingel (Australia) 
* Toshi Takagi (Japan)
* Yusuke Miyamoto (Japan)
* Kelley Hess (EU)
* Dirk Petry (EU) 
* Alvaro Hacar (EU) 
* Adele Plunkett (NA) 
* Devaky Kunneriath (NA)
* Peter Teuben (NA) 
* Brian Mason (NA) *will participate in August*
* Urvashi Rau (NA) *will participate in August*
* Tim Braun (NA) *to be confirmed*

*Anyone who would like to dedicate time to this is welcome to participate!  Contact Adele, or anyone listed here.*


## TECHNIQUES

   * [feather](https://casa.nrao.edu/casadocs/casa-5.4.1/image-combination/feather) Team: Devaky, Melissa
   * [tp2vis](https://github.com/tp2vis/distribute) Team: Peter
   * [hybrid](https://sites.google.com/site/jenskauffmann/research-notes/adding-zero-spa) Team: Adele
   * [sdint](https://github.com/urvashirau/WidebandSDINT) Team: Dirk, Urvashi, Tim
   * [Faridani](https://arxiv.org/pdf/1709.09365.pdf) Team: Nick

## OBSERVATIONAL DATASETS
   * M100, Team: Peter
   * SMC, Team: Dirk
   * Lupus 3 mms outflow, Team: Adele
   * HI, Team: Nick, Kelley

## SIMULATED DATA
   * Led by Toshi, Yusuke
   
## ASSESSMENT METHODS
   * Led by Alvaro
