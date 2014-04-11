import random
import unittest
import collections

import nose.case
import nose.suite
import nose.proxy

import checkmate.runtime.interfaces


class TestCase(nose.case.Test):
    """"""
    def runTest(self, result):
        """Run the test. Plugins may alter the test by returning a
        value from prepareTestCase. The value must be callable and
        must accept one argument, the result instance.
        """
        test = self.test
        plug_test = self.config.plugins.prepareTestCase(self)
        if plug_test is not None:
            test = plug_test
        config_as_dict = self.config.todict()
        if checkmate.runtime.interfaces.IProcedure.providedBy(test):
            if len(config_as_dict['system_under_test_list']) > 0:
                for sut in config_as_dict['system_under_test_list']:
                    test(sut, result)
            else:
                test(config_as_dict['system_under_test'], result)
        else:
            test(result, self.resultProxy)

class FunctionTestCase(nose.case.FunctionTestCase):
    def __init__(self, test, config, **kwargs):
        super(FunctionTestCase, self).__init__(test, **kwargs)
        self.config = config

    def run(self, result, resultProxy):
        self.resultProxy = resultProxy
        if self.resultProxy:
            result = self.resultProxy(result, self)
        try:
            self.runTest(result)
        except KeyboardInterrupt:
            raise
        except:
            err = sys.exc_info()
            result.addError(self, err)

    def runTest(self, result):
        """"""
        config_as_dict = self.config.todict()
        if len(config_as_dict['system_under_test_list']) > 0:
            for sut in config_as_dict['system_under_test_list']:
                self.test(sut, result)
        else:
            self.test(config_as_dict['system_under_test'], result)

    def shortDescription(self):
        if hasattr(self.test, 'description'):
            return self.test.description
        return str(self)


class ContextSuite(nose.suite.ContextSuite):
    """"""
    randomized_run = False

    def _get_wrapped_tests(self):
        for test in self._get_tests():
            if isinstance(test, TestCase) or isinstance(test, unittest.TestSuite):
                yield test
#            elif checkmate.runtime.interfaces.IProcedure.providedBy(test):
            else:
                yield TestCase(test,
                           config=self.config,
                           resultProxy=self.resultProxy)

    _tests = property(_get_wrapped_tests, nose.suite.ContextSuite._set_tests, None,
                      "Access the tests in this suite. Access is through a "
                      "generator, so iteration may not be repeatable.")

    def run(self, result):
        if self.randomized_run:
            _list = list(self._tests)
            self._tests = random.sample(_list, len(_list))
        super(ContextSuite, self).run(result)


class ContextSuiteFactory(nose.suite.ContextSuiteFactory):
    """"""
    def wrapTests(self, tests):
        if callable(tests) or isinstance(tests, unittest.TestSuite):
            return tests
        wrapped = []
        for test in tests:
            if isinstance(test, TestCase) or isinstance(test, unittest.TestSuite):
                wrapped.append(test)
            elif isinstance(test, ContextSuite):
                wrapped.append(self.makeSuite(test, context=test.context))
            else:
                wrapped.append(
                    TestCase(test, config=self.config, resultProxy=self.resultProxy)
                    )
        return wrapped

