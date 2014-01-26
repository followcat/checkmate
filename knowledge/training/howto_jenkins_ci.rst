Setup continuous integration (CI)
=================================
Introduction to CI
------------------
Continuous integration is tool to implement the strategy of early testing.
Early testing stratey is based on the fact that the learlier a problem is found, the cheaper it is to fix.

Continuous integration is an test tool that allow the user to delegate regression tests.
The regression tests should be run often so that the time between the problem appear and when the prolbme is identified is as short as possible.
Regression tests are based on running the existing test suite on all system configurations.

The continuous integration requires the tests to be fully automatic (setup, run, diagnostic, ...).
This is supported by the use of nosetests tool in checkmate project.

The selected continuous integration tool for checkmate project is open source jenkins CI.
Jenkins CI is developed in Java. Documentation can be found in http://jenkins-ci.org


Jenkins installation
--------------------
The continuous integration is run on the user account.
Consequently, we do not use the default configuration where a jenkins user is created.

The installation of jenkins CI is thus reduced to download of the jenkins.war from the official website.

Later in this document, the war file is supposed to be stored in the $JENKINS_WAR_DIR directory.


Virtual environment
-------------------
The CHECKMATE_HOME is expected to be set in the user profile (~/bashrc). This is where the checkmate source sits.

The python 3 and checkmate dependencies must be installed using the virtualenv tool. 

We assume that a script is written to add have the $CHECKMATE_HOME path to be added into PYTHONPATH environment variable.
This script should source the virtualenv's activate script.


Jenkins configuration
---------------------
The different scripts to run for regresion tests are stored in mercurial under

    $CHECKMATE_HOME/checkmate/tools/jenkins-ci/

These tools are based on the following settings

    CHECKMATE_HG_HOME
        this is the local directory where the result of 'hg clone' from http://bitbucket.org is stored.
        This variable is set to the value of CHECKMATE_HOME.
        The reason for this duplicate is that jenkins-ci will override the CHECKMATE_HOME value.

    CHECKMATE_CI_HOME
        this is where the CI will be run.
        Given that the CI will make a 'hg clone' from $CHECKMATE_HG_HOME, this should refer to a directory in an encrypted partition.
        After cloning mercurial repository, the CHECKMATE_HOME should be set to point to $CHECKMATE_CI_HOME before starting jenkins CI.
        Remember that hg clone will not copy uncommited changes to $CHECKMATE_CI_HOME. The 'default' branch will be used.
        If a 'hg pull; hg up' is done from $CHECKMATE_CI_HOME, the newest code will be used from the next job to run.

    JENKINS_HOME=$CHECKMATE_CI_HOME/checkmate/tools/jenkins-ci
        this is the path where jenkins CI will look for scripts to run (which jenkins CI calls 'jobs').

The scripts are configured by default to be running every 15 minutes, starting from doctest followed by sample_app and pytango in parallel.
It is possible to modify this behavior by changing the content of file config.xml under checkmate/tools/jenkins-ci/jobs/* or to use the web interface available at http://localhost:8080 (default port), select the job and hit the 'Configure' button.

A failure in any script will break the chain and all following scripts will not be run until 15 minutes later.


Running continuous integration
------------------------------
The scripts stored for continuous integration are requiring to be under checkmate virtualenv.

Running jenkins CI at this time also requires the tango framework to be started. See the `tango related documentation`_.

In order to start jenkins CI, the following command must be launched from virtualenv:

    java -jar $JENKINS_WAR_DIR/jenkins.war > /dev/null &

Continuous integration will until the java process is killed.

The script to setup the jenkins-ci will look like this::
    export JENKINS_HOME=$CHECKMATE_CI_HOME/checkmate/tools/jenkins-ci
    export CHECKMATE_HOME=$CHECKMATE_CI_HOME

    source $HOME/Projects/tango-controls/cme-tango-8.1.2.bashrc

    export JENKINS_WAR_DIR=/Download

    skill java

    rm -Rf $CHECKMATE_CI_HOME
    hg clone -b default $CHECKMATE_HG_HOME $CHECKMATE_CI_HOME

    java -jar $JENKINS_WAR_DIR/jenkins.war > /dev/null &

where
    $HOME/Projects/tango-controls/cme-tango-8.1.2.bashrc should be the script to export PYTHONPATH
and
    /Download is the path where jenkins.war has been stored.

We see that CHECKMATE_HOME is now pointing to $CHECKMATE_CI_HOME for the shell from where jenkins is started.
This allow to use the original CHECKMATE_HOME for interactive testing while jenkins CI is running.


.. _tango related documentation: training_pytango_app.html 
