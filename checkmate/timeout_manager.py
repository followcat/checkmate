# This code is part of the checkmate project.
# Copyright (C) 2014-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import time
import timeit
import logging
import functools


SAMPLE_APP_RECEIVE_SEC = 1
PYTANGO_RECEIVE_SEC = 0.001
PYTANGO_REGISTRY_SEC = 1

CHECK_COMPARE_STATES_SEC = 0.01
VALIDATE_SEC = 0.1
SUT_COMMUNICATE_DELAY = 0.002

POLLING_TIMEOUT_MILLSEC = 1000

THREAD_STOP_SEC = 1


class TimeoutManager():
    # set it to None to use timeit computation
    timeout_value = 1
    processing_benchmark = False
    logger = logging.getLogger('checkmate.timeout_manager.TimeoutManager')

    @staticmethod
    def get_timeout_value():
        if TimeoutManager.timeout_value is None:
            TimeoutManager.machine_benchmark()
        return TimeoutManager.timeout_value

    @staticmethod
    def machine_benchmark():
        if TimeoutManager.processing_benchmark:
            TimeoutManager.timeout_value = 1
            return
        TimeoutManager.processing_benchmark = True
        test_code = timeit.Timer("""
import logging

import checkmate.exchange
import checkmate.component
import checkmate.application
import checkmate.tymata.engine
import checkmate.runtime._pyzmq
import checkmate.runtime._runtime
import checkmate.runtime.component

class Comp(checkmate.component.Component):
    name = ''
    service_classes = []
    engine = checkmate.tymata.engine.StateMachine()
    connector_list = (checkmate.runtime._pyzmq.Connector,)

class App(checkmate.application.Application):
    __module__ = 'timeout_manager.test.App'
    exchange_module = checkmate.exchange
    def __init__(self):
        super().__init__()
        self.components = {'a': Comp('a', self.component_registry),
             'b': Comp('b', self.component_registry)}
        self.components['a'].connecting_components = ['b']
        self.components['b'].connecting_components = ['a']

runtime = checkmate.runtime._runtime.Runtime(App,
            checkmate.runtime._pyzmq.Communication, True)

runtime.setup_environment(['b'])
sa = runtime.runtime_components['a']
sb = runtime.runtime_components['b']
runtime.start_test()

e = checkmate.exchange.Exchange('Exchange')
e.origin_destination('a', 'b')

runtime_log = logging.getLogger('checkmate')
logging.disable(logging.INFO)
for i in range(0, 10000):
    sa.client.send(e)
logging.disable(logging.NOTSET)

#stop everything except the logger
sa.stop(); sb.stop();
runtime.communication_list['default'].close();
runtime.communication_list[''].close();
sa.join(); sb.join();
runtime.communication_list['default'].registry.join();
runtime.communication_list[''].registry.join()
""")
        TimeoutManager.timeout_value = round(
            max(test_code.repeat(1, 1)) / 4, 2)
        TimeoutManager.processing_benchmark = False
        TimeoutManager.logger.info("TimeoutManager.timeout_value is %f" %
                                   TimeoutManager.timeout_value)


class SleepAfterCall():
    def __init__(self, timeout=0.06):
        self.timeout = timeout

    def __call__(self, func):
        def call_(func):
            @functools.wraps(func)
            def new_f(*args, **kwargs):
                sleep_time = self.timeout * TimeoutManager.get_timeout_value()
                return_value = func(*args, **kwargs)
                time.sleep(sleep_time)
                return return_value
            return new_f

        if not func:
            def go_without_args(func):
                return call_(func)
            return go_without_args
        else:
            return call_(func)


class WaitOn():
    """
        >>> import time
        >>> import threading
        >>> import checkmate.timeout_manager
        >>> class TestThread(threading.Thread):
        ...     def __init__(self):
        ...         super(TestThread, self).__init__()
        ...     def run(self):
        ...         time.sleep(1)
        ...         self.after_run_have_num = 0
        ...     def get_after_run_have_num(self):
        ...         print(self.after_run_have_num)
        ...     @checkmate.timeout_manager.WaitOnException(timeout=2)
        ...     def get_after_run_have_num_with_function_waiter(self):
        ...         print(self.after_run_have_num)
        >>> tt = TestThread()
        >>> tt.start()
        >>> try:
        ...     tt.get_after_run_have_num()
        ... except Exception as e:
        ...     print(e)
        'TestThread' object has no attribute 'after_run_have_num'
        >>> tt2 = TestThread()
        >>> tt2.start()
        >>> tt2.get_after_run_have_num_with_function_waiter()
        0
    """
    def __init__(self, timeout=1, loops=10):
        self.loops = loops
        self.timeout = timeout
        self.logger = logging.getLogger(
            'checkmate.timeout_manager.WaitOnException')

    def __call__(self, func):
        global EXCEPTION, FALSE

        def call_(func):
            @functools.wraps(func)
            def new_f(*args, **kwargs):
                raised_exception = None
                sleep_time = self.timeout * \
                    TimeoutManager.get_timeout_value() / self.loops

                for loop_times in range(self.loops):
                    begin_time = time.time()
                    try:
                        return_value = self.run_rule(func, *args, **kwargs)
                        break
                    except Exception as e:
                        raised_exception = e
                    run_time = time.time() - begin_time
                    try:
                        time.sleep(sleep_time - run_time)
                    except ValueError:
                        # sleep_time - run_time < 0
                        continue
                    self.logger.debug(
                        "%s, At %s, Has Been Sleep %f" %
                        (self, func, ((loop_times + 1) * sleep_time)))
                else:
                    self.logger.info("%s, %s, At %s, Use %d Loop, Sleep %f,\
                        But Not Enough." % (self, raised_exception, func,
                                            loop_times,
                                            ((loop_times + 1) * sleep_time)))
                    return func(*args, **kwargs)
                return return_value
            return new_f

        if not func:
            def go_without_args(func):
                return call_(func)
            return go_without_args
        else:
            return call_(func)

    def run_rule(self, func, *args, **kwargs):
        """"""


class WaitOnException(WaitOn):
    def run_rule(self, func, *args, **kwargs):
        return func(*args, **kwargs)


class WaitOnFalse(WaitOn):
    def run_rule(self, func, *args, **kwargs):
        return_value = func(*args, **kwargs)
        if return_value is False:
            raise Exception("return False")
        return return_value
