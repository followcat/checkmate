When no component is defined in an application, the systenm_under_test
should be an empty list:

    >>> import checkmate.application
    >>> app = checkmate.application.Application()
    >>> app.start()
    >>> app.system_under_test
    []
    >>> app.sut('C1') #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    IndexError: 
    >>> app.system_under_test
    []

