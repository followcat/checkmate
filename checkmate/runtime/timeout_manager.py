import time
import timeit
import logging
import functools


class TimeoutManager():
    timeout_value = None
    logger = logging.getLogger('checkmate.runtime.timeout_manager.TimeoutManager')
    @staticmethod
    def get_timeout_value():
        if TimeoutManager.timeout_value is None:
            TimeoutManager.machine_benchmark()
        return TimeoutManager.timeout_value

    @staticmethod
    def machine_benchmark():
        TimeoutManager.timeout_value = timeit.timeit("""
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

r.registerAdapter(checkmate.runtime.component.ThreadedStub,(checkmate.component.IComponent,), checkmate.runtime.component.IStub)
r.registerAdapter(checkmate.runtime.component.ThreadedSut,(checkmate.component.IComponent,), checkmate.runtime.component.ISut)

r.registerUtility(checkmate.application.Application(), checkmate.application.IApplication)

r.registerUtility(c, checkmate.runtime.interfaces.ICommunication, 'default')
sa = r.getAdapter(checkmate.component.Component('a'),checkmate.runtime.component.IStub)
sb = r.getAdapter(checkmate.component.Component('b'),checkmate.runtime.component.ISut)
c.initialize(); sa.initialize(); sb.initialize()
c.start(); sa.start(); sb.start()

e = checkmate.exchange.Exchange()
e.origin_destination('a', 'b')
sa.internal_client_list[0].send(e)
sb.stop(); sa.stop(); c.close()
checkmate.runtime.registry.global_registry = gr
""", number=2)/5
        TimeoutManager.logger.debug("TimeoutManager.timeout_value is %f"%TimeoutManager.timeout_value)

class SleepAfterCall():
    loop_times = 10

    def __init__(self, timeout = None):
        self.sleep_time =  timeout
    def __call__(self, func):
        def call_(func):
            @functools.wraps(func)
            def new_f(*args, **kwargs):
                return_value = func
                if self.sleep_time is None:
                    self.sleep_time = TimeoutManager.get_timeout_value() / self.loop_times
                return_value = func(*args,**kwargs)
                time.sleep(self.sleep_time)
                return return_value
            return new_f

        if not func:
            def go_without_args(func):
                return call_(func)
            return go_without_args
        else:
            return call_(func)

class WaitOnException():
    """
        >>> import time
        >>> import threading
        >>> import checkmate.runtime.timeout_manager
        >>> class TestThread(threading.Thread):
        ...     def __init__(self):
        ...         super(TestThread, self).__init__()
        ...     def run(self):
        ...         time.sleep(1)
        ...         self.after_run_have_num = 0
        ...     def get_after_run_have_num(self):
        ...         print(self.after_run_have_num)
        ...     @checkmate.runtime.timeout_manager.WaitOnException(timeout=2)
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
    loop_times = 10
    
    def __init__(self, timeout = None):
        self.timeout = timeout
        self.already_sleep_time = 0
        self.already_loop_times = 0
        self.exception_saver = None
        self.logger = logging.getLogger('checkmate.runtime.timeout_manager.WaitOnException')
    def __call__(self, func):
        def call_(func):
            @functools.wraps(func)
            def new_f(*args, **kwargs):
                if self.timeout is None:
                    self.timeout = TimeoutManager.get_timeout_value()
                self.sleep_totaltime = self.timeout
                self.sleep_time = self.sleep_totaltime / self.loop_times
                return_value = func
                while(self.already_loop_times < self.loop_times):
                    try:
                        return_value = func(*args,**kwargs)
                        break
                    except Exception as e:
                        time.sleep(self.sleep_time)
                        self.already_sleep_time += self.sleep_time
                        self.already_loop_times += 1
                        self.exception_saver = e
                        self.logger.debug("%s,At %s,Has Been Sleep %f"%(self,func,self.already_sleep_time))
                if self.already_loop_times >= self.loop_times:
                    self.logger.info("%s,%s,At %s,Use %d Loop,Sleep %f,But Not Enough."%(self,self.exception_saver,func,self.already_loop_times,self.already_sleep_time))
                return return_value
            return new_f

        if not func:
            def go_without_args(func):
                return call_(func)
            return go_without_args
        else:
            return call_(func)

