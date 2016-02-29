Procedure for Taurus installation
==================================

Some of the following softwares can be installed from source code and there would be installation guidance in the directory.
These steps may still be done outside the checkmate virtualenv using the ***python version 2.7***

    0. if you don't have python 2.7 installed, you can try with python 2.6, but still 2.7 is recommanded. 
       Make a virtualenv for python 2.7, the following softwares will be installed inside this virtualenv.


    1. install Sip
        wget http://tcpdiag.dl.sourceforge.net/project/pyqt/sip/sip-4.15.5/sip-4.15.5.tar.gz
        unzip
        python configure.py
        make
        sudo make install


    2. install qmake and qt4
        sudo apt-get install libqt4-dev libqt4-dbg libqt4-gui libqt4-sql qt4-dev-tools qt4-doc qt4-designer qt4-qtconfig


    3. install PyQt
        wget http://jaist.dl.sourceforge.net/project/pyqt/PyQt4/PyQt-4.10.4/PyQt-x11-gpl-4.10.4.tar.gz
        unzip
        python configure-ng.py
        make
        make install
		
		You might see a message like make: [install_pyuic4] Error 1 (ignored). This is not an error, but rather a warning that can be safely ignored (as explained in this page: this happens when attempting to strip a file that is not a binary but a script, as is the case of pyuic4).

    4. install taurus
        wget https://pypi.python.org/packages/source/t/taurus/taurus-3.2.0.tar.gz
        unzip
        python setup.py build
        python setup.py install



The following softwares are also need to be installed in python 2.7 virtual environment in order to run our new pytango component_2 combining with taurus.

    5. boost_python, should install the same version as in python 3.3.
       If boost was installed successfully, there should be a library like "libboost_python.so" in the InstallDir/lib.
       Make a symbolic link to it through "libboost_python-py27.so".


    6. numpy
        pip install numpy==1.7.0.


    7. PyTango, should install the same version as in python 3.3.

pos-install: After this virtualenv created, new environment variables PY2_VIRTUAL_ENV and BOOST_ROOT_PY2 should be set to the shell that execute our checkmate test.
    
