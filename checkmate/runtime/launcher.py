import os
import shlex
import argparse
import importlib
import subprocess

import checkmate.timeout_manager
import checkmate.runtime._pyzmq
import checkmate.runtime._runtime
import checkmate.runtime.component


class Launcher(object):
    def __init__(self, component=None, command=None, command_env=None,
                 runtime=None, *args):
        """"""
        self.command = command
        self.runtime = runtime
        self.component = component
        self.command_env = command_env
        if self.command is not None:
            pass
        elif self.component is not None:
            self.runtime_component = \
                checkmate.runtime.component.ThreadedComponent(self.component)
            self.runtime_component.setup(self.runtime)
        else:
            raise Exception("No command nor component")

    def initialize(self):
        if self.command is not None:
            command_env = dict(os.environ)
            if self.command_env is not None:
                command_env.update(self.command_env) 
            self.process = \
                subprocess.Popen(
                    shlex.split(self.command.format(component=self.component)),
                    env=command_env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
        else:
            self.runtime_component.initialize()

    def start(self):
        if self.command is None:
            self.runtime_component.start()

    def end(self):
        if self.command is not None:
            self.process.terminate()
            try:
                outs, errs = \
                    self.process.communicate(
                        timeout=checkmate.timeout_manager.THREAD_STOP_SEC)
            except subprocess.TimeoutExpired:
                self.process.kill()
        else:
            self.runtime_component.stop()

