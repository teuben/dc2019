#

CASA = time casa --nogui -c 

all: FeatheringPresentation.ipynb


FeatheringPresentation.ipynb:
	wget https://keflavich.github.io/talks/FeatheringPresentation/FeatheringPresentation.ipynb



# some processing that can be done here



# full resolution data (all producte will be in current directory)
# 5525.68user 168.67system 30:08.01elapsed 314%CPU
M100:
	$(CASA) M100_combine1.py > M100_combine1.log  2>&1

# NOTE: the order of these is important:   2-4-3
M100all: M100data M100qac M100tp2vis M100sdint

# QAC benchmark data (all data in M100qac) - this needs the new qac_bench5.tar.gz
M100data:
	curl http://admit.astro.umd.edu/~teuben/QAC/qac_bench5.tar.gz | tar zxf -

# alias for first 
M100feather: M100qac

# first
# 5896.76user 327.50system 31:34.06elapsed 328%CPU
# 13'
M100qac:
	$(CASA) M100_combine2.py > M100_combine2.log  2>&1
# second
# 25672.90user 1579.76system 1:33:14elapsed 487%CPU
# 27225.50user 1630.18system 2:51:30elapsed 280%CPU 
# 68'
M100tp2vis: M100qac
	$(CASA) M100_combine4.py > M100_combine4.log  2>&1

# third
# 1803.70user 547.31system 26:14.28elapsed 149%CPU
# 2636.82user 326.08system 17:37.00elapsed 280%CPU
# 46'
M100sdint: M100qac
	$(CASA) M100_combine3.py use12m=0 > M100_combine3a.log  2>&1
	$(CASA) M100_combine3.py use12m=1 > M100_combine3b.log  2>&1

# final, some summary plots
M100final:
	$(CASA) M100_final.py > M100_final.log  2>&1	
