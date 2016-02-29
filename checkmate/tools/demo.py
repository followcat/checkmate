# This code is part of the checkmate project.
# Copyright (C) 2015-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate._visual
import checkmate.pathfinder
import checkmate.runtime._pyzmq
import checkmate.runtime._runtime
import checkmate.runtime.test_plan

import sample_app.application


runs = []
runtime = checkmate.runtime._runtime.Runtime(
            sample_app.application.TestData,
            checkmate.runtime._pyzmq.Communication, True)
app = runtime.application
runs = []

runtime.setup_environment(['C1'])

def start(r=runtime):
    r.start_test()

def stop(r=runtime):
    r.stop_test()

def show_run(run):
    print(checkmate._visual.run(run, show_states=False))

def show_all_runs(run_list=runs):
    for _r in run_list:
        show_run(_r)

def how_many_runs(run_list=runs):
    return len(runs)

def can_run(run, r=runtime):
    return run.compare_initial(r.application)

def show_path(run):
    show_all_runs(checkmate.pathfinder._find_runs(
                    runtime.application, run))
        
def run_transition(name):
    for component in app.component:
        transition = app.components[component].block_by_name(name)
        if transition is not None:
            break
    else:
        return None
    r = checkmate.runtime.test_plan.get_runs_from_transition(app, t)
    if r[0].compare_initial(app):
        runtime.execute(r[0])
    else:
        print('Need a path')
    

