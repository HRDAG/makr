#! /usr/bin/env python3
''' given a task, finds all the upstream_tasks, in order '''
# -*- mode: python; fill-column: 79; comment-column: 50 -*-
#
# Author(s):  JK, PB
# Maintainer: PB
# Created:    20181211
# License:    (c) 2018 HRDAG, GPL-v2 or greater
# ============================================
#
#
# derived from the Jeff+Scott follow-task-symlink-dependencies script
# from the old Benetech-HRDAG run approach, c.2007
#
# migrated to py3k + git-style projects, without env vars, by PB
# migrated again to depend on git and to parse Makefile databases
#
#
# :input: path to an HRDAG task
# :on stdout: list of paths that this task depends from earliest to latest
# :on stderr: messages about discovered dependencies and execution order
#             for human consumption, if --verbose
# ============================================

import sys
import re
import os
from pathlib import Path
import functools
from collections import deque
import subprocess

assert sys.version_info.major >= 3 and sys.version_info.minor >= 2


def preserve_cwd(function):
    ''' from https://stackoverflow.com/questions/169070/
            how-do-i-write-a-decorator-that-restores-the-cwd/ '''
    @functools.wraps(function)
    def decorator(*args, **kwargs):
        cwd = Path.cwd()
        try:
            return function(*args, **kwargs)
        finally:
            os.chdir(cwd)
    return decorator


def is_a_task(taskdir):
    ''' tests dir for presence of at least one task leaf '''
    task_subdirs = ("input", "output", "src", "frozen", "hand")
    taskdir = Path(taskdir).resolve()
    if not taskdir.is_dir():
        return False
    return any(taskdir.joinpath(subdir).is_dir()
               for subdir in task_subdirs)


def get_git_root():
    prox = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                          capture_output=True)
    pth = Path(prox.stdout.strip().decode('utf-8'))
    return str(pth)


def get_task_path(tpath):
    tpath = Path(tpath).resolve()
    opath = tpath                           # for error reporting
    git_root = Path(get_git_root())

    while tpath.is_file() or not is_a_task(tpath):
        tpath = tpath.parent
        if tpath == tpath.parent or tpath == Path.home():
            raise OSError(f"no task found starting at {opath}")

    errmsg = f"get_task_path: tpath={tpath} not in git_root={git_root}"
    assert git_root.parts == tpath.parts[:len(git_root.parts)], errmsg

    return str(tpath)


def exec_make(make_args):
    ''' in cwd, either `make` or `make -f src/Makefile` '''
    assert make_args[0] == 'make'
    if Path('src/Makefile').exists():
        make_args.extend(["--makefile", "src/Makefile"])
    elif not Path('Makefile').exists():
        raise FileNotFoundError(f"Makefile not found in {Path.cwd()}")
    prox = subprocess.run(make_args, capture_output=True)
    make_stdout = prox.stdout.decode('utf-8')
    make_stderr = prox.stderr.decode('utf-8')
    rc = prox.returncode
    if rc in [1, 2]:
        print(f"make returns with {rc} --> {make_stderr}", file=sys.stderr)
    return make_stdout


@preserve_cwd
def get_deps_from_make(task_path):
    ''' note: this outputs raw strings extracted from make output '''
    os.chdir(task_path)
    assert is_a_task('.')
    db = exec_make(['make', '--dry-run', '--print-data-base'])

    tofilter = re.compile(r'^%|^#|^make|^\.|^\(%|^all|^clean')
    white = re.compile(r'\s+')
    deps = list()
    for line in db.split(os.linesep):
        # NB: the space after : rules out :=
        if ": " in line and not tofilter.match(line):
            line = line.split(":")[1]
            deps.extend([d.strip() for d in white.split(line) if d.strip()])

    return sorted(set(deps))


@preserve_cwd
def get_tasks_from_deps(base_task, deps):
    ''' given dep,
        return project-root abs task path
    '''
    base_task = Path(base_task).resolve()
    os.chdir(base_task)
    tasks = [get_task_path(d) for d in deps]
    return sorted(set([t for t in tasks if t != str(base_task)]))


@preserve_cwd
def follow_deps(base_task):
    ''' follow a task's dependencies recursively to the first files
        return pairs (prereq, task)
    '''
    base_task = Path(base_task).resolve()
    deps = get_deps_from_make(base_task)
    tasks = get_tasks_from_deps(base_task, deps)
    base_task = get_task_path(base_task)
    pairs = [(t, base_task) for t in tasks]
    for task in tasks:
        pairs.extend(follow_deps(task))
    return sorted(set(pairs))


def topological_sort(deps):
    """ Takes a list of (a,b) pairs representing a->b deps
        and returns a sequence of items such that no item in the
        sequence depends on an earlier item.
    """
    def prereqs_of(task):
        ''' return all prereqs for task '''
        return set([p for (p, t) in deps if t == task])

    tasks_with_prereqs = set([t for p, t in deps])

    all_tasks = tasks_with_prereqs | set(p for p, t in deps)

    tasks_without_prereqs = all_tasks - tasks_with_prereqs
    sorted_tasks = list(tasks_without_prereqs)

    while len(sorted_tasks) < len(all_tasks):
        unsorted_tasks = all_tasks - set(sorted_tasks)

        one_step_downstream_tasks = set([
            t for t in unsorted_tasks
            if prereqs_of(t) <= set(sorted_tasks)])

        next_tasks = list(one_step_downstream_tasks)
        if not next_tasks:
            errmsg = ("Cycle found in upstream task dependency network. "
                      "run -L can't tell which task should be run first.")
            raise RuntimeError(errmsg)
            # find_and_print_cycle(deps)
        sorted_tasks.extend(next_tasks)

    return sorted_tasks


@preserve_cwd
def make_all(base_task):
    base_task = Path(base_task).resolve()
    os.chdir(base_task)
    pairs = follow_deps(str(base_task))
    que = topological_sort(pairs)
    for task in que:
        os.chdir(task)
        exec_make(['make'])


# done.
