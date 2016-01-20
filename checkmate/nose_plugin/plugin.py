# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import sys
import time
import shlex
import inspect
import importlib
import collections

import nose
import nose.core
import nose.util
import nose.config
import nose.failure
import nose.plugins

import checkmate.nose_plugin
import checkmate.runtime._runtime
import checkmate.nose_plugin.suite
import checkmate.runtime.interfaces


class Checkmate(nose.plugins.Plugin):
    """"""
    config=nose.config.Config()
    sut = []

    def options(self, parser, env):
        """"""
        nose.plugins.Plugin.options(self, parser, env)
        parser.add_option('--sut', action='store',
                          dest='sut',
                          metavar="COMP1,COMP2",
                          default=os.getenv('CHECKMATE_RUNTIME_SUT', ''),
                          help="Specify the system under test.")
        parser.add_option('--components', action='store',
                          dest='components',
                          metavar="COMP1,COMP2",
                          default=os.getenv('CHECKMATE_RUNTIME_COMPONENTS', ''),
                          help="Specify the list of components. then the list will become combination of suts")
        parser.add_option('--random', action='store_true', default=False,
                          dest='randomized_run',
                          help="Require the tests to be run in random order.")
        parser.add_option('--runs', action='store', default=1,
                          dest='loop_runs', type='int', 
                          help="Specify the number of loops to run [default: 1]"),
        parser.add_option('--runlog', action='store_true',
                          dest='runlog',
                          default=False,
                          help="if run from the log file")
        parser.add_option('--application', action='store',
                          dest='app_class',
                          default=os.getenv('CHECKMATE_RUNTIME_APPLICATION', "sample_app.application.TestData"),
                          help="Specify the application class in runtime")
        parser.add_option('--communication', action='store',
                          dest='comm_class',
                          default=os.getenv('CHECKMATE_RUNTIME_COMMUNICATION', "checkmate.runtime._pyzmq.Communication"),
                          help="Specify the communication class in runtime")
        return parser

    def configure(self, options, config):
        """Read system under test from options"""
        nose.plugins.Plugin.configure(self, options, config)
        if len(options.sut) != 0:
            self.sut = options.sut.split(',')
        self.components = []
        if len(options.components) != 0:
            components_list = options.components.split(',')
            #define a generator to generate combination from a list
            def _combinator(s):
                if len(s) == 1:
                    def gen(lst):
                        yield []
                        yield [lst[0],]
                else:
                    def gen(a):
                        lst = a[:]
                        item = lst.pop()
                        for i in _combinator(lst):
                            b = i[:]
                            c = i[:]
                            c.append(item)
                            yield b
                            yield c
                generator = gen(s)
                return generator
            for _sut in _combinator(components_list):
                if len(_sut) == 0:
                    continue
                is_inserted = False
               #create a list with order of the length of items from short to long
                for item in self.components:
                    if len(_sut) < len(item):
                        self.components.insert(self.components.index(item), _sut)
                        is_inserted = True
                        break
                if not is_inserted:
                    self.components.append(_sut)
        if self.sut and len(self.components) == 0:
            self.components.append(self.sut)
        self.runlog = options.runlog
        self.loop_runs = options.loop_runs
        self.randomized_run = options.randomized_run
        self.application_class = self.get_option_value(options.app_class)
        self.communication_class = self.get_option_value(options.comm_class)
    
    def get_option_value(self, value):
        if len(value) == 0:
            return
        try:
            module, classname = value[0: value.rindex('.')], value[value.rindex('.')+1:]
            option_value = getattr(importlib.import_module(module), classname)
        except:
            raise ValueError("either env or command option is not properly specified")
        return option_value

    def prepareTestLoader(self, loader):
        """Set the system under test in loader config"""
        checkmate.nose_plugin.ContextSuite.randomized_run = self.randomized_run
        loader.suiteClass=checkmate.nose_plugin.ContextSuiteFactory(config=self.config,
                                        suiteClass=checkmate.nose_plugin.ContextSuite)
        self.suiteClass = loader.suiteClass
        self.loader = loader

    def prepareTestRunner(self, runner):
        """Replace test runner with TestRunner.
        """
        TestRunner.plugin_config = dict(self.__dict__)

    def wantClass(self, cls):
        """Select only classes implementing checkmate.runtime.interfaces.IProcedure"""
        return not(self.runlog) and checkmate.runtime.interfaces.IProcedure.implementedBy(cls)
        
    def wantFunction(self, function):
        """Do not select TestLogProcedureGenerator"""
        if self.runlog:
            return "TestLog" in function.__name__
        return self.runlog or "TestProcedure" in function.__name__ 

    def makeTest(self, obj, parent=None):
        """"""
        if nose.util.isclass(obj):
            if checkmate.runtime.interfaces.IProcedure.implementedBy(obj):
                return self.loadTestsFromTestCase(obj)
        elif inspect.isfunction(obj):
            if parent and obj.__module__ != parent.__name__:
                obj = nose.util.transplant_func(obj, parent.__name__)
            if nose.util.isgenerator(obj):
                return self.loadTestsFromGenerator(obj, parent)

    def loadTestsFromTestCase(self, cls):
        """"""
        return self.suiteClass(tests=[cls(application_class=self.application_class),])

    def loadTestsFromGenerator(self, generator, module):
        """"""
        def generate(g=generator, m=module):
            generated = False
            try:
                for test in g(self.application_class):
                    test_func, arg = self.loader.parseGeneratedTest(test)
                    if not isinstance(test_func, collections.Callable):
                        test_func = getattr(m, test_func)
                    generated = True
                    yield checkmate.nose_plugin.suite.FunctionTestCase(test_func, config=self.config, arg=arg, descriptor=g)
                if not generated:
                    yield self.no_generate
            except KeyboardInterrupt:
                raise
            except:
                exc = sys.exc_info()
                yield nose.failure.Failure(exc[0], exc[1], exc[2],
                              address=nose.util.test_address(generator))
        return self.suiteClass(generate, context=generator, can_split=False)
    
    def no_generate(self, args):
        """this function is defined to skip test if a generator create nothing to test"""
        pass


class TestRunner(nose.core.TextTestRunner):
    plugin_config = {}

    def run(self, test):
        """Overrides to provide plugin hooks and defer all output to
        the test result class.
        """
        #from father class code
        wrapper = self.config.plugins.prepareTest(test)
        if wrapper is not None:
            test = wrapper

        wrapped = self.config.plugins.setOutputStream(self.stream)
        if wrapped is not None:
            self.stream = wrapped

        result = self._makeResult()
        start = time.time()

        #specific code
        components = self.plugin_config['components']
        application_class = self.plugin_config['application_class']
        if 'pytango' in application_class.__module__ and len(components) > 1:
            raise Exception("'pytango' application is not supported with more than one components set")
        for index, _sut in enumerate(components):
            runtime = checkmate.runtime._runtime.Runtime(application_class, self.plugin_config['communication_class'], threaded=True)
            runtime.setup_environment(_sut)
            runtime.start_test()
            time.sleep(3)
            setattr(test.config, 'runtime', runtime)
            if len(components) > 1:
                #do some dirty print
                result.stream.writeln('sut=' + ','.join(_sut) + ':')
            for _loop in range(self.plugin_config['loop_runs']):
                test(result)
            runtime.stop_test()
            if index < len(components)-1:
                result.stream.writeln()

        #from father class code
        stop = time.time()
        result.printErrors()
        result.printSummary(start, stop)
        self.config.plugins.finalize(result)
        return result

class TestProgram(nose.core.TestProgram):
    def runTests(self):
        self.testRunner = TestRunner(stream=self.config.stream,
                                              verbosity=self.config.verbosity,
                                              config=self.config)
        super(TestProgram, self).runTests()


if __name__ == '__main__':
    sys.argv = sys.argv + shlex.split('--nologcapture')
    TestProgram(addplugins=[Checkmate()])

