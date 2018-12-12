#!/usr/bin/env bash

# run from anywhere inside the makr/ project,


cd $(git rev-parse --show-toplevel)/tests/data/task-0
make
cd ../task-1
make
cd ../task-2
make
cd ../task-3
make
cd ../task-4
make


# done.
