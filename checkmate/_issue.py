import os
import doctest
import functools
import multiprocessing


__all__ = ['report', 'fix']

def runtest(failure_count, filename):
    (failure_count, test_count) = doctest.testfile(
        os.path.sep.join([os.getenv('CHECKMATE_HOME'), filename]),
                         module_relative=False)

def _failed_doctest_file(filename):
    failure_count = multiprocessing.Value('i', 1)
    process = multiprocessing.Process(target=runtest, args=(failure_count, filename))
    process.start()
    process.join()
    return failure_count

def issue_record(filename):
    if not _failed_doctest_file(filename):
        raise doctest.DocTestFailure('Issue not occuring: '+filename, 'Failure', 'Success')

def issue_regression(filename):
    if _failed_doctest_file(filename):
        raise doctest.DocTestFailure('Issue regression: '+filename, 'Success', 'Failure')


def report(filename):
    def append_docstring(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__doc__ += """
            \n        FIXME: Outstanding issue
            \n            >>> import checkmate._issue
            \n            >>> checkmate._issue.issue_record('%s')
            """%filename
        return wrapper
    return append_docstring

def fix(filename):
    def append_docstring(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__doc__ += """
            \n            >>> import checkmate._issue
            \n            >>> checkmate._issue.issue_regression('%s')
            """%filename
        return wrapper
    return append_docstring

