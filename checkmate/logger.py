import logging


logger = logging.getLogger("checkmate")  
logger.setLevel(logging.DEBUG)  

# add a general file log handler to handle DEBUG level log message
fhandler=logging.FileHandler("runtime.log")
fhandler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s] - [%(name)s] - %(levelname)s: %(message)s")
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)

#add a streamHandler to handler the ERROR level log message
shandler=logging.StreamHandler()
shandler.setLevel(logging.ERROR)
shandler.setFormatter(formatter)
logger.addHandler(shandler)

