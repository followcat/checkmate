Introduction to checkmate testing
=================================
Design decisions
----------------
The first decision for the testing strategy with checkmate is to load the component state machine into the stub.
This way, the control flow from the test driver to the stubs can be spared.
The stub will then understand what it has to do based on its state and the incoming exchanges coming from the system under test.

As the test driver has access to every component state machines, it will be able to compute on the fly the direct path
from the current state of the system and the initial state of the procedure.
Consequently the procedure setup and teardown is not required and can be discarded.

In order to have access to every component states, the system under test is duplicated with another test tool, called Sut.
The Sut will host a copy of the components in the system under test.
These copies will not have any interaction with the SUT but will be forwarded the exchanges to have their state updated.
These copies will provide an interface for the test driver to get their current state.

Consequently, the test driver have access to all component states through the stubs or sut.
It gives that there is no direct interaction between the test driver and the system under test.

Here is a diagram showing the deployment of a checkmate test environment for testing C1 and C3 together:

.. graphviz::

    digraph finite_state_machine {
        newrank=true;
        compound=true;
        node [shape = rectangle];
        edge [decorate = true];
        splines=ortho;
        labeldistance=0;
        subgraph cluster_driver { 
            label = "Test driver";
            Driver [label="Driver\nSUT=C1,C3"];
            Procedure [label="Procedure", shape=folder];
            Driver -> Procedure [shape="vee"];
        }
        subgraph cluster_stub { 
            label = "Stub";
            bgcolor = "yellow";
            subgraph cluster_C2 {
                label = "";
                C2 [shape=none];
                node [label="", shape=circle];
                S0 -> S1;
                S0 -> S2;
                S1 -> S2 [constraint=false];
                {rank=same; C2; S0}
            }
        }
        subgraph cluster_stub_sut { 
            label = "Sut";
            bgcolor = "yellow";
            subgraph cluster_sut_C1 {
                label = "";
                sut_C1 [label="C1", shape=none];
                node [label="", shape=circle];
                C1_S0 -> C1_S1;
                C1_S0 -> C1_S2;
                C1_S1 -> C1_S2 [constraint=false];
            }
            subgraph cluster_sut_C3 {
                label = "";
                sut_C3 [label="C3", shape=none];
                node [label="", shape=circle];
                C3_S0 -> C3_S1;
                C3_S0 -> C3_S2;
                C3_S1 -> C3_S2 [constraint=false];
            }
        }
        {rank=same; Procedure; sut_C3; C3_S0; sut_C1; C1_S0}
        {rank=same; Driver; C2;}
        subgraph cluster_sut { 
            label = "System under test";
            bgcolor = "green";
            C1 [width=2];
            C3 [width=2];
        }
        C2 -> C1 [ headlabel = "1.AC",ltail="cluster_C2" ];
        C2 -> sut_C1 [ headlabel = "1.AC", lhead="cluster_sut_C1", ltail="cluster_C2"];
        C1 -> C2 [ headlabel = "3.ARE", lhead="cluster_C2"];
        C1 -> C3 [ headlabel = "2.RE" ];
        sut_C1 -> sut_C3 [ headlabel = "2.RE", lhead="cluster_sut_C3", ltail="cluster_sut_C1"];
        C2 -> C1 [ headlabel = "4.AP",ltail="cluster_C2" ];
        C2 -> sut_C1 [ headlabel = "4.AP", lhead="cluster_sut_C1", ltail="cluster_C2"];
        C1 -> C2 [ headlabel = "5.DA", lhead="cluster_C2" ];
        Driver -> C2 [label="simulate", lhead="cluster_stub"];
        Driver -> C2 [label="validate", lhead="cluster_stub"];
        Driver -> C2 [label="get state", lhead="cluster_stub"];
        Driver -> sut_C3 [taillabel="simulate", lhead="cluster_stub_sut"];
        Driver -> sut_C3 [taillabel="get state", lhead="cluster_stub_sut"];
    }

Provided that the design of checkmate leaves the procedure with no need to specify any setup/teardown logic that would have depend on the test setting,
the procedure is valid for any setting.
As a consequence, checkmate is able to use and re-use the same procedure for different settings, leading to no duplication and reduced maintenance costs.

When running checkmate test, the test driver is given the definition of the system under test (SUT) and will setup stub and sut accordingly.

As the test driver has access to the application state machines, it can adapt to any current state and find a path to reach the procedure initial state.
This way the procedures can be run in any random order. The randomness can come either from automatic procedure collection
or intented random runs to simulate different race conditions.


checkmate vs checkmate.runtime
------------------------------
As introduced before, checkmate components are able to process state transitions but they can only return the outgoing exchanges.
In that sense, checkmate is still a static framework.

Still testing require to be able to send away exchange from one component to the others. This responsibility is given to checkmate.runtime.
The dynamic checkmate runtime is loading up the static checkmate and provide additional functionalities to send the exchanges across the application.

