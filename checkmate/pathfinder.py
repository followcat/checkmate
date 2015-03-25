# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate.sandbox


@checkmate.fix_issue("checkmate/issues/pathfinder_find_runs.rst")
@checkmate.fix_issue("checkmate/issues/get_path_from_pathfinder.rst")
@checkmate.fix_issue("checkmate/issues/pathfinder_find_AC-OK_path.rst")
def _find_runs(application, target):
    """"""
    used_runs = _next_run(application, target, application.run_collection(),
                    list())
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
