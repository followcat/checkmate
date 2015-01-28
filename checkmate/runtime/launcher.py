import os
import shlex
import subprocess

import checkmate.timeout_manager
import checkmate.runtime.component


class Launcher(object):
    def __init__(self, component=None, command=None, command_env=None,
                 runtime=None, *args):
        """"""
        self.command = command
        self.runtime = runtime
        self.component = component
        self.command_env = command_env
        if self.is_runtime_component():
            if runtime is not None:
                self.runtime_component = \
                    checkmate.runtime.component.ThreadedComponent(component)
                self.runtime_component.setup(runtime)
            else:
                raise Exception("No command nor component")
        else:
            pass

    def is_runtime_component(self):
        return self.runtime is not None

    def initialize(self):
        if self.is_runtime_component():
            self.runtime_component.initialize()
        else:
            command_env = dict(os.environ)
            if self.command_env is not None:
                command_env.update(self.command_env) 
            self.process = \
                subprocess.Popen(
                    shlex.split(self.command.format(component=self.component)),
                    env=command_env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)

    def start(self):
        if self.is_runtime_component():
            self.runtime_component.start()

    def end(self):
        if self.is_runtime_component():
            self.runtime_component.stop()
        else:
            self.process.terminate()
            try:
                outs, errs = \
                    self.process.communicate(
                        timeout=checkmate.timeout_manager.THREAD_STOP_SEC)
            except subprocess.TimeoutExpired:
                self.process.kill()

