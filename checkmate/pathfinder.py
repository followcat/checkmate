# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import time

import numpy

import checkmate.runs
import checkmate.sandbox


@checkmate.fix_issue("checkmate/issues/pathfinder_find_runs.rst")
@checkmate.fix_issue("checkmate/issues/get_path_from_pathfinder.rst")
@checkmate.fix_issue("checkmate/issues/pathfinder_find_AC-OK_path.rst")
def _find_runs(application, target, origin):
    """"""
    if target.collected_run is not None:
        target = target.collected_run
    if origin.collected_run is not None:
        origin = origin.collected_run
    used_runs = []
    checkmate.pathfinder.get_runs(used_runs, application, origin, target)
    return used_runs


@checkmate.fix_issue("checkmate/issues/pathfinder_next_run.rst")
def _next_run(application, target, runs, used_runs):
    """"""
    for _run in runs:
        if _run in used_runs:
            continue
        box = checkmate.sandbox.Sandbox(type(application), application)
        box(_run)
        if box.is_run:
            used_runs.append(_run)
            if target.compare_initial(box.application):
                return used_runs
            else:
                returned_runs = _next_run(box.application, target, runs,
                                    used_runs)
                if len(returned_runs) == 0:
                    used_runs.pop()
                    box = checkmate.sandbox.Sandbox(\
                            type(application), application)
                    continue
                else:
                    return returned_runs
    return list()


def get_matrix_by_run(application, run):
    """
    >>> import checkmate.pathfinder
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> runs = app.run_collection()
    >>> pp = runs[3]
    >>> checkmate.pathfinder.get_matrix_by_run(app, pp)
    matrix([[0, 0, 0, 1]])
    """
    runs_matrix = [0] * len(application.run_collection())
    runs_matrix[application.run_collection().index(run)] = 1
    run_matrix = numpy.matrix(runs_matrix)
    return run_matrix


def fill_matrix(runtime_app, app, run, des_matrix):
    """
    >>> import checkmate.pathfinder
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> runs = app.run_collection()
    >>> des_matrix = checkmate.pathfinder.get_matrix_by_run(app, runs[1])
    >>> checkmate.pathfinder.fill_matrix(app, app, runs[3], des_matrix)
    True
    >>> app._matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 0, 0],
            [0, 1, 0, 1],
            [1, 0, 0, 0]])
    """
    followed_runs = checkmate.runs.followed_runs(app, run)
    if (des_matrix * app._matrix.getT()).any(1):
        return True
    for run in followed_runs:
        run_index = app.run_collection().index(run)
        if app._runs_found[run_index] is True:
            continue
        box = checkmate.sandbox.Sandbox(type(app), app)
        if box(run) is False:
            continue
        if fill_matrix(runtime_app, box.application, run, des_matrix) is True:
            return True
    return False


def get_path_from_matrix(ori_matrix, des_matrix, app_matrix, path):
    """
    >>> import checkmate.runs
    >>> import checkmate.sandbox
    >>> import checkmate.pathfinder
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> runs  = app.run_collection()
    >>> _run = runs[3]
    >>> des_matrix = checkmate.pathfinder.get_matrix_by_run(app, runs[1])
    >>> des_matrix
    matrix([[0, 1, 0, 0]])
    >>> ori_matrix = checkmate.pathfinder.get_matrix_by_run(app, _run)
    >>> ori_matrix
    matrix([[0, 0, 0, 1]])
    >>> checkmate.pathfinder.fill_matrix(app, app, _run, des_matrix)
    True
    >>> path = []
    >>> checkmate.pathfinder.get_path_from_matrix(ori_matrix,
    ...     des_matrix, app._matrix, path)
    True
    >>> path
    [matrix([[1, 0, 0, 0]]), matrix([[0, 0, 1, 0]]), matrix([[0, 1, 0, 1]])]
    """
    new_ori_matrix = ori_matrix * app_matrix
    path.append(new_ori_matrix)
    if (des_matrix * new_ori_matrix.getT()).sum() > 0:
        return True
    if get_path_from_matrix(new_ori_matrix, des_matrix, app_matrix, path):
        return True


class Timer():
    def __init__(self, limit):
        self.start = 0
        self.limit = limit

    def reset(self):
        self.start = time.time()

    def check(self):
        return (time.time() < self.start + self.limit)

timer = Timer(5)

def fail_fast(depth):
    global timer
    if depth == 0:
        timer.reset()
        return False
    else:
        return not timer.check()
    
def get_runs(runs, app, ori_run, nr, diff_set=None, depth=0):
    """
    >>> import checkmate.runs
    >>> import checkmate.sandbox
    >>> import checkmate.pathfinder
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> runs  = app.run_collection()
    >>> r0 = runs[3]
    >>> nr = runs[1]
    >>> path_runs = []
    >>> checkmate.pathfinder.get_runs(path_runs, app, r0, nr)
    True
    >>> [_r.root.name for _r in path_runs]
    ["Press C2's Button AC", "Press C2's Button RL"]
    """
    if fail_fast(depth):
        return False

    if diff_set is None:
        diff_set = set()
        for _state in app.state_list():
            for _store in _state.partition_storage.storage:
                if _state.value == _store.value:
                    diff_set.add(_store)
                    break

    if depth == app.path_finder_depth:
        return False
    next_runs = checkmate.runs.followed_runs(app, ori_run)
    for run1 in next_runs[:]:
        new_state_set = set(diff_set)
        if not new_state_set.issuperset(run1.initial):
            next_runs.remove(run1)
            continue
        if run1 == nr:
            return True
        if run1 == ori_run or run1 in runs:
            next_runs.pop(next_runs.index(run1))
            continue

    nr_classes = [s.partition_class for s in nr.initial.difference(diff_set)]
    next_runs_1 = filter(lambda r: len(nr.initial.intersection(
                    r.final.difference(diff_set))) > 0, next_runs)
    next_runs_2 = filter(lambda r: len(nr.initial.intersection(
                    r.final.difference(diff_set))) == 0, next_runs)
    sorted_list_1 = sorted(next_runs_1, key=lambda r: len(
                        nr.initial.intersection(r.final.difference(diff_set))),
                        reverse=True)
    sorted_list_2 = sorted(next_runs_2, key=lambda r: len([s for s in r.final
                        if s not in r.initial and
                        s.partition_class in nr_classes]), reverse=True)

    for run in sorted_list_1 + sorted_list_2:
        runs.append(run)
        diff_set1 = set(diff_set)
        for di in diff_set:
            if (di.partition_class in
                    [_f.partition_class for _f in run.final]):
                diff_set1.remove(di)
        if (checkmate.pathfinder.get_runs(runs,
                app, run, nr, diff_set1.union(run.final), depth + 1)):
            return True
        else:
            runs.pop()
    return False
