import collections

import checkmate.sandbox


@checkmate.fix_issue("checkmate/issues/pathfinder_find_runs.rst")
@checkmate.report_issue("checkmate/issues/pathfinder_find_AC-OK_path.rst", failed=1)
def _find_runs(application, target):
    """"""
    used_runs = _next_run(application, target, application.run_collection, collections.OrderedDict())
    return used_runs


@checkmate.fix_issue("checkmate/issues/pathfinder_next_run.rst")
def _next_run(application, target, runs, used_runs):
    """"""
    for _run in runs:
        if _run in used_runs:
            continue
        box = checkmate.sandbox.Sandbox(application)
        box(_run.root)
        if box.is_run:
            if box.application.compare_states(target):
                used_runs[_run] = box
                return used_runs
            else:
                used_runs.update({_run: box})
                returned_runs = _next_run(box.application, target, runs, used_runs)
                if len(returned_runs) == 0:
                    del used_runs[_run]
                    box = checkmate.sandbox.Sandbox(application)
                    continue
                else:
                    return returned_runs
    return collections.OrderedDict()
