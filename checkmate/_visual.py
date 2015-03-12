# This code is part of the checkmate project.
# Copyright (C) 2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

def visual_states(dump_states, level=0):
    return_str = ""
    tab_space = ' ' * 6 * level
    for _c, states in dump_states.items():
        if len(states) == 0:
            continue
        return_str += "\n{space}{owner}:".format(space=tab_space, owner=_c)
        for state, values in states.items():
            return_str += "\n{space}  {state}:".format(space=tab_space, state=state)
            for name, value in values.items():
                return_str += "\n{space}    {name}: {value}".format(space=tab_space, name=name, value=value)
    return return_str


def visual_run_steps(run, level=0):
    visual_dump = run.visual_dump_steps()
    tab_space = ' ' * 6 * level
    final_states = visual_states(visual_dump['states'], level + 1)
    string = "\n\
{space}|\n\
{space}|_____|-{incoming}\n\
{space}      |-{outgoing}\n{final}".format(space=tab_space, incoming=visual_dump['incoming'], outgoing=visual_dump['outgoing'], final=final_states)
    for element in run.nodes:
        string += visual_run_steps(element, level + 1)
    return string


def visual_run(run, level=0):
    return_str = visual_states(run.visual_dump_initial(), level)
    return_str += visual_run_steps(run, level)
    return_str += visual_states(run.visual_dump_final(), level)
    return return_str
