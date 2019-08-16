#

CASA = time casa --nogui -c 

all: FeatheringPresentation.ipynb


FeatheringPresentation.ipynb:
	wget https://keflavich.github.io/talks/FeatheringPresentation/FeatheringPresentation.ipynb



# some processing that can be done here


# full data
M100:
	$(CASA) M100_combine1.py > M100_combine1.log  2>&1

# qac/benchmark data
M100qac:
	$(CASA) M100_combine2.py > M100_combine2.log  2>&1

# sdint
M100sd:
	$(CASA) M100_combine3.py > M100_combine3.log  2>&1
