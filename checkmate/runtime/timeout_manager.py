import timeit
import time

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
		>>> tt = TestThread()
		>>> tt.start()
		>>> try:
		...     tt.get_after_run_have_num()
		... except Exception as e:
		...     print(e)
		'TestThread' object has no attribute 'after_run_have_num'
		>>> tt2 = TestThread()
		>>> tt2.start()
		>>> checkmate.runtime.timeout_manager.TimeoutManager.function_waiter(func=tt2.get_after_run_have_num,timeout=1)
		0
	"""
	timeout_value = None
	@staticmethod
	def function_waiter(args=(),kwargs={},func=None,timeout=None,times=5,watch_error=None):
		if TimeoutManager.timeout_value is None:
			TimeoutManager.machine_benmark()
		if timeout is None:
			timeout = TimeoutManager.timeout_value
		while(times):
			try:
				return func(*args,**kwargs)
			except:
				time.sleep(timeout)
				times-=1
				timeout*=1.25
		if not times:
			raise ValueError("I sleep %d s at TimeoutManager!"%(timeout))

	@staticmethod
	def machine_benmark():
		TimeoutManager.timeout_value = timeit.timeit('"-".join(str(n) for n in range(100))', number=2000)