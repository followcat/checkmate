import os
import gettext
import collections

import fresher
import pyparsing
import fresher.core
import fresher.parser


def get_feature_language():
    _languages = ['en', 'zh-CN']
    feature_dir, _f = os.path.split(os.path.abspath(__file__))
    for feature_name in os.listdir(feature_dir):
        if feature_name.endswith('.feature'):
            for _language in _languages:
                try:
                    _feat = fresher.parser.parse_file(os.path.join(feature_dir, feature_name), 
                                                        fresher.core.load_language(_language))
                except pyparsing.ParseException:
                    continue
                return _language    

lang_en = gettext.translation("steps_en", localedir=os.path.join(os.getenv('CHECKMATE_HOME'),'sample_app/itp/locale'), languages=["en_US"])
lang_en.install()

@fresher.Before
def before(sc):
    fresher.scc.array_items = []
    lang_cn = gettext.translation("steps_cn", localedir=os.path.join(os.getenv('CHECKMATE_HOME'),'sample_app/itp/locale'), languages=["en_US"])
    if get_feature_language() == 'zh-CN':
        lang_cn.install()

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
