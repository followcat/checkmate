General principle
=================

checkmate is a state machine based testing program for distributed software systems.
Distributed software systems are composed of different components that are interacting through interfaces.
In the scope of checkmate the distributed software system is called with the generic name 'application'.

The interface of each component is defining which command is can receive, service it is providing and which data it is managing. These different types of information managed by a software component are called with the generic name 'exchanges' in the scope of checkmate project.
The component interface does not define the component behavior but only the type of communication it is supporting.
The behavior of the component is defined by its state machine.

If a component's state machine is shown through a diagram, this could look like:

::

    Component C1 state machine
    --------------------------

        +-------------+
        |  True, Q()  |X----+
        +-------------+     |
               |            |
               | AC()       |
               | /RE()      |
               | /ARE()     |
               X            |
        +-------------+     | PP()
        |  False, Q() |     | /PA()
        +-------------+     |
               |            |
               | AP(R)      |
               | /DA()      |
               |            |
               X            |
        +-------------+     |
        | False, Q(R) |-----+
        +-------------+


The different boxes show the state of the component, the arrows show the transition between states with the trigger and the output (preceded with a '/').
The trigger and the output of a state transition is part of the interface of the application's components.
In the scope of checkmate, the trigger is called 'incoming' and the output is called 'outgoing' exchanges.


While diagrams are easy to read, they are difficult to parse by a program. For this reason, state machine in checkmate are defined using tables.
When defined using a table, the state machine looks like:

::

    +---------------------------+---------------------+----------------------------+
    | [Exchange/State/Exchange] | [-/Initial state/-] | [Incoming/Final/Outgoing]  |
    +===========================+=====================+============================+
    | Action                    | x                   | AC()                       |
    +---------------------------+---------------------+----------------------------+
    | State                     | M0(True)            | M0(False)                  |
    +---------------------------+---------------------+----------------------------+
    | Reaction                  | x                   | RE()                       |
    +---------------------------+---------------------+----------------------------+
    | AnotherReaction           | x                   | ARE()                      |
    +---------------------------+---------------------+----------------------------+

    +---------------------------+---------------------+----------------------------+
    | [Exchange/State/Exchange] | [-/Initial state/-] | [Incoming/Final/Outgoing]  |
    +===========================+=====================+============================+
    | Action                    | x                   | AP(R)                      |
    +---------------------------+---------------------+----------------------------+
    | AnotherState              | Q0()                | Q0.append(R)               |
    +---------------------------+---------------------+----------------------------+
    | ThirdAction               | x                   | DA()                       |
    +---------------------------+---------------------+----------------------------+

    +---------------------------+---------------------+----------------------------+
    | [Exchange/State/Exchange] | [-/Initial state/-] | [Incoming/Final/Outgoing]  |
    +===========================+=====================+============================+
    | Action                    | x                   | PP()                       |
    +---------------------------+---------------------+----------------------------+
    | State                     | M0(False)           | M0(True)                   |
    +---------------------------+---------------------+----------------------------+
    | AnotherState              | Q0()                | Q0.pop()                   |
    +---------------------------+---------------------+----------------------------+
    | Pause                     | x                   | PA()                       |
    +---------------------------+---------------------+----------------------------+

Table in checkmate are formated using reStructuredText_


This table is refering to two types of items:
    - states
    - exchanges

    state
        State and AnotherState are two states. The states are defined for the given component.
        Components usually do not share states with each other and consequently a state definition is owned by the component.

    exchange
        Action, Reaction, AnotherReaction and Pause are all exchanges.
        As exchanges are shared between several components (at least a sending and one or several receiving sides), the definition of the exchange is not owned by a component.
        Consequently the definition of an exchange is global for the application.


When put together into an application different components are interacting using their interface based on their state machines.
The state machine are synchronized by matching one component's output with another component's trigger.

::

    Component C1 state machine          Component C3 state machine
    --------------------------          --------------------------

        +-------------+                    +-------------+           
        |  True, Q()  |X----+              |    False    |X----+      
        +-------------+     |              +-------------+     |      
               |            |                     |            |      
               | AC()       |     matches         |            |      
               | /RE() .....|.....................|.RE()       |
               | /ARE()     |                     |            |      
               X            |                     |            |      
        +-------------+     | PP()     matches    |            |      
        |  False, Q() |     | /PA() ..............|............|.PA()
        +-------------+     |                     X            |      
               |            |              +-------------+     |
               | AP(R)      |              |     True    |-----+ 
               | /DA()      |              +-------------+    
               |            |                 |       X       
               X            |                 |  RL() |                  
        +-------------+     |                 |       |           
        | False, Q(R) |-----+                 +-------+       
        +-------------+                    


One of the important part at testing distributed software systems is to check that the different component state machines are compatible (no deadlock).


.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html

