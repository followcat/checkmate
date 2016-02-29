State machine driven testing
============================
State machine availability
--------------------------
Using state machine to power a test framework as checkmate provides different benefits.

First state machine is a standard design pattern for software.
It is very likely that a recently designed software system has a state machine defined during design step.

Some older software might not have a state machine available from the design but it is still very likely that some state machine has been implemented in the code.
That could be either a centralized state machine or a logic of storage of information in order to be used in a set of if/then/else condition.
Writing the state machine equivalent of existing code is a standard refactoring method.

State machine power
-------------------
The state machine is usually available during the design phase of a software system. Consequently it is available at early stage of the development.

The state machine is also a very good way to communicate between developers and end user.
If the state machine is using terms that are familiar to the end user, they will be able to understand the flow of information and make sure it matches with the process applied to the business.

End user validation of state machines is a good way to detect bad understanding of the business by the software designer or indentify shortcoming of the software solution.


State machine driven testing
----------------------------
Having a state machine powered testing framework has multiple advantages:
    early availability
        Given that the state machine is available at design phase, a test system that uses it can be available early.
        This is very helpful if the software development process is using test driven development, early integration and continuous integration.
    no information loss
        When the test system is based on state machine, the output from the design is directly fed into the test system.
        This prevents from having any information loss during a process of translation into test procedure.
    no test procedure needed
        The test procedure is a direct application of the state machine, so it does not have to be prepared before running the test.
    easy stub implementation
        When running integration test, a classic problem is to develop stubs to replace missing components.
        If the test system is able to read the missing components state machine, it is able to implement a stub without additional effort.
    no need to test setup/teardown logic
        If the initial state of the system to run a test is one of the state of the state machine, the setup of this procedure is easily derived from the state machine
        by executing the different steps from the state machine to bring the system to the desired state.

        Similarly, teardown of a test is just applying a set of state transitions to bring back the system to the original state.
    random testing
        Provided that we can change the state of the system by triggering state transition, we can dynamically compute the teardown of any test.
        Consequently the teardown between a test procedure and the next one is not hardcoded. We can reorder the test procedures in any way we want.

        Running the tests in any random order is supported easily. This allows to cover different user behaviors without additional work.


