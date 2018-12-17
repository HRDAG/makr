#!/usr/bin/env bash

# run from anywhere inside the makr/ project,


cd $(git rev-parse --show-toplevel)/tests/data/task-0
make clean
cd ../task-1
make clean -f src/Makefile
cd ../task-2
make clean
cd ../task-3
make clean
cd ../task-4
make clean


# done.
