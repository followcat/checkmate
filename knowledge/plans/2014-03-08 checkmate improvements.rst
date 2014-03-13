Checkmate improvements
======================
checkmate runner
----------------

.. warning::

  Conflicting rules

        "Don't re-invent the wheel"

  vs.
        "If it's a core business function -- do it yourself, no matter what."


The relation between nose plugin and runtime is one to one.
The nose plugin is instantiating only one runtime with a SUT definition.

The test collection is currently done independently from the SUT definition.
This means that the procedure collection is done repeatedly with no change in the output.

Thsi is the same with the state machine. The state machine is parsed each time with the same result.

One of the possible improvement would be that the test collection and state machine parsing is separated from the runner.
A single test collection could support different runs.
These runs might be done in parallel (run at the same time) using one single runner or different concurrent runners.

In order to be able to have concurrent runners to run at the same time, we need the runtime to access to resources that are not shared.
In its current state, the global registry and the logger are shared across different runtime instances.


SUT extraction
--------------
It is possible to extract the list of SUT (--sut=... setting) from the list of exchanges.
All components that interact through exchanges should be tested together.

::

    C1     C2     C3     C4     C5     C6     C7     C8     C9     .....  .....  Cn     .....  ..... Cz>100
     T      T      T      T      T      T      T      T      T      T      T      T      T      T      T 
     |      |      |      |      |      |      |      |      |      |      |      |      |      |      | 
     |      |      |      |      |      |      |      |      |                                         | 
     |      |      |      |      |      |      |      |      \........................................./
     |      |      |      |      |      |      |      |      |\ These components are tested together  /|
     |      |      |      |      |      |      |      |      | \ only is they have direct exchanges  / |
     |      |      |      |      |      |      |      |      |  \ (origin:C9/Cz, destination Cz/C9) /  |
     |      |      |      |      |      |      |      |      |                                         | 


For all components that do not directly interact through exchange, testing them together would bring no different from testing them independently.

Given that all configurations of SUT with 2 components are known, we can retrieve the configuration of SUt with more components.
For definition of SUT with 3 components, we can combine any SUT with 2 components with any third component that forms a 2-component SUT with any.
The same logic can be used in an iterative way to form SUT with more components.


SKipping procedure
------------------
An argument can be made on which procedures must be run for each SUT setting.
Two logics can be put forward

    - run any procedure that can be run
        Following this logic, we focus on running as many procedure as possible to increase the coverage.
        This allows to skip SUT settings that are not interesting as the same tests will be run for SUT that include the original settings.
        An example would be to run a procedure that activate only C1 and C2 when --sut=C1,C2,C3,C4. This test would lead to same result as when using --sut=C1,C2.
    - run any procedure that can bring new information
        Any procedure is checked that it is bringing new information on the system under test.
        An example would be to check a procedure that activate only C1 and C2 when --sut=C1,C2,C3,C4.
        This test would lead to same result as when using --sut=C1,C2. Consequently it would be bypassed for more complex SUT definition.
        That would be assuming that running other procedures with --sut=C1,C2,C3,C4 would not have any impact on the procedure that activate only C1 and C2.
        Based on this logic, all simple SUT must always be run as the tests would not be run for more complex SUT definition.
        That might create some setup or deployment issues.

A procedure should only be run if all components in SUT are activated in the test procedure.
A stricter criteria is that exchanges should involve all combinations of two components to be run.


checkmate visualization
-----------------------
Two types of visualization might be needed for checkmate

    - activity from log files
        The visualization is done using data gathered in log file. The visualization is done after the run.
        This can help to understand *what happened*.
        Mostly for displaying stats (how many tests, how many exchanges, ...)
    - real time activity
        The visualization is done during the run. The data is fed real time to the visualization system.
        This can help showing *what happens*.


State machine as a script
-------------------------
We could reformat the state machine to be able to become script from the checkmate framework.

If the state machine is some script embedded in checkmate, we could achieve

    - reloading state machine changes during checkmate run
    - state machine script can be compiled (syntax check)
    - syntax error in state machine does not break the run
    - state machine script can be shown to user and modify on the fly




