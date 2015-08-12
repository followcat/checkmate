# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import sys
import numpy
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
            gen = self.runTest_gen(config_as_dict['generator_test_info'],\
                                   runtime)
            for _test, _path in gen:
                transform_state(runtime, _path)
                setattr(_test, '__name__', \
                        _test.root.name+str(runs.index(_test))+\
                        ' path:'+str([runs.index(i) for i in _path]))
                _FunctionTestCase = FunctionTestCase(_test,
                                                     config=self.config)
                _FunctionTestCase(self.proxyResult)
        elif hasattr(self.test, '__name__'):
            runtime.execute(self.test, transform=False)
        else:
            runtime.execute(self.test, transform=True)

    def runTest_gen(self, generator_test_info, runtime):
        if generator_test_info['tested'] and generator_test_info['random']:
            return random_generator(generator_test_info['history_runs'],
                             runtime.application,
                             self.test)
        elif generator_test_info['tested'] and not generator_test_info['random']:
            def gen(x):
                for _run, _path in x:
                    yield _run, _path
            return gen(generator_test_info['history_track'])
        else:
            generator_test_info['tested'] = True
            return generate_test_from_exchange(self.test, runtime.application,
                                       generator_test_info['history_track'],
                                       generator_test_info['history_runs'])

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
        runtime.execute(_run, transform=False)


def generate_test_from_exchange(exchanges, application,
                                history_track, history_runs):
    """
    in charge of the runnable test yielding
    step1. find current application what exchange we can run
    step2. choose the untested one yield,if no untested runs go step3 else go step4
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
    >>> origin_exchanges = checkmate.runs.get_origin_exchanges(app)
    >>> runs = app.run_collection()
    >>> def run():
    ...     for _test, _path in su.generate_test_from_exchange(
    ...                             origin_exchanges, r.application,[],[]):
    ...         su.transform_state(r, _path)
    ...         print('run:', str(runs.index(_test)),
    ...               'path:', [runs.index(i) for i in _path])
    ...         r.execute(_test)
    ...
    >>> run()
    run: 0 path: []
    run: 1 path: []
    run: 2 path: []
    run: 3 path: [1]
    >>> r.stop_test()
    """
    untested_runs = []
    application.reliable_matrix = numpy.matrix([])
    yield_run = None
    while True:
        yield_path = []
        next_runs = []
        next_runs = checkmate.runs.find_next_runs(application, exchanges, yield_run)
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
            yield_run, yield_path = \
                checkmate.pathfinder.find_path_to_nearest_target(application,
                                                                 next_runs,
                                                                 untested_runs)
            if yield_run is None:
                return
            untested_runs.remove(yield_run)
        # step4
        history_runs.append(yield_run)
        history_track.append((yield_run, yield_path))
        yield yield_run, yield_path


def random_generator(history_runs, application, origin_exchanges):
    """
    generate run by random sequence,and transform application is necessary.
    
    """
    randomed_runs = random.sample(history_runs, len(history_runs))
    ret_run = None
    ret_path = None
    for _run in randomed_runs:
        next_runs = checkmate.runs.find_next_runs(application,
                                                  origin_exchanges, ret_run)
        if _run in next_runs:
            box = checkmate.sandbox.Sandbox(type(application), application)
            assert box(_run.exchanges)
            ret_run = box.blocks
            ret_path = []
        else:
            _run, _path = checkmate.pathfinder.find_path_to_nearest_target(application,
                                                                           next_runs,
                                                                           [_run])
            # synchronize application and yield proper run
            box = checkmate.sandbox.Sandbox(type(application), application)
            ret_path = []
            for item in _path:
                assert box(item.exchanges)
                ret_path.append(box.blocks)
            assert box(_run.exchanges)
            ret_run = box.blocks
        yield ret_run, ret_path
