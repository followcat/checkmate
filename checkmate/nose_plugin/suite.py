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
import checkmate.pathfinder


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
        runs = runtime.application.run_collection()
        if isinstance(self.test, list):
            for _test, _path in \
                    generate_test_from_exchange(self.test,
                                                runtime.application):
                transform_state(runtime, _path)
                setattr(_test, '__name__', _test.root.name+str(runs.index(_test)))
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

def transform_state(runtime, path):
    """
    transform the state of application
    """
    for _run in path:
        runtime.execute(_run)


def generate_test_from_exchange(exchanges, application):
    """
    in charge of the runnable test yielding
    step1. find current application what exchange we can run
    step2. choose the untested one yield,if no untested runs go step3
    step3. find untested run and return a path
    step4. yield untested run and path

    >>> import sample_app.application
    >>> import checkmate.runs
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.nose_plugin.suite as su
    >>> com = checkmate.runtime._pyzmq.Communication
    >>> app = sample_app.application.TestData
    >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
    >>> r.setup_environment(['C2'])
    >>> r.start_test()
    >>> origin_exchanges = checkmate.runs.get_origin_exchanges(r.application)
    >>> runs = app.run_collection()
    >>> def run():
    ...     for _test, _path in su.generate_test_from_exchange(origin_exchanges, r.application):
    ...         su.transform_state(r, _path)
    ...         print(str(runs.index(_test)))
    ...         r.execute(_test)
    ...
    >>> run()
    0
    2
    1
    3
    >>> r.stop_test()
    """
    history_runs = []
    untested_runs = []
    yield_run_index = -1
    import numpy  # for random mode
    application.reliable_matrix = numpy.matrix([])
    while True:
        yield_path = []
        next_runs = []
        # step1
        next_exchanges = checkmate.runs.find_next_exchanges(application,
                                                            exchanges,
                                                            yield_run_index)
        for exchange in next_exchanges:
            sandbox = checkmate.sandbox.Sandbox(type(application),
                                                application)
            assert sandbox([exchange])
            next_runs.append(sandbox.blocks)
        new_untested_runs = [_run for _run in next_runs\
                             if _run not in history_runs]
        # step2
        if len(new_untested_runs) > 0:
            untested_runs.extend([_run for _run in new_untested_runs\
                                  if _run not in untested_runs])
            yield_run = new_untested_runs[0]
            if yield_run in untested_runs:
                untested_runs.remove(yield_run)
        # step3
        else:
            yield_run, yield_path =\
                checkmate.pathfinder.find_untested_path(application, next_runs,
                                                        untested_runs,
                                                        history_runs, exchanges)
            if yield_run is None:
                return
            untested_runs.remove(yield_run)
        # step4
        yield_run_index += 1
        history_runs.append(yield_run)
        yield yield_run, yield_path
