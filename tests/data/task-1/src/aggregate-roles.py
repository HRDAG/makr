#!/usr/bin/env python3
#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-1/src/aggregate-roles.py
#
import argparse
import json


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--remap")
    parser.add_argument("--output")
    return parser.parse_args()


def readrow(line):
    return [r.strip() for r in line.split('|')]


if __name__ == '__main__':
    args = get_args()

    with open(args.remap, 'rt') as jfile:
        remapper = json.load(jfile)

    with open(args.input, 'rt') as ifile:
        header = readrow(ifile.readline())
        header.append('role_type')
        rows = [header]
        for line in ifile.readlines():
            line = line.strip()
            if not line:
                continue
            row = readrow(line)
            role_type = remapper.get(row[1], None)
            assert role_type is not None
            row.append(role_type)
            rows.append(row)

    with open(args.output, 'wt') as ofile:
        ofile.write('|'.join(rows[0]) + "\n")
        for row in rows[1:]:
            ofile.write('|'.join([str(f) for f in row]) + "\n")

# done.
