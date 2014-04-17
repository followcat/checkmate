Class-responsibility-collaboration
===================================
list
*****
checkmate.application.ApplicationMeta
+--------------------------------------------+
| ApplicationMeta                            |
+------------------------------+-------------+
| application meta data set up | Declarator  |  
| exchanges definition import  |             |  
+------------------------------+-------------+

checkmate.application.Application
+----------------------------------------------+
| Application                                  |
+---------------------------+------------------+
| component list definition | Component        |  
| component control         | ApplicationMeta  |  
| identify stub/sut         |                  |
| (load itp transitons)     | (dtvisitor)      |
+---------------------------+------------------+

checkmate.component.ComponentMeta
+----------------------------------------------+
| ComponentMeta                                |
+---------------------------------+------------+
| component meta data set up      | Declarator |  
| state-machine definition import |            |  
+---------------------------------+------------+

checkmate.component.Component
+---------------------------------------+
| Component                             |
+-----------------------+---------------+
| state-machine execute | ComponentMeta |  
| state maintain        | StateMachine  |  
+-----------------------+---------------+

checkmate.partition_declarator.Declarator
+------------------------------------------------------+
| Declarator                                           |
+---------------------------------+--------------------+
| partitions create from visitor  | DocTreeVisitor     |
| transitions create from visitor | PartitionStorage   |
|                                 | Data               |
|                                 | TransitionStorage  |
|                                 | Transition         |
+---------------------------------+--------------------+

checkmate.data_structure.DataStructure
+------------------------------------------+
| DataStructure                            |
+--------------------------+---------------+
| DataStructure Definition | Partition     |
+--------------------------+---------------+

checkmate.state.State
+----------------------------------+
| State                            |
+------------------+---------------+
| State Definition | Partition     |
+------------------+---------------+

checkmate.exchange.Exchange
+-------------------------------------+
| Exchange                            |
+---------------------+---------------+
| exchange Definition | Partition     |
+---------------------+---------------+

checkmate.logger.Logger
+-------------------------------------------+
| Logger                                    |
+---------------------------+---------------+
| global logger definition  |               |
| determine what/how to log |               |
+---------------------------+---------------+

checkmate.partition.Partition
+--------------------------------------------+
| Partition                                  |
+------------------------+-------------------+
| base class of State/   | IArgumentStorage  |
| DataStructure/Exchange |                   |
+------------------------+-------------------+

checkmate.sandbox.Sandbox
+--------------------------------------------+
| Sandbox                                    |
+------------------------------------+-------+
| simulate an application            |  Tree |
| process transition list            |       |
| fill procedure with process result |       |
+------------------------------------+-------+

checkmate.service_registry.ServiceFactory
+---------------------------------------------+
| ServiceFactory                              |
+-------------------------+-------------------+
| republish exchange with | IArgumentStorage  |
| destination             |                   |
+-------------------------+-------------------+

checkmate.service_registry.ServiceRegistry
+-------------------------------------------------------+
| ServiceRegistry                                       |
+-----------------------------------+-------------------+
| register exchange and component   | ServiceFactory    | 
| for exchange's destination query  |                   | 
+-----------------------------------+-------------------+

checkmate._storage.PartitionStorage
+------------------------------------------+
| PartitionStorage                         |
+---------------------------------+--------+
| get partition storage from Data |  Data  |
+---------------------------------+--------+

checkmate._storage.Data
+-----------------------------------------------------------+
| Data                                                      |
+---------------------------------------+-------------------+
| prepare data to be store              |  InternalStorage  |
| provide interface to store partition  |                   |
+---------------------------------------+-------------------+

checkmate._storage.InternalStorage
+---------------------------------------------------------+
| InternalStorage                                         |    
+-------------------------------------+-------------------+
| define storage of partition         |                   | 
| wrap internal detail until resolved |                   | 
+-------------------------------------+-------------------+

checkmate._storage.TransitionStorage
+---------------------------------------------------------------+
| PartitionStorage                                              |
+--------------------------------------------+------------------+
| get partitions storage from TransitionData |  TransitionData  |
| add resolve logic for each partition       |                  |
+--------------------------------------------+------------------+

checkmate._storage.TransitionData
+-----------------------------------------------------+
| TransitionData                                      |
+-------------------------------------+---------------+
| create OrderedDict to store Data    |  OrderedDict  |
|                                     |  Data         |
+-------------------------------------+---------------+

checkmate.transition.Transition
+---------------------------------------------------------------+
| Transition                                |                   |
+-------------------------------------------+-------------------+
| rule for exchange in/out and state change |                   |
| state/exchange validation and resolvation |                   |
+-------------------------------------------+-------------------+

checkmate._tree.Tree
+-----------------------------------------------+
| Tree                                          |
+-------------------------------+---------------+
| tree structure to store data  |               |
+-------------------------------+---------------+

checkmate._util.ArgumentStorage
+-----------------------------------------------------+
| ArgumentStorage                                     |
+--------------------------------------------+--------+
| tuple extends to store partition arguments |  tuple |     
+--------------------------------------------+--------+

checkmate.parser.dtvisitor.Writer
+---------------------------------------------------------------------+
| Writer                                                              |
+------------------------------------------+--------------------------+
| inherit from docutils.writers.Writer     |  docutils.writers.Writer |
| call translator to visit input document  |  DocTreeVisitor          |
+------------------------------------------+--------------------------+

checkmate.parser.dtvisitor.DocTreeVisitor
+-------------------------------------------------------------------------------------------+
| DocTreeVisitor                                                                            |
+-------------------------------------------------------+-----------------------------------+
| inherit from docutils.nodes.GenericNodeVisitor        | docutils.nodes.GenericNodeVisitor |
| extract data by visiting defferent part of a document |                                   |
+-------------------------------------------------------+-----------------------------------+

checkemate.runtime.component.Component
+-------------------------------------------------------------------------------------------+
| Component                                                                                 |
+-------------------------------------------------------+-----------------------------------+
| base class define of runtime component                |                                   |
| own component as context to maintain state-machine    |                                   |
| create clients to implement communication             |                                   |
| process/simulate exchange and deliver the output      |                                   |
+-------------------------------------------------------+-----------------------------------+

checkemate.runtime.component.Sut
+-------------------------------------------------------------------------------------------+
| Sut                                                                                       |
+--------------------------------------------------+----------------------------------------+
| implment checkmate.component.Component utilities | checkemate.runtime.component.Component |
| deliver process output via internal client       | checkemate.runtime.component.Component |
+--------------------------------------------------+----------------------------------------+

checkemate.runtime.component.Stub
+----------------------------------------------------------------------------------------------------+
| Stub                                                                                               | 
+-----------------------------------------------------------+----------------------------------------+
| deliver output via both internal/external client          | checkemate.runtime.component.Component |
| validate whether its internal client received exchange    |                                        |
+-----------------------------------------------------------+----------------------------------------+

checkemate.runtime.component.ThreadedComponent
+----------------------------------------------------------------------------------------+
| ThreadedComponent                                                                      |
+-----------------------------------------------+----------------------------------------+
| create different type of threadedclients      | checkmate.runtime._threading.Thread    |
| checkmate.runtime._pyzmq.connector            | checkemate.runtime.component.component |
| keep trying to recieve exchange from client   | checkmate.runtime._pyzmq.Connector     |
| process exchange once recieved                | ThreadedClient                         |
| deliver output exchanges via clients          | zmq.Context                            |
|                                               | zmq.Poller                             |
+-----------------------------------------------+----------------------------------------+

checkemate.runtime.component.ThreadedSut
+---------------------------------------------------------------------------+
| ThreadedSut                                                               |
+---------------------------------------+-----------------------------------+
| implement Sut utilities               | ThreadedComponent                 |
| implement ThreadedComponent utilities | checkemate.runtime.component.Sut  |
+---------------------------------------+-----------------------------------+

checkemate.runtime.component.ThreadedStub
+----------------------------------------------------------------------------+
| ThreadedStub                                                               |                       
+---------------------------------------+------------------------------------+
| implement Stub utilities              | ThreadedComponent                  |
| implement ThreadedComponent utilities | checkemate.runtime.component.Stub  |
|                                       | SleepAfterCall                     |
|                                       | WaitOnFalse                        |
|                                       | Lock                               |
+---------------------------------------+------------------------------------+

checkemate.runtime.client.Client
+--------------------------------------+
| Client                               | 
+-----------------------+--------------+
| base class definition |              |
+-----------------------+--------------+

checkemate.runtime.client.ThreadedClient
+-----------------------------------------------------------------------------------------+
| ThreadedClient                                                                          |
+---------------------------------------------------+-------------------------------------+
| communicate with other components with connection | checkmate.runtime._threading.Thread |
| commnnicate with owner component with pyzmq       | zmq.Context                         |
| recieve exchange from other component's client    |                                     |
| foward exchange to owner component once recieved  |                                     |
+---------------------------------------------------+-------------------------------------+

checkemate.runtime.communication.Connector
+--------------------------------------+
| Connector                            |
+-----------------------+--------------+
| base class definition |              |
+-----------------------+--------------+

checkemate.runtime.communication.Communication
+--------------------------------------+
| Communication                        |  
+-----------------------+--------------+
| base class definition |              |
+-----------------------+--------------+

checkemate.runtime._pyzmq.Communication
+----------------------------------------------------------------------+
| Communication                                                        |
+--------------------------------+-------------------------------------+
| define a communication type    | checkmate.runtime._threading.Thread |
| to be used by connectionstry   | zmq.Context                         |
+--------------------------------+-------------------------------------+

checkemate.runtime._pyzmq.Registry
+---------------------------------------------------------------------+
| Registry                                                            |
+-------------------------------+-------------------------------------+
| listen to port request        | checkmate.runtime._threading.Thread |
| pick up random free port      | zmq.Context                         | 
| reply with free port by zmq   | zmq.Poller                          |
|                               | socket.socket                       |
+-------------------------------+-------------------------------------+

checkemate.runtime._pyzmq.Connector
+-------------------------------------------------------------------------------------+
| Connector                                                                           |                  
+-----------------------------------------+-------------------------------------------+
| implement communication type to set up  | checkmate.runtime.communication.Connector |
| connection for message send/recieve     | checkemate.runtime._pyzmq.Communication   |
|                                         | checkemate.runtime._pyzmq.Encoder         |
|                                         | zmq.Poller                                |
|                                         | zmq.Context                               |
+-----------------------------------------+-------------------------------------------+

checkemate.runtime._pyzmq.Encoder
+-----------------------------------------------+
| Encoder                                       |
+-------------------------------------+---------+
| use pickle to de/serialize message  | pickle  |
+-------------------------------------+---------+

checkemate.runtime._runtime.Runtime
+-------------------------------------------------------------------------------------+
| Runtime                                                                             |
+-----------------------------------------------+-------------------------------------+
| define the runtime enviroment                 |                                     |
| to run checkmate test                         |                                     |
| adapt different application and communication |                                     |
+-----------------------------------------------+-------------------------------------+

