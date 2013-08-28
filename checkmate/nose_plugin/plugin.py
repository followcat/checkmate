import time
import string

import nose
import nose.util
import nose.config
import nose.plugins

import checkmate.test_data
import checkmate.nose_plugin
import checkmate.runtime._pyzmq
import checkmate.runtime._runtime
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
        return parser

    def configure(self, options, config):
        """Read system under test from options"""
        nose.plugins.Plugin.configure(self, options, config)
        if len(options.sut) != 0:
            self.sut = options.sut.split(',')

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
        
    def makeTest(self, obj, parent=None):
        """"""
        if nose.util.isclass(obj):
            if checkmate.runtime.interfaces.IProcedure.implementedBy(obj):
                return self.loadTestsFromTestCase(obj)

    def loadTestsFromTestCase(self, cls):
        """"""
        return self.suiteClass(tests=[cls(),])

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

