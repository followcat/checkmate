import logging

import checkmate.runtime.communication


class Communication(checkmate.runtime.communication.Communication):
    """
        >>> import time
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime
        >>> import checkmate.component
        >>> import sample_app.application
        >>> a = sample_app.application.TestData
        >>> c = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(a, c, True)
        >>> r.setup_environment(['C3'])
        >>> r.start_test()
        >>> c2_stub = r.runtime_components['C2']
        >>> c1_stub = r.runtime_components['C1']
        >>> c2 = r.application.components['C2']
        >>> simulated_transition = c2.state_machine.transitions[0]
        >>> o = c2_stub.simulate(simulated_transition)
        >>> t = c1_stub.context.state_machine.transitions[0]
        >>> t.is_matching_incoming(o)
        True
        >>> c1_stub.validate(t)
        True
        >>> time.sleep(1)
        >>> r.stop_test()
    """
    def __init__(self, component=None):
        """"""
        super(Communication, self).__init__(component)
        self.logger = \
            logging.getLogger('checkmate.runtime._pyzmq.Communication')
        self.logger.info("%s initialize" % self)

    def close(self):
        super(Communication, self).close()
        self.logger.info("%s close" % self)
