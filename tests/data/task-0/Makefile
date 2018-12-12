#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-0/Makefile
#
.PHONY: all clean
all: output/cast.csv
clean:
	rm output/*


output/cast.csv: \
		src/letter-counter.py \
		input/cast.csv
	python3 $< \
		--input=input/cast.csv \
		--output=output/cast.csv

# done

