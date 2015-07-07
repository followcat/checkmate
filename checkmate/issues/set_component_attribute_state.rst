Should be able to set component state with component instance's attribute
        >>> import os
        >>> import collections
        >>> import checkmate._module
        >>> import checkmate._storage
        >>> import checkmate.component
        >>> import sample_app.application
        >>> class_name = 'Dummycomponent'
        >>> class_file = 'sample_app/component/dummycomponent.yaml'
        >>> component_module = checkmate._module.get_module(
        ...                         'sample_app.application', 
        ...                         class_name.lower(), 'component')
        >>> exchange_module = sample_app.exchanges
        >>> data_structure_module = sample_app.data_structure
        >>> state_module = checkmate._module.get_module(
        ...                     'checkmate.application', 'states')

    use yaml tab self define declarator @from_attribute
    to set state 'InitState' from attribute ID
        >>> data_source = collections.OrderedDict([
        ... ('data_structure', [{
        ...     'signature': 'Identify',
        ...     'codes_list': [],
        ...     'values_list': [],
        ...     'full_description': None,
        ...     'attributes': {},
        ...     'define_attributes': {}}]),
        ... ('exchanges', [{
        ...    'signature': 'IDAction(I:Identify)',
        ...    'codes_list': ['IDA()'],
        ...    'values_list': ['IDA'],
        ...    'full_description': None,
        ...    'attributes': {},
        ...    'define_attributes': {}}])
        ... ])
        >>> de = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module, state_module=state_module)
        >>> de.new_definitions(data_source)

        >>> class_content = "---\ntitle: 'State identification'\ndata:"
        >>> class_content += "\n  - @from_attribute(I=ID, C=Channel) 'InitState(I:Identify, C:Channel)'"
        >>> _file = open(class_file, 'w')
        >>> _num = _file.write(class_content)
        >>> _file.close()
        >>> _dict = sample_app.application.TestData.communication_list
        >>> communication_list = _dict.keys()
        >>> instance_attributes = collections.defaultdict(dict)
        >>> instance_transitions = collections.defaultdict(dict)

    set component instance attribute "ID" to 1
        >>> instance_attributes['D1'] = {'ID': 1}
        >>> d = {'exchange_module': exchange_module,
        ...  'data_structure_module': data_structure_module,
        ...  '__module__': component_module.__name__,
        ...  'component_definition': class_file,
        ...  'instance_attributes': instance_attributes,
        ...  'instance_transitions': instance_transitions,
        ...  'communication_list': communication_list}

        >>> _class = checkmate.component.ComponentMeta(class_name,
        ...             (checkmate.component.Component,), d)
        >>> setattr(component_module, class_name, _class)
        >>> _app = sample_app.application.TestData()
        >>> d1 = _class('D1', _app.component_registry)
        >>> len(d1.states)
        0
        >>> d1.start()
        >>> len(d1.states)
        1
        >>> d1.ID
        1
        >>> d1.states[0].I.value
        1

    Revert changes for further use in doctest:
        >>> del sample_app.data_structure.Identify
        >>> del sample_app.exchanges.IDAction
        >>> os.remove(class_file)


