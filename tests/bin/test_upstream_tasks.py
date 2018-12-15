#!/usr/bin/env pytest -v

# Author(s):  PB
# Maintainer: PB
# Created:    20181211
# License:    (c) 2018 HRDAG, GPL-v2 or greater
# ============================================
#
# makr/tests/bin/test_upstream_tasks.py
#
# execute with pytest test_upstream_tasks.py from this dir

import os
import os.path
from pathlib import Path
import pytest
import sys
sys.path.append("../../bin")

import upstream_tasks as ut
MODULE_PATH = Path.cwd()


def setup_function():
    # before every test
    os.chdir(MODULE_PATH)


def test_test_from_bin():
    assert str(MODULE_PATH).endswith("tests/bin")


def test_get_git_root():
    assert ut.get_git_root() == 'makr'


def test_is_a_task_yes():
    assert ut.is_a_task('../data/task-0')


def test_is_a_task_no():
    assert not ut.is_a_task(str(Path.cwd()))


def test_get_task_path():
    assert ut.get_task_path('../data/task-2') == 'makr/tests/data/task-2'


def test_get_task_path_file():
    fname = '../data/task-2/output/cast.csv'
    assert ut.get_task_path(fname) == 'makr/tests/data/task-2'


def test_get_task_path_symlink():
    symlinked_file = '../data/task-1/input/cast.csv'
    assert ut.get_task_path(symlinked_file) == 'makr/tests/data/task-0'


def test_get_task_path_notproj():
    with pytest.raises(OSError):
        ut.get_task_path(Path.home())


def test_exec_make_empty_args():
    with pytest.raises(TypeError):
        ut.exec_make()


def test_exec_make_empty_list():
    with pytest.raises(IndexError):
        ut.exec_make([])


def test_exec_make_no_makefile():
    with pytest.raises(FileNotFoundError):
        ut.exec_make(['make', '-n'])


def test_exec_make_db_correct0():
    os.chdir("../data/task-0")   # task-0/Makefile
    db = ut.exec_make(['make', '-n', '--print-data-base'])
    assert db.startswith("make:")


def test_exec_make_db_correct1():
    os.chdir("../data/task-1")   # task-1/src/Makefile
    db = ut.exec_make(['make', '-n', '--print-data-base'])
    assert db.startswith("make:")


def test_get_deps_from_make_0():
    deps = ut.get_deps_from_make("../data/task-0")
    assert deps == ['input/cast.csv', 'src/letter-counter.py']


def test_get_deps_from_make_3():
    deps = ut.get_deps_from_make("../data/task-3")
    assert deps == ['../task-0/input/cast.csv',
                    '../task-1/output/cast.csv',
                    '../task-2/output/cast.csv',
                    'src/count-w-agg.py',
                    'src/counter.py']


def test_get_deps_from_make_4():
    deps = ut.get_deps_from_make("../data/task-4")
    assert deps == ['../task-1/input/cast.csv',
                    '../task-3/output/counts.json',
                    'src/write-report.py']


def test_get_task_from_dep():
    deps = ut.get_deps_from_make("../data/task-4")
    assert ut.get_task_from_deps(deps) == 'makr/tests/data/task-1'

# done.
