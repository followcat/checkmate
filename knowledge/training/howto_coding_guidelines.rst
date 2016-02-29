Coding guidelines
=================
::

    Code is read more often than it is written.
    Consequently:

        readability supersedes coding speed.

----

    Class names are CamelCased [1_]

    Packages and modules names are underscore ('_') separated lower cased [1_]

    Variable, attribute and method names are underscore ('_') separated lower cased.

    Use '_' prefix to hint private attributes and local variables

    Names are *never* shortened.
        Use 'device' and 'communication' instead of 'dev' and 'com'.

        Exception: for a local variable containing a value of an iterator with self-describing name, a one-letter name is allowed.

            >>> for _i in interfaces:
            ... 
        
    Voyels are **never** removed to shorten names.
        Use 'index' instead of 'indx'.

    Names of variable in **doctest** can be shortened.
        Exception: short name matching ipython global variables are not allowed (like _i, _ii , ...)

    Acronyms follow general rules.
        >>> rst_parser = RstParser('exchanges.rst')

    Avoid repetition in semantic between module, class and attribute/method
        Instead of
            >>> manager.treatment_manager.TreatmentManager.init_manager()
        use
            >>> manager.treatment.Manager.init()


    Import are ordered as:
        - Import build-in modules first
        - Leave a blank line
        - Import third party module
        - Leave a blank line between each third party
        - Import checkmate modules
        - Import checkmate.runtime modules
        - Leave a blank line
        - Import checkmate side module (sample_app, pytango)
        - Leave a blank line between each checkmate side module
        - Leave two blank lines after import section
        - Within each import block the shortest module name is imported first

        >>> import os
        >>> import sys
        >>> import time
        >>> 
        >>> import nose
        >>> import nose.core
        >>> import nose.util
        >>> 
        >>> import checkmate.nose_plugin
        >>> import checkmate.runtime._runtime
        >>> 
        >>> 


    **Never** use:
        >>> [...] import [...] as [...]

    Do not use:
        >>> from [...] import [...]

    Do not use relative path:
        >>> import .[...]

    No code in __init__.py

    An exception is to handle problem in compatibility with external module.
    For example the following code could be allowed in __init__.py,
    to handle possible differences between python2 and python3.
        >>> if sys.version_info[0] >= 3:
        ... 

    or
        >>> try:
        ...     import ...
        ... except ImportError:
        ...     #do something wise
        ...
        
    The code to implement compatibility should be in a standalone module.

    In order to import a module into __init__.py, the use of relative path
    is required.
        >>> import .[...]

    Utility code (debug, sleep, ...) that can possibly be used anywhere
    can be imported in __init__.py to simplify use (no import needed).
    The syntax to import this code in __init__.py should be:
        >>> from .[...] import *

    The [...] should be directly under the same directory as __init__.py.
    Consequently 'from .[...].[...] import ...' should not be used.
    The imported module should define __all__ list of exported symbols.
    An example from checkmate/_issue.py:
        >>> __all__ = ['report_issue', 'fix_issue']
        >>> 

    The exported symbols are not embedded in code (for example decorators).
    The imported module should not import other modules from the project.


----

::

    Any failure to abide to these rules is a bug.
    Consequently:

        it should be reported and fixed.
        The fix should be done in a standalone commit.



.. [1] Exception: third party module as kept with their original case.

