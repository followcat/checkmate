Coding guidelines: pep8 waiver
==============================
Introduction
------------
    The pep8 [1_] is introducing general guidelines for coding
    python code. The purpose is to have common ground across
    python projects for readability.

    The pep8 is generaly enforced for the project. The project coding
    guidelines are a restriction that is compatible with pep8.

    This document is a description of the project guidelines that
    conflict with pep8. In this case, the following guidelines supersede
    pep8.  If a tool is used for checking pep8, the guidelines here
    under should be applied instead of the suggested corrections from
    the tool.


    The main of contention with pep8 is about the multi-lines.
    Given that the project enforce a global reference to module, names
    in the code might be quite long, hitting often the maximum line
    length.

    The following rules should be followed in these cases.


Function calls
--------------
    The continuation:

+            self.logger.info("%s send exchange %s to %s" %
+                (self.context.name, _o.value, _o.destination))

    is prefered to:

+            self.logger.info("%s send exchange %s to %s" %
+                             (self.context.name, _o.value, _o.destination))

    The continuation:

+        self.logger = \
+            logging.getLogger('checkmate.runtime.component.Component')
    
    is prefered to:
    
+        self.logger = logging.getLogger(
+                          'checkmate.runtime.component.Component')
    
    The continuation:

+            self.client.internal_connector = \
+                connector_factory(self.context, _communication,
+                    is_reading=self.reading_internal_client)

    is prefered to:

+            self.client.internal_connector = connector_factory(
+                self.context, _communication,
+                is_reading=self.reading_internal_client)

    When the parameters to a function call is taking for than two lines,
    it is required to put one parameter per line.
    The first parameter will be put on the *second* line.
    
    As:

+                self.launcher = checkmate.runtime.launcher.Launcher(
+                                    command=self.context.launch_command,
+                                    command_env=self.context.command_env,
+                                    component=self.context)


Statement: if
-------------
    If a condition within a if() statement is longer than the max line
    length, the condition must be enclosed around parentheses.
    The line continuation within the condition is following pep8 and
    the rules stated above.

    Hence:

+            if (hasattr(_device, 'subscribe_event_done') and
+                    not _device.subscribe_event_done):


Statement: for
--------------
[TBD]


Function declaration
--------------------
    When a function parameters is too long to be defined in a oneliner,
    the hanging indent [2_] will be aligned on the parenthesis.

    Consequently:

+    def __init__(self, component, communication=None, is_reading=True,
+                 is_broadcast=False):

    When the parameters to a function declaration is taking more than
    two lines, it is required to put one parameter per line.
    The first parameter will be put on the *first* line.


.. [1] http://www.python.org/dev/peps/pep-0008
.. [2] https://www.python.org/dev/peps/pep-0008/#id3

