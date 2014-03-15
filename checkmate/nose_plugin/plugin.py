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
        config_as_dict = self.config.todict()
        config_as_dict['system_under_test'] = self.sut
        self.config.update(config_as_dict)
        checkmate.nose_plugin.ContextSuite.randomized_run = self.randomized_run
        loader.suiteClass=checkmate.nose_plugin.ContextSuiteFactory(config=self.config,
                                        suiteClass=checkmate.nose_plugin.ContextSuite)
        self.suiteClass = loader.suiteClass
        self.loader = loader

    def prepareTestRunner(self, runner):
        """Replace test runner with TestRunner.
        """
        TestRunner.loop_runs = self.loop_runs

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
            try:
                for test in g(self.application_class):
                    test_func, arg = self.loader.parseGeneratedTest(test)
                    if not isinstance(test_func, collections.Callable):
                        test_func = getattr(m, test_func)
                    yield checkmate.nose_plugin.suite.FunctionTestCase(test_func, config=self.config, arg=arg, descriptor=g)
            except KeyboardInterrupt:
                raise
            except:
                exc = sys.exc_info()
                yield nose.failure.Failure(exc[0], exc[1], exc[2],
                              address=nose.util.test_address(generator))
        return self.suiteClass(generate, context=generator, can_split=False)

    def begin(self):
        """Start the system under test"""
        self.runtime = checkmate.runtime._runtime.Runtime(self.application_class, self.communication_class, threaded=True)
        self.runtime.setup_environment(self.sut)
        self.runtime.start_test()
        time.sleep(3)
    
        
    def finalize(self, result):
        """"""
        self.runtime.stop_test()


class TestRunner(nose.core.TextTestRunner):
    loop_runs = 1

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
        for _loop in range(self.loop_runs):
            test(result)

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

