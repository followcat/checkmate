import time
import os.path
import logging


def _log_name(output='out'):
    return os.path.join(os.getenv("CHECKMATE_LOG", "."), output + "-" + time.asctime().replace(' ', '-') + ".log")

def runtime_log_name():
    return _log_name('runtime')

def exchange_log_name():
    return _log_name('exchange')

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

