#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-4/Makefile
#
.PHONY: all clean
all: output/report.md
clean:
	rm output/*


output/report.md: \
		src/write-report.py \
		../task-1/input/cast.csv \
		../task-3/output/counts.json
	python3 $< \
		--input1=../task-1/output/cast.csv \
		--input3=../task-3/output/counts.json \
		--output=$@

# done

