Introduction to checkmate storage
=================================
Introduction
------------
One important thing to understand about transition is that the information stored in a transition does not always correspond to a hard coded data but rather to a undetermined possibility of data.
In order to support this undetermined character, the states (initial, final) and the exchanges (incoming, outgoing) defined in a transition are handled using an object.
In checkmate this object is a 'InternalStorage'.

    >>> import sample_app.application
    >>> import sample_app.component_1.component 
    >>> c1 = sample_app.component_1.component.Component_1('C1')
    >>> transition = c1.state_machine.transitions[0] 
    >>> type(transition.incoming[0])
    <class 'checkmate._storage.InternalStorage'>
    >>> type(transition.final[0])
    <class 'checkmate._storage.InternalStorage'>

Value storage
-------------
Let's first have a look to a simple case of internal storage to see its inner mechanism.

One of the important feature of these InternalStorage objects is to have factory method.
By calling this factory method, we will create different object that will be either a state or an exchange based on the information stored in the internal storage

    >>> incoming = transition.incoming[0].factory()
    >>> type(incoming)
    <class 'sample_app.exchanges.Action'>
    >>> final = transition.final[0].factory()
    >>> type(final)
    <class 'sample_app.component_1.states.State'>
    >>> incoming.action == 'AC' and final.value == 'False'
    True

Internally this factory is powered by the function attribute of the InternalStorage.
When looking at the different function attribute for different storages, it is easier to understand the change in behaviour.
The function of an InternalStorage is unfortunately not always a function. It is rather always a callable.

    >>> callable(transition.incoming[0].function) and callable(transition.final[0].function)
    True
    >>> transition.incoming[0].function
    functools.partial(<class 'sample_app.exchanges.Action'>, 'AC')
    >>> transition.final[0].function
    <class 'sample_app.component_1.states.State'>

So we see that value storage is done using a function callcable that is a class.
Calling this storage factory will return an instance of that class with attribute set to the stored value.

Logic storage
-------------
Another case is when the value to store in not set in the storage. It will be programmatically defined when the factory is called.
Let's set up a component for the test

    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> out = c1.process([sample_app.exchanges.AC()]); len(out) == 2
    True
    >>> out = c1.process([sample_app.exchanges.AP(R=True)]); len(out) == 1
    True
    >>> out = c1.process([sample_app.exchanges.AP(R=False)]); len(out) == 1
    True
    >>> c1.states[-1].value
    [{'R': True}, {'R': False}]


The last transition of component 1 has a function attribute that is a real function.

    >>> t = c1.state_machine.transitions[-1]
    >>> t.final[0].function
    <class 'sample_app.component_1.states.State'>
    >>> t.final[1].function
    <function pop at 0x7fa0e99b05f0>

It has no argument and consequently stores no value.

    >>> t.final[1].arguments
    ((), {})

Still after the transition is executed, the final state is not empty. The final state is the resulting state from the application of the function stored in the transition to the initial state of the component. In this case it removes the first element in the list of c1.states[-1].value.

    >>> t.process(c1.states, [sample_app.exchanges.PP()])
    [<sample_app.exchanges.Pause object at 0x7fa0e7825790>]
    >>> c1.states[-1].value
    [{'R': False}]

Let's have a look to the second transition of component C1:

    >>> t = c1.state_machine.transitions[1]

The function attribute of the final storage is also a function. It has a keyword argument that will be taken as default value.

    >>> t.final[0].function
    <function append at 0x7fbb45c67560>
    >>> t.final[0].arguments
    ((), {'R': None})

If we provide enough data during execution of the transition, the factory does not use the default value.
In this case the 'R' attribute is set to the value given in the incoming exchange AP.

    >>> t.process(c1.states, [sample_app.exchanges.AP(R=True)])
    [<sample_app.exchanges.ThirdAction object at 0x7fa0e7825950>]
    >> c1.states[-1].value
    [{'R': False}, {'R': True}]

On this other hand, if we give no information, the factory will use the default value.

    >>> t.process(c1.states, [sample_app.exchanges.AP()])
    [<sample_app.exchanges.ThirdAction object at 0x7fa0e78257d0>]
    >>> c1.states[-1].value
    [{'R': False}, {'R': True}, {'R': <sample_app.data_structure.ActionRequest object at 0x7fa0e7825850>}]

