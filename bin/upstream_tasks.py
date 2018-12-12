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
# todo: output something usable by run
# todo: change cmd line semantics to assume path as last arg

import sys
import re
import os
from os.path import (abspath, isdir, dirname, exists,
                     normpath, islink)
import os.path   # not os.path.join bc confusing with base join
import argparse
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


def get_git_root():
    prox = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                          capture_output=True)
    pth = prox.stdout.strip().decode('utf-8')
    return os.path.split(pth)[1]


def filelist(directory):
    """Get a list of files in directory, excluding any that start with '.'
       Returns absolute paths."""
    entries = [e for e in os.listdir(directory) if not e.startswith('.')]
    return [abspath(os.path.join(directory, entry)) for entry in entries]


def truncate_to_project(absolute_task_dir):
    ''' This task's project path
        e.g., for the Syria match task, given
           /Users/pball/project/hrdag/SY/match/DCHRS+SCSR+SNHR+VDC/import
        return
           SY/match/DCHRS+SCSR+SNHR+VDC/import
        by walking up from task looking for .git dir
    '''
    assert absolute_task_dir.startswith("/")
    project_top = absolute_task_dir
    while True:
        entries = set(os.listdir(project_top))
        if '.git' in entries and isdir(os.path.join(project_top, '.git')):
            project = os.path.basename(project_top)
            within_proj_path = absolute_task_dir[(len(project_top) + 1):]
            project_dir = os.path.join(project, within_proj_path)
            return project_dir
        project_top = dirname(project_top)
        if project_top == '/':
            raise OSError('no .git dir found in path')


def dereference_symlink(link):
    ''' returns absolute path of symlink target '''
    return normpath(os.path.join(dirname(link), os.readlink(link)))


def is_a_task(taskdir):
    ''' tests dir for presence of at least one task leaf '''
    has_input_or_output_or_src = any(exists(os.path.join(taskdir, subdir))
                                     for subdir in ("input", "output", "src"))
    # sys.stderr.write("%s is a task? %s \n" % (dir, has_input_or_output_or_src))
    return has_input_or_output_or_src


def get_symlink_dependencies(task):
    """ With a task, check all symlinks S in /input/:
        if S is in /output/, add S's task to list.

        The input files *not* from /output/ dirs are immutable,
        so would not need to be recalculated.

        NB that there are complete /output/ dirs linked into /input/
        so consider that possibility; it affects the trim-to-task step

        what to do if there's no input/ dir? return list()
    """
    _output = re.compile('/output.*$')
    def trim_to_task(tpath):
        ''' discard path after (and including) /output
            return None if /output isn't found
        '''
        if '/output' in tpath:
            return _output.sub('', tpath)
        else:
            return None
    input_dir = os.path.join(task, "input")
    if not exists(input_dir):
        return list()
    #print(input_dir, '\n0-\n')
    symlink_paths = [path for path in filelist(input_dir) if islink(path)]
    # print(symlink_paths, '\n1-\n')
    symlink_targets = [dereference_symlink(link) for link in symlink_paths]
    # print(symlink_targets, '\n2-\n')
    target_tasks = set([trim_to_task(target) for target in symlink_targets])
    target_tasks -= {task, None}   # exclude None and self-task
    return list(target_tasks)


def topological_sort(dependencies):
    """ Takes a list of (a,b) pairs representing a->b dependencies
        and returns a sequence of items such that no item in the
        sequence depends on an earlier item.
    """
    def prereqs_of(task):
        ''' return all prereqs for task '''
        return set([p for (t, p) in dependencies
                    if t == task and is_a_task(p)])

    all_tasks = (set(t for t, p in dependencies) |
                 set(p for t, p in dependencies))
    all_tasks = set([task for task in all_tasks if is_a_task(task)])

    tasks_with_prereqs = set([t for t, p in dependencies])
    tasks_without_prereqs = all_tasks - tasks_with_prereqs
    sorted_tasks = list(tasks_without_prereqs)

    while len(sorted_tasks) < len(all_tasks):
        unsorted_tasks = all_tasks - set(sorted_tasks)
        one_step_downstream_tasks = set([
            t for t in unsorted_tasks
            if prereqs_of(t) <= set(sorted_tasks)])
        next_tasks = list(one_step_downstream_tasks)
        if not next_tasks:
            sys.stderr.write("Cycle found in upstream task dependency network.\n")
            sys.stderr.write("run -L cannot determine which of these tasks should be run first:\n")
            find_and_print_cycle(dependencies)
            sys.exit(1)
        sorted_tasks.extend(next_tasks)
    return sorted_tasks


def find_and_print_cycle(dependencies):
    """ Assume there at least one cycle in dependencies.  Print
        one of the shortest to stderr.
    """
    starts = [t for (t, p) in dependencies]
    paths = [[t] for t in starts]
    while True:
        extended_paths = list()
        for path in paths:
            advancing_edge = path[-1]
            next_steps = [p for (t, p) in dependencies if t == advancing_edge]
            for next_step in next_steps:
                extended_path = path+[next_step]
                if extended_path[0] == extended_path[-1]:
                    cycle = extended_path
                    commonprefix = os.path.commonprefix(cycle)
                    while commonprefix and commonprefix[-1] != '/':
                        commonprefix = commonprefix[:-1]
                    common_prefix_length = len(commonprefix)
                    for task in cycle:
                        msg = "\t{} depends on...\n".format(
                            task[common_prefix_length:])
                        sys.stderr.write(msg)
                    return
                extended_paths.append(extended_path)
        paths = extended_paths
        extended_paths = list()


def find_task_dependencies(starting_task):
    ''' from starting_task, recursively search for all prerequisite tasks '''
    unexplored_tasks = set([starting_task])
    explored_tasks = set()
    dependencies = set()
    while unexplored_tasks:
        task = unexplored_tasks.pop()
        task_prerequisites = get_symlink_dependencies(task)
        for prereq in task_prerequisites:
            if prereq == task or not is_a_task(prereq):
                continue
            dependencies.add((task, prereq))
            if prereq not in explored_tasks:
                unexplored_tasks.add(prereq)
        explored_tasks.add(task)
    return dependencies


def main(starting_task, verbose, required_parent_dir):
    ''' called from cmdline invocation '''
    dependencies = find_task_dependencies(starting_task)
    if verbose:
        for (task, prereq) in dependencies:
            msg = "{}\tdepends on\t{}\n".format(
                truncate_to_project(task), truncate_to_project(prereq))
            sys.stderr.write(msg)
    dependency_list = topological_sort(dependencies)
    execution_list = [path for path in dependency_list if is_a_task(path)]
    if verbose:
        sys.stderr.write("\nTask execution order\n--------------------\n")
    for path in execution_list:
        if not path.startswith(required_parent_dir):
            continue
        if verbose:
            sys.stderr.write("%s\n" % truncate_to_project(path))
        sys.stdout.write("%s\n" % path)


if __name__ == '__main__':
    args = get_args()
    if not isdir(os.path.join(args.starting_task, 'input')):
        sys.stderr.write("\n  start in a task directory with an input/\n")
        sys.exit(1)
    main(starting_task=abspath(args.starting_task),
         verbose=args.verbose,
         required_parent_dir=args.required_parent_dir)

# done.
