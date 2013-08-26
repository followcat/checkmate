import time
import threading

import zope.interface

import checkmate.runtime.communication


@zope.interface.implementer(checkmate.runtime.communication.IConnection)
class Client(threading.Thread):
    """"""
    def __init__(self, name=None):
        super(Client, self).__init__(name=name)
        self.received_lock = threading.Lock()
        self.request_lock = threading.Lock()
        self.stop_lock = threading.Lock()
        self.end = False
        self.out_buffer = []

    def run(self):
        """"""
        while(1):
            self.process_request()
            self.stop_lock.acquire()
            if self.end:
                self.stop_lock.release()
                break
            self.stop_lock.release()
            self.process_receive()
            time.sleep(0.1)

    def stop(self):
        self.stop_lock.acquire(timeout=0.3)
        self.end = True
        self.stop_lock.release()

    def send(self, exchange):
        """"""
        self.request_lock.acquire()
        self.out_buffer.append(exchange)
        self.request_lock.release()


    def received(self, exchange):
        result = False
        self.received_lock.acquire()
        _local_copy = copy.deepcopy(self.in_buffer)
        self.received_lock.release()
        if exchange in _local_copy:
            result = True
            self.received_lock.acquire()
            self.in_buffer.remove(exchange)
            self.received_lock.release()
        return result
            
    def process_request(self):
        self.request_lock.acquire()
        left_over = (len(self.out_buffer) != 0)
        self.request_lock.release()
        while(left_over):
            self.request_lock.acquire()
            exchange = self.out_buffer.pop()
            left_over = (len(self.out_buffer) != 0)
            self.request_lock.release()
            # Send exchange using protocol here
            #

    def process_receive(self):
        incoming_list = []
        # Receive exchange using protocol here
        #
        if len(incoming_list) != 0:
            self.received_lock.acquire()
            for _incoming in incoming_list:
                self.in_buffer.append(_incoming)
            self.received_lock.release()
        


@zope.interface.implementer(checkmate.runtime.communication.IProtocol)
class Communication(object):
    """"""
    def initialize(self):
        """"""

