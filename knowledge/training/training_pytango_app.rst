The pytango checkmate application
==================================
Introduction to pytango
------------------------
The pytango third party is an official python binding for the tango framework.
While the binding is officially released for python2.x, it actually works well with python 3.
Most documentation for pytango is based on itango, the pytango support within ipython.
Unfortunately, at this hour, itango do not run under python 3 without slight changes.

The `tango framework`_ is an open-source framework for distributed control system development.
The development is commitee driven around a set of research institutes mainly in continental Europe.

The philosophy of tango  is to hide complexity behind standard interface definition (CORBA),
coding automation (pogo code generator) and strong design decisions.

The programming languages supported by tango project are C++, JAVA and python and the supported platforms are MS Windows and Ubuntu GNU/linux.

The `install pytango procedure`_ might be tricky and documented in the scope of checkmate project (usable on debian).


Rationale for pytango use
-------------------------
Given that tango is developed by various institutes active in particule physics,
the framework is focussing on high performance (use of zmq) and highly distributed architecture.

The strong design decisions is providing good guidelines for teams to develop devices that can easily integrate.
Consequently, selecting this framework for development of commercial products can make integration work easier.
For example all devices in tango are sharing the same set of basic states.

The design of tango is based on newer good practices than the older concurrent framework like ECLIPS.
It also provide official interface to state of the art languages like python.

Given that different particule physics research institutes are involved, a growing library of device for commercial equipments is available.


The pytango checkmate application
---------------------------------
The pytango application in checkmate is supporting fully implemented components.
These components are implementing the `sample_app state machine`_ and will be started as indepedent processes.
Consequently all tests written for sample_app can be recycled to be applied to pytango application.

A new type of communication has been developed to allow checkmate stubs to connect to pytango system under test for exchanges.

Beside installation of pytango, running the pytango application requires the tango backbone to be operational.

This can be done in a three step sequence.
    1. Start the mysql database

        ::

            ssh root@localhost /etc/init.d/mysql.server restart

    2. Create tango dedicated database and populate

        ::

            (cd /opt/tango-controls/tango-8.1.2/pytango/cppserver/database; make)

    3. Start tango database device server

        ::

            DataBaseds 2 -ORBendPoint giop:tcp::10000&



When tango is started, the sample_app test suite can be run with the pytango application.

For example::

    cd $CHECKMATE_HOME
    python checkmate/nose_plugin/plugin.py --with-checkmate --application=pytango.checkmate.application.Application --sut=C1 sample_app/

The --application directive is used to specify to the checkmate Runtime that pytango application should be used instead of the default.




.. _tango framework: http://tango-controls.org
.. _install pytango procedure: howto_install_pytango.html
.. _sample_app state machine: training_sample_app.html

