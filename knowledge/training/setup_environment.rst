Environment setup
=================
General rules
-------------
The checkmate third party dependencies are controlled using a KGS ('known good set' [of dependencies]).
It is mandatory to use one of the KGS for dependency selection. Update of any dependency from the KGS version must be approved beforehand.
The process of installing a new version of a dependency will be followed by the release of a new KGS.

The support of different environments will be done using virtualenv.  Note that the venv module in python 3 is not used for multiple environment support.
All virtual environments are stored under $HOME.


KGS-03
------
General dependencies

::
    python==3.4.1
    zmq==4.0.4


Python related dependencies

::
    PyYAML==3.11
    fresher==0.4.0
    ipython==2.1.0
    nose==1.3.3
    pyparsing==2.0.2
    pyzmq==14.3.1
    six==1.7.3
    zope.component==4.2.1
    zope.interface==4.1.1

    #this is ipython notebook related dependencies
    Jinja2==2.7.3
    Pygments==1.6
    matplotlib==1.3.1
    numpy==1.8.2
    pandas==0.14.1
    pytz==2014.4
    tornado==4.0



KGS-01
------
General dependencies

::

    dot==2.34.0
    python==3.3.2
    zmq==3.2.4


Python related dependencies

::

    PyYAML==3.10
    docutils==0.10
    fresher==0.4.0
    nose==1.3.0
    pyparsing==2.0.1
    pyzmq==13.1.0
    six==1.5.2
    sphinx==1.2
    virtualenv==1.10.1
    zope.component==4.1.0
    zope.interface==4.0.5

