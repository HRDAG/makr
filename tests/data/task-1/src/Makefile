#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-1/Makefile
#
.PHONY: all clean

all: output/cast.csv

clean:
	rm output/*

output/cast.csv: \
		src/aggregate-roles.py \
		hand/remapped-roles.json \
		input/cast.csv
	python3 $< \
		--input=input/cast.csv \
		--remap=hand/remapped-roles.json \
		--output=output/cast.csv

# done

