Exchange init func should have action, value and args, kwargs. And value should not in args or kwargs.
    >>> import inspect
    >>> import sample_app.application 
    >>> ap = sample_app.exchange.AP()
    >>> signature_ap = inspect.signature(ap.__init__)
    >>> signature_ap.parameters.get('action')  #doctest: +ELLIPSIS
    <Parameter at ...
    >>> signature_ap.parameters.get('value')  #doctest: +ELLIPSIS
    <Parameter at ...
