carbon copy partition value fail to copy list value
should do a "deepcopy" to list value
    >>> import sample_app.application
    >>> import checkmate.sandbox
    >>> cls = sample_app.application.TestData
    >>> runs = cls.run_collection()
    >>> box = checkmate.sandbox.Sandbox(cls)
    >>> box(runs[0])
    True
    >>> box(runs[2])
    True
    >>> box(runs[3])
    True
    >>> new_box = checkmate.sandbox.Sandbox(cls, box.application)
    >>> box_c1 = box.application.components['C1']
    >>> new_c1 = new_box.application.components['C1']
    >>> box_c1.states[1].value
    []
    >>> new_c1.states[1].value
    []
    >>> new_box(runs[0])
    True
    >>> new_c1.states[1].value # doctest: +ELLIPSIS
    [{'R': <sample_app.data_structure.ActionRequest object at ...
    >>> box_c1.states[1].value
    []
