[Title]
=======
[Next line is not a subtitle]

[Heading 2]
-----------
Data structure
+++++++++++++++
TESTAttribute
**************
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TESTAttribute

Value partitions
^^^^^^^^^^^^^^^^^

+---------------+-----------+--------------------------+--------------------------+
| Partition     | State     | Valid value              | Comment                  |
+===============+===========+==========================+==========================+
| D-ATTR-01     | B0('AT1') | AT1 valid value          | AT1 attribute value      |
+---------------+-----------+--------------------------+--------------------------+
| D-ATTR-02     | B0('AT2') | AT2 valid value          | AT1 attribute value      |
+---------------+-----------+--------------------------+--------------------------+



TESTAction priority
********************
Definition
^^^^^^^^^^^
TESTActionPriority

Value partitions
^^^^^^^^^^^^^^^^^

+---------------+-----------+--------------------------+--------------------------+
| Partition     | State     | Valid value              | Comment                  |
+===============+===========+==========================+==========================+
| D-PRIO-01     | Q0('NORM')| NORM valid value         | NORM priority value      |
+---------------+-----------+--------------------------+--------------------------+
| D-PRIO-02     | Q0('HIGH')| HIGH valid value         | HIGH priority value      |
+---------------+-----------+--------------------------+--------------------------+



TESTAction request
*******************
Definition
^^^^^^^^^^^
TESTActionRequest(Q=TESTActionPriority, B=TESTAttribute)




Exchange identification
++++++++++++++++++++++++
TESTAction
***********
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TESTAction(T=TESTActionRequest)

Value partitions
^^^^^^^^^^^^^^^^^

+---------------+---------+----------------+-------------------+
| Partition     | Service | Valid value    | Comment           |
+===============+=========+================+===================+
| X-ACTION-01   | TC()    | Action action  | Comment AC action |
+---------------+---------+----------------+-------------------+
| X-ACTION-02   | TP(R)   | Append action  | Comment AP action |
+---------------+---------+----------------+-------------------+
| X-ACTION-03   | TP(R)   | Pop action     | Comment PP action |
+---------------+---------+----------------+-------------------+



TESTReaction
*************
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TESTReaction

Value partitions
^^^^^^^^^^^^^^^^^

+----------------+-----------------+----------------------+---------+
| Partition      | Service         | Valid value          | Comment |
+================+=================+======================+=========+
| X-REACTION-01  | TE()            | Valid reaction       | Comment |
+----------------+-----------------+----------------------+---------+

