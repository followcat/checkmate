import time
import timeit
import functools


def sleep_after_call(func=None,usetime=None):
    def call_(func):
        @functools.wraps(func)
        def new_f(*args,**kwargs):
            timeout = usetime
            if TimeoutManager.timeout_value is None:
                TimeoutManager.machine_benchmark()
            if timeout is None:
                timeout = TimeoutManager.timeout_value
            return_value = func(*args,**kwargs)
            time.sleep(timeout)
            return return_value
        return new_f

    if not func:
        def go_without_args(func):
            return call_(func)
        return go_without_args
    else:
        return call_(func)


def wait_on_exception(func=None,usetime=None):
    def call_(func):
        @functools.wraps(func)
        def new_f(*args,**kwargs):
            sleep_totaltime = 0
            timeout = usetime
            if TimeoutManager.timeout_value is None:
                TimeoutManager.machine_benchmark()
            times = TimeoutManager.times
            if timeout is None:
                timeout = TimeoutManager.timeout_value
            while(True):
                try:
                    return_value = func(*args,**kwargs)
                    sleep_totaltime += timeout
                    break
                except Exception as e:
                    time.sleep(timeout)
                    sleep_totaltime += timeout
                    times-=1
                    if not times:
                        raise ValueError(e,func,"Has Been Sleep %f"%(sleep_totaltime))
            return return_value
        return new_f

    if not func:
        def go_without_args(func):
            return call_(func)
        return go_without_args
    else:
        return call_(func)


class TimeoutManager():
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
        ...     @checkmate.runtime.timeout_manager.wait_on_exception(usetime=0.5)
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
    timeout_value = None
    times = 10

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
""", number=2)/50

