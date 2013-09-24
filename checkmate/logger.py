import time
import pickle
import os.path
import logging


def _log_name(output='out'):
    return os.path.join(os.getenv("CHECKMATE_LOG", "."), output + "-" + time.asctime().replace(' ', '-') + ".log")

def runtime_log_name():
    return _log_name('runtime')

def exchange_log_name():
    return _log_name('exchange')

def start_runtime_logger():
    logger = logging.getLogger("checkmate")  
    logger.setLevel(logging.DEBUG)  

    # add a general file log handler to handle DEBUG level log message
    fhandler=logging.FileHandler(runtime_log_name())
    fhandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] - [%(name)s] - %(levelname)s: %(message)s")
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)

    #add a streamHandler to handler the ERROR level log message
    shandler=logging.StreamHandler()
    shandler.setLevel(logging.ERROR)
    shandler.setFormatter(formatter)
    logger.addHandler(shandler)

class Logger(object):
    """"""
    def __init__(self):
        """"""
        start_runtime_logger()

    def start_exchange_logger(self):
        """"""
        _ex_filename = exchange_log_name()
        self.wf = open(_ex_filename, 'wb')

    def log_exchange(self, exchange):
        """"""
        if self._isexchangelogstarted() and exchange is not None:
            pickle.dump(exchange, self.wf)
        
    def _isexchangelogstarted(self):
        try:
            if self.wf.writable():
                return True
        except:
            return False

    def stop_exchange_logger(self):
        assert self._isexchangelogstarted()
        self.wf.flush()
        self.wf.close()

global_logger = Logger()
