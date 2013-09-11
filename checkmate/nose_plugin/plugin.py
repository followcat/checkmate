import sys
import time
import inspect
import collections

import nose
import nose.util
import nose.config
import nose.failure
import nose.plugins

import checkmate.test_data
import checkmate.nose_plugin
import checkmate.runtime._pyzmq
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
                          default="",
                          help="Specify the system under test.")
        parser.add_option('--runlog', action='store_true',
                          dest='runlog',
                          default=False,
                          help="if run from the log file")
        return parser

    def configure(self, options, config):
        """Read system under test from options"""
        nose.plugins.Plugin.configure(self, options, config)
        if len(options.sut) != 0:
            self.sut = options.sut.split(',')
        self.runlog = options.runlog

    def prepareTestLoader(self, loader):
        """Set the system under test in loader config"""
        config_as_dict = self.config.todict()
        config_as_dict['system_under_test'] = self.sut
        self.config.update(config_as_dict)
        loader.suiteClass=checkmate.nose_plugin.ContextSuiteFactory(config=self.config,
                                        suiteClass=checkmate.nose_plugin.ContextSuite)
        self.suiteClass = loader.suiteClass
        self.loader = loader

    def wantClass(self, cls):
        """Select only classes implementing checkmate.runtime.interfaces.IProcedure"""
        return checkmate.runtime.interfaces.IProcedure.implementedBy(cls)
        
    def wantFunction(self, function):
        """Do not select TestLogProcedureGenerator"""
        if self.runlog:
            return "Test" in function.__name__
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
        return self.suiteClass(tests=[cls(),])

    def loadTestsFromGenerator(self, generator, module):
        """"""
        def generate(g=generator, m=module):
            try:
                for test in g():
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
        a = checkmate.test_data.App()
        c = checkmate.runtime._pyzmq.Communication()
        self.runtime = checkmate.runtime._runtime.Runtime(a, c, threaded=True)
        self.runtime.setup_environment(self.sut)
        self.runtime.start_test()
        time.sleep(3)
    
        
    def finalize(self, result):
        """"""
        self.runtime.stop_test()


if __name__ == '__main__':
    nose.main(addplugins=[Checkmate()])

