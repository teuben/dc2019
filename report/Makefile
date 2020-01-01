#


qac:
	pdflatex memo_qac.tex


# M100:        https://www.overleaf.com/project/5d55486d26900c000189ce35    git clone https://git.overleaf.com/5d55486d26900c000189ce35
#              ok
# N346:        https://www.overleaf.com/5263516468jywmsrvcyddn              git clone https://git.overleaf.com/5d52bbb6f8724362e46b0e07
#              ok
# skymodel:    https://www.overleaf.com/6799949182tqhbtvcxbwdd              git clone https://git.overleaf.com/5d557ff05a59b7784800c1bb
#              missing images/tp2vispl.png file
# GaussSim     https://www.overleaf.com/3355477475zffqdkpnjpjp              git clone https://git.overleaf.com/5d55330c1d7b3e0001c38c10
#              dir ; 2 missing figures
# outflow:     https://www.overleaf.com/4861457898hvpzhnhknscg              git clone https://git.overleaf.com/5d4fb7bad655257fb6a01710
#              ok
# HI:          https://www.overleaf.com/read/dnstbdwtxpjk                   git clone https://git.overleaf.com/5d52b2439221d17e41ad5a7e
#              ok

ALL = m100 skymodel gausssim outflow n346 HI

m100:
	git clone https://git.overleaf.com/5d55486d26900c000189ce35 m100

skymodel:
	git clone https://git.overleaf.com/5d557ff05a59b7784800c1bb skymodel

gausssim:
	git clone https://git.overleaf.com/5d55330c1d7b3e0001c38c10 gausssim

outflow:
	git clone https://git.overleaf.com/5d4fb7bad655257fb6a01710 outflow

n346:
	git clone https://git.overleaf.com/5d52bbb6f8724362e46b0e07 n346

HI:
	git clone https://git.overleaf.com/5d52b2439221d17e41ad5a7e HI


# update all git repo's

pull:
	for i in $(ALL); do\
	(cd $$i; echo $$i; git pull); done
	git pull











