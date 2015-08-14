Add one Component_2's instance with request=R2, runs
collected from application should be increased.

    >>> import sample_app.application
    >>> import checkmate.tymata.engine
    >>> C2_cls = sample_app.component.component_2.Component_2
    >>> classes = sample_app.application.TestData.component_classes
    >>> C2 = [c for c in classes if c['class'] == C2_cls][0]
    >>> len(C2['instances'])
    1
    >>> C2['instances'].append({'name': 'C4',
    ...     'attributes': {'request': {'C': 'AT2', 'P': 'HIGH'}}})

    >>> C2_cls.instance_attributes['C4'] = {'request':
    ...      {'P': 'HIGH', 'C': 'AT2'}}

    >>> C2_cls.instance_engines['C4'] = checkmate.tymata.engine.AutoMata(
    ...                C2_cls.exchange_module, C2_cls.state_module,
    ...                C2_cls.component_definition)

    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c4 = app.components['C4']
    >>> c4.states[0].R.C.value
    'AT2'

No run should contain more than 1 'AP'
    >>> ap_list = []
    >>> for r in app.run_collection():
    ...     for t in r.walk():
    ...         if len(t.outgoing)>0 and t.outgoing[0].code == 'AP':
    ...             ap_list.append(t.outgoing[0].code)
    ...     if len(ap_list) > 1:
    ...         print(ap_list)
    ...     ap_list = []

revert..
    >>> _v = C2_cls.instance_attributes.pop('C4')
    >>> C2['instances'].remove({'name': 'C4',
    ...     'attributes': {'request': {'C': 'AT2', 'P': 'HIGH'}}})
    >>> _e = C2_cls.instance_engines.pop('C4')
    >>> application_class = sample_app.application.TestData
    >>> delattr(application_class,
    ...     application_class._origin_exchanges_attribute)
    >>> delattr(application_class,
    ...     application_class._run_collection_attribute)
