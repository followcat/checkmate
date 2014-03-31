import time
import timeit
import logging
import functools


class TimeoutManager():
    timeout_value = None
    logger = logging.getLogger('checkmate.timeout_manager.TimeoutManager')
    @staticmethod
    def get_timeout_value():
        if TimeoutManager.timeout_value is None:
            TimeoutManager.machine_benchmark()
        return TimeoutManager.timeout_value

    @staticmethod
    def machine_benchmark():
        test_code = timeit.Timer("""
import checkmate.exchange
import checkmate.component
import checkmate.application
import checkmate.state_machine
import checkmate.runtime._pyzmq
import checkmate.runtime.registry
import checkmate.runtime.component
import checkmate.runtime.interfaces

setattr(checkmate.component.Component, 'state_machine', checkmate.state_machine.StateMachine())
setattr(checkmate.component.Component, 'services', [])

c = checkmate.runtime._pyzmq.Communication()
gr = checkmate.runtime.registry.global_registry
r = checkmate.runtime.registry.RuntimeGlobalRegistry()
checkmate.runtime.registry.global_registry = r

r.registerAdapter(checkmate.runtime.component.ThreadedStub, (checkmate.component.IComponent,), checkmate.runtime.component.IStub)
r.registerAdapter(checkmate.runtime.component.ThreadedSut, (checkmate.component.IComponent,), checkmate.runtime.component.ISut)

r.registerUtility(checkmate.application.Application(), checkmate.application.IApplication)

r.registerUtility(c, checkmate.runtime.interfaces.ICommunication, 'default')
sa = r.getAdapter(checkmate.component.Component('a'), checkmate.runtime.component.IStub)
sb = r.getAdapter(checkmate.component.Component('b'), checkmate.runtime.component.ISut)
c.initialize(); sa.initialize(); sb.initialize()
c.start(); sa.start(); sb.start()

e = checkmate.exchange.Exchange()
e.origin_destination('a', 'b')
sa.internal_client_list[0].send(e)
sb.stop(); sa.stop(); c.close()
checkmate.runtime.registry.global_registry = gr
""")
        TimeoutManager.timeout_value = round(min(test_code.repeat(5, 1))/1.2, 2)
        TimeoutManager.logger.info("TimeoutManager.timeout_value is %f"%TimeoutManager.timeout_value)

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
    def __init__(self, timeout=1):
        self.loops = 10
        self.timeout = timeout
        self.logger = logging.getLogger('checkmate.timeout_manager.WaitOnException')

    def __call__(self, func):
        global EXCEPTION, FALSE
        def call_(func):
            @functools.wraps(func)
            def new_f(*args, **kwargs):
                raised_exception = None
                sleep_time = self.timeout * TimeoutManager.get_timeout_value() / self.loops

                for loop_times in range(self.loops):
                    try:
                        return_value = self.run_rule(func, *args, **kwargs)
                        break
                    except Exception as e:
                        raised_exception = e

                    time.sleep(sleep_time)
                    self.logger.debug("%s, At %s, Has Been Sleep %f"%(self, func, ((loop_times+1) * sleep_time)))
                else:
                    self.logger.info("%s, %s, At %s, Use %d Loop, Sleep %f, But Not Enough."%(self, raised_exception, func, loop_times, ((loop_times+1) * sleep_time)))
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