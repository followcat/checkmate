def visual_states(dump_states, level=0):
    return_str = ""
    for _c, states in dump_states.items():
        tab_space = ' ' * 6 * level
        for state, values in states.items():
            state_str = """
{space}{owner}: {state} - {value}""".format(space=tab_space, owner=_c, state=state, value=values['value'])
            return_str += state_str
            attr_space_len = len(state_str) - len(values['value'].__str__())
            for name, value in values.items():
                if name != 'value':
                    return_str += """
{space}{name}: {value}""".format(space=' ' * attr_space_len, name=name, value=value)
    return return_str


def visual_run_steps(run, level=0):
    visual_dump = run.visual_dump_steps()
    tab_space = ' ' * 6 * level
    final_states = visual_states(visual_dump['states'], level + 1)
    string = """
{space}|
{space}|     +-----------------------+
{space}|     | {incoming}
{space}|_____|
{space}      | {outgoing}
{space}      +-----------------------+{final}
    """.format(space=tab_space, incoming=visual_dump['incoming'], outgoing=visual_dump['outgoing'], final=final_states)
    for element in run.nodes:
        string += visual_run_steps(element, level + 1)
    return string


def visual_run(run):
    return_str = visual_states(run.visual_dump_initial())
    return_str += visual_run_steps(run)
    return_str += visual_states(run.visual_dump_final())
    return return_str
