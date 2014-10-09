Sample application
==================
checkmate is coming with a sample application. It is used for both testing and documentation.
The sample application (often referenced as 'sample_app') is composed of four components C1, C2, C3 and USER.
Each of them is powered by a state machine defined in checkmate using reStructuredText format.

Given the limited number of component in sample_app, it is possible to consolidate the state machines by matching one component outgoing with other components' incoming.
The consolidated flows of exchange in the sample application are represented in the following diagram (one flow per column):

::

    Run 1                                 Run 2                             Run 3                             Run 4                         
    -----                                 -----                             -----                             -----                        
                 C1: True, Q()                     C1:                               C1: False, Q(R)                   C1: False 
                 C2:                               C2:                               C2:                               C2:               
                 C3: False                         C3: True                          C3: False                         C3: 

             +------+                          +------+                          +------+                          +------+ 
             | USER |                          | USER |                          | USER |                          | USER |   
             +------+                          +------+                          +------+                          +------+    
                |                                 |                                 |                                 |           
                | PBAC                            | PBRL                            | PBPP                            | PBAC  
                |                                 |                                 |                                 |          
             +------+                          +------+                          +------+                          +------+  
             |  C2  |                          |  C2  |                          |  C2  |                          |  C2  | 
             +------+                          +------+                          +------+                          +------+                  
                |                                 |                                 |                                 |                     
                | AC                              | RL                              | PP                              | AC  
                |                                 |                                 |                                 |   
             +------+                          +------+                          +------+                          +------+ 
             |  C1  | < C1 is True             |  C3  | < C3 is True             |  C1  | < C1 is False            |  C1  | < C1 is False
             +------+ > False, Q()             +------+ > toggle()               +------+   C1 is Q                +------+ 
                |                                 |                                 |     > toggle(), Q.pop()         |    
        +---------------+                         | DR                     +----------------+                         | ER
        |               |                         |                        |                |                         |     
        | RE            | ARE                  +------+                    | PA             | PA                   +------+                  
        |               |                      |  C2  |                    |                |                      |  C2  |                 
    +------+         +------+                  +------+                 +------+         +------+                  +------+                
    |  C3  | < C3 is |  C2  |                     |                     |  C3  | < C3 is |  C2  |                     |                   
    +------+   False +------+                     | VODR                +------+   False +------+                     | VOER             
             > toggle() |                         |                              > False    |                         |
                        | AP                   +------+                                     | VOPA                 +------+    
                        |                      | USER |                                     |                      | USER |      
                     +------+                  +------+                                  +------+                  +------+      
                     |  C1  | < C1 is Q                                                  | USER |
                     +------+ > Q.append()         C1:                                   +------+                      C1: False     
                        |                          C2:                                                                 C2:
                        | DA                       C3: False                                 C1: True, Q()             C3:
                        |                                                                    C2:
                     +------+                                                                C3: False
                     |  C2  |                            
                     +------+                            
                        |                 
                        | VODA
                        |                 
                     +------+                                         
                     | USER |                            
                     +------+                            

                         C1: False, Q(R)
                         C2:
                         C3: True



It is usually impossible to consolidate this kind of flow when number of component in an application increases.
In the context of checkmate, a flow of exchange is called a 'run'.

The initial state for the flow to happen is listed in the first three lines. The boxes represent one exchange. The arrow on top of a box is labelled with the component that send the exchange and the arrow below the box is the component receiving the exchange (the right part showing the final state after the transition is completed.

On the right of the box, is the check done on the receiving component to perform the transition.

Given that sample_app is a simple application, the final state of the system at the end of the last run is matching the initial state of the first run.
The three runs can thus be performed in a loop.


The possible runs for sample_app appplication are based on different exchanges. As explained, the exchange definition is done at application level.
For the record, here is the definition of several exchanges within sample_app application:

::

    Definition and accessibility
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Action(R=ActionRequest)

    Value partitions
    ^^^^^^^^^^^^^^^^^

    +----------------+-----------------+----------------------+-------------------+
    | Partition      | Service         | Valid value          | Comment           |
    +================+=================+======================+===================+
    | X-ACTION-01    | AC()            | Action action        | Comment AC action |
    +----------------+-----------------+----------------------+-------------------+
    | X-ACTION-02    | AP(R)           | Append action        | Comment AP action |
    +----------------+-----------------+----------------------+-------------------+
    | X-ACTION-03    | PP(R)           | Pop action           | Comment PP action |
    +----------------+-----------------+----------------------+-------------------+


As the definition of the exchanges in sample_app is done in reStructuredText, the python code in sample_app does not include any definition.

If we check the content of sample/exchanges.py module, we see no trace of sample_app Action exchange type.
    >>> import sample_app.exchanges
    >>> 'Action' in dir(sample_app.exchanges)
    False

The sample/exchanges.py module doesn't contain any definition matching the RST table.
    >>> dir(sample_app.exchanges)
    ['__builtins__', '__cached__', '__doc__', '__file__', '__initializing__', '__loader__', '__name__', '__package__', 'checkmate', 'declare', 'declare_interface', 'zope']

However, as soon as we import the sample_app/application.py module, things are different
    >>> import sample_app.application
    >>> 'Action' in dir(sample_app.exchanges)
    True
    >>> dir(sample_app.exchanges)
    ['AC', 'AL', 'AP', 'ARE', 'Action', 'AnotherReaction', 'DA', 'IAction', 'IAnotherReaction', 'IPause', 'IReaction', 'IThirdAction', 'PA', 'PP', 'Pause', 'RE', 'RL', 'Reaction', 'ThirdAction', '__builtins__', '__cached__', '__doc__', '__file__', '__initializing__', '__loader__', '__name__', '__package__', 'checkmate', 'declare', 'declare_interface', 'zope']
    >>> type(sample_app.exchanges.Action)
    <class 'type'>


This is due to the particular definition of sample_app TestData class:
    >>> import checkmate.application
    >>> class TestData(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    ...     """"""
    ...     __test__ = False
    ...     data_structure_module = sample_app.data_structure
    ...     exchange_module = sample_app.exchanges
    ... 

This class is based on both the checkmate.application.Application ancestor and the checkmate.application.ApplicationMeta metaclass.

Here is a snipset of the application metaclass that allows populating the sample/exchanges.py when defining the TestData class:
    >>> class ApplicationMeta(type):
    ...     def __new__(cls, name, bases, namespace, **kwds):
    ...         data_structure_module = namespace['data_structure_module']
    ...         exchange_module = namespace['exchange_module']
    ...         path = os.path.dirname(exchange_module.__file__)
    ...         filename = 'exchanges.rst'
    ...         _file = open(os.sep.join([path, filename]), 'r')
    ...         matrix = _file.read()
    ...         _file.close()
    ...         try:
    ...             global checkmate
    ...             declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module=exchange_module, content=matrix)
    ... 

Without going too deep in this code, we see that the 'exchange.rst' file is open and used by checkmate.partition_declarator.Declarator that has access to TestData.exchange_module.

The Declarator will parse the RST and will dynamically add the definition of the exchanges found in the RST tables. He will also add the definition of an interface for each of the exchange class:
    >>> type(sample_app.exchanges.IAction)
    <class 'zope.interface.interface.InterfaceClass'>
    >>> sample_app.exchanges.IAction.implementedBy(sample_app.exchanges.Action)
    True

One thing to mind when dealing with dynamic created exchange class is that two different applications that use the same exchanges.py module will override the previous class definition.
    >>> import sample_app.exchanges
    >>> import sample_app.data_structure
    >>> class TestData(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    ...     """"""
    ...     data_structure_module = sample_app.data_structure
    ...     exchange_module = sample_app.exchanges
    ...     __module__='checkmate.sample_app.application'
    ... 

    >>> a1 = sample_app.exchanges.Action()
    >>> class AnotherTestData(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    ...     """"""
    ...     data_structure_module = sample_app.data_structure
    ...     exchange_module = sample_app.exchanges
    ...     __module__='checkmate.sample_app.application'
    ... 

    >>> a2 = sample_app.exchanges.Action()

Instances of old exchange class will not inherit from the new exchange class:
    >>> type(a1)
    <class 'sample_app.exchanges.Action'>
    >>> type(a2)
    <class 'sample_app.exchanges.Action'>
    >>> type(a1) == type(a2)
    False

