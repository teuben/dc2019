# DC2019 benchmark

There is a bench.md in QAC, but here we want a much simpler one. Probably the goal here
is to have a benchmark that also tests if the results of the
computation are same/close enough to what we consider the correct answer.
In QAC we use qac_stats(), which prints some simple mean/rms/min/max/flux/sratio
of a given map. The precision can be choosen. E.g.

                                              mean     rms       min      max         flux     sratio
     QAC_STATS: export/sky_tweak_box1.fits   0.855257 1.335149 -0.431050 7.741113 6489.699216 0.961874 

In qac we have

     OMP_NUM_THREAD=1 make sky4z sky4z-bench

to test a full script, as well a single longish combination tclean.  Also note the number of cores
that is used for the bench can be important, but we could do a single and full core experience, but
keeping in mind that the maximum number of cores often involved hitting all threads per core, which
can be over the sweet spot as we have seen in many experiments.
