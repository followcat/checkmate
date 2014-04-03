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
+------------------------------------------+
| Logger                                   |
+--------------------------+---------------+
| global logger definition | Partition     |
+--------------------------+---------------+

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

