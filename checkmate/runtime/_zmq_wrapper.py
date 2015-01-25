import time

import zmq

import checkmate.timeout_manager


class Poller(zmq.Poller):
    timeout_value = checkmate.timeout_manager.POLLING_TIMEOUT_MILLSEC

    def poll(self, timeout=None):
        if self.sockets:
            return super().poll(timeout)
        if timeout > 0:
            time.sleep(timeout / 1000)
        return []

    def register(self, socket):
        super().register(socket, zmq.POLLIN)

    @checkmate.report_issue("checkmate/issues/poll_with_timeout.rst")
    def poll_with_timeout(self):
        return dict(super().poll(self.timeout_value))

