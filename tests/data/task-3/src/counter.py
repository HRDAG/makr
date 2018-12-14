#!/usr/bin/env python3
#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-3/src/counter.py
#
import argparse
import json
import collections


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input1")
    parser.add_argument("--input2")
    parser.add_argument("--output")
    return parser.parse_args()


def readrow(line):
    return [r.strip() for r in line.split('|')]


if __name__ == '__main__':
    args = get_args()
    counts = collections.defaultdict(int)

    with open(args.input1, 'rt') as ifile:
        header = readrow(ifile.readline())
        rows = [header]
        weight_fld = header.index('weight')
        sum_weights_incl_dead = 0
        for line in ifile.readlines():
            line = line.strip()
            if not line:
                continue
            row = readrow(line)
            counts['sum_weights_incl_dead'] += int(row[weight_fld])

    with open(args.input2, 'rt') as ifile:
        header = readrow(ifile.readline())
        rows = [header]
        weight_fld = header.index('weighted_weight')
        sum_wtd_weights_not_dead = 0
        for line in ifile.readlines():
            line = line.strip()
            if not line:
                continue
            row = readrow(line)
            counts['sum_wtd_weights_not_dead'] += int(row[weight_fld])

    with open(args.output, 'wt') as ofile:
        json.dump(counts, ofile)

# done.
