Component example
=================
Component state
---------------
Beside exchanges, an application must define components that will be using them for communication.

As much as an application is owning the exchanges, the component is owning its own states.
For checkmate the states will be defined by the component in a similar way as application exchanges using RST tables.

This is an example of state definition:

::

    Definition and accessibility
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    State

    Value partitions
    ^^^^^^^^^^^^^^^^^

    +---------------+-----------+--------------------------+--------------------------+
    | Partition     | State     | Valid value              | Comment                  |
    +===============+===========+==========================+==========================+
    | S-STATE-01    | M0(True)  | True valid value         | State true value         |
    +---------------+-----------+--------------------------+--------------------------+
    | S-STATE-02    | M0(False) | False valid value        | State false value        |
    +---------------+-----------+--------------------------+--------------------------+


The way the RST table is parsed to create class and interface for each state is identical to the way exchanges are handled.
The created states will however only be known by the component who define them though.

The first value of the table is assumed to be the initial state of the component.

That will be the component state after startup:
    >>> import sample_app.application
    >>> import sample_app.component.component_1
    >>> c1 = sample_app.component.component_1.Component_1('C1')
    >>> c1.start()
    >>> type(c1.states[0]) is sample_app.component_1.states.State
    True
    >>> c1.states[0].value
    'True'

State transition
----------------
Given that an application is defining exchanges and her components are defining states, by combining both, it is possible to parse a transition from the state machine.


::

    Component C1 state machine
    --------------------------
                                +===========================+=====================+============================+
                                | [Exchange/State/Exchange] | [-/Initial state/-] | [Incoming/Final/Outgoing]  |
        +-------------+         +===========================+=====================+============================+
        |  True, Q() .|...\ /...|.Action                    | x                   | AC() ......................|.....transition.incoming[0]
        +-------------+    X    +---------------------------+---------------------+----------------------------+
               | AC() ..../ \...|.State.....................|.M0(True)...      ...|.M0(False) .................|.....transition.final[0]
               |                +---------------------------+-----------.------.--+----------------------------+
               | /RE() .........|.Reaction                  | x         .      .  | RE() ......................|.....transition.outgoing[0]
               |                +---------------------------+-----------.------.--+----------------------------+
               | /ARE() ........|.AnotherReaction           | x         .      .  | ARE() .....................|.....transition.outgoing[1]
               |                +---------------------------+-----------.------.--+----------------------------+
               |                                                        .      . 
        +-------------+                              transition.initial[0]     . 
        |  False, Q().|.........................................................
        +-------------+

This mapping between the table and the transition can be found in the transition definition stored in the component:
    >>> import sample_app.application
    >>> import sample_app.component.component_1
    >>> c1 = sample_app.component.component_1.Component_1('C1')
    >>> transition = c1.state_machine.transitions[0]

The initial and final states for this transition are:
    >>> transition.initial[0].arguments
    (('True',), {})
    >>> transition.final[0].arguments
    (('False',), {})

The incoming and the two outgoing exchanges for this transition are:
    >>> transition.incoming[0].code
    'AC'
    >>> transition.outgoing[0].code
    'RE'
    >>> transition.outgoing[1].code
    'ARE'

If the component current state is matching the initial state of the transition:
    >>> c1 = sample_app.component.component_1.Component_1('C1')
    >>> c1.start()
    >>> transition = c1.state_machine.transitions[0]
    >>> transition.is_matching_initial(c1.states)
    True

The component can process the process the incoming of the transition:
    >>> output = transition.process(c1.states, [sample_app.exchanges.AC()])

It will have its state changed according to the transition definition:
    >>> c1.states[0].value
    'False'

It will output the outgoing defined by the transition:
    >>> output[0].action
    'RE'
    >>> output[1].action
    'ARE'

On the other hand, if its state does not match the initial, it will be unable to process the incoming:
    >>> c1.states[0].value
    'False'
    >>> transition.is_matching_initial(c1.states)
    False
    >>> transition.process(c1.states, [sample_app.exchanges.AC()])
    []

