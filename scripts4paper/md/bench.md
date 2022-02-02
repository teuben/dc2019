# DC2019 benchmark

There is a bench.md in QAC, but here we want a much simpler one. Probably the goal here
is to have a benchmark that also tests if the results of the
computation are same/close enough to what we consider the correct answer.
In QAC we use qac_stats(), which prints some simple mean/rms/min/max/flux/sratio
of a given map. The precision can be choosen. E.g.

                                              mean     rms       min      max         flux     sratio
     QAC_STATS: export/sky_tweak_box1.fits   0.855257 1.335149 -0.431050 7.741113 6489.699216 0.961874 

In qac we have

     OMP_NUM_THREAD=1 make sky4z sky4z-bench2

to test a full script, as well a single longish combination tclean.  Also note the number of cores
that is used for the bench can be important, but we could do a single and full core experience, but
keeping in mind that the maximum number of cores often involved hitting all threads per core, which
can be over the sweet spot as we have seen in many experiments.


## Parallel CASA

There are two ways to exploit some parallelism in CASA: MPI and OpenMP.  Let's look at the sky4z-bench2
benchmark, which runs tclean for niter=100,000. Here on a i7-4930K CPU wiht 6 cores, and 2 hyper-threads
per core (which should not be used):

     # single core
     OMP_NUM_THREADS=1 make sky4z-bench2
     385.93user 20.92system 7:38.47elapsed 88%CPU
     QAC_STATS: 5.8807340538948054 7.705096874227821 -20.720354080200195 27.191093444824219 69635.755146266558 0.930926
     
     # all cores
     OMP_NUM_THREADS=6 make sky4z-bench2

     # all cores and hyper-threads (12 virtual cores)
     make sky4z-bench2
     943.39user 32.12system 9:06.77elapsed 178%CPU

     # one for MPI, and one for computing
     make sky4z-bench2mpi ONT=2
     395.34user 22.64system 9:51.74elapsed 70%CPU

     # one for MPI, and 4 for computing
     make sky4z-bench2mpi ONT=5
     400.32user 24.26system 9:48.00elapsed 72%CPU
