# Startmodel + Feather Method

Here we describe the method that uses TCLEAN with a startmodel,
followed by feather.

An example is by Hoffman & Kepley (https://library.nrao.edu/public/memos/gbt/GBT_300.pdf).

An extended version is by Kauffman (http://tinyurl.com/zero-spacing)

## Imaging script

The script is found here: ...

Important steps are:

(1) The single dish image needs to be in Jy/pixel.  This is done with
the commands: 

      immath
      imhead

(2) TCLEAN is run with

      startmodel  = '[SD image, in Jy/pixel]'

(3) Feather

Mention any issues to consider.

## Output images:

(1) Point source(s)

(2) Sky model 

(3) M100


