
#!/usr/bin/env pytest -v

# Author(s):  PB
# Maintainer: PB
# Created:    20181211
# License:    (c) 2018 HRDAG, GPL-v2 or greater
# ============================================
#
# makr/tests/bin/test_upstream_tasks.py
#

import os
import os.path
import pytest
import sys
sys.path.append("../../bin")

import upstream_tasks as ut
MODULE_PATH = os.path.abspath(os.path.curdir)


def test_test_from_bin():
    assert MODULE_PATH.endswith("tests/bin")


def setup_function():
    os.chdir(MODULE_PATH)


def test_get_git_root():
    assert ut.get_git_root() == 'makr'


def test_exec_make():
    with pytest.raises(TypeError):
        ut.exec_make()
    with pytest.raises(IndexError):
        ut.exec_make([])
    with pytest.raises(OSError):
        ut.exec_make(['make', '-n'])
    os.chdir("../data/task-0")   # task-0/Makefile
    db = ut.exec_make(['make', '-n', '--print-data-base'])
    assert db.startswith("make:")
    os.chdir("../task-1")   # task-1/src/Makefile
    db = ut.exec_make(['make', '-n', '--print-data-base'])
    assert db.startswith("make:")


def test_get_deps_from_make_0():
    deps = ut.get_deps_from_make("../data/task-0")
    assert deps == ['input/cast.csv', 'src/letter-counter.py']


def test_get_deps_from_make_3():
    deps = ut.get_deps_from_make("../data/task-3")
    assert deps == ['../task-0/input/cast.csv',
                    '../task-2/output/cast.csv', 'src/counter.py']

# done.
