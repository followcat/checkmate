# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import sys
import random
import unittest
import collections

import nose.case
import nose.suite
import nose.proxy
import nose.plugins.skip

import checkmate.runs
import checkmate.sandbox


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
        if isinstance(test, checkmate.runs.Run):
            config_as_dict = self.config.todict()
            result.startTest(self)
            try:
                config_as_dict['runtime'].execute(test, result)
            except nose.plugins.skip.SkipTest as e:
                result.addSkip(self, Exception(str(e)))
            except:
                err = sys.exc_info()
                result.addError(self, err)
            result.stopTest(self)
        else:
            if isinstance(test.test, list):
                setattr(test, 'proxyResult', result.result)
                test()
            else:
                test(result)

class FunctionTestCase(nose.case.FunctionTestCase):
    def __init__(self, test, config, **kwargs):
        super(FunctionTestCase, self).__init__(test, **kwargs)
        self.config = config

    def runTest(self):
        """"""
        config_as_dict = self.config.todict()
        runtime = config_as_dict['runtime']
        if isinstance(self.test, list):
            def generate_test_from_exchange(exchanges, application):
                for item in exchanges:
                    for exchange in exchanges:
                        sandbox = checkmate.sandbox.Sandbox(type(application),
                                                            application)
                        if sandbox([exchange]):
                            yield sandbox.blocks
                            break
            for _test in generate_test_from_exchange(self.test,
                                                     runtime.application):
                setattr(_test, '__name__', _test.root.name)
                _FunctionTestCase = FunctionTestCase(_test,
                                                     config=self.config)
                _FunctionTestCase(self.proxyResult)
        else:
            runtime.execute(self.test, transform=True)

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
                    TestCase(test, config=self.config)
                    )
        return wrapped

