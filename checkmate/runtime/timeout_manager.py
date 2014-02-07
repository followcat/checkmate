import time
import timeit
from functools import wraps

def functionwaiter(func=None,usetime=None):
	def call_(func):
		@wraps(func)
		def new_f(*args,**kwargs):
			timeout = usetime
			if TimeoutManager.timeout_value is None:
				TimeoutManager.machine_benmark()
			times = TimeoutManager.times
			if timeout is None:
				timeout = TimeoutManager.timeout_value
			while(True):
				try:
					return_value = func(*args,**kwargs)
					time.sleep(timeout)
					break
				except Exception as e:
					time.sleep(timeout)
					times-=1
					if not times:
						raise ValueError(e,"Has Been Sleep %f"%(TimeoutManager.times*timeout))
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
		...     @checkmate.runtime.timeout_manager.functionwaiter(usetime=0.5)
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
	def machine_benmark():
		TimeoutManager.timeout_value = timeit.timeit('"-".join(str(n) for n in range(100))', number=2000)