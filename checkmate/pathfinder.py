# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
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
    run, used_runs = find_path_to_nearest_target(application, [target], 
            exchanges, origin)
    return used_runs


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
    >>> nr = runs[2]
    >>> path_runs = []
    >>> checkmate.pathfinder.get_runs(path_runs, app, r0, nr)
    True
    >>> [_r.root.name for _r in path_runs]
    ['C2 callback on AC button', 'C2 callback on AC button']
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
        # Modify to support sample_app, diff_set hasn't RequestState
        if (not diff_set.issuperset(run1.initial) and not
           run1.initial.issuperset(diff_set)):
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
        select_partition_class = [_f.partition_class for _f in run.final]
        for di in diff_set:
            if di.partition_class in select_partition_class:
                diff_set1.remove(di)
        if (checkmate.pathfinder.get_runs(runs,
                app, run, nr, diff_set1.union(run.final_alike()), depth + 1)):
            return True
        else:
            runs.pop()
    return False


def find_path_to_nearest_target(application, target_runs, exchanges, current_run=None):
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
    >>> run, path = checkmate.pathfinder.find_path_to_nearest_target(
    ...     app, [target], exchanges)
    >>> run.exchanges[0].value
    'PBPP'
    >>> len(path)
    2
    >>> (path[0].exchanges[0].value, path[1].exchanges[0].value)
    ('PBAC', 'PBRL')
    >>> target2 = [_r for _r in runs
    ...     if _r.exchanges[0].value == 'PBRL'][0]
    >>> run, path = checkmate.pathfinder.find_path_to_nearest_target(
    ...     app, [target, target2], exchanges)
    >>> run.exchanges[0].value
    'PBRL'
    >>> len(path)
    1
    >>> path[0].exchanges[0].value
    'PBAC'
    """
    run_list = []
    matrix = application.run_matrix
    target_runs_indexes = [application.run_matrix_index.index(item) \
                           for item in target_runs]
    box = checkmate.sandbox.Sandbox(type(application), application)
    if current_run is None:
        next_runs = []
        next_runs = checkmate.runs.find_next_runs(application, exchanges)
        current_run_row = [application.run_matrix_index.index(item)
                             for item in next_runs]
    else:
        current_run_row = matrix[application.run_matrix_index.\
                            index(current_run)].nonzero()[1].tolist()[0]
    length = len(matrix.tolist())
    paths = [[item] for item in current_run_row]
    while len(paths) != 0:
        path = paths.pop(0)
        end = path[-1]
        children = matrix[end].nonzero()[1].tolist()[0]
        for child in children:
            if child in target_runs_indexes:
                ret_path = []
                for _index in path:
                    assert box(application.run_matrix_index[_index].exchanges)
                    ret_path.append(box.blocks)
                return application.run_matrix_index[child], ret_path
            elif len(path)+1 == length:  # cannot find path
                return None, []
            else:
                new_path = path[:]
                new_path.append(child)
                paths.append(new_path)
