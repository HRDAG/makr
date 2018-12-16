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
import argparse
import functools
from collections import deque
import subprocess

assert sys.version_info.major >= 3 and sys.version_info.minor >= 2


def get_args():
    ''' read and parse command line arguments '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--starting-task', action="store", required=True,
                        help="Root task for which to find all"
                             " prerequisite tasks.")
    parser.add_argument('-E', '--skip-external-tasks',
                        dest='required_parent_dir',
                        action="store", default='/',
                        metavar='DIR', required=False,
                        help="Skip tasks External to DIR.")
    parser.add_argument('-v', '--verbose', action="store_true", default=False,
                        help="Show dependency search on stderr.")
    return parser.parse_args()


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
    return pth.parts[-1]


def get_task_path(tpath):
    tpath = Path(tpath).resolve()
    opath = tpath                           # for error reporting
    git_root = get_git_root()

    while tpath.is_file() or not is_a_task(tpath):
        tpath = tpath.parent
        if tpath == tpath.parent or tpath == Path.home():
            raise OSError(f"no task found starting at {opath}")

    proj = deque()
    while tpath != tpath.parent:
        proj.appendleft(tpath.parts[-1])
        if proj[0] == git_root:
            break
        tpath = tpath.parent
    else:
        raise OSError(f"from {opath}, no git_root ({git_root}) "
                      f"found in {tpath}")

    return str(Path(*proj))


def exec_make(make_args):
    ''' in cwd, either `make` or `make -f src/Makefile` '''
    assert make_args[0] == 'make'
    if Path('src/Makefile').exists():
        make_args.extend(["--makefile", "src/Makefile"])
    elif not Path('Makefile').exists():
        raise FileNotFoundError(f"Makefile not found in {Path.cwd()}")
    prox = subprocess.run(make_args, capture_output=True)
    return prox.stdout.decode('utf-8')


@preserve_cwd
def get_deps_from_make(task_path):
    ''' task_path: project_path; relative to cwd; or absolute '''
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
    base_task = get_task_path(base_task)
    tasks = [get_task_path(d) for d in deps]
    return sorted(set([t for t in tasks if t != base_task]))


@preserve_cwd
def follow_deps(base_task):
    base_task = Path(base_task).resolve()
    deps = get_deps_from_make(base_task)
    tasks = get_tasks_from_deps(base_task, deps)   # FIXME: what's base_task?
    base_task = get_task_path(base_task)
    pairs = [(base_task, t) for t in tasks]
    for task in tasks:
        pairs.extend(follow_deps(task))
    return sorted(set(pairs))

# ====================================================================


#def topological_sort(dependencies):
#    """ Takes a list of (a,b) pairs representing a->b dependencies
#        and returns a sequence of items such that no item in the
#        sequence depends on an earlier item.
#    """
#    def prereqs_of(task):
#        ''' return all prereqs for task '''
#        return set([p for (t, p) in dependencies
#                    if t == task and is_a_task(p)])

#    all_tasks = (set(t for t, p in dependencies) |
#                 set(p for t, p in dependencies))
#    all_tasks = set([task for task in all_tasks if is_a_task(task)])

#    tasks_with_prereqs = set([t for t, p in dependencies])
#    tasks_without_prereqs = all_tasks - tasks_with_prereqs
#    sorted_tasks = list(tasks_without_prereqs)

#    while len(sorted_tasks) < len(all_tasks):
#        unsorted_tasks = all_tasks - set(sorted_tasks)
#        one_step_downstream_tasks = set([
#            t for t in unsorted_tasks
#            if prereqs_of(t) <= set(sorted_tasks)])
#        next_tasks = list(one_step_downstream_tasks)
#        if not next_tasks:
#            sys.stderr.write("Cycle found in upstream task dependency network.\n")
#            sys.stderr.write("run -L cannot determine which of these tasks should be run first:\n")
#            find_and_print_cycle(dependencies)
#            sys.exit(1)
#        sorted_tasks.extend(next_tasks)
#    return sorted_tasks


#def find_and_print_cycle(dependencies):
#    """ Assume there at least one cycle in dependencies.  Print
#        one of the shortest to stderr.
#    """
#    starts = [t for (t, p) in dependencies]
#    paths = [[t] for t in starts]
#    while True:
#        extended_paths = list()
#        for path in paths:
#            advancing_edge = path[-1]
#            next_steps = [p for (t, p) in dependencies if t == advancing_edge]
#            for next_step in next_steps:
#                extended_path = path+[next_step]
#                if extended_path[0] == extended_path[-1]:
#                    cycle = extended_path
#                    commonprefix = os.path.commonprefix(cycle)
#                    while commonprefix and commonprefix[-1] != '/':
#                        commonprefix = commonprefix[:-1]
#                    common_prefix_length = len(commonprefix)
#                    for task in cycle:
#                        msg = "\t{} depends on...\n".format(
#                            task[common_prefix_length:])
#                        sys.stderr.write(msg)
#                    return
#                extended_paths.append(extended_path)
#        paths = extended_paths
#        extended_paths = list()


#def find_task_dependencies(starting_task):
#    ''' from starting_task, recursively search for all prerequisite tasks '''
#    unexplored_tasks = set([starting_task])
#    explored_tasks = set()
#    dependencies = set()
#    while unexplored_tasks:
#        task = unexplored_tasks.pop()
#        task_prerequisites = get_symlink_dependencies(task)
#        for prereq in task_prerequisites:
#            if prereq == task or not is_a_task(prereq):
#                continue
#            dependencies.add((task, prereq))
#            if prereq not in explored_tasks:
#                unexplored_tasks.add(prereq)
#        explored_tasks.add(task)
#    return dependencies


#def main(starting_task, verbose, required_parent_dir):
#    ''' called from cmdline invocation '''
#    dependencies = find_task_dependencies(starting_task)
#    if verbose:
#        for (task, prereq) in dependencies:
#            msg = "{}\tdepends on\t{}\n".format(
#                truncate_to_project(task), truncate_to_project(prereq))
#            sys.stderr.write(msg)
#    dependency_list = topological_sort(dependencies)
#    execution_list = [path for path in dependency_list if is_a_task(path)]
#    if verbose:
#        sys.stderr.write("\nTask execution order\n--------------------\n")
#    for path in execution_list:
#        if not path.startswith(required_parent_dir):
#            continue
#        if verbose:
#            sys.stderr.write("%s\n" % truncate_to_project(path))
#        sys.stdout.write("%s\n" % path)


#if __name__ == '__main__':
#    args = get_args()
#    if not isdir(os.path.join(args.starting_task, 'input')):
#        sys.stderr.write("\n  start in a task directory with an input/\n")
#        sys.exit(1)
#    main(starting_task=abspath(args.starting_task),
#         verbose=args.verbose,
#         required_parent_dir=args.required_parent_dir)

# done.
