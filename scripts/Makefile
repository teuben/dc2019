#

CASA = time casa --nogui -c 

all: FeatheringPresentation.ipynb


FeatheringPresentation.ipynb:
	wget https://keflavich.github.io/talks/FeatheringPresentation/FeatheringPresentation.ipynb



# some processing that can be done here



# full resolution data (all producte will be in current directory)
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
M100qac:
	$(CASA) M100_combine2.py > M100_combine2.log  2>&1
# second
M100tp2vis: M100qac
	$(CASA) M100_combine4.py > M100_combine4.log  2>&1

# third
M100sdint: M100qac
	$(CASA) M100_combine3.py use12m=0 > M100_combine3a.log  2>&1
	$(CASA) M100_combine3.py use12m=1 > M100_combine3b.log  2>&1
