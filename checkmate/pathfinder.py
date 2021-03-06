# This code is part of the checkmate project.
# Copyright (C) 2014-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import time

import checkmate.runs
import checkmate.sandbox


@checkmate.fix_issue("checkmate/issues/pathfinder_find_runs.rst")
@checkmate.fix_issue("checkmate/issues/get_path_from_pathfinder.rst")
@checkmate.fix_issue("checkmate/issues/pathfinder_find_AC-OK_path.rst")
def _find_runs(application, target, origin):
    """"""
    if target.collected_run is not None:
        target = target.collected_run
    if origin is not None and origin.collected_run is not None:
        origin = origin.collected_run
    exchanges = application.origin_exchanges()
    run, used_runs = find_path(application, [target], 
            exchanges, origin)
    return used_runs


def find_path(application, target_runs, exchanges, current_run=None):
    """
    find nearest untested run from current runtime state.
    this is used in condition of no run matches current runtime
    state.and we need to find a way to transform our runtime.
    it can also find the path to specified target.

    >>> import sample_app.application
    >>> import checkmate.pathfinder
    >>> import checkmate.runs
    >>> app = sample_app.application.TestData()
    >>> runs = app.run_collection()
    >>> exchanges = app.origin_exchanges()
    >>> target = [_r for _r in runs
    ...     if _r.exchanges[0].value == 'PBPP'][0]
    >>> run, path = checkmate.pathfinder.find_path(
    ...     app, [target], exchanges)
    >>> run.exchanges[0].value
    'PBPP'
    >>> len(path)
    2
    >>> (path[0].exchanges[0].value, path[1].exchanges[0].value)
    ('PBAC', 'PBRL')
    >>> target2 = [_r for _r in runs
    ...     if _r.exchanges[0].value == 'PBRL'][0]
    >>> run, path = checkmate.pathfinder.find_path(
    ...     app, [target, target2], exchanges)
    >>> run.exchanges[0].value
    'PBRL'
    >>> len(path)
    1
    >>> path[0].exchanges[0].value
    'PBAC'
    """
    run_list = []
    matrix = application._matrix
    runs = application._matrix_runs
    target_runs_indexes = [runs.index(item) for item in target_runs]
    if current_run is None:
        next_runs = []
        next_runs = checkmate.runs.followed_runs(application, exchanges)
        current_run_row = [runs.index(item) for item in next_runs]
    else:
        _index = runs.index(current_run)
        current_run_row = matrix[_index].nonzero()[1].tolist()[0]
    length = len(matrix.tolist())
    paths = [[item] for item in current_run_row]
    while len(paths) != 0:
        path = paths.pop(0)
        end = path[-1]
        children = matrix[end].nonzero()[1].tolist()[0]
        for child in children:
            if child in target_runs_indexes:
                ret_path = []
                box = checkmate.sandbox.Sandbox(type(application), application)
                for _index in path + [child]:
                    if not runs[_index].compare_initial(box.application):
                        break
                    box(runs[_index].exchanges)
                    ret_path.append(box.blocks)
                else:
                    return ret_path.pop(), ret_path
            elif len(path)+1 == length:  # cannot find path
                return None, []
            else:
                new_path = path[:]
                new_path.append(child)
                paths.append(new_path)

