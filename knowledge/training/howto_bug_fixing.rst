How to fix a problem
====================
Finding a problem in the code is a good thing.
This gives an importunity to improve the code for users and help co-workers.

When a problem is found, this also highlight that a test was missing.
If the code that had the problem was fully tested, the problem would have been identified earlier.
It is important to use the opportunity given by the identification of the problem to improve both the code and the tests.

Here is the good way to fix a problem found in the code.

When a problem occurs, we have to analyze the error reported with care. It is usually useful to have a traceback for that the flow of function calls can help identifying the source of the problem.
The error is not always in the last file of the stack!

::

    $ python checkmate/nose_plugin/plugin.py --with-checkmate --sut=C1,C3 checkmate/
    EE
    ======================================================================
    ERROR: >>> import time
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "$CHECKMATE_HOME/checkmate/nose_plugin/suite.py", line 37, in runTest
        self.test(system_under_test=config_as_dict['system_under_test'])
      File "$CHECKMATE_HOME/checkmate/runtime/procedure.py", line 95, in __call__
        self._run_from_startpoint(self.exchanges)
      File "$CHECKMATE_HOME/checkmate/runtime/procedure.py", line 199, in _run_from_startpoint
        stub.simulate(current_node.root)
      File "$CHECKMATE_HOME/checkmate/runtime/component.py", line 269, in simulate
        output = self.context.simulate(exchange)
      File "$CHECKMATE_HOME/checkmate/component.py", line 104, in simulate
        for _outgoing in _transition.process(self.states, exchange):
      File "$CHECKMATE_HOME/checkmate/transition.py", line 210, in process
        if not self.is_matching_initial(states) or not self.is_matching_incoming(_incoming):
      File "$CHECKMATE_HOME/checkmate/transition.py", line 60, in is_matching_incoming
        return len(exchange_list) == 0
    TypeError: object of type 'Action' has no len()
    
    ======================================================================
    ERROR: >>> import time
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "$CHECKMATE_HOME/checkmate/nose_plugin/suite.py", line 37, in runTest
        self.test(system_under_test=config_as_dict['system_under_test'])
      File "$CHECKMATE_HOME/checkmate/runtime/procedure.py", line 90, in __call__
        self.transform_to_initial()
      File "$CHECKMATE_HOME/checkmate/runtime/procedure.py", line 111, in transform_to_initial
        _procedure(system_under_test=self.system_under_test)
      File "$CHECKMATE_HOME/checkmate/runtime/procedure.py", line 95, in __call__
        self._run_from_startpoint(self.exchanges)
      File "$CHECKMATE_HOME/checkmate/runtime/procedure.py", line 199, in _run_from_startpoint
        stub.simulate(current_node.root)
      File "$CHECKMATE_HOME/checkmate/runtime/component.py", line 269, in simulate
        output = self.context.simulate(exchange)
      File "$CHECKMATE_HOME/checkmate/component.py", line 104, in simulate
        for _outgoing in _transition.process(self.states, exchange):
      File "$CHECKMATE_HOME/checkmate/transition.py", line 210, in process
        if not self.is_matching_initial(states) or not self.is_matching_incoming(_incoming):
      File "$CHECKMATE_HOME/checkmate/transition.py", line 60, in is_matching_incoming
        return len(exchange_list) == 0
    TypeError: object of type 'Action' has no len()
    
    ----------------------------------------------------------------------
    Ran 2 tests in 0.099s
    
    FAILED (errors=2)

With some grunt analysis, we found out the problem lies in this code.

::

    def simulate(self, exchange):
        _transition = self.get_transition_by_output([exchange])
        if _transition is None:
            return []
        output = []
        _incoming = _transition.generic_incoming(self.states)
        for _outgoing in _transition.process(self.states, _incoming):
            for _e in checkmate.service_registry.global_registry.server_exchanges(_outgoing, self):
                output.append(_e)
        return output


From there it is important to exercize the code to try to reproduce the error and try to simplify the test to help identifying the source of the problem.
This is where the power of the python console helps.

::

    $ python
    Python 3.3.2 (default, Jul 18 2013, 11:39:28) 
    [GCC 4.4.5] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import sample_app.application
    >>> import sample_app.component_2.component
    >>> c2 = sample_app.component_2.component.Component_2('C2')
    >>> c2.start()
    >>> c2.simulate(sample_app.exchanges.AC())
    Traceback (most recent call last):
      File "<ipython-input-6-0b6c53d112ed>", line 1, in <module>
        c2.simulate(sample_app.exchanges.AC())
      File "./checkmate/component.py", line 104, in simulate
        for _outgoing in _transition.process(self.states, exchange):
      File "./checkmate/transition.py", line 210, in process
        if not self.is_matching_initial(states) or not self.is_matching_incoming(_incoming):
      File "./checkmate/transition.py", line 60, in is_matching_incoming
        return len(exchange_list) == 0
    TypeError: object of type 'Action' has no len()


When the same problem has been reproduced in the python console, we should refrain from fixing the problem at once. We have to remember that beside the problem, we need to fix the lack of testing.
The reason we are using doctest is that we can just paste the output from the python console and fix it with the output we expected to find::

    def simulate(self, exchange):
        """
            >>> import sample_app.application
            >>> import sample_app.component_2.component
            >>> c2 = sample_app.component_2.component.Component_2('C2')
            >>> c2.start()
            >>> out = c2.simulate(sample_app.exchanges.AC())
            >>> out[0].action == 'AC'
            True
        """

It is them important to run the doctest to confirm that it is still catching the problem we have met.
The nosetest tool allows to run doctest on a single module::

    $ nosetests --with-doctest checkmate/component.py
    ..F
    ======================================================================
    FAIL: Doctest: checkmate.component.Component.simulate
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/usr/local/products/python-3.3.2/lib/python3.3/doctest.py", line 2154, in runTest
        raise self.failureException(self.format_failure(new.getvalue()))
    AssertionError: Failed doctest test for checkmate.component.Component.simulate
      File "$CHECKMATE_HOME/checkmate/component.py", line 99, in simulate
    
    ----------------------------------------------------------------------
    File "$CHECKMATE_HOME/checkmate/component.py", line 105, in checkmate.component.Component.simulate
    Failed example:
        out = c2.simulate(sample_app.exchanges.AC())
    Exception raised:
        Traceback (most recent call last):
          File "/usr/local/products/python-3.3.2/lib/python3.3/doctest.py", line 1287, in __run
            compileflags, 1), test.globs)
          File "<doctest checkmate.component.Component.simulate[4]>", line 1, in <module>
            out = c2.simulate(sample_app.exchanges.AC())
          File "$CHECKMATE_HOME/checkmate/component.py", line 113, in simulate
            for _outgoing in _transition.process(self.states, exchange):
          File "$CHECKMATE_HOME/checkmate/transition.py", line 210, in process
            if not self.is_matching_initial(states) or not self.is_matching_incoming(_incoming):
          File "$CHECKMATE_HOME/checkmate/transition.py", line 60, in is_matching_incoming
            return len(exchange_list) == 0
        TypeError: object of type 'Action' has no len()
    ----------------------------------------------------------------------
    File "$CHECKMATE_HOME/checkmate/component.py", line 106, in checkmate.component.Component.simulate


As we are now having a test to check the fix we are ready to implement in the code, we can do our change::

             _transition = self.get_transition_by_output([exchange])
             if _transition is None:
                 return []
             output = []
    -        for _outgoing in _transition.process(self.states, exchange):
    +        _incoming = _transition.generic_incoming(self.states)
    +        for _outgoing in _transition.process(self.states, _incoming):


We can run the doctest again, to see that the problem is really solved::

    $ nosetests --with-doctest checkmate/component.py
    ...
    ----------------------------------------------------------------------
    Ran 3 tests in 0.942s

    OK

We also have to run the other tests to check again any regression::

    $ nosetests --with-doctest checkmate/
    ......................s...........
    ----------------------------------------------------------------------
    Ran 34 tests in 14.015s
    
    OK (SKIP=1)

    
    $ python checkmate/nose_plugin/plugin.py --with-checkmate --sut=C1,C3 checkmate/ sample_app/
    .....s
    ----------------------------------------------------------------------
    Ran 6 tests in 1.024s
    
    OK

Given that all tests are passed OK, we can then commit the change::

    $ hg ci -m "Fix simulate() logic by using transition generic_incoming()" checkmate/component.py 

