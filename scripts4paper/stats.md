# STATS

A table of stats per run would be useful, so we can compare.
They would have to be taken from the same maps, at the same resolution, which excludes
the TP map. But we seem to agree on the area as explained in skymodel.md with the
caveat small differences can happen if you use an RA/DEC region=.
Also to follow the QA team: these maps need to have been smoothed to a circular 2" beam.

Here are the ones we could consider:

      mean    Jy/beam
      rms     Jy/beam
      min     Jy/beam
      max     Jy/beam
      flux    Jy
      sratio  dimensionless, typically [0,1], 1 is perfect       sratio=(FluxP-FluxN)/(FluxP+FluxN)
      SSIM    dimensionless, [0,1], 1 is perfect
      A       dimensionless, 0 is perfect

On the Google Drive in sky_qac/qac_stats.txt a example file is maintained for skymodel-b (see sky4.py)
