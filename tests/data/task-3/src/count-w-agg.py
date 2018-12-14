#!/usr/bin/env python3
#
# Author: PB
# Maintainer: PB
# Copyright: HRDAG 2018, GPL-3 or better
#
# makr/tests/data/task-3/src/count-w-agg.py
#
import argparse
import json
import collections


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input0")
    parser.add_argument("--input2")
    parser.add_argument("--output")
    return parser.parse_args()


def readrow(line):
    return [r.strip() for r in line.split('|')]


if __name__ == '__main__':
    args = get_args()
    counts = collections.defaultdict(int)

    # count by role_type
    actors = set()
    counts = collections.defaultdict(int)
    with open(args.input2, 'rt') as ifile:
        header = readrow(ifile.readline())
        rows = [header]
        role_type_fld = header.index('role_type')
        actor_fld = header.index('actor')
        for line in ifile.readlines():
            line = line.strip()
            if not line:
                continue
            row = readrow(line)
            role_type = row[role_type_fld]
            counts[role_type] += 1
            actors.add(row[actor_fld])

    with open(args.input0, 'rt') as ifile:
        header = readrow(ifile.readline())
        rows = [header]
        role_fld = header.index('role')
        actor_fld = header.index('actor')
        for line in ifile.readlines():
            line = line.strip()
            if not line:
                continue
            row = readrow(line)
            actor = row[actor_fld]
            if actor in actors:
                continue
            counts[role_fld] += 1
            actors.add(actor)

    counts['total_actors'] = len(actors)
    assert counts['total_actors'] == 7

    with open(args.output, 'wt') as ofile:
        json.dump(counts, ofile)

# done.
