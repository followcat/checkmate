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
    if origin.collected_run is not None:
        origin = origin.collected_run
    used_runs = []
    checkmate.pathfinder.get_runs(used_runs, application, origin, target)
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


def find_untested_path(application, next_runs, target_runs,
                       history_runs, origin_exchanges):
    """
    find path of nearest untested run.

    >>> import sample_app.application
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.pathfinder as pf
    >>> import checkmate.runs
    >>> com = checkmate.runtime._pyzmq.Communication
    >>> app = sample_app.application.TestData
    >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
    >>> r.setup_environment(['C2'])
    >>> r.start_test()
    >>> runs = app.run_collection()
    >>> origin_exchanges = checkmate.runs.get_origin_exchanges(app)
    >>> r.execute(runs[0])
    >>> checkmate.runs.find_next_exchanges(r.application,origin_exchanges,0) #doctest: +ELLIPSIS
    [<sample_app.exchanges.ExchangeButton ...
    >>> r.execute(runs[1])
    >>> checkmate.runs.find_next_exchanges(r.application,origin_exchanges,1) #doctest: +ELLIPSIS
    [<sample_app.exchanges.ExchangeButton object ...
    >>> r.execute(runs[2])
    >>> checkmate.runs.find_next_exchanges(r.application,origin_exchanges,2) #doctest: +ELLIPSIS
    [<sample_app.exchanges.ExchangeButton object at ...
    >>> untested_runs = [runs[3]]
    >>> tested_runs = [runs[0],runs[1],runs[2]]
    >>> run, path = pf.find_untested_path(r.application, [runs[1]],
    ...                         untested_runs, tested_runs, origin_exchanges)
    >>> runs.index(run)
    3
    >>> runs.index(path[0])
    1
    >>> r.stop_test()

    """
    if len(target_runs) == 0:
        return None, None
    paths = []
    for next_run in next_runs:
        sandbox = checkmate.sandbox.Sandbox(type(application), application)
        assert sandbox(next_run.exchanges)
        paths.append(dict({'path': [next_run],
                           'application': sandbox.application}))
    while len(paths) != 0:
        path = paths.pop(0)
        end_index = history_runs.index(path['path'][-1])
        for next_exchange_index in\
                application.reliable_matrix[
                    end_index].nonzero()[1].tolist()[0]:
            sandbox = checkmate.sandbox.Sandbox(type(application),
                                                path['application'])
            if sandbox([origin_exchanges[next_exchange_index]]):
                if sandbox.blocks in target_runs:
                    return sandbox.blocks, path['path']
                else:
                    new_path = {'path': path['path'][:],
                                'application': sandbox.application}
                    new_path['path'].append(sandbox.blocks)
                    paths.append(new_path)

def find_path_to_nearest_target(application, next_runs, target_runs):
    """
    find nearest untested run from current runtime state.
    this is used in condition of no run matches current runtime
    state.and we need to find a way to transform our runtime.
    it can also find the path to specified target.

    >>> import sample_app.application
    >>> import checkmate.pathfinder
    >>> app = sample_app.application.TestData()
    >>> runs = app.run_collection()
    >>> app.run_matrix_index.append(runs[0])  # update run_matrix_index
    >>> app.update_matrix([runs[1]], runs[0])
    >>> app.update_matrix([runs[2], runs[3]], runs[1])
    >>> app.update_matrix([runs[1]], runs[2])
    >>> run, path = checkmate.pathfinder.find_path_to_nearest_target(app, [runs[1]], [runs[3]])
    >>> runs.index(run)
    3
    >>> path #doctest: +ELLIPSIS
    [<checkmate.runs.Run ...
    >>> runs.index(path[0])
    1
    """
    matrix = application.run_matrix
    target_runs_indexes = [application.run_matrix_index.index(item) \
                           for item in target_runs]
    current_run_row = [application.run_matrix_index.index(item) \
                       for item in next_runs]
    length = len(matrix.tolist())
    paths = [[item] for item in current_run_row]
    while len(paths) != 0:
        path = paths.pop(0)
        end = path[-1]
        children = matrix[end].nonzero()[1].tolist()[0]
        for child in children:
            if child in target_runs_indexes:
                return application.run_matrix_index[child], \
                       [application.run_matrix_index[i] for i in path]
            elif len(path)+1 == length:  # cannot find path
                return None, None
            else:
                new_path = path[:]
                new_path.append(child)
                paths.append(new_path)