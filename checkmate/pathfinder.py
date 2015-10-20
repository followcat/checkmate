# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import time

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


def find_path(application, target_runs, exchanges, current_run=None,
                skip_unsafe_run=False):
    """
    find nearest untested run from current runtime state.
    this is used in condition of no run matches current runtime
    state.and we need to find a way to transform our runtime.
    it can also find the path to specified target.

    >>> import sample_app.application
    >>> import checkmate.pathfinder
    >>> app = sample_app.application.TestData()
    >>> runs = app.run_collection()
    >>> exchanges = app.origin_exchanges()
    >>> target = [_r for _r in runs
    ...     if _r.exchanges[0].value == 'PBPP'][0]
    >>> run, path = checkmate.pathfinder.find_path(
    ...     app, [target], exchanges, skip_unsafe_run=True)
    >>> len(path)
    0
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
    for item in target_runs:
        if item.compare_initial(application):
            return item, []
    target_runs_indexes = [application._matrix_runs.index(item) \
                           for item in target_runs]
    box = checkmate.sandbox.Sandbox(type(application), application)
    if current_run is None:
        current_run_row = [application._matrix_runs.index(r) for r in \
                        followed_runs(application, exchanges)]
    else:
        current_run_row = matrix[application._matrix_runs.\
                            index(current_run)].nonzero()[1].tolist()[0]
    if skip_unsafe_run:
        skip_unsafe_runs(application, current_run_row)
    length = len(matrix.tolist())
    paths = [[item] for item in current_run_row]
    while len(paths) != 0:
        path = paths.pop(0)
        end = path[-1]
        children = matrix[end].nonzero()[1].tolist()[0]
        if skip_unsafe_run:
            skip_unsafe_runs(application, children)
        for child in children:
            if child in target_runs_indexes:
                ret_path = []
                for _index in path:
                    assert box(application._matrix_runs[_index].exchanges)
                    ret_path.append(box.blocks)
                return application._matrix_runs[child], ret_path
            elif len(path)+1 == length:  # cannot find path
                break
            else:
                new_path = path[:]
                new_path.append(child)
                paths.append(new_path)
    return None, []


def skip_unsafe_runs(application, indexes):
    for index in indexes:
        if application._matrix_runs[index] in [_tmp[0] for _tmp in \
            application._unsafe_runs]:
            indexes.remove(index)

@checkmate.fix_issue('checkmate/issues/pathfinding_from_safe_runs.rst')
def followed_runs(application, exchanges, current_run=None):
    """
    3 conditions:
        1. we find next runs by matrix
        2. current_run is None, find next runs by exchanges
        3. find next runs by exchanges and update matrix
    >>> import sample_app.application
    >>> import checkmate.sandbox
    >>> app = sample_app.application.TestData
    >>> exchanges = app.origin_exchanges()
    >>> box = checkmate.sandbox.Sandbox(app)
    >>> next_runs = [_r for _r in checkmate.pathfinder.followed_runs(
    ...     box.application, exchanges, None)]
    >>> next_runs[0].validate_items[0][0].value
    'PBAC'
    >>> box(next_runs[0].exchanges)
    True
    >>> next_runs = [_r for _r in checkmate.pathfinder.followed_runs(
    ...     box.application, exchanges, next_runs[0])]
    >>> next_runs[0].validate_items[0][0].value
    'PBRL'
    """
    _class = type(application)
    runs = application._matrix_runs
    next_runs = []
    if current_run is not None:
        if current_run in runs:
            _index = runs.index(current_run)
            if application._runs_found[_index]:
                for i in application._matrix[_index].nonzero()[1].tolist()[0]:
                    if runs[i] not in next_runs:
                        next_runs.append(runs[i])
                    yield runs[i]
    box = checkmate.sandbox.Sandbox(_class, application)
    for _exchange in exchanges:
        if _exchange in [_r.exchanges[0] for _r in next_runs]:
            continue
        box.restart()
        if box([_exchange]):
            _run = box.blocks
            if _run not in next_runs:
                next_runs.append(_run)
                application.update_matrix([_run], current_run)
                yield _run


def update_matrix(application, run, next_runs):
    path = None
    transform_runs = []
    for _run, _path in application._safe_runs:
        if run == _run:
            path = _path
        if _run in next_runs:
            if len(_path) > 0:
                transform_runs.append(_path[-1])
            else:
                transform_runs.append(_run)
    if path is not None:
        _current_run = run
        for _r in path:
            application.update_matrix([_r], _current_run)
            _current_run = _r
    for _r in transform_runs:
        application.update_matrix(next_runs, _r)
   

def filter_run(application, run, previous_run=None):
    """
        >>> import checkmate.pathfinder
        >>> import sample_app.application
        >>> app = sample_app.application.TestData()
        >>> app.reset()
        >>> app.start()
        >>> len(app._unsafe_runs)
        0
        >>> exchanges = app.origin_exchanges()
        >>> box = checkmate.sandbox.Sandbox(type(app), app)
        >>> box([ex for ex in exchanges if ex.value == 'PBAC'])
        True
        >>> run = box.blocks
        >>> checkmate.pathfinder.filter_run(app, run, None)
        >>> len(app._unsafe_runs)
        1
        >>> run in [tmp[0] for tmp in app._unsafe_runs]
        True
    """
    path = return_path(application, run)
    _unsafe_runs = []
    if previous_run is None or previous_run not in \
        [_tmp[0] for _tmp in application._unsafe_runs]:
        if path is not None:
            if (run, path) not in application._safe_runs:
                application._safe_runs.append((run, path))
        else:
            _unsafe_runs.append((run, path))
    else:
        _unsafe_runs.append((run, path))
    application._unsafe_runs.extend([_tmp for _tmp in _unsafe_runs
        if _tmp not in application._unsafe_runs])

    
def return_path(application, run):
    """
    run are safe only when there is one-step way found
    that can use to transform to initial states
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import sample_app.application
        >>> app = sample_app.application.TestData()
        >>> box = checkmate.sandbox.Sandbox(type(app), app)
        >>> box2 = checkmate.sandbox.Sandbox(type(app), app)
        >>> exchanges = app.origin_exchanges()
        >>> pbac = [ex for ex in exchanges if ex.value == 'PBAC'][0]
        >>> pbrl = [ex for ex in exchanges if ex.value == 'PBRL'][0]
        >>> box([pbac]), box2([pbac])
        (True, True)
        >>> box2([pbrl])
        True
        >>> run_pbac_ok = box.blocks
        >>> run_pbrl = box2.blocks
        >>> path = checkmate.pathfinder.return_path(box.application,
        ...     run_pbac_ok)
        >>> path is not None
        False
        >>> path = checkmate.pathfinder.return_path(box.application,
        ...     run_pbrl)
        >>> path is not None
        True
        >>> box([pbrl]), box2([pbac])
        (True, True)
        >>> run_pbac_er = box2.blocks
        >>> run_pbac_er.compare_initial(box.application)
        True
        >>> path = checkmate.pathfinder.return_path(box.application,
        ...     run_pbac_er)
        >>> path is not None
        True
    """
    path = None
    if run.compare_initial(application):
        _cls = type(application)
        box = checkmate.sandbox.Sandbox(_cls, application)
        _states0 = application.copy_states()
        box(run.exchanges)
        _states1 = box.application.copy_states()
        if _states0 == _states1:
            path = []
        else:
            exchanges = box.application.origin_exchanges()
            for _ex in exchanges[:]:
                sandbox = checkmate.sandbox.Sandbox(_cls, box.application)
                if sandbox([_ex]):
                    tmp_run = sandbox.blocks
                    _states2 = sandbox.application.copy_states()
                    if  _states0 == _states2:
                        path = [tmp_run]
                        break
    return path

