Environment setup
=================
General rules
-------------
checkmate third party dependencies are controlled using a KGS (know good set [of dependencies]).
It is mandatory to use one of the KGS for dependency selection. Update of one a dependency from the KGS version must be approved beforehand.
The process of installing a new version of a dependency will be followed by the release of a new KGS.

The support of different environments will be done using virtualenv.  Note that the venv module in python 3 is not used for multiple environment support.
All virtual environments are stored under $HOME.


KGS-01
------
General dependencies

::

    dot==2.34.0


Python related dependencies

::

    python==3.3.2
    docutils==0.10
    nose==1.3.0
    pyzmq==13.1.0
    virtualenv==1.10.1
    zope.component==4.1.0
    zope.interface==4.0.5
    sphinx==1.2
    PyYAML==3.10
    pyparsing==2.0.1
    fresher==0.4.0

