#!/usr/bin/env python3 #
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-4/src/write-report.py
#
import argparse
import json
import time
from collections import Counter

report = """
# My report

In my little dataset, we have the following findings:

* there were {player} players;
* there were {attacker} attackers;
* the sum of the actors' weights, including the dead, was {sum_weights_incl_dead}
* and the sum of the actors weighted-weights, not including the dead, was {sum_wtd_weights_not_dead}

Note that the numbers here are inserted from the data.

<!-- done -->
"""


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input1")
    parser.add_argument("--input3")
    parser.add_argument("--output1")
    parser.add_argument("--output2")
    return parser.parse_args()


def readrow(line):
    return [r.strip() for r in line.split('|')]


def yield_role_type(ifile, role_type_fld):
    for line in ifile.readlines():
        line = line.strip()
        if not line:
            continue
        row = readrow(line)
        yield row[role_type_fld]


if __name__ == '__main__':
    args = get_args()
    start_time = time.time()

    # calc a counter of role_types
    with open(args.input1, 'rt') as ifile:
        header = readrow(ifile.readline())
        rows = [header]
        role_type_fld = header.index('role_type')
        ctr = Counter([rt for rt in yield_role_type(ifile, role_type_fld)])
    ctr = dict(ctr)

    with open(args.input3, 'rt') as jfile:
        ctr.update(json.load(jfile))

    with open(args.output1, 'wt') as ofile:
        ofile.write(report.format(**ctr))

    with open(args.output2, 'wt') as jfile:
        json.dump({'time_elapsed': (time.time() - start_time)}, jfile)

# done.
