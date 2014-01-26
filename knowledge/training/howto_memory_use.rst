A guide to analyzing Python performance
=======================================


Use pdb to make a breakpoint
****************************

insert into your code a statement to invoke the debugger:

::

	import pdb; pdb.set_trace()

then can Use pdb commands, such as:

::

	Just type the command and hit enter.

	s	step into, go into the function in the cursor
	n	step over, execute the function under the cursor without stepping into it
	c	continue, resume program
	w	where am I? displays current location in stack trace
	b	set breakpoint
	cl	clear breakpoint
	bt	print stack trace
	up	go to the scope of the caller function
	pp	pretty print object

and so on,you can see more at: `Python3PdbCommand
<http://docs.python.org/3/library/pdb.html#debugger-commands>`_.

How much memory does it use?
****************************

:To Install:

- **$ pip install -U memory_profiler**

- **$ pip install psutil**

(Installing the psutil package here is recommended because it greatly improves the performance of the memory_profiler).

:To Use @profile:

memory_profiler requires that you decorate your function of interest with an @profile decorator like so:

| *@profile*
| def test(n):
|         pass

To see how much memory your function uses run the following:

**$ python -m memory_profiler primes.py**

or

**import memory_profiler import profile** at your @profile file

::

	You should see output that looks like this once your program exits:
	Line #    Mem usage  Increment   Line Contents
	==============================================
	    2                           @profile
	    3    7.9219 MB  0.0000 MB   def test(n): 
	    4    7.9219 MB  0.0000 MB       if n==2:
	    5                                   return [2]
	    6    7.9219 MB  0.0000 MB       elif n<2:
	    7                                   return []
	    8    7.9219 MB  0.0000 MB       s=range(3,n+1,2)
	    9    7.9258 MB  0.0039 MB       mroot = n ** 0.5
	   10    7.9258 MB  0.0000 MB       half=(n+1)/2-1
	   11    7.9258 MB  0.0000 MB       i=0
	   12    7.9258 MB  0.0000 MB       m=3
	   13    7.9297 MB  0.0039 MB       while m <= mroot:
	   14    7.9297 MB  0.0000 MB           if s[i]:
	   15    7.9297 MB  0.0000 MB               j=(m*m-3)/2
	   16    7.9258 MB -0.0039 MB               s[j]=0
	   17    7.9297 MB  0.0039 MB               while j<half:
	   18    7.9297 MB  0.0000 MB                   s[j]=0
	   19    7.9297 MB  0.0000 MB                   j+=m
	   20    7.9297 MB  0.0000 MB           i=i+1
	   21    7.9297 MB  0.0000 MB           m=2*i+3
	   22    7.9297 MB  0.0000 MB       return [2]+[x for x in s if x]

Another Example:

::


	Line #    Mem usage  Increment   Line Contents
	==============================================
	     3                           @profile
	     4      5.97 MB    0.00 MB   def my_func():
	     5     13.61 MB    7.64 MB       a = [1] * (10 ** 6)
	     6    166.20 MB  152.59 MB       b = [2] * (2 * 10 ** 7)
	     7     13.61 MB -152.59 MB       del b
	     8     13.61 MB    0.00 MB       return a

Use memory_usage(proc=-1, interval=.1, timeout=None) returns the memory usage over a time interval. 

::

	>>> from memory_profiler import memory_usage
	>>> mem_usage = memory_usage(-1, interval=.2, timeout=1)
	>>> print(mem_usage)
    	[7.296875, 7.296875, 7.296875, 7.296875, 7.296875]

github && memory_profiler Doc Here:`memory profiler Doc
<https://github.com/fabianp/memory_profiler/>`_.

Where’s the memory leak?
************************

The cPython interpreter uses reference counting as it’s main method of keeping track of memory. This means that every object contains a counter, which is incremented when a reference to the object is stored somewhere, and decremented when a reference to it is deleted. When the counter reaches zero, the cPython interpreter knows that the object is no longer in use so it deletes the object and deallocates the occupied memory.

A memory leak can often occur in your program if references to objects are held even though the object is no longer in use.

The quickest way to find these “memory leaks” is to use an awesome tool called objgraph written by Marius Gedminas. This tool allows you to see the number of objects in memory and also locate all the different places in your code that hold references to these objects.

To get started, first install objgraph:

::

	pip install objgraph

Which objects are the most common?
----------------------------------

At run time, you can inspect the top 20 most prevalent objects in your program by running:

::

	(pdb) import objgraph
	(pdb) objgraph.show_most_common_types()
	
	MyBigFatObject             20000
	tuple                      16938
	function                   4310
	dict                       2790
	wrapper_descriptor         1181
	builtin_function_or_method 934
	weakref                    764
	list                       634
	method_descriptor          507
	getset_descriptor          451
	type                       439

Which objects have been added or deleted?
-----------------------------------------

::

	(pdb) import objgraph
	(pdb) objgraph.show_growth()
	.
	.
	.
	(pdb) objgraph.show_growth()   # this only shows objects that has been added or deleted since last show_growth() call

	traceback                4        +2
	KeyboardInterrupt        1        +1
	frame                   24        +1
	list                   667        +1
	tuple                16969        +1


You can read more information about at: `objgraph Page
<http://mg.pov.lt/objgraph/>`_.

.. [#] This Passage Recompose From http://www.huyng.com/posts/python-performance-analysis/
