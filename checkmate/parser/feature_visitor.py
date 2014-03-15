#-*- coding: utf8 -*-

# Experimental - a non-nose runner for tests, may end up being compatible
# with Cucumber commandline

import os
import sys
import copy
import gettext

import pyparsing
import fresher.cuke
import fresher.core
import fresher.stepregistry

import checkmate.partition_declarator


def new_load_step_definitions(paths):
    """
        the load_steps_impl function at load_step_definitions in fresher.cuke only has 2 arguments,has problem:

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

def new_load_features(paths, language):
    """
        >>> import os
        >>> import checkmate.parser.feature_visitor
        >>> itp_paths = os.path.join(os.getenv('CHECKMATE_HOME'), 'sample_app/itp')
        >>> features = checkmate.parser.feature_visitor.new_load_features([itp_paths],
        ...                     fresher.core.load_language('en'))
        >>> features # doctest: +ELLIPSIS
        [<Feature "Third run PP": 1 scenario(s)>, ...
        >>> len(features)
        4
        >>> features = checkmate.parser.feature_visitor.new_load_features([itp_paths],
        ...                     fresher.core.load_language('zh-CN'))
        >>> features # doctest: +ELLIPSIS
        [<Feature "第三运行PP": 1 scenario(s)>, ...
        >>> len(features)
        4
    """
    result = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for feature_file in filenames:
                if feature_file.endswith(".feature"):
                    feature_file = os.path.join(dirpath, feature_file)
                    try:
                        result.append(fresher.core.load_feature(feature_file, language))
                    except pyparsing.ParseException:
                        continue
    return result

def new_run_features(step_registry, features, handler):
    if fresher.glc.array_list is None:
        fresher.glc.array_list = []
    for feature in features:
        fresher.cuke.run_feature(step_registry, feature, handler)
        fresher.glc.array_list.extend(fresher.ftc.scenarios)

def translate_registry(registry, lang):
    local_registry = copy.deepcopy(registry)
    if lang == 'zh-CN':
        _locale = gettext.translation("checkmate-features", localedir=os.path.join(os.getenv('CHECKMATE_HOME'),'sample_app/itp/translations'), languages=["zh_CN"])
    else:
        _locale = gettext.translation("checkmate-features", localedir=os.path.join(os.getenv('CHECKMATE_HOME'),'sample_app/itp/translations'), languages=["en_US"])
    _locale.install()

    for keyword in ['given', 'when', 'then']:
        for step in local_registry.steps[keyword]:
            step.spec = _(step.spec)
            if hasattr(step, 're_spec'):
                del step.re_spec
            local_registry.add_step(keyword, step)
    return local_registry


def get_array_list(paths):
    """
        >>> import os
        >>> import checkmate.parser.feature_visitor
        >>> itp_path = 'sample_app/itp'
        >>> itp_absolute_path = os.path.join(os.getenv('CHECKMATE_HOME'),itp_path)
        >>> len(checkmate.parser.feature_visitor.get_array_list([itp_absolute_path]))
        8
    """
    _languages = ['en', 'zh-CN']
    fresher.glc.clear() 
    for _lang in _languages:
        _locale = gettext.translation("checkmate-features", localedir=os.path.join(os.getenv('CHECKMATE_HOME'),'sample_app/itp/translations'), languages=["en_US"])
        _locale.install()
        language_set = fresher.core.load_language(_lang)
        registry = new_load_step_definitions(paths)
        lang_registry = translate_registry(registry, _lang)
        features = new_load_features(paths, language_set)
        handler = fresher.cuke.FresherHandlerProxy([fresher.cuke.FresherHandler()])
        new_run_features(lang_registry, features, handler)
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
            8
            >>> transitions # doctest: +ELLIPSIS
            [<checkmate._storage.TransitionStorage object at ...
        """
    array_list = get_array_list([os.path.join(os.getenv('CHECKMATE_HOME'), 'sample_app/itp/')])
    initial_transitions = []
    for array_items in array_list:
        initial_transitions.append(checkmate.partition_declarator.get_procedure_transition(array_items, exchange_module, state_modules))
    return initial_transitions 

