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


def report_issue(filename):
    def append_docstring(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__doc__ += """
            \n        FIXME: Outstanding issue
            \n            >>> import checkmate._issue
            \n            >>> checkmate._issue._issue_record('%s')
            """%filename
        return wrapper
    return append_docstring

def fix_issue(filename):
    def append_docstring(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__doc__ += """
            \n            >>> import checkmate._issue
            \n            >>> checkmate._issue._issue_regression('%s')
            """%filename
        return wrapper
    return append_docstring

