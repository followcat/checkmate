Information exchange
====================
Communication
-------------
We have seen that checkmate.runtime Component are adapting the components listed by the application to add an interface to send and receive exchanges.

The send/receive of exchanges is done based on the Communication defined in the application.

The communication is defined once. Each component can use one or several communication to transfer exchanges.
The communication is initializing common resources inside the communication registry.
For example, the registry can manage a table to do the matching between the components and the sockets.

The communication is thus defining a protocol for connection between components.


The pyzmq communication
-----------------------
The sockets used in checkmate.runtime for sending internally the exchanges are based on the ZMQ socket framework.

The ZMQ framework comes with python binding called pyzmq.


Connector
---------
The checkmate.runtime component are not using the communication as such but are using a connector for the communication.
When the communication requires to open a socket, the connector will be responsible for the direct management of the socket.

In the case where different components need different data to open connection, they will be using different connectors for the same communication.

A connector can be open is two modes:
    server
        the server mode of the connector will be used by the component to receive requests for the services it is providing
    non-server
        this mode is used by the components to send request of service from the server


Client
------
The component is not managing the connector directly but delegate this task to Client instances.
In a threaded runtime, each client is a dedicated thread.

The client will read the exchange on the connector and forward them to the component for processing.
The client is also used by the component to send outgoing exchanges.

Two types of client are possible.
The external clients are open by the component for interactions with the system under test.

The internal clients are open for interactions with the sut.
The exchanges sent through internal clients are duplicated from exchanges sent through external clients.

