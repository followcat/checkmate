import time
import unittest.case

from freshen import *
from freshen.checks import *

import checkmate.component
import checkmate.runtime._pyzmq
import checkmate.runtime._runtime
import checkmate.runtime.registry
import checkmate.runtime.procedure
import checkmate.runtime.test_plan
import checkmate.partition_declarator

import sample_app.application

@Before
def before(sc):
    scc.system_under_test = ['C1']
    scc.runtime = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
    scc.runtime.setup_environment(scc.system_under_test)
    scc.runtime.start_test()
    time.sleep(3)
    scc.result = None
    scc.array_items = []

@Given("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$")
def set_initial(component_name, state, value):
    _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, component_name)
    scc.array_items.append([state, value, 'x'])
    

@When("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$")
def set_incoming(component, exchange, action):
    scc.array_items.insert(0, [exchange, 'x', action])

@Then("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$")
def set_final(component_name, state, value):
    _component = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, component_name)
    for i in range(len(scc.array_items)):
        if scc.array_items[i][0] == state:
            scc.array_items[i][2] = value
    exchange_module = scc.runtime.application.exchange_module
    state_modules = []
    for _name in scc.runtime.application.components.keys():
        state_modules.append(scc.runtime.application.components[_name].state_module)
    transition = checkmate.partition_declarator.new_procedure(scc.array_items, exchange_module, state_modules)
    for (procedure, *left_over) in checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData, [transition]):
        try:
            procedure(scc.system_under_test)
        except Exception as e:
            assert(isinstance(e, unittest.case.SkipTest))
            
    scc.runtime.stop_test()

