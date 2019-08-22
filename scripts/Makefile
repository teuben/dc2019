#

CASA = time casa --nogui -c 

all: FeatheringPresentation.ipynb


FeatheringPresentation.ipynb:
	wget https://keflavich.github.io/talks/FeatheringPresentation/FeatheringPresentation.ipynb



# some processing that can be done here


M100all: M100 M100qac M100tp2vis M100sdint


# full data (in current directory)
M100:
	$(CASA) M100_combine1.py > M100_combine1.log  2>&1

# NOTE: the order of these is important:   2-4-3

# QAC benchmark data (all data in M100qac) - this needs the new qac_bench5.tar.gz
M100feather: M100qac

M100qac:
	$(CASA) M100_combine2.py > M100_combine2.log  2>&1

M100tp2vis: M100qac
	$(CASA) M100_combine4.py > M100_combine4.log  2>&1

# sdint (M100qac needs to run first; data in M100qac directory)
M100sdint: M100qac
	$(CASA) M100_combine3.py use12m=0 > M100_combine3a.log  2>&1
	$(CASA) M100_combine3.py use12m=1 > M100_combine3b.log  2>&1
