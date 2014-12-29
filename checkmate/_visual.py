def visual_states(dump_states, owner="", level=0):
    tab_space = ' ' * 6 * level
    return_str = ""
    for state, values in dump_states.items():
        state_str = """
{space}{owner}: {state} - {value}""".format(space=tab_space, owner=owner, state=state, value=values['value'])
        return_str += state_str
        attr_space_len = len(state_str) - len(values['value'].__str__())
        for name, value in values.items():
            if name != 'value':
                return_str += """
{space}{name}: {value}""".format(space=' ' * attr_space_len, name=name, value=value)
    return return_str
