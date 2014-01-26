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

    4. install omniORB (4.1.7)
        This might require to install python dev package.

    5. install Tango (8.1.2b)
        In case you hit the following error message

        ::

            /bin/bash ../../cppserver/database/create_db.sh < ../../cppserver/database/create_db.sql
            Warning: Using a password on the command line interface can be insecure.
            ERROR 1366 (HY000) at line 25: Incorrect integer value: 'nada' for column 'exported' at row 1
            make[3]: *** [all-local] Error 1
            make[3]: Leaving directory `/opt/tango-controls/tango-8.1.2/pytango/cppserver/database'
            make[2]: *** [all-recursive] Error 1
            make[2]: Leaving directory `/opt/tango-controls/tango-8.1.2/pytango/cppserver'
            make[1]: *** [all-recursive] Error 1
            make[1]: Leaving directory `/opt/tango-controls/tango-8.1.2/pytango'
            make: *** [all] Error 2

        You need to edit the file cppserver/database/create_db.sql, and do the following changes

        ::

            diff cppserver/database/create_db.sql.in cppserver/database/create_db.sql.in.new
            25,26c25,26
            < INSERT INTO device VALUES ('sys/database/2',NULL,'sys','database','2','nada','nada','nada','DataBaseds/2','nada','DataBase','nada','nada','nada','nada');
            < INSERT INTO device VALUES ('dserver/DataBaseds/2',NULL,'dserver','DataBaseds','2','nada','nada','nada','DataBaseds/2','nada','DServer','nada','nada','nada','nada');
            ---
            > INSERT INTO device VALUES ('sys/database/2',NULL,'sys','database','2',0,'nada','nada','DataBaseds/2',NULL,'DataBase','nada',NULL,NULL,'nada');
            > INSERT INTO device VALUES ('dserver/DataBaseds/2',NULL,'dserver','DataBaseds','2',0,'nada','nada','DataBaseds/2',NULL,'DServer','nada',NULL,NULL,'nada');
            32,33c32,33
            < INSERT INTO device VALUES ('sys/tg_test/1',NULL,'sys','tg_test','1','nada','nada','nada','TangoTest/test','nada','TangoTest','nada','nada','nada','nada');
            < INSERT INTO device VALUES ('dserver/TangoTest/test',NULL,'dserver','TangoTest','test','nada','nada','nada','TangoTest/test','nada','DServer','nada','nada','nada','nada');
            ---
            > INSERT INTO device VALUES ('sys/tg_test/1',NULL,'sys','tg_test','1',0,'nada','nada','TangoTest/test',NULL,'TangoTest','nada',NULL,NULL,'nada');
            > INSERT INTO device VALUES ('dserver/TangoTest/test',NULL,'dserver','TangoTest','test',0,'nada','nada','TangoTest/test',NULL,'DServer','nada',NULL,NULL,'nada');
            39,40c39,40
            < INSERT INTO device VALUES ('sys/access_control/1',NULL,'sys','access_control','1','nada','nada','nada','TangoAccessControl/1','nada','TangoAccessControl','nada','nada','nada','nada');
            < INSERT INTO device VALUES ('dserver/TangoAccessControl/1',NULL,'dserver','TangoAccessControl','1','nada','nada','nada','TangoAccessControl/1','nada','DServer','nada','nada','nada','nada');
            ---
            > INSERT INTO device VALUES ('sys/access_control/1',NULL,'sys','access_control','1',0,'nada','nada','TangoAccessControl/1',NULL,'TangoAccessControl','nada',NULL,NULL,'nada');
            > INSERT INTO device VALUES ('dserver/TangoAccessControl/1',NULL,'dserver','TangoAccessControl','1',0,'nada','nada','TangoAccessControl/1',NULL,'DServer','nada',NULL,NULL,'nada');



The following software need extra care.
Up to this point, the operation must be done using the checkmate virtual environment.

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

            using python : 3.3 : /YOUR_CHECKMATE_ENV/bin/python : YOUR_CHECKMATE_ENV/include/python3.3m : YOUR_CHECKMATE_ENV/lib ;



    7. install PyTango (8.1.1)
        Just follow the offical installation guidance.
            http://www.tango-controls.org/static/PyTango/latest/doc/html/start.html

        Use $python setup.py build; sudo python setup.py install to compile and install. 
        The problem met when building is -lboost_python-py33 did not exist.
        But if boost was installed successfully, there should be a a library like "libboost_python-py3.3.so".
        Make a symbolic link to it through "libboost_python-py33.so".
        After installation, an ImportError when trying to import PyTango and it showed something like "libboost_python3.so no such file or directory".
        Solve this problem by adding a line to the VIRTUALENV/bin/activate:

                export LD_LIBRARY_PATH=YOUR_CHECKMATE_ENV/lib:$LD_LIBRARY_PATH
    
Three steps to start tango on my computer before using checkmate pytango:

    1. Start the mysql database

            ssh root@localhost /etc/init.d/mysql.server restart

    2. Create tango dedicated database and populate

            (cd /opt/tango-controls/tango-8.1.2/pytango/cppserver/database; make)

    3. Start tango database device server

            DataBaseds 2 -ORBendPoint giop:tcp::10000&

   Need to set your mysql password if has:

        ::

            export MYSQL_USER=root

            export MYSQL_PASSWORD=mysql-root-password

            export MYSQL_HOST=localhost

            export TANGO_HOST=localhost:10000

    Or add mysql configure file .my.cnf at ~/(root at /root):

        ::

            [client]
                user=mysql_user_name
                password=mysql_user_password
