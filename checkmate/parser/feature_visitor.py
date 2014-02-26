#-*- coding: utf8 -*-

# Experimental - a non-nose runner for tests, may end up being compatible
# with Cucumber commandline

import sys
import logging

import fresher.cuke
import fresher.core
import fresher.context
import fresher.stepregistry

import checkmate._utils
import checkmate._storage
import checkmate.partition_declarator


def new_load_step_definitions(paths):
    """
        the load_steps_impl function at load_step_definitions in fresher.cuke only has 2 arguments,has problem:

        >>> import fresher.cuke
        >>> import fresher.core
        >>> import fresher.context
        >>> import fresher.stepregistry
        >>> paths = sys.argv[1:] or ["features"]
        >>> fresher.context.glc.clear() 
        >>> language = fresher.core.load_language('en')
        >>> registry = fresher.cuke.load_step_definitions(paths)
        Traceback (most recent call last):
        ...
        TypeError: load_steps_impl() missing 1 required positional argument: 'path'
        >>> registry = new_load_step_definitions(paths)
    """
    loader = fresher.stepregistry.StepImplLoader()
    sr = fresher.stepregistry.StepImplRegistry(fresher.core.TagMatcher)
    for path in paths:
        loader.load_steps_impl(sr, path, path)
    return sr

def new_run_features(step_registry, features, handler):
    if fresher.context.glc.itp_list is None:
        fresher.context.glc.itp_list = []
    for feature in features:
        fresher.cuke.run_feature(step_registry, feature, handler)
        fresher.context.glc.itp_list.append(fresher.context.ftc.itp)

def get_itp_from_feature(language,paths):
    """
        >>> import os
        >>> import checkmate.parser.feature_visitor
        >>> itp_path = 'sample_app/itp/itp_features'
        >>> itp_absolute_path = os.path.join(os.getenv('CHECKMATE_HOME'),itp_path)
        >>> len(checkmate.parser.feature_visitor.get_itp_from_feature('en',[itp_absolute_path]))
        4
    """
    #logging.basicConfig(level=logging.DEBUG)
    fresher.context.glc.clear() 
    language_set = fresher.core.load_language(language)
    registry = new_load_step_definitions(paths)
    features = fresher.cuke.load_features(paths, language_set)
    handler = fresher.cuke.FresherHandlerProxy([fresher.cuke.FresherHandler()])
    new_run_features(registry, features, handler)
    return fresher.context.glc.itp_list

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