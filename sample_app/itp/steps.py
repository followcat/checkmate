import collections

import fresher


@fresher.Before
def before(sc):
    fresher.scc.exchange = collections.OrderedDict()
    fresher.scc.exchange['Init'] = collections.OrderedDict()
    fresher.scc.exchange['Action'] = collections.OrderedDict()
    fresher.scc.exchange['Final'] = collections.OrderedDict()

@fresher.Given("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$")
def set_initial(component_name, state, value):
    fresher.scc.exchange['Init'] ['component_name'] = component_name
    fresher.scc.exchange['Init'] ['state'] = state
    fresher.scc.exchange['Init'] ['value'] = value

@fresher.When("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$")
def set_incoming(component, exchange, action):
    fresher.scc.exchange['Action'] ['component_name'] = component
    fresher.scc.exchange['Action'] ['action'] = exchange
    fresher.scc.exchange['Action'] ['value'] = action

@fresher.Then("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$")
def set_final(component_name, state, value):
    fresher.scc.exchange['Final'] ['component_name'] = component_name
    fresher.scc.exchange['Final'] ['state'] = state
    fresher.scc.exchange['Final'] ['value'] = value

@fresher.After
def after(sc):
    if fresher.ftc.itp is None:
        fresher.ftc.itp = []
    fresher.ftc.itp.append(fresher.scc.exchange)
