__all__ = ['run_steps', 'run']


def visual_states(dump_states, level=0):
    return_str = ""
    tab_space = ' ' * 4 * level
    for _c, states in dump_states.items():
        if len(states) == 0:
            continue
        return_str += "\n{space}{owner}:".format(space=tab_space, owner=_c)
        for state, values in states.items():
            return_str += "\n{space}  {state}:".format(space=tab_space, state=state)
            for name, value in values.items():
                return_str += "\n{space}    {name}: {value}".format(space=tab_space, name=name, value=value)
    return return_str


def run_steps(run, level=0, show_states=True):
    visual_dump = run.visual_dump_steps()
    tab_space = ' ' * 4 * level
    string = "\n\
{space}|\n\
{space}|_____{incoming}".format(space=tab_space, incoming=visual_dump['incoming'])
    if len(visual_dump['outgoing']) < 2:
        string += "\n\
{space}    | {outgoing}".format(space=tab_space, outgoing=visual_dump['outgoing'])
    else:
        prefix = "\n{space}    | ['".format(space=tab_space)
        for _o in visual_dump['outgoing']:
            string += prefix + "{outgoing}".format(space=tab_space, outgoing=_o)
            prefix = "',\n{space}    |  '".format(space=tab_space)
        else:
            string += "']"
            
    if show_states:
        final_states = visual_states(visual_dump['states'], level + 1)
        string += "\n{final}".format(final=final_states)
    for element in run.nodes:
        string += run_steps(element, level + 1, show_states)
    return string


def run(run, level=0, show_states=True):
    return_str = '\n' + run.root.name + '\n' + '=' * len(run.root.name)
    if show_states:
        return_str += visual_states(run.visual_dump_initial(), level)
    return_str += run_steps(run, level, show_states)
    if show_states:
        return_str += visual_states(run.visual_dump_final(), level)
    return return_str
