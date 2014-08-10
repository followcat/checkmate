import os
import doctest
import functools
import multiprocessing


__all__ = ['report_issue', 'fix_issue', 'runtest']


class Runner(doctest.DocTestRunner):
     def report_unexpected_exception(self, *args, **kwargs):
         """Remove junk from failure output"""
         pass
     def report_failure(self, *args, **kwargs):
         pass


def runtest(filename):
    with open(os.path.sep.join([os.getenv('CHECKMATE_HOME'), filename])) as _f:
        test = _f.read()
    _r = Runner(verbose=False)
    return _r.run(doctest.DocTestParser().get_doctest(test, locals(), filename, None, None))

def _issue_record(filename):
    result = runtest(filename)
    if result.failed == 0:
        raise doctest.DocTestFailure('Issue: '+filename, 'Expected: failure', 'Got: success')

def _issue_regression(filename):
    result = runtest(filename)
    if result.failed != 0:
        raise doctest.DocTestFailure('Issue regression: '+filename, 'Expected: success', 'Got: failure')

def _add_issue_doctest(filename, doctest_function):
    def append_docstring(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        if wrapper.__doc__ is None:
            wrapper.__doc__ = ""
        wrapper.__doc__ += """
            \n            >>> %s.%s('%s')
            """ % (__name__, doctest_function.__name__, filename)
        return wrapper
    return append_docstring

def report_issue(filename):
    """
        >>> import os
        >>> import doctest
        >>> import checkmate._issue
        >>> filename = 'dt1.rst'

    Hardcoded failed doctest:
        >>> with open(os.sep.join([os.getenv('CHECKMATE_HOME'), filename]), 'w') as f:
        ...     n = f.write(\">>> print(False)\\nFalse\")
        ... 
        >>> @checkmate._issue.report_issue(filename)
        ... def func():
        ...     pass
        >>> _r = checkmate._issue.Runner(verbose=False)
        >>> _r.run(doctest.DocTestParser().get_doctest(func.__doc__, locals(), func.__name__, None, None)) # doctest: +ELLIPSIS
        TestResults(failed=1, ...

    Hardcoded successful doctest:
        >>> with open(os.sep.join([os.getenv('CHECKMATE_HOME'), filename]), 'w') as f:
        ...     n = f.write(\">>> print(True)\\nFalse\")
        ... 
        >>> @checkmate._issue.report_issue(filename)
        ... def func():
        ...     pass
        ... 
        >>> doctest.run_docstring_examples(func, locals())
        >>> os.remove(os.sep.join([os.getenv('CHECKMATE_HOME'), filename]))
    """
    return _add_issue_doctest(filename, _issue_record)

def fix_issue(filename):
    """
        >>> import os
        >>> import doctest
        >>> import checkmate._issue
        >>> filename = 'dt1.rst'

    Hardcoded successful doctest:
        >>> with open(os.sep.join([os.getenv('CHECKMATE_HOME'), filename]), 'w') as f:
        ...     n = f.write(\">>> print(False)\\nFalse\")
        ... 
        >>> @checkmate._issue.fix_issue(filename)
        ... def func():
        ...     pass
        ... 
        >>> doctest.run_docstring_examples(func, locals())

    Hardcoded failed doctest:
        >>> with open(os.sep.join([os.getenv('CHECKMATE_HOME'), filename]), 'w') as f:
        ...     n = f.write(\">>> print(True)\\nFalse\")
        ... 
        >>> @checkmate._issue.fix_issue(filename)
        ... def func():
        ...     pass
        >>> _r = checkmate._issue.Runner(verbose=False)
        >>> _r.run(doctest.DocTestParser().get_doctest(func.__doc__, locals(), func.__name__, None, None)) # doctest: +ELLIPSIS
        TestResults(failed=1, ...
        >>> os.remove(os.sep.join([os.getenv('CHECKMATE_HOME'), filename]))
    """
    return _add_issue_doctest(filename, _issue_regression)

