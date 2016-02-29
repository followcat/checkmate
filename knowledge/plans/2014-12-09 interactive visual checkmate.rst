Development of checkmate
========================
- debug, logging
- replay, interactive mode
- data visualization


Debug, logging
--------------
We should be logging in a way that
  - allow the events to be replayed
  - allow the events to be used in statistics
  - does not need to support human reading, step by step debugging

We should support debug in a way that is:
  - interactive
  - repeatable
  - visual


Replay, interactive mode
------------------------
Given that the tests are run mainly in a automatic mode, in case of failure, the run should not be interupted.
The need is thus to report any failure in a way that can be investigated afterwards.
The replay is the use of logged information to restore failure conditions afterward and support investigation.

The investigation is done in an interactive more (like a debugger).
We should support replay step by step. The system should allow easy access to current state.


Data visualization
------------------
Visualization is making complex set of information to be more easily understood.
The successful visualization is based on the adoption of the right format based on the nature of information.

As checkmate is based on non-dulication input data and repetitive runs, it make some information hard to understand:

Input:
  - the input of checkmate is broken between application (exchanges) and components (state_machine).
  - input of checkmate component is broken between partition (state, data structure) and transition (state_machine).
  - input of checkmate partition is broken between partition definition and data values.
  - the transitions for different components can be combined into runs
  - different runs can be combined into path
  - each component can be either stub or ST with different expected behavior

Output:
  - repetitive testing is leading to numerous outcomes.
    The outcomes are in part identical (sequence, successes) in part different (random, failures)
  - when reporting to the user it is important to report in a fair way (percentage of success, failures, ...)
  - over time, the nuerous outcomes can help drawing statistics on the reliability of the testing and the system under test.

All these different aspects must be shown to the user in a fair, complete and understandable way.



Tools
=====
Given that checkmate is developed in python, python tools will be targeted to support replay, interactive mode and visualization.
The tools will have to support interaction with state-of-the-art tools (continuous integration, browser, javascript ...)

The current candidate to support these features is the ipython notebook.
The reasons are:
  - written for python
  - ipython is well know helper in development and testing for python
  - used from the browser (firefox, chrome)
  - developed by a strong team (ipython)
  - used by smart people (scipy)

The feature from ipython notebook that will be useful are:
  - notebooks are saved in structured files
  - notebooks can be sent and replayed
  - builtin interaction with matplotlib for plotting data
  - integration with javascript for interactive drawing

Other features include:
  - serving notebooks through the internet
  - running notebooks in the cloud
  - presentations from notebook (using node.js)


The required software to use ipython notebook will be added as checkmate dependencies.
The versions will be controlled through definition of KGS (known good set).



Design for interactive, visual checkmate
========================================
The basic information to define checkmate setting are:
  - application definition (list of components)
  - components selection (stubs and SUT)
  - runtime and communication

That should be able to be set in an interactive way using widgets (SUT definition, random, number of runs, ...).


The basic information to interact with checkmate are:
  - runs
  - paths
  - ITP procedures
To some extend it is possible that only part of a run is used (by controlling if the stub will process an incmoing exchange).


The user should be able to visualize runs, see how they come from transitions, associate several runs into a path and request the execution of a set of runs.
Runs should be visualized as tree. The runs can be associated by matching the states and exchanges. Runs should be able to be sent to checkmate for execution.
The ability to control the execution of a set of runs will depend on the SUT definition (checkmate does not control a component in SUT).


It the user want to replay a failure case, he should be able to select the failure, load the scenario and run it with some control.



