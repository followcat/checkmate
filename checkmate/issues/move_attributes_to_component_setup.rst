move extra attributes from AutoMata to ComponentMeta. Actually the
attributes services, service_classes and communications are not
necessary to be collected from blocks in ComponentMeta, specially when
block list will be extended. So They can be collected when they are
used during runtime communication setup.

    >>> import sample_app.application
    >>> c1_cls = sample_app.component.component_1.Component_1
    >>> c1_attr = c1_cls.instance_attributes['C1']
    >>> attributes = list(c1_attr.keys())
    >>> 'services' in attributes
    False
    >>> 'service_classes' in attributes
    False
    >>> app = sample_app.application.TestData()
    >>> c1 = app.components['C1']
    >>> c1.setup()
    >>> hasattr(c1, 'services')
    True
    >>> hasattr(c1, 'service_classes')
    True
    >>> hasattr(c1, 'communications')
    True

