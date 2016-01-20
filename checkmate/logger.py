# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import time
import os.path
import logging

import checkmate._visual


def _log_name(output='out'):
    """"""
    return os.path.join(os.getenv("CHECKMATE_LOG", "."), output + "-" + time.asctime().replace(' ', '-') + ".log")

def runtime_log_name():
    """"""
    return _log_name('runtime')

def runs_log_name():
    """"""
    return _log_name('runs')

def start_runtime_logger():
    logger = logging.getLogger("checkmate")
    logger.setLevel(logging.INFO)

    # add a general file log handler to handle DEBUG level log message
    fhandler = logging.FileHandler(runtime_log_name())
    fhandler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] - [%(name)s] - %(levelname)s: %(message)s")
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)

    #add a streamHandler to handler the ERROR level log message
    shandler = logging.StreamHandler()
    shandler.setLevel(logging.ERROR)
    shandler.setFormatter(formatter)
    logger.addHandler(shandler)

    # add a general file log handler to handle runs log message
    rlogger = logging.getLogger("runs")
    rlogger.setLevel(logging.INFO)

    rfhandler = logging.FileHandler(runs_log_name())
    rfhandler.setLevel(logging.INFO)
    rformatter = RunsFormatter("%(message)s")
    rfhandler.setFormatter(rformatter)
    rlogger.addHandler(rfhandler)


class RunsFormatter(logging.Formatter):
    def format(self, record):
        if record.msg[0] == 'Run':
            record.msg = "---\nRun: %s" % record.msg[1]
        elif record.msg[0] == 'State':
            record.msg = "---\nApplication State:%s" % checkmate._visual.visual_states(record.msg[1], level=1)
        elif record.msg[0] == 'Exception':
            record.msg = "---\nException Application State:%s" % checkmate._visual.visual_states(record.msg[1], level=1)
        return super().format(record)


start_runtime_logger()
