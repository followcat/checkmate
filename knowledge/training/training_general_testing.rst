General testing
===============
Distributed system testing
--------------------------
Standard techniques for testing distributed system have been developed.

Suppose an application composed of 3 components that have interactions as illustred in the following diagram:

.. graphviz::

    digraph finite_state_machine {
        rankdir=LR;
        size="8,5"
        node [shape = rectangle];
        C2 -> C1 [ label = "1.AC" ];
        C1 -> C2 [ label = "3.ARE" ];
        C1 -> C3 [ label = "2.RE" ];
        C2 -> C1 [ label = "4.AP" ];
        C1 -> C2 [ label = "5.DA" ];
    }

A basic method is to have the components to log all the interactions into file and parse the output to compare to expected log files.
This technique suffer some limitations including:

    - this does not cover how to input the test scenario into the application
    - trouble to finely compare log files 
    - heavy duplication of scenario/logs due to limitation at combining them
    - log file generation may change the behavior of the system under test (slowing down, race conditions, ...)


An improved technique is to introduce a testing component that listen to the interactions between the component under test.
Given that a test dedicated to the system, it is easy to embebbed in this component logic to interact with the system under test.
New limitations appear in this setting:

    - need to have the testing component not to interfere with the system under test
    - some interactions are difficult to listen to
    - all the components from the application under test need to be available


Standard test setting
---------------------
Consequently throughout the years, new techniques were developed including stubbing, test procedure, test setup and test teardown.
The stubbing technique is important as it allow the tests to be run while some component are missing.
They could be missing to make the testing easier (avoid full application deployment) or because the component code is not available (phasing in development, third party component, proprietary code ...)

A configuration like the one described below would be used when we test the application without component C2:

.. graphviz::

    digraph finite_state_machine {
        compound=true;
        rankdir=LR;
        size="8,5"
        node [shape = rectangle];
        splines="ortho";
        subgraph cluster_driver { 
            label = "Test driver";
            Driver;
        }
        subgraph cluster_stub { 
            label = "Stub";
            bgcolor = "yellow";
            C2;
        }
        subgraph cluster_sut { 
            label = "System under test";
            bgcolor = "green";
            C1; C3;
        }
        Driver -> C1 [ label = "1.AC" ];
        C1 -> C2 [ label = "3.ARE" ];
        C1 -> C3 [ label = "2.RE" ];
        Driver -> C1 [ label = "4.AP" ];
        C1 -> C2 [ label = "5.DA" ];
        Driver -> C2 [label="controls", lhead="cluster_stub"];
        Driver -> C2 [label="checks", lhead="cluster_stub"];
        Driver -> C3 [label="setup", lhead="cluster_sut"];
        Driver -> C3 [label="teardown", lhead="cluster_sut"];
    }

The test driver is used to synchronize with the stub and to do the processing of the test procedure.

The stub is passive and the driver is used directly to input action to the system under test.
In order to feed the test driver with the relevant information to run the test, the test procedure must define a setup and teardown process.

    setup
        is used before running the test to set the system under test to the right state.
        The current state of the system under test is not an input to the setup.
        So an assumption on the current state of the system is made when writing the setup.
        The setup can be a reference to an existing test procedure.
        
    teardown
        is used after the procedure is run to bring back the system under test to original state.
        The teardown is defined because the next procedure setup is making an assumption on the state of the system under test.
        It is thus the responsibility of the procedure to bring back the system under test to the expected state.
        The teardown can be a reference to an existing test procedure.

.. graphviz::

    digraph finite_state_machine {
        compound=true;
        rankdir=LR;
        size="8,5"
        node [shape = rectangle];
        splines="ortho";
        subgraph cluster_driver { 
            label = "Test driver";
            Driver;
            Procedure [label="Procedure\n-setup()\n-teardown()", shape=folder];
            Driver -> Procedure [shape="vee"];
        }
        subgraph cluster_stub { 
            label = "Stub";
            bgcolor = "yellow";
            C2;
        }
        subgraph cluster_sut { 
            label = "System under test";
            bgcolor = "green";
            C1; C3;
        }
        Driver -> C1 [ label = "1.AC" ];
        C1 -> C2 [ label = "3.ARE" ];
        C1 -> C3 [ label = "2.RE" ];
        Driver -> C1 [ label = "4.AP" ];
        C1 -> C2 [ label = "5.DA" ];
        Driver -> C2 [label="controls", lhead="cluster_stub"];
        Driver -> C2 [label="checks", lhead="cluster_stub"];
        Driver -> C3 [label="setup", lhead="cluster_sut"];
        Driver -> C3 [label="teardown", lhead="cluster_sut"];
    }

The state of the system under test used as reference for setup and teardown is either a standard state of the system or depend on the procedure.

    standard state
        in case of a standard state being used in setup and teardown, each procedure is bringing the system to that state.

        As a consequence, the procedures can be run in any order as they all written using the same reference.
        However this strategy makes the test to require a lot of setup and teardown that can slow the tests.
    
        Furthermore, the system being always brought down to the same state, the system is always exercized in the same way.
        As a consequence, the flow of the tests might be different from the actual flow in the application when used by average users
        that usually will try to use the system following the path of less effort.

    variable state
        in case the referenced state in setup and teardown is tailored to the procedure, this will add constraints on the succession of procedures.
        This will exclude automatic collection of test procedures as the order cannot be guaranteed.

        Again the path from a procedure will be predefined and the test will not copy the actual flow in the application when used by users.


Another limitations of this strategy is that a lot of logic is defined in the procedure.
Consequently, if the test configuration is changed, some part of the logic must be changed which will require to create a new procedure.
Some part of the new procedure will be the same as the original one leading to duplication or overhead in maintenance costs.

For example if in the same application we are stubbing component C1, the setup and teardown to bring the new system under test at the right state will have to change.

.. graphviz::

    digraph finite_state_machine {
        compound=true;
        rankdir=LR;
        size="8,5"
        node [shape = rectangle];
        splines="ortho";
        subgraph cluster_driver_2 { 
            label = "Test driver";
            Driver_2 [label="Driver"];
            Procedure_2 [label="Procedure\n-setup2()\n-teardown2()", shape=folder];
            Driver_2 -> Procedure_2 [shape="vee"];
        }
        subgraph cluster_stub_2 { 
            label = "Stub";
            bgcolor = "yellow";
            C1b [label="C1"];
        }
        subgraph cluster_sut_2 { 
            label = "System under test";
            bgcolor = "green";
            C2b [label="C2"]; C3b [label="C3"];
        }
        C2b -> C1b [ label = "1.AC" ];
        Driver_2 -> C2b [ label = "3.ARE" ];
        Driver_2 -> C3b [ label = "2.RE" ];
        C2b -> C1b [ label = "4.AP" ];
        Driver_2 -> C2b [ label = "5.DA" ];
        Driver_2 -> C1b [label="controls", lhead="cluster_stub_2"];
        Driver_2 -> C1b [label="checks", lhead="cluster_stub_2"];
        Driver_2 -> C3b [label="setup2", lhead="cluster_sut_2"];
        Driver_2 -> C3b [label="teardown2", lhead="cluster_sut_2"];
    }

If the number of component increases this is leading to a level of complexity that is difficult to handle.
