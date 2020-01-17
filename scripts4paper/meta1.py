#

def data_combine(method, data, prefix=None, **kwargs):
    """
    For a given 'method' and dataset (directory) 'data'
    do the combination
    Optionally allow a prefix to all data?

    E.g. we could see:

    data/tp.fits
    data/int.ms

    and produce files in

    data/method/
    """
    

for d in ['m100', 'skymodel',  'lupus', 'n346', 'hi']:
  for m in ['feather', 'tp2vis', 'sdint']:
     data_combine(m,d)
