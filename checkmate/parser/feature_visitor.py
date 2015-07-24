# This code is part of the checkmate project.
# Copyright (C) 2014-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import re
import copy
import gettext

import pyparsing
import fresher.cuke
import fresher.core
import fresher.stepregistry

import checkmate.runs
import checkmate.partition_declarator


MAKEFILE_LANG = re.compile("LANG\s*=\s*([ \w]*)\n")


def new_load_step_definitions(paths):
    """
    The load_steps_impl function at load_step_definitions in
    fresher.cuke only has 2 arguments,has problem:

        >>> import sys
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
        >>> itp_paths = os.path.join(os.getenv('CHECKMATE_HOME'),
        ...                 'sample_app/itp')
        >>> visitor = checkmate.parser.feature_visitor
        >>> features = visitor.new_load_features([itp_paths],
        ...                 fresher.core.load_language('en'))
        >>> len(features)
        3
        >>> feature_names = []
        >>> for _f in features:
        ...     feature_names.append(_f.name)
        >>> 'Third run PP' in feature_names
        True
        >>> features = visitor.new_load_features([itp_paths],
        ...                 fresher.core.load_language('zh-CN'))
        >>> len(features)
        3
        >>> feature_names.clear()
        >>> for _f in features:
        ...     feature_names.append(_f.name)
        >>> '第三运行PP' in feature_names
        True

    """
    result = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for feature_file in filenames:
                if feature_file.endswith(".feature"):
                    feature_file = os.path.join(dirpath, feature_file)
                    try:
                        result.append(fresher.core.load_feature(feature_file,
                            language))
                    except pyparsing.ParseException:
                        continue
    return result

def new_run_features(step_registry, features, handler):
    if fresher.glc.array_list is None:
        fresher.glc.array_list = []
    for feature in features:
        fresher.cuke.run_feature(step_registry, feature, handler)
        for index, _s in enumerate(feature.scenarios):
                fresher.ftc.scenarios[index].update({'name': _s.name})
        fresher.glc.array_list.extend(fresher.ftc.scenarios)

def translate_registry(registry, lang, localization_path):
    local_registry = copy.deepcopy(registry)
    if lang == 'zh-CN':
        _locale = gettext.translation("checkmate-features",
                    localedir=os.path.join(localization_path, 'translations'),
                    languages=["zh_CN"])
    else:
        _locale = gettext.translation("checkmate-features",
                    localedir=os.path.join(localization_path, 'translations'),
                    languages=["en_US"])
    _locale.install()

    for keyword in ['given', 'when', 'then']:
        for step in local_registry.steps[keyword]:
            step.spec = _(step.spec)
            if hasattr(step, 're_spec'):
                del step.re_spec
            local_registry.add_step(keyword, step)
    return local_registry


def _compatible_fresher_language(languages):
    fresher_languages = list(languages)
    conversion = {'en_US': 'en', 'zh_CN': 'zh-CN'}
    for _id in range(len(languages)):
        if languages[_id] in conversion.keys():
            fresher_languages[_id] = conversion[languages[_id]]
    return fresher_languages


def _get_languages(makefile_path):
    """
        >>> import os
        >>> import checkmate.parser.feature_visitor
        >>> makefile_path = os.path.join(os.getenv('CHECKMATE_HOME'),
        ...                     'sample_app/itp')
        >>> checkmate.parser.feature_visitor._get_languages(
        ...     makefile_path)
        ['en', 'zh-CN']
    """
    makefile = open(os.path.join(makefile_path, 'Makefile'), 'r')
    text = makefile.read()
    makefile.close()
    matching = MAKEFILE_LANG.search(text)
    if matching is None:
        return ['en_US']
    else:
        return _compatible_fresher_language(matching.group(1).split(' '))

def get_array_list(paths, localization_path=None):
    """
        >>> import os
        >>> import checkmate.parser.feature_visitor
        >>> path = os.path.join('sample_app', 'itp')
        >>> absolute_path = os.path.join(os.getenv('CHECKMATE_HOME'),
        ...                     path)
        >>> len(checkmate.parser.feature_visitor.get_array_list(
        ...         [absolute_path]))
        6
    """
    if localization_path is None:
        localization_path = paths[0]
    _languages = _get_languages(localization_path)
    fresher.glc.clear()
    for _lang in _languages:
        _locale = gettext.translation("checkmate-features",
                    localedir=os.path.join(localization_path, 'translations'),
                    languages=["en_US"])
        _locale.install()
        language_set = fresher.core.load_language(_lang)
        registry = new_load_step_definitions(paths)
        lang_registry = translate_registry(registry, _lang, localization_path)
        features = new_load_features(paths, language_set)
        handler = fresher.cuke.FresherHandlerProxy(
                    [fresher.cuke.FresherHandler()])
        new_run_features(lang_registry, features, handler)
    return fresher.glc.array_list

def data_from_files(application):
    """
            >>> import checkmate.state
            >>> import checkmate.exchange
            >>> import checkmate.component
            >>> import checkmate.parser.feature_visitor
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> state_modules = []
            >>> for name, component in a.components.items():
            ...     state_modules.append(component.state_module)
            >>> visitor = checkmate.parser.feature_visitor
            >>> data = visitor.data_from_files(a)
            >>> len(data)
            6
        """
    try:
        path = os.path.join(os.getenv('CHECKMATE_HOME'),
                    application.feature_definition_path)
    except AttributeError:
        path = os.path.join(os.getenv('CHECKMATE_HOME'),
                    os.path.dirname(application.exchange_module.__file__),
                    'itp')
    try:
        array_list = get_array_list([path])
    except FileNotFoundError:
        return []
    return array_list
