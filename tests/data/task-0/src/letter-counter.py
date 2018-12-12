#!/usr/bin/env python3
#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-0/src/letter-counter.py
#
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    return parser.parse_args()


def readrow(line):
    return [r.strip() for r in line.split('|')]


if __name__ == '__main__':
    args = get_args()

    with open(args.input, 'rt') as ifile:
        header = readrow(ifile.readline())
        header.append('nchars')
        rows = [header]
        for line in ifile.readlines():
            line = line.strip()
            if not line:
                continue
            row = readrow(line)
            if row[1] == 'dead':
                continue
            row.append(len(row[0]))
            rows.append(row)

    with open(args.output, 'wt') as ofile:
        ofile.write('|'.join(rows[0]) + "\n")
        for row in rows[1:]:
            ofile.write('|'.join([str(f) for f in row]) + "\n")

# done.
