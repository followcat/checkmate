# This code is part of the checkmate project.
# Copyright (C) 2014 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import time

import zmq

import checkmate.timeout_manager


class Poller(zmq.Poller):
    def poll(self, timeout=None):
        if self.sockets:
            return super().poll(timeout)
        if timeout > 0:
            time.sleep(timeout / 1000)
        return []

    def register(self, socket):
        super().register(socket, zmq.POLLIN)

    def poll_with_timeout(self):
        return dict(super().poll(checkmate.timeout_manager.POLLING_TIMEOUT_MILLSEC))

