#
TIME = OMP_NUM_THREADS=1 /usr/bin/time
#TIME = /usr/bin/time
CASA = casa-config --version; $(TIME) casa --nogui -c

help:
	@echo "Various targets related to M100"
	@echo "  M100        - basically the full casaguide, used 40+ GB"
	@echo "  M100trim    - trim 23GB down to 105MB for faster testing"
	@echo "  M100feather - "
	@echo "  M100sdint   - "

all: FeatheringPresentation.ipynb


FeatheringPresentation.ipynb:
	wget https://keflavich.github.io/talks/FeatheringPresentation/FeatheringPresentation.ipynb



# - M100 processing ------------------------------------------------------------------
# timing examples from subaru: i7-4930K CPU @ 3.40GHz

# full resolution data (all products will be in current directory)
# 3387.45user 340.07system 26:48.33elapsed 231%CPU 
M100:
	$(CASA) M100_combine1.py > M100_combine1.log  2>&1

# NOTE: the order of these is important:   2-4-3
M100all: M100data M100feather M100tp2vis M100sdint

#  Create new version of the QAC benchmark data
#  137.97user 4.35system 2:25.42elapsed  97%CPU
M100trim:
	$(CASA) M100_trimdata.py > M100_trimdata.log  2>&1

# QAC benchmark data (all data in M100qac) - this needs the new qac_bench5.tar.gz
M100data:
	curl http://admit.astro.umd.edu/~teuben/QAC/qac_bench5.tar.gz | tar zxf -

# first
# 4293.13user 616.55system 29:33.87elapsed 276%CPU
M100feather:
	$(CASA) M100_combine2.py > M100_combine2.log  2>&1

# second
# 56911.62user 12147.88system 4:33:03elapsed 421%CPU 
M100tp2vis: M100feather
	$(CASA) M100_combine4.py > M100_combine4.log  2>&1

# third
# 4555.63user 1056.86system 1:21:02elapsed 115%CPU  (old sdint)
# 3875.22user 827.46system 55:52.46elapsed 140%CPU  (sdintimaging)
M100sdint: M100feather
	$(CASA) M100_combine3.py use12m=0 > M100_combine3a.log  2>&1
	$(CASA) M100_combine3.py use12m=1 > M100_combine3b.log  2>&1

# final, some summary plots
# 288.39user 119.37system 2:19.47elapsed 292%CPU
M100final:
	$(CASA) M100_final.py > M100_final.log  2>&1	


# M51 from simScript:
#     currently this script is interactive, and needs you to enter RETURN a few (2) times
M51:
	(cd simScript; $(CASA) ACASimulation.py )
