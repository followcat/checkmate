Coding guidelines
=================
::

    Code is read more often than it is written.
    Consequently:

        readability supersedes coding speed.

----

    Class names are CamelCased [1_]

    Packages and mdoules names are underscore ('_') separated lower cased [1_]

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

    Never use:
        >>> from [...] import [...]

    Never use:
        >>> [...] import [...] as [...]

    Never use relative path:
        >>> import .[...]

    No code in __init__.py

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


----

::

    Any failure to abide to these rules is a bug.
    Consequently:

        it should be reported and fixed.



.. [1] Exception: third party module as kept with their original case.

