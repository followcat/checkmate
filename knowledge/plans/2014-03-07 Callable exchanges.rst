Exchange definition
===================
Problem statement
-----------------
Some exchange in checkmate are corresponding to function calls.
A function in a static typed language can be defined as:

    int func(char* name, int id);

This function will be called by passing the expected paramters and the return code will be catched.

    rc = func('device', 1);


Exchange definition
-------------------
The exchange in checkmate is defined using python. The exchange is an object that can be passed around before being actually called.
Typically an exchange is created by a component state machine and will be passed to a client for calling the corresponding server.

Python is not a statically typed language but some support for type definition can be implemented using annotations.
A function can be defined using annotation in the following way:

    >>> def func(name:str, id:int) -> int:
    ...     pass
    ...

The annotations can be retrieved using the inspect module:

    >>> import inspect
    >>> sig = inspect.signature(func)
    >>> sig.parameters['name'].annotation
    <class 'str'>
    >>> sig.return_annotation
    <class 'int'>

Lets note that the annotations is not enforced in the python code:
    >>> func(name='device', id=1)
    >>> func(name=1, id='device')
    >>> type(sig.bind(1, 'device').arguments['name']) == sig.parameters['name'].annotation
    False


The current definition of exchange in checkmate could be done using annotations.

.. note:: the parsing of the following code is done in checkmate using the ast module.
.. warning:: The parsing is supporting both the class definition and the partition value definition

For example, the following class definition::

    Data structure
    +++++++++++++++
    Attribute
    **********
    Definition and accessibility
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Attribute


    Action priority
    ****************
    Definition
    ^^^^^^^^^^^
    ActionPriority


    Action request
    ***************
    Definition
    ^^^^^^^^^^^
    ActionRequest(P=ActionPriority, A=Attribute)



    Exchange identification
    ++++++++++++++++++++++++
    Action
    *******
    Definition and accessibility
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Action(R=ActionRequest)


could be done in python annotation with:

    >>> class Attribute(object):
    ...     """"""
    ... 
    >>> class ActionPriority(object):
    ...     """"""
    ... 
    >>> class ActionRequest(object):
    ...     def __init__(self, P: ActionPriority, A:Attribute):
    ...         pass
    ... 
    >>> import checkmate.exchange
    >>> class Action(checkmate.exchange.Exchange):
    ...     def __init__(self, R:ActionRequest):
    ...         pass
    ... 

The corresponding reStructuredText would be::
    
    Action request
    ***************
    Definition
    ^^^^^^^^^^^
    ActionRequest(P:ActionPriority, A:Attribute)

The class can be defined based on the annotation read from rst:

    >>> import sample_app.exchanges
    >>> hasattr(sample_app.exchanges, 'ActionRequest')
    False
    >>> rst = "ActionRequest(P:ActionPriority, A:Attribute)"
    >>> code = """class ActionRequest(object):
    ...     def __init__""" + str(sig).replace('(', '(self, ') + """:
    ...         pass"""
    >>> exec(code,globals(),sample_app.exchanges.__dict__)
    >>> sample_app.exchanges.ActionRequest
    <class '__main__.ActionRequest'>


Exchange call
-------------
Currently in checkmate, an exchange is sent using the syntax:

    >>> c1.process(ex)

where
    ex
        is the exchange
    c1
        is a component the exchange is sent to.
        This is usually coming from the destination attribute of ex
 

This syntax is pretty far from the original C syntax for function call.

An alternative definition of the exchange would allow to just call the exchange to get it processed.
    >>> import sample_app.application
    >>> import sample_app.data_structure
    >>> class Action(sample_app.exchanges.Action):
    ...     def __init__(self, R:sample_app.data_structure.ActionRequest):
    ...         super().__init__(self)
    ...         self.value = R
    ...     def __call__(self):
    ...         self.destination.process([self])
    ...
    >>> ex = Action('AC')
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> c2 = app.components['C2']
    >>> ex.origin_destination(c2, c1)
    >>> c1.states[0].value
    True
    >>> ex()
    >>> c1.states[0].value
    False

.. todo:: The current implementation of ServiceRegistry is setting component's *name* in origin_destination()


Exchange return
---------------
Given an exchange with the following definition::

    Action
    *******
    Definition
    ^^^^^^^^^^^
    Action(R:ActionRequest) -> int

This could be implemented in python by the following code:

    >>> class Action(sample_app.exchanges.Action):
    ...     def __init__(self, R:sample_app.data_structure.ActionRequest):
    ...         super().__init__(self)
    ...         self.value = R
    ...     def __call__(self) -> int:
    ...         return self.destination.process([self])
    ...

.. todo:: This requires Component's process() method to return the return code instead of the outgoing exchanges

Doing so, the execution of the exchange would then be similar to the call of a function:

    >>> rc = ex()


Outgoing exchange
-----------------
If the process() method is returning the return code, there must be a way to pass the outgoing exchanges from the transition triggered by incoming.
One way is to have all the outgoing exchanges to be sent before the process() method returns.
This can only be done is the outgoing exchanges are callable and use resource that are globally available (like service registry).

The resource to perform the execution of the exchange may depend on the type of application that is running (runtime, threaded, non-threaded).
For example when running from a Runtime, the code self.destination.process([self]) does not work as destination is a checkmate.component.Component
and not a checkmate.runtime.component.Component.

    >>> import zope.interface
    >>> import sample_app.exchanges
    >>> import checkmate.application
    >>> import sample_app.application
    >>> import sample_app.data_structure
    >>> import zope.component.globalregistry
    >>> app = sample_app.application.TestData()
    >>> @zope.interface.implementer(checkmate.application.IApplication)
    ... class App(object):
    ...     def execute(self, exchange):
    ...         (rc, outgoing) = exchange.destination.process([exchange])
    ...         for _out in outgoing:
    ...             self.execute(_out)
    ...         return rc
    ... 
    >>> reg  = zope.component.globalregistry.BaseGlobalComponents()
    >>> reg.registerUtility(App(), checkmate.application.IApplication)
    >>> class Action(sample_app.exchanges.Action):
    ...     def __init__(self, R:sample_app.data_structure.ActionRequest):
    ...         super().__init__(self)
    ...         self.value = R
    ...     def __call__(self) -> int:
    ...         application = reg.getUtility(checkmate.application.IApplication)
    ...         return application.execute(ex)
    ... 
    >>> ex = Action('AC')
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> c2 = app.components['C2']
    >>> ex.origin_destination(c2, c1)
    >>> c1.states[0].value
    >>> rc = ex()

.. todo:: This requires Component's process() method to return the return code and the outgoing exchanges as a tuple




