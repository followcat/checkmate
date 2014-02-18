import collections

import freshen


@freshen.Before
def before(sc):
    freshen.scc.exchange = collections.OrderedDict()
    freshen.scc.exchange['Init'] = collections.OrderedDict()
    freshen.scc.exchange['Action'] = collections.OrderedDict()
    freshen.scc.exchange['Final'] = collections.OrderedDict()

@freshen.Given("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$")
def set_initial(component_name, state, value):
    freshen.scc.exchange['Init'] ['component_name'] = component_name
    freshen.scc.exchange['Init'] ['state'] = state
    freshen.scc.exchange['Init'] ['value'] = value

@freshen.When("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$")
def set_incoming(component, exchange, action):
    freshen.scc.exchange['Action'] ['component_name'] = component
    freshen.scc.exchange['Action'] ['action'] = exchange
    freshen.scc.exchange['Action'] ['value'] = action

@freshen.Then("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$")
def set_final(component_name, state, value):
    freshen.scc.exchange['Final'] ['component_name'] = component_name
    freshen.scc.exchange['Final'] ['state'] = state
    freshen.scc.exchange['Final'] ['value'] = value

@freshen.After
def after(sc):
    if freshen.ftc.itp is None:
        freshen.ftc.itp = []
    freshen.ftc.itp.append(freshen.scc.exchange)
