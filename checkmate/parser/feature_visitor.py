#-*- coding: utf8 -*-

# Experimental - a non-nose runner for tests, may end up being compatible
# with Cucumber commandline

import os
import sys
import logging

import freshen.core
import freshen.context
import freshen.handlers
import freshen.stepregistry

import checkmate._utils
import checkmate._storage
import checkmate.partition_declarator


class FreshenHandlerProxy(object):
    """ Acts as a handler and proxies callback events to a list of actual handlers. """
        
    def __init__(self, handlers):
        self._handlers = handlers
    
    def __getattr__(self, attr):
        def proxy(*args, **kwargs):
            for h in self._handlers:
                method = getattr(h, attr)
                method(*args, **kwargs)
        return proxy


def run_scenario(step_registry, scenario, handler):
    
    runner = freshen.core.StepsRunner(step_registry)
    freshen.context.scc.clear()
    
    for hook_impl in step_registry.get_hooks('before', scenario.get_tags()):
        hook_impl.run(scenario)
    
    for step in scenario.iter_steps():
        
        called = False
        try:
            runner.run_step(step)
        except AssertionError as e:
            handler.step_failed(step, e)
            called = True
        except freshen.stepregistry.UndefinedStepImpl as e:
            handler.step_undefined(step, e)
            called = True
        except freshen.stepregistry.AmbiguousStepImpl as e:
            handler.step_ambiguous(step, e)
            called = True
        except Exception as e:
            handler.step_exception(step, e)
            called = True
        
    for hook_impl in step_registry.get_hooks('after', scenario.get_tags()):
        hook_impl.run(scenario)

def run_feature(step_registry, feature, handler):
    freshen.context.ftc.clear()
    for scenario in feature.iter_scenarios():
        run_scenario(step_registry, scenario, handler)
    if freshen.context.glc.itp_list is None:
        freshen.context.glc.itp_list = []
    freshen.context.glc.itp_list.append(freshen.context.ftc.itp)

def run_features(step_registry, features, handler):
    for feature in features:
        run_feature(step_registry, feature, handler)

def load_step_definitions(paths):
    loader = freshen.stepregistry.StepImplLoader()
    sr = freshen.stepregistry.StepImplRegistry(freshen.core.TagMatcher)
    for path in paths:
        loader.load_steps_impl(sr, path)
    return sr

def load_features(paths, language):
    result = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for feature_file in filenames:
                if feature_file.endswith(".feature"):
                    feature_file = os.path.join(dirpath, feature_file)
                    result.append(freshen.core.load_feature(feature_file, language))
    return result

def get_itp_from_feature(paths):
    """
        >>> import checkmate.parser.feature_visitor
        >>> len(checkmate.parser.feature_visitor.get_itp_from_feature(['/home/followcat/Projects/checkmate/sample_app/itp']))
        4
    """
    #logging.basicConfig(level=logging.DEBUG)
    freshen.context.glc.clear() 
    language = freshen.core.load_language('en')
    registry = load_step_definitions(paths)
    features = load_features(paths, language)
    handler = FreshenHandlerProxy([freshen.handlers.ConsoleHandler()])
    run_features(registry, features, handler)
    return freshen.context.glc.itp_list

def feature_new_produce(array_items, exchange_module, state_modules=[]):
    initial_state = []
    input = []
    final_state = []

    for each_exchange in array_items:
        for s_module in state_modules:
            if hasattr(s_module, checkmate.partition_declarator._to_interface(each_exchange['Init']['state'])):
                interface = getattr(s_module, checkmate.partition_declarator._to_interface(each_exchange['Init']['state']))
                cls = checkmate._utils.get_class_implementing(interface)
                initial_state.append(checkmate._storage.Data('states', interface, [each_exchange['Init']['value']]))

    for each_exchange in array_items:
        try:
            interface = getattr(exchange_module, checkmate.partition_declarator._to_interface(each_exchange['Action']['action']))
        except AttributeError:
            raise attributeError(exchange_module,__name__+' has no interface defined:'+_to_interface(each_exchange['Action']['action']))
        input.append(checkmate._storage.Data('exchanges', interface, [each_exchange['Action']['value']]))
        break

    for each_exchange in array_items:
        for s_module in state_modules:
            if hasattr(s_module, checkmate.partition_declarator._to_interface(each_exchange['Final']['state'])):
                interface = getattr(s_module, checkmate.partition_declarator._to_interface(each_exchange['Final']['state']))
                cls = checkmate._utils.get_class_implementing(interface)
                final_state.append(checkmate._storage.Data('states', interface, [each_exchange['Final']['value']]))

    ts = checkmate._storage.TransitionStorage(checkmate._storage.TransitionData(initial_state, input, final_state, []))
    return ts