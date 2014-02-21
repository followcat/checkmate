========================================
What should we do to use fresher
========================================
************************
How to install fresher?
************************
------------------------------------
Make pip faster
------------------------------------
In China,pypi and pip server sometimes cannot connected,then we can't use pip install.
To solve this,we can use Tsinghua University's mirror:

 ::

    Edit $HOME/.pip/pip.conf , Add:

    [global]
    index-url=http://mirrors.tuna.tsinghua.edu.cn/pypi/simple

------------------------------------
Install fresher
------------------------------------
Use this command:

 ::

    pip install "fresher==0.4.0"

--------------------------------------------
About dependencies libyaml
--------------------------------------------
Fresher use PyYAML . And LibYAML is a YAML parser and emitter written in C.
One of PyYAML's feature:

::

    both pure-Python and fast LibYAML-based parsers and emitters.

So If you want to use LibYAML bindings, you need to download and install LibYAML. Then you may install the bindings by executing when you install PyYAML

::

    $ python setup.py --with-libyaml install

------------------------------------------------------------
UnicodeDecodeError when using fresher
------------------------------------------------------------
After install fresher,if you meet UnicodeDecodeError when using fresher like this:

::
    
    ...
    File "/home/vcr/Projects/tango-controls/cme-tango-8.1.2/lib/python3.3/site-packages/yaml/reader.py", line 178, in update_raw
    data = self.stream.read(size)
    File "/home/vcr/Projects/tango-controls/cme-tango-8.1.2/lib/python3.3/encodings/ascii.py", line 26, in decode
        return codecs.ascii_decode(input, self.errors)[0]
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xd8 in position 893: ordinal not in range(128)

And PyYAML has this  `feature <http://pyyaml.org/wiki/PyYAML>`_ :

::

    Unicode support including UTF-8/UTF-16 input/output and \u escape sequences.

So you should set your system locale to utf-8.(`Help Here  <https://wiki.debian.org/Locale#Configuration>`_.)



************************
How fresher work?
************************
At the cuke.py we can find the call to order:

::

    language = load_language('en')
    registry = load_step_definitions(paths)
    features = load_features(paths, language)
    handler = FreshenHandlerProxy([ConsoleHandler()])
    run_features(registry, features, handler)

Then entry run_features(registy, features, handler) function

::

    run_features
        ↓
    run_feature   #loop#
        ↓
    print before_feature    #handler:ConsoleHandler#
        ↓
    ftc.clear()
        ↓
    for each scenario
        run_scenario
        ↓
    print after_feature    #handler:ConsoleHandler#

Let's go into the run_scenario function,each function in steps.py is fresher.stepregistry.StepImpl(HookImpl),it's:

::

    def run(self, *args, **kwargs):
        self.func(*args, **kwargs)

::

    Into run_scenario
        ↓
    print before_scenario    #handler:ConsoleHandler#
        ↓
    StepsRunner(registry)
        ↓
    scc.clear()
        ↓
    for each before:
        get_hook(before,get_tags())
        hook_impl.run(before)
        ↓
    for each step:    #scenario.iter_steps#
        print before_step    #handler:ConsoleHandler#
        runner.run_step(step)
        print after_step    #handler:ConsoleHandler#
        ↓
    for each after_step:
        get_hooks(after,get_tags())
        hook_impl.run(after)
    print after_scenario    #handler:ConsoleHandler#


************************
What function should we define?
************************
-------------------------
Get the itp list
-------------------------
1.Use fresher's global var

::

    glc : never cleared
    ftc : cleared at the start of each feature
    scc : cleared at the start of each scenario

2.Use ourselves' import global var

itp : Many features, use one setps.py

-------------------------
How to run it?
-------------------------
Like cuke.py : Maybe we willn't use ConsoleHandler()

::

    at steps.py
    @After
    def after(sc):
        if ftc.temp is None:
            ftc.temp = []
        ftc.temp.append(scc.temp)

    at get_itp.py
    def run_feature(step_registry, feature, handler):
        handler.before_feature(feature)
        ftc.clear()
        for scenario in feature.iter_scenarios():
            run_scenario(step_registry, scenario, handler)
        handler.after_feature(feature)
        glc.itp.append(ftc)
        
    def get_itps(paths):
        #enter fresher runtime
        glc.clear()
        language = load_language('en')
        registry = load_step_definitions(paths,language)
        features = load_features(paths, language)
        handler = FreshenHandlerProxy([FresherHandler()])
        run_features(registry,features,#handler)
    
    get_itps(paths)
    itp = glc.itp

In the paths Directory:
paths: itp { itp_run1.feature,
itp_run2.feature,
itp_run3.feature....,
steps.py}


You can download this : `rst file Here  <how_to_fresher.rst>`_.