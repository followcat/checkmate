The checkmate nose plugin
=========================
The nosetests tool
------------------
nosetests is a python test tool build upon the standard unittest module.


The checkmate plugin
--------------------
The nosetests tools is a tool to run tests in a unified way in python. It can be used to collect and run the doctest in checkmate code.

A new checkmate plugin has been defined in order to run checkmate based tests using nosetests.
From the nosetests framework, checkmate inherit from automatic test collection. 
The collected tests are sorted in test suites in an alphabetical order.

The plugin is understanding the folowing options:
    sut=...
        define the system under test to set for running the procedures.
        If not provided, the system under test is empty and all started components are stubs.
    runs=...
        define the number of repetition of the collected procedures.
        Each procedure is run once before the loop is started over.
    random
        add randomness *within each test suite* to the order of procedure.
        When combined with the runs=... option, each loop will be randomized independently.


