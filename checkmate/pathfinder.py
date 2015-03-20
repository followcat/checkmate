# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import collections

import numpy

import checkmate.runs
import checkmate.sandbox


@checkmate.fix_issue("checkmate/issues/pathfinder_find_runs.rst")
@checkmate.fix_issue("checkmate/issues/get_path_from_pathfinder.rst")
@checkmate.fix_issue("checkmate/issues/pathfinder_find_AC-OK_path.rst")
def _find_runs(application, target):
    """"""
    used_runs = _next_run(application, target, application.run_collection,
                    collections.OrderedDict())
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
            if target.compare_initial(box.application):
                used_runs[_run] = box
                return used_runs
            else:
                used_runs.update({_run: box})
                returned_runs = _next_run(box.application, target, runs,
                                    used_runs)
                if len(returned_runs) == 0:
                    del used_runs[_run]
                    box = checkmate.sandbox.Sandbox(\
                            type(application), application)
                    continue
                else:
                    return returned_runs
    return collections.OrderedDict()


def get_matrix_by_run(application, run):
    """
    >>> import checkmate.pathfinder
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> runs = app.run_collection
    >>> pp = runs[3]
    >>> checkmate.pathfinder.get_matrix_by_run(app, pp)
    matrix([[0, 0, 0, 1]])
    """
    runs_matrix = [0] * len(application.run_collection)
    runs_matrix[application.run_collection.index(run)] = 1
    run_matrix = numpy.matrix(runs_matrix)
    return run_matrix


def fill_matrix(runtime_app, app, run, des_matrix, depth=0, best=0):
    """
    >>> import checkmate.pathfinder
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> runs = app.run_collection
    >>> des_matrix = checkmate.pathfinder.get_matrix_by_run(app, runs[1])
    >>> checkmate.pathfinder.fill_matrix(app, app, runs[3], des_matrix)
    2
    >>> app.matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 0, 0],
            [0, 1, 0, 1],
            [1, 0, 0, 0]])
    """
    if best and depth > best:
        return best
    followed_runs = checkmate.runs.followed_runs(app, run)
    runtime_app.matrix = app.matrix
    runtime_app.runs_found = app.runs_found
    if (des_matrix * app.matrix.getT()).sum():
        best = depth
    for run in followed_runs:
        run_index = app.run_collection.index(run)
        if app.runs_found[run_index] is True:
            continue
        box = checkmate.sandbox.Sandbox(type(app), app)
        box.application.matrix = runtime_app.matrix
        box.application.runs_found = runtime_app.runs_found
        box.application.run_collection = runtime_app.run_collection
        if box(run) is False:
            continue
        fill_depth = fill_matrix(runtime_app, box.application, run,
                                 des_matrix, depth + 1, best)
        if best == 0 or fill_depth < best:
            best = fill_depth
    return best


def get_path_from_matrix(ori_matrix, des_matrix, app_matrix, path):
    """
    >>> import checkmate.runs
    >>> import checkmate.sandbox
    >>> import checkmate.pathfinder
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> runs  = app.run_collection
    >>> _run = runs[3]
    >>> des_matrix = checkmate.pathfinder.get_matrix_by_run(app, runs[1])
    >>> des_matrix
    matrix([[0, 1, 0, 0]])
    >>> ori_matrix = checkmate.pathfinder.get_matrix_by_run(app, _run)
    >>> ori_matrix
    matrix([[0, 0, 0, 1]])
    >>> checkmate.pathfinder.fill_matrix(app, app, _run, des_matrix)
    2
    >>> path = []
    >>> checkmate.pathfinder.get_path_from_matrix(ori_matrix,
    ...     des_matrix, app.matrix, path)
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
