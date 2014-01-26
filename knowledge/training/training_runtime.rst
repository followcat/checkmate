Dynamic checkmate.runtime
=========================
The checkmate.runtime Runtime
-----------------------------
The checkmate.runtime Runtime is a dynamic environment where a checkmate application can be loaded and 
where components of this application can exchange messages.

The runtime must be given the application to load:

    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.test_data
    >>> r = checkmate.runtime._runtime.Runtime(checkmate.test_data.App, checkmate.runtime._pyzmq.Communication, threaded=True)
 
Following the checkmate design, if we want to run a procedure in some setting we have to specify the SUT (system under test).
This information should be given to the runtime otherwise it will not be able to know which stub must be created:

    >>> try:
    >>>     r.start_test()
    >>> except Exception as e:
    >>>     print(e)
    'TestData' object has no attribute 'stubs'

This is how it is done:

    >>> r.setup_environment(sut=['C1'])

The environment is then fully set:
    >>> type(r.application)
    <class 'sample_app.application.TestData'>
    >>> r.application.system_under_test
    ['C1']
    >>> r.application.stubs
    ['C3', 'C2']

As we know the application is only containing static components. They will be started at the begining of the test.

    >>> r.start_test()
    >>> r.application.components['C1'].states[0].value
    'True'

The runtime is also keeping reference to the dynamic component using a global registry:

    >>> import checkmate.runtime.registry
    >>> import checkmate.component
    >>> c2 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
    >>> type(c2)
    <class 'checkmate.runtime.component.ThreadedStub'>

The dynamic component has its own reference to the static component in order to delegate management of the state machine
    >>> type(c2.context)
    <class 'sample_app.component_2.component.Component_2'>

The runtime environment is dynamic, so if a checkmate.runtime component is processing an exchange,
the resulting outgoing will be sent to the corresponding component based on the state machine.

    >>> import sample_app.exchanges
    >>> ac = sample_app.exchanges.AC()
    >>> c2.simulate(ac)
    [<sample_app.exchanges.Action object at 0x7f4030e4e210>]
    >>> c3 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C3')
    >>> c3.validate(sample_app.exchanges.RE())
    True
    >>> c2.validate(sample_app.exchanges.DA())
    True

The component states have been updated dynamically

    >>> c1 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C1')
    >>> c1.context.states[0].value
    'False'

We should stress that there is usually no way to access the system under test state.
It can be done because c1 is not the system under test but only the sut:

    >>> type(c1)
    <class 'checkmate.runtime.component.ThreadedSut'>

It is required to stop the runtime environment before quiting:

    >>> r.stop_test()


The checkmate.runtime Component
-------------------------------
We have just seen that there are two types of component:

    checkmate.component
        - static component
        - has a state
        - has a state machine
        - defined by application

    checkmate.runtime.component
        - dynamic component
        - has no state nor state machine
        - not defined in application
        - has a reference to corresponding checkmate.component

Given that the runtime is only given an application (defining checkmate.component) as input, it must create checkmate.runtime.component based on that.
We will now see how.

Lets consider a runtime environment that we load with an application and that we set with SUT=C1:

    >>> import checkmate.runtime.registry
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.test_data
    >>> r = checkmate.runtime._runtime.Runtime(checkmate.test_data.App, checkmate.runtime._pyzmq.Communication, threaded=True)
    >>> r.setup_environment(sut=['C1'])

Based on the SUT definition, the component C2 is not in the system under test and a corresponing stub need to be defined by the runtime.

    >>> 'C2' not in r.application.system_under_test and 'C2' in r.application.stubs
    True

The stub will be created by adapting the C2 Component_2 object defined in the application to implement the IStub interface for stubs:

    >>> import checkmate.runtime.component
    >>> c2_stub = checkmate.runtime.registry.global_registry.getAdapter(r.application.components['C2'], checkmate.runtime.component.IStub)
    >>> type(c2_stub)
    <class 'checkmate.runtime.component.ThreadedStub'>
    >>> checkmate.runtime.component.IStub.providedBy(c2_stub)
    True

By adapting C2 Component_2, c2_stub will automatically get a reference to the object it is adapting in its context attribute

    >>> type(c2_stub.context)
    <class 'sample_app.component_2.component.Component_2'>
    >>> c2_stub.context.name
    'C2'

Consequently the resulting object will be a stub.
It will interact with system under test and will be able to validate incoming exchanges have arrived

    >>> 'validate' in dir(c2_stub)
    True

The component C1 is part  of the system under test and the checkmate.runtime Component will be created by adapting C1 Component_1 with ISut interface.
The resulting object will be a sut and will not interact with the system under test.
It will not provide a validate() method to validate incoming exchanges from system under test.

    >>> 'C1' in r.application.system_under_test
    True
    >>> c1_sut = checkmate.runtime.registry.global_registry.getAdapter(r.application.components['C1'], checkmate.runtime.component.ISut)
    >>> type(c1_sut)
    <class 'checkmate.runtime.component.ThreadedSut'>
    >>> checkmate.runtime.component.ISut.providedBy(c1_sut)
    True
    >>> 'validate' in dir(c1_sut)
    False

