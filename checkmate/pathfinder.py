# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import numpy

import checkmate.runs
import checkmate.sandbox


@checkmate.fix_issue("checkmate/issues/pathfinder_find_runs.rst")
@checkmate.fix_issue("checkmate/issues/get_path_from_pathfinder.rst")
@checkmate.fix_issue("checkmate/issues/pathfinder_find_AC-OK_path.rst")
def _find_runs(application, target, origin=None):
    """"""
    if origin is None:
        # Hardcoded value that fits sample_app application
        origin = application.run_collection()[-1]
    if target.collected_run is not None:
        target = target.collected_run
    if origin.collected_run is not None:
        origin = origin.collected_run
    path = []
    ori_matrix = checkmate.pathfinder.get_matrix_by_run(application, origin)
    des_matrix = checkmate.pathfinder.get_matrix_by_run(application, target)
    checkmate.pathfinder.fill_matrix(
        application, application, origin, des_matrix)
    get_path_from_matrix(ori_matrix, des_matrix, application._matrix, path)

    used_runs = []
    checkmate.pathfinder.get_runs_from_path(used_runs, path, origin.final,
        application, des_matrix, target)
    return used_runs[:-1]


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


def get_runs_from_path(runs, path, diff_set, app, des_matrix, nr):
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
    >>> des_matrix = checkmate.pathfinder.get_matrix_by_run(app, nr)
    >>> ori_matrix = checkmate.pathfinder.get_matrix_by_run(app, r0)
    >>> diff_set = r0.final
    >>> checkmate.pathfinder.fill_matrix(app, app, r0, des_matrix)
    True
    >>> path = []
    >>> checkmate.pathfinder.get_path_from_matrix(ori_matrix,
    ...     des_matrix, app._matrix, path)
    True
    >>> path_runs = []
    >>> checkmate.pathfinder.get_runs_from_path(path_runs, path,
    ... diff_set, app, des_matrix, nr)
    True
    >>> [_r.root.name for _r in path_runs][:-1]
    ["Press C2's Button AC", "Press C2's Button RL"]
    """
    if len(path) == 0:
        return False
    pp1 = path[0].nonzero()[1].tolist()[0]
    for t1 in range(len(pp1)):
        index1 = pp1[t1]
        run1 = app.run_collection()[index1]
        diff_set1 = diff_set.union(run1.final)
        if len(nr.initial.difference(diff_set1)) > len(nr.initial.difference(diff_set)):
            continue                   
        if not run1.compare_initial(app):
            continue
        runs.append(run1)
        v1 = get_matrix_by_run(app, run1)
        if (des_matrix*v1.getT()).sum() > 0:
            return True
        else:
            box = checkmate.sandbox.Sandbox(type(app), app)
            box(run1)
            if checkmate.pathfinder.get_runs_from_path(runs, path[1:], diff_set1, box.application, des_matrix, nr):
                return True
            else:
                runs.pop()
    return False

