import collections

import fresher


@fresher.Before
def before(sc):
    fresher.scc.array_items = []

@fresher.Given("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$")
def set_initial(component_name, state, value):
    fresher.scc.array_items.append([state, value, 'x'])

@fresher.When("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$")
def set_incoming(component, exchange, action):
    fresher.scc.array_items.insert(0, [exchange, 'x', action])

@fresher.Then("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$")
def set_final(component_name, state, value):
    for _item in fresher.scc.array_items:
        if _item[0] == state:
            _item[2] = value

@fresher.After
def after(sc):
    if fresher.ftc.scenarios is None:
        fresher.ftc.scenarios = []
    fresher.ftc.scenarios.append(fresher.scc.array_items)
