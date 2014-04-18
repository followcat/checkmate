import builtins

import fresher


setattr(builtins, '_', lambda x: x)


@fresher.Before
def before(sc):
    fresher.scc.dict_items =   {
        "initial": [],
        "incoming": [],
        "final": []
        }


@fresher.Given(_("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$"))
def set_initial(component_name, state, value):
    fresher.scc.dict_items['initial'].append({state: value})

@fresher.When(_("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$"))
def set_incoming(component, exchange, action):
    fresher.scc.dict_items['incoming'].append({exchange: action})

@fresher.Then(_("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$"))
def set_final(component_name, state, value):
    fresher.scc.dict_items['final'].append({state: value})

@fresher.After
def after(sc):
    if fresher.ftc.scenarios is None:
        fresher.ftc.scenarios = []
    fresher.ftc.scenarios.append(fresher.scc.dict_items)
