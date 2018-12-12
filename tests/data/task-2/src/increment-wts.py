#!/usr/bin/env python3
#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-2/src/increment-wts.py
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
    increments = {'player': 1, 'attacker': 2, 'dead': 0}

    with open(args.input, 'rt') as ifile:
        header = readrow(ifile.readline())
        header.append('weighted_weight')
        rows = [header]
        weight_fld = header.index('weight')
        role_type_fld = header.index('role_type')
        for line in ifile.readlines():
            line = line.strip()
            if not line:
                continue
            row = readrow(line)
            weight = int(row[weight_fld])
            role_type = row[role_type_fld]
            weighted_weight = weight * increments.get(role_type, None)
            row.append(weighted_weight)
            rows.append(row)

    with open(args.output, 'wt') as ofile:
        ofile.write('|'.join(rows[0]) + "\n")
        for row in rows[1:]:
            ofile.write('|'.join([str(f) for f in row]) + "\n")

# done.
