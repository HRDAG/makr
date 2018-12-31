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
import time
import subprocess
from pathlib import Path
import pytest
import sys

import makr as ut
MODULE_PATH = Path.cwd() / 'tests'


def apath(p):
    p = Path(MODULE_PATH) / 'data' / p
    return str(p.resolve())


OUTPUTS = [apath(p) for p in [
    'task-0/output/cast.csv',
    'task-1/output/cast.csv',
    'task-2/output/cast.csv',
    'task-3/output/counts.json',
    'task-3/output/counts-w-agg.json',
    'task-4/output/report.md',
    'task-4/output/timings.json',
]]


def get_mtimes():
    times = {p: Path(p).stat().st_mtime for p in OUTPUTS}
    return times


def setup_function():
    # before every test
    os.chdir(MODULE_PATH)


def absppath(pth):
    ''' pth is a string, return abspth '''
    assert not pth.startswith('/')
    if not pth.startswith('makr/'):
        pth = 'makr/' + pth
    local = list()
    for p in Path.cwd().parts:
        if p == 'makr':
            break
        local.append(p)
    pth = Path(*local) / pth
    return str(pth)


def test_from_testdir():
    assert str(MODULE_PATH)[-5:] == "tests"


def test_get_git_root():
    assert ut.get_git_root().endswith('makr')


def test_is_a_task_yes():
    assert ut.is_a_task('data/task-0')


def test_is_a_task_no():
    assert not ut.is_a_task(str(Path.cwd()))


def test_get_task_path():
    assert ut.get_task_path('data/task-2') == absppath('tests/data/task-2')


def test_get_task_path_file():
    fname = 'data/task-2/output/cast.csv'
    assert ut.get_task_path(fname) == absppath('tests/data/task-2')


def test_get_task_path_symlink():
    symlinked_file = 'data/task-1/input/cast.csv'
    assert ut.get_task_path(symlinked_file) == absppath('tests/data/task-0')


def test_get_task_path_abspath():
    abs_file = str(Path("data/task-1/input/cast.csv").resolve())
    assert ut.get_task_path(abs_file) == absppath('tests/data/task-0')


def test_get_task_path_notproj():
    with pytest.raises(AssertionError):
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
    os.chdir("data/task-0")   # task-0/Makefile
    db = ut.exec_make(['make', '-n', '--print-data-base'])
    assert "# GNU Make" in db[0:100]


def test_exec_make_db_correct1():
    ''' for symlink: this is tricky bc make fails if target file
        doesn't exist '''
    os.chdir("data/task-1")   # task-1/src/Makefile
    db = ut.exec_make(['make', '-n', '--print-data-base'])
    assert "# GNU Make" in db[0:100]


def test_get_deps_from_make_0():
    deps = ut.get_deps_from_make("data/task-0")
    assert deps == ['input/cast.csv', 'src/letter-counter.py']


def test_get_deps_from_make_3():
    deps = ut.get_deps_from_make("data/task-3")
    assert deps == ['../task-0/input/cast.csv',
                    '../task-1/output/cast.csv',
                    '../task-2/output/cast.csv',
                    'src/count-w-agg.py',
                    'src/counter.py']


def test_get_deps_from_make_1_onetarg():
    ''' just from one target, get deps '''
    exp_deps = ['hand/remapped-roles.json', 'input/cast.csv',
                'src/aggregate-roles.py']
    base_task = "data/task-1"
    deps = ut.get_deps_from_make(base_task, target='output/cast.csv')
    assert exp_deps == deps


def test_get_deps_from_make_3_onetarg():
    ''' just from one target, get deps '''
    exp_deps = ['../task-0/input/cast.csv', '../task-2/output/cast.csv',
                'src/count-w-agg.py']
    base_task = "data/task-3"
    deps = ut.get_deps_from_make(base_task, target='output/counts-w-agg.json')
    assert exp_deps == deps


def test_get_deps_from_make_4():
    deps = ut.get_deps_from_make("data/task-4")
    assert deps == ['../task-1/input/cast.csv',
                    '../task-3/output/counts.json',
                    'src/write-report.py']


def test_get_task_from_dep0():
    base_task = "data/task-0"
    deps = ut.get_deps_from_make(base_task)
    tasks = ut.get_tasks_from_deps(base_task, deps)
    assert len(tasks) == 0


def test_get_task_from_dep4():
    base_task = "data/task-4"
    deps = ut.get_deps_from_make(base_task)
    tasks = ut.get_tasks_from_deps(base_task, deps)
    # NB that task-1/input/cast.csv is symlink
    assert tasks[0] == absppath('tests/data/task-0')
    assert tasks[1] == absppath('tests/data/task-3')
    # note that the third dep is inside task-4 so is filtered
    assert len(tasks) == 2


def test_follow_deps0():
    base_task = "data/task-0"
    pairs = ut.follow_deps(base_task)
    assert pairs == list()


def intpairs(pairs):
    return [(int(u[-1:]), int(d[-1:])) for u, d in pairs]


def test_follow_deps1():
    base_task = "data/task-1"
    obs_pairs = intpairs(ut.follow_deps(base_task))
    assert [(0, 1)] == obs_pairs


def test_follow_deps2():
    base_task = "data/task-2"
    obs_pairs = intpairs(ut.follow_deps(base_task))
    assert [(0, 1), (1, 2)] == obs_pairs


def test_follow_deps4():
    base_task = "data/task-4"
    obs_pairs = intpairs(ut.follow_deps(base_task))
    exp_pairs = [(0, 1),  # 1 depends on 0
                 (0, 3),
                 (0, 4),
                 (1, 2),
                 (1, 3),
                 (2, 3),
                 (3, 4)]   # 4 depends on 3
    assert exp_pairs == obs_pairs


def test_topo_sort_a():
    pairs = [(0, 1), (1, 2)]
    exp_q = [0, 1, 2]
    obs_q = ut.topological_sort(pairs)
    assert exp_q == obs_q


def test_topo_sort_cycle():
    pairs = [(0, 1), (1, 2), (2, 0)]
    with pytest.raises(RuntimeError):
        ut.topological_sort(pairs)


def test_topo_sort2():
    base_task = "data/task-2"
    pairs = ut.follow_deps(base_task)
    obs_q = ut.topological_sort(pairs)
    obs_seq = [int(t[-1:]) for t in obs_q]
    assert obs_seq == [0, 1, 2]


def test_remake_clean():
    prox = subprocess.run(['./bin/reset.sh'], capture_output=False)
    prox = subprocess.run(['./bin/clean.sh'], capture_output=True)
    assert prox.returncode == 0
    ut.make_all("data/task-4")
    for output in OUTPUTS:
        print(output)
        assert Path(output).exists()


def test_remake_1change():
    prox = subprocess.run(['./bin/reset.sh'], capture_output=False)
    time.sleep(0.25)
    prox = subprocess.run(['touch', 'data/task-0/input/cast.csv'],
                          capture_output=True)
    assert prox.returncode == 0
    pre_times = get_mtimes()
    time.sleep(0.25)
    ut.make_all("data/task-4")
    post_times = get_mtimes()
    assert all([pre_times[p] < post_times[p] for p in OUTPUTS])

# done.

