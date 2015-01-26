With empty poller, the poll() function returns when time is out:
    >>> import time
    >>> import checkmate.runtime._zmq_wrapper
    >>> poll = checkmate.runtime._zmq_wrapper.Poller()
    >>> ct = time.time()
    >>> message= poll.poll_with_timeout()
    >>> value = poll.timeout_value/1000.
    >>> assert(((time.time())-ct) > value)
    >>>
