#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-3/Makefile
#
.PHONY: all clean
all: output/counts.json
clean:
	rm output/*


output/counts.json: \
		src/counter.py \
		../task-0/input/cast.csv \
		../task-2/output/cast.csv
	python3 $< \
		--input0=../task-0/output/cast.csv \
		--input2=../task-2/output/cast.csv \
		--output=$@

output/counts-w-agg.json: \
		src/count-w-agg.py \
		../task-0/input/cast.csv \
		../task-2/output/cast.csv
	python3 $< \
		--input0=../task-0/output/cast.csv \
		--input2=../task-2/output/cast.csv \
		--output=$@
# done

