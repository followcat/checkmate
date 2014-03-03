#-*- coding: utf8 -*-

# Experimental - a non-nose runner for tests, may end up being compatible
# with Cucumber commandline

import os
import sys
import logging

import fresher
import fresher.cuke
import fresher.core
import fresher.stepregistry

import checkmate.partition_declarator


def new_load_step_definitions(paths):
    """
        the load_steps_impl function at load_step_definitions in fresher.cuke only has 2 arguments,has problem:

        >>> import fresher
        >>> import fresher.cuke
        >>> import fresher.core
        >>> import fresher.stepregistry
        >>> paths = sys.argv[1:] or ["features"]
        >>> fresher.glc.clear() 
        >>> language = fresher.core.load_language('en')
        >>> registry = fresher.cuke.load_step_definitions(paths)
        Traceback (most recent call last):
        ...
        TypeError: load_steps_impl() missing 1 required positional argument: 'path'
        >>> registry = new_load_step_definitions(paths)
    """
    loader = fresher.stepregistry.StepImplLoader()
    sr = fresher.stepregistry.StepImplRegistry(fresher.core.TagMatcher)
    cwd = os.getcwd()
    for path in paths:
        loader.load_steps_impl(sr, cwd, path)
    return sr

def new_run_features(step_registry, features, handler):
    if fresher.glc.array_list is None:
        fresher.glc.array_list = []
    for feature in features:
        fresher.cuke.run_feature(step_registry, feature, handler)
        fresher.glc.array_list.extend(fresher.ftc.scenarios)

def get_array_list(language,paths):
    """
        >>> import os
        >>> import checkmate.parser.feature_visitor
        >>> itp_path = 'sample_app/itp/itp_features'
        >>> itp_absolute_path = os.path.join(os.getenv('CHECKMATE_HOME'),itp_path)
        >>> len(checkmate.parser.feature_visitor.get_array_list('en',[itp_absolute_path]))
        4
    """
    #logging.basicConfig(level=logging.DEBUG)
    fresher.glc.clear() 
    language_set = fresher.core.load_language(language)
    registry = new_load_step_definitions(paths)
    features = fresher.cuke.load_features(paths, language_set)
    handler = fresher.cuke.FresherHandlerProxy([fresher.cuke.FresherHandler()])
    new_run_features(registry, features, handler)
    return fresher.glc.array_list

def get_transitions_from_features(exchange_module, state_modules):
    """
            >>> import sample_app.application
            >>> import checkmate.component
            >>> import checkmate.parser.feature_visitor
            >>> import os
            >>> import checkmate.state
            >>> import checkmate.exchange
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> state_modules = []
            >>> for name in list(a.components.keys()):
            ...     state_modules.append(a.components[name].state_module)
            >>> transitions = checkmate.parser.feature_visitor.get_transitions_from_features(a.exchange_module, state_modules)
            >>> len(transitions)
            4
            >>> transitions # doctest: +ELLIPSIS
            [<checkmate._storage.TransitionStorage object at ...
        """
    language = 'zh-CN'
    itp_path = 'sample_app/itp/itp_zh_features'
    itp_absolute_path = os.path.join(os.getenv('CHECKMATE_HOME'),itp_path)
    array_list = get_array_list(language,[itp_absolute_path])
    initial_transitions = []
    for array_items in array_list:
        initial_transitions.append(checkmate.partition_declarator.get_procedure_transition(array_items, exchange_module, state_modules))
    return initial_transitions 

