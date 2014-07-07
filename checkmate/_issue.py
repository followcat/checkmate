import os
import doctest
import functools
import multiprocessing


__all__ = ['report_issue', 'fix_issue']

def runtest(failure_count, filename):
    (failure_count.value, test_count) = doctest.testfile(
        os.path.sep.join([os.getenv('CHECKMATE_HOME'), filename]),
                         module_relative=False)

def _failed_doctest_file(filename):
    failure_count = multiprocessing.Value('i', 1)
    process = multiprocessing.Process(target=runtest, args=(failure_count, filename))
    process.start()
    process.join()
    return failure_count

def _issue_record(filename):
    _synchronized = _failed_doctest_file(filename)
    if _synchronized.value == 0:
        raise doctest.DocTestFailure('Issue: '+filename, 'Expected: failure', 'Got: success')

def _issue_regression(filename):
    _synchronized = _failed_doctest_file(filename)
    if _synchronized.value > 0:
        raise doctest.DocTestFailure('Issue regression: '+filename, 'Expected: success', 'Got: failure')

def _add_issue_doctest(filename, doctest_function):
    def append_docstring(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        #Need to destroy zmq context due to conflict
        #between zmq threading and multiprocessing (src/mailbox.cpp)
        wrapper.__doc__ += """
            \n        FIXME: Outstanding issue
            \n            >>> import zmq
            \n            >>> import checkmate._issue
            \n            >>> zmq.Context.instance().destroy()
            \n            >>> %s.%s('%s')
            """ % (__name__, doctest_function.__name__, filename)
        return wrapper
    return append_docstring

def report_issue(filename):
    return _add_issue_doctest(filename, _issue_record)

def fix_issue(filename):
    return _add_issue_doctest(filename, _issue_regression)

