import unittest
import collections

import nose.case
import nose.suite

import checkmate.runtime.interfaces


class TestCase(nose.case.Test):
    """"""
    def __init__(self, *arg, **kw):
        nose.case.Test.__init__(self, *arg, **kw)

    def runTest(self, result):
        """Run the test. Plugins may alter the test by returning a
        value from prepareTestCase. The value must be callable and
        must accept one argument, the result instance.
        """
        test = self.test
        plug_test = self.config.plugins.prepareTestCase(self)
        if plug_test is not None:
            test = plug_test
        if checkmate.runtime.interfaces.IProcedure.providedBy(test):
            config_as_dict = self.config.todict()
            test(result, config_as_dict['system_under_test'])
        else:
            test(result)


class ContextSuite(nose.suite.ContextSuite):
    """"""
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

