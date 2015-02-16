After running run1(PBAC). And run1.final has not Component_2 state. 
If component c2 add an exchange with attribute 'R' and R.C != 'AT1'
to it's validation_list.
The application.compare_states should get True.

    >>> import checkmate.sandbox
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> runs = app.run_collection

    >>> compare_box1 = checkmate.sandbox.Sandbox(app)
    >>> compare_box2 = checkmate.sandbox.Sandbox(app)
    >>> compare_app1 = compare_box1.application
    >>> compare_app2 = compare_box2.application

    >>> box = checkmate.sandbox.Sandbox(app)
    >>> box_app = box.application
    >>> box(runs[0])
    True

    >>> c1 = box_app.components['C1']
    >>> c2 = box_app.components['C2']
    >>> ac = c1.get_all_validated_incoming()[0]
    >>> add_ac = sample_app.exchanges.Action()
    >>> ac.carbon_copy(add_ac)
    >>> add_ac.R.C = 'AT2'

    >>> box_app.compare_states(runs[0].final, compare_app1.state_list())
    True
    >>> c2.validation_list[-1].append(add_ac)
    >>> c2.validation_list.validated_items[-1].append(add_ac)
    >>> box_app.compare_states(runs[0].final, compare_app2.state_list())
    True

