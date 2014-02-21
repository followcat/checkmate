import collections

import fresher


@fresher.Before
def before(sc):
    fresher.scc.exchange = {}
    fresher.scc.exchange['Init'] = []
    fresher.scc.exchange['Action'] = []
    fresher.scc.exchange['Final'] = []

@fresher.Given("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$")
def set_initial(component_name, state, value):
    _initial = {}
    _initial['component_name'] = component_name
    _initial['state'] = state
    _initial['value'] = value
    fresher.scc.exchange['Init'].append(_initial)

@fresher.When("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$")
def set_incoming(component, exchange, action):
    _incoming = {}
    _incoming['component_name'] = component
    _incoming['action'] = exchange
    _incoming['value'] = action
    fresher.scc.exchange['Action'].append(_incoming)

@fresher.Then("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$")
def set_final(component_name, state, value):
    _final = {}
    _final['component_name'] = component_name
    _final['state'] = state
    _final['value'] = value
    fresher.scc.exchange['Final'].append(_final)

@fresher.After
def after(sc):
    if fresher.ftc.itp is None:
        fresher.ftc.itp = []
    fresher.ftc.itp.append(fresher.scc.exchange)
