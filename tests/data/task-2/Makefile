#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-2/Makefile
#
.PHONY: all clean
all: output/cast.csv
clean:
	rm output/*


output/cast.csv: \
		src/increment-wts.py \
		../task-1/output/cast.csv
	python3 $< \
		--input=../task-1/output/cast.csv \
		--output=output/cast.csv

# done

