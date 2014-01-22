[Title]
=======
[Next line is not a subtitle]

[Heading 2]
-----------
Data structure
+++++++++++++++
Attribute
**********
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Attribute

Value partitions
^^^^^^^^^^^^^^^^^

+---------------+-----------+--------------------------+--------------------------+
| Partition     | State     | Valid value              | Comment                  |
+===============+===========+==========================+==========================+
| D-ATTR-01     | A0('AT1') | AT1 valid value          | AT1 attribute value      |
+---------------+-----------+--------------------------+--------------------------+
| D-ATTR-02     | A0('AT2') | AT2 valid value          | AT1 attribute value      |
+---------------+-----------+--------------------------+--------------------------+



Action priority
****************
Definition
^^^^^^^^^^^
ActionPriority

Value partitions
^^^^^^^^^^^^^^^^^

+---------------+-----------+--------------------------+--------------------------+
| Partition     | State     | Valid value              | Comment                  |
+===============+===========+==========================+==========================+
| D-PRIO-01     | P0('NORM')| NORM valid value         | NORM priority value      |
+---------------+-----------+--------------------------+--------------------------+
| D-PRIO-02     | P0('HIGH')| HIGH valid value         | HIGH priority value      |
+---------------+-----------+--------------------------+--------------------------+



Action request
***************
Definition
^^^^^^^^^^^
ActionRequest(P=ActionPriority, A=Attribute)




Exchange identification
++++++++++++++++++++++++
Action
*******
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Action(R=ActionRequest)

Value partitions
^^^^^^^^^^^^^^^^^

+---------------+---------+----------------+-------------------+
| Partition     | Service | Valid value    | Comment           |
+===============+=========+================+===================+
| X-ACTION-01   | AC()    | Action action  | Comment AC action |
+---------------+---------+----------------+-------------------+
| X-ACTION-02   | AP(R)   | Append action  | Comment AP action |
+---------------+---------+----------------+-------------------+
| X-ACTION-03   | PP(R)   | Pop action     | Comment PP action |
+---------------+---------+----------------+-------------------+



Reaction
*********
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Reaction

Value partitions
^^^^^^^^^^^^^^^^^

+----------------+-----------------+----------------------+---------+
| Partition      | Service         | Valid value          | Comment |
+================+=================+======================+=========+
| X-REACTION-01  | RE()            | Valid reaction       | Comment |
+----------------+-----------------+----------------------+---------+
| X-REACTION-02  | RL()            | Release reaction     | Comment |
+----------------+-----------------+----------------------+---------+



AnotherReaction
****************
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AnotherReaction

Value partitions
^^^^^^^^^^^^^^^^^

+----------------+-----------------+----------------------+---------+
| Partition      | Service         | Valid value          | Comment |
+================+=================+======================+=========+
| X-ANOREACT-01  | ARE()           | Valid ano-reaction   | Comment |
+----------------+-----------------+----------------------+---------+



ThirdReaction
****************
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ThirdReaction

Value partitions
^^^^^^^^^^^^^^^^^

+----------------+-----------------+----------------------+---------+
| Partition      | Service         | Valid value          | Comment |
+================+=================+======================+=========+
| X-THRDREACT-01 | DR()            | Valid thd-reaction   | Comment |
+----------------+-----------------+----------------------+---------+



Pause
******
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Pause

Value partitions
^^^^^^^^^^^^^^^^^

+----------------+-----------------+----------------------+---------+
| Partition      | Service         | Valid value          | Comment |
+================+=================+======================+=========+
| X-PAUSE-01     | PA()            | Valid pause          | Comment |
+----------------+-----------------+----------------------+---------+



ABS allocation request
***********************
Definition and accessibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ThirdAction

+==+=========+=========+=========+
|  | Field 1 | Field 2 | Field 4 |
+--+---------+---------+---------+

Type of data
^^^^^^^^^^^^^
Description

Exchange
^^^^^^^^^

+----------------+--------------+-----------------------+
| Origin         | Destination  | Comment               |
+================+==============+=======================+
| component 1    | component 2  | third action          |
+----------------+--------------+-----------------------+


Value partitions
^^^^^^^^^^^^^^^^^

+--------------+-----------+----------------------+----------------------------------+
| Service      | Partition | Valid value          | Comment                          |
+==============+===========+======================+==================================+
| X-THRDACT-01 | AL()      | Third action valid 1 | Third action first valid value   |
+--------------+-----------+----------------------+----------------------------------+
| X-THRDACT-02 | DA()      | Third action valid 2 | Third action second valid value  |
+--------------+-----------+----------------------+----------------------------------+

