Procedure for pytango installation
==================================

The following software can be installed from source code and there would be installation guidance in the directory.
These steps may still be done outside the checkmate virtualenv using the default python version.
Some library should be add to LIBRARY_PATH
Some source file should be add to CPLUS_INCLUDE_PATH if you don't instll in checkmate virtualenv.


    1. install Cmake (2.8.10.2)
        This is required for mysql installation.
        This sould be done from source code.

    2. install MySQL (5.6.14)

        ::

            As normal user
            --------------
            export PATH=/usr/local/mysql/bin:$PATH
            cmake .
            make

            As root
            -------
            groupadd mysql
            useradd -g mysql mysql
            make install
            cd /usr/local/mysql
            chown -R mysql:mysql .
            ./scripts/mysql_install_db --user=mysql
            chown -R root .
            chown -R mysql data
            /etc/init.d/mysql.server start
            ./bin/mysqladmin -u root password 'asafepassword'
            /usr/local/mysql/bin/mysqld_safe --user=mysql &

            cp support-files/mysql.server /etc/init.d/mysql.server
            /etc/init.d/mysql.server stop

            chown -R root .
            chown -R mysql data

            /etc/init.d/mysql.server start

            As normal user
            --------------
            mysql -u mysql



    3. install zmq (3.2.4)
        It is best to install zeromq in the virtual environment in case different versions need to be supported.

            ./configure --prefix=$VIRTUAL_ENV

        In order to fully support the installation of zeromq in virtual environment, it is required to set the following variables:

            export INCLUDE_PATH=$VIRTUAL_ENV/include:$INCLUDE_PATH
            export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
            export PKG_CONFIG_PATH=$VIRTUAL_ENV/lib/pkgconfig:$PKG_CONFIG_PATH


    4. install omniORB (4.1.7)
        This might require to install python dev package.



The following software need extra care.
Up to this point, the operation must be done using the checkmate virtual environment.

    5. install Tango (8.1.2b)

        YOU MUST DO THIS BEFORE INSTALLING TANGO !This `page <https://www.tango-controls.org/howtos/binary_deb>`_ show Why and How to.

            Disable IPv6

            Set system /etc/hosts file

        The default tango database device server is connecting to a DB whose name is set at configuration time (--with-tango-db-name=...)
        However in order to be able to run different instances of checkmate runtime at the same time, we need to have a database server that
        links dynamically to the database set in TANGO_DB_NAME variable environment.

        This is done by applying a set of change in the source file of tango to support dynamic setting of DB name (see patch_ file).

        The TANGO_DB_NAME must be set when configuring the tango compilation chain.

        Given that checkmate use a patched version of tango, it is advised to install it in the virtual environment.
        This is done by using the command:

            ./configure --prefix=$VIRTUAL_ENV --with-mysql-admin=$MYSQL_USER --with-zmq=$VIRTUAL_ENV

    6. install boost (1.54.0)
        The installation step should have been as follows (read the offical doc first): 
            1) ./bootstrap.sh
            2) ./b2
            3) ./b2 install

        Enter the boost source code main directory and edit bootstrap.sh:

        ::

            - PYTHON_ROOT=`$PYTHON -c "import sys; print sys.prefix"`
            + PYTHON_ROOT=`$PYTHON -c "import sys; print(sys.prefix)"`

        Otherwise syntax error would occur when building with python3.

        Do specify the --with-python and --prefix option when using ./bootstrap to configure. 
        Assign virtualenv directory to the "--prefix=..."
        Specifically, use "--with-python=python3.3".

        Config file is:
            WHERE_YOUR_BOOST_FILE/tools/build/v2/user-config.jam

        If you go to the bottom line, you should see a line like this to specify using python3.3

            using python : 3.3 : $VIRTUAL_ENV/bin/python : $VIRTUAL_ENV/include/python3.3m : $VIRTUAL_ENV/lib ;



    7. install PyTango (8.1.1)
        Just follow the offical installation guidance.
            http://www.tango-controls.org/static/PyTango/latest/doc/html/start.html

        Use 'python setup.py build; python setup.py install' to compile and install. 
        The problem met when building is -lboost_python-py33 did not exist.
        But if boost was installed successfully, there should be a a library like "libboost_python3.so".
        Make a symbolic link to it through "libboost_python-py33.so".
        After installation, an ImportError when trying to import PyTango and it showed something like "libboost_python3.so no such file or directory".
        Solve this problem by adding a line to the $VIRTUALENV/bin/activate:

                export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH


    8. install JtangoServer (1.11.1)

        This is done by copying the downloaded jar (from http://www2.synchrotron-soleil.fr/controle/maven2/soleil/org/tango/JTangoServer/) file in a directory in classpath:

                cp /Download/JTangoServer-1.1.1-all.jar $VIRTUAL_ENV/share/java
                (cd $VIRTUAL_ENV/share/java; ln -s JTangoServer-1.1.1-all.jar JTangoServer.jar)
                export TANGO_CLASSPATH=$VIRTUAL_ENV/share/java/JTangoServer.jar:$CHECKMATE_HOME
                export CHECKMATE_CLASSPATH=$TANGO_CLASSPATH
                export CLASSPATH=$TANGO_CLASSPATH

    
Three steps to start tango on my computer before using checkmate pytango:

    1. Start the mysql database

            ssh root@localhost /etc/init.d/mysql.server restart

    2. Create tango dedicated database and populate

            (export TANGO_DB_NAME=checkmate; cd /opt/tango-controls/tango-8.1.2/pytango/cppserver/database; make)

    3. Start tango database device server

            (export TANGO_DB_NAME=checkmate; DataBaseds 2 -ORBendPoint giop:tcp::10000&)

   Need to set your mysql password if has:

        ::

            export MYSQL_USER=root

            export MYSQL_PASSWORD=mysql-root-password

            export MYSQL_HOST=localhost

            export TANGO_DB_NAME=checkmate

            export TANGO_HOST=localhost:10000

    Or add mysql configure file .my.cnf at ~/(root at /root):

        ::

            [client]
                user=mysql_user_name
                password=mysql_user_password


.. _patch: ./_static/patch-tango-8.1.2.diff
   
