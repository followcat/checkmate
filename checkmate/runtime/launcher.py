import time
import subprocess

import checkmate.runtime.component


class Launcher(object):
    def __init__(self, command=None, args=[''], component=None, wait_sec=0):
        if command is not None:
            self.process = subprocess.Popen(command)
            time.sleep(wait_sec)
        elif component is not None:
            self.process = None
            self.runtime_component = checkmate.runtime.component.ThreadedComponent(component)
            self.runtime_component.start()
        else:
            raise Exception("No command nor component")

    def end(self):
        if self.process is not None:
            self.process.terminate()
            self.process.communicate()
        else:
            self.runtime_component.stop()
