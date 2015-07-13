After running run1(PBAC). And run1.final has not Component_2 state. 
If component c2 add an exchange with attribute 'R' and R.C != 'AT1'
to it's validation_dict.
The application.compare_states should get True.

    >>> import checkmate.sandbox
    >>> import sample_app.application
    >>> cls = sample_app.application.TestData
    >>> app = cls()
    >>> runs = app.run_collection()

    >>> compare_box1 = checkmate.sandbox.Sandbox(cls)
    >>> compare_box2 = checkmate.sandbox.Sandbox(cls)
    >>> compare_app1 = compare_box1.application
    >>> compare_app2 = compare_box2.application

    >>> box = checkmate.sandbox.Sandbox(cls)
    >>> box_app = box.application
    >>> box(runs[0].exchanges)
    True

    >>> c1 = box_app.components['C1']
    >>> c2 = box_app.components['C2']
    >>> c1_ac_trian = runs[0].nodes[0].validate_items
    >>> ac = c1_ac_trian[0][0]
    >>> add_ac = sample_app.exchanges.Action()
    >>> ac.carbon_copy(add_ac)
    >>> add_ac.R.C = 'AT2'

    >>> runs[0].compare_final(box_app)
    True
    >>> items = ((add_ac,), c1_ac_trian[1])
    >>> c2.validation_dict.record(items)
    >>> runs[0].compare_final(box_app)
    True

