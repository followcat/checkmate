import os
import gettext
import collections

import fresher
import pyparsing
import fresher.core
import fresher.parser


def get_feature_language(feature_dirname):
    _languages = ['en', 'zh-CN']
    _dir, _f = os.path.split(os.path.abspath(__file__))
    feature_dirpath = os.path.join(_dir, feature_dirname)
    for feature_name in os.listdir(feature_dirpath):
        if feature_name.endswith('.feature'):
            for _language in _languages:
                try:
                    _feat = fresher.parser.parse_file(os.path.join(feature_dirpath, feature_name), 
                                                        fresher.core.load_language(_language))
                except pyparsing.ParseException:
                    continue
                return _language    

feature_dirname = 'itp_zh_features'
lang_en = gettext.translation("steps_en", languages=["en_US"])
lang_cn = gettext.translation("steps_cn", languages=["en_US"])
if get_feature_language(feature_dirname) == 'en':
    lang_en.install()
elif get_feature_language(feature_dirname) == 'zh-CN':
    lang_cn.install()

@fresher.Before
def before(sc):
    fresher.scc.array_items = []

@fresher.Given(_("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$"))
def set_initial(component_name, state, value):
    fresher.scc.array_items.append([state, value, 'x'])

@fresher.When(_("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$"))
def set_incoming(component, exchange, action):
    fresher.scc.array_items.insert(0, [exchange, 'x', action])

@fresher.Then(_("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$"))
def set_final(component_name, state, value):
    for i in range(len(fresher.scc.array_items)):
        if fresher.scc.array_items[i][0] == state:
            fresher.scc.array_items[i][2] = value

@fresher.After
def after(sc):
    if fresher.ftc.scenarios is None:
        fresher.ftc.scenarios = []
    fresher.ftc.scenarios.append(fresher.scc.array_items)
