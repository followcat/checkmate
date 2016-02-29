# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import re
import pickle
import inspect
import os.path
import checkmate._tree
import checkmate.runtime.procedure


def read_log(_f):
    class TestProc(checkmate.runtime.procedure.Procedure):
        """"""
            
    _e = pickle.load(_f)
    proc = TestProc()
    setattr(proc, 'exchanges', checkmate._tree.Tree(_e, []))
    _n = proc.exchanges
    try:
        while True:
            _e = pickle.load(_f)
            _n.add_node(checkmate._tree.Tree(_e, []))
            _n = _n.nodes[0]
    except EOFError:
        pass
    return proc

def TestLogProcedureGenerator(application_class):
    """
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_procedure
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> for g in checkmate.runtime.test_procedure.TestLogProcedureGenerator(sample_app.application.TestData):
        ...     g(r.application.system_under_test)
        >>> r.stop_test()
    """
    a = application_class()
    for dirpath, dirnames, filenames in os.walk(os.path.dirname(inspect.getfile(application_class))):
        for _filename in [_f for _f in filenames if re.match('exchange-.*\.log', _f) is not None]:
            try:
                _f = open(os.path.join(dirpath, _filename), 'rb')
                yield read_log(_f), _filename
                _f.close()
            except FileNotFoundError:
                continue
            except EOFError:
                continue

