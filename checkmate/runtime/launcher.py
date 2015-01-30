import os
import shlex
import subprocess

import checkmate.timeout_manager


class Launcher(object):
    def __init__(self, component, command, command_env=None,
                 runtime=None, threaded=False, *args):
        """"""
        self.command = command
        self.runtime = runtime
        self.threaded = threaded
        self.component = component
        self.command_env = command_env
        if self.threaded:
            self.runtime_component = command(component)
            if runtime is not None:
                self.runtime_component.setup(runtime)
        else:
            pass

    def initialize(self):
        if self.threaded:
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
        if self.threaded:
            self.runtime_component.start()

    def end(self):
        if self.threaded:
            self.runtime_component.stop()
        else:
            self.process.terminate()
            try:
                outs, errs = \
                    self.process.communicate(
                        timeout=checkmate.timeout_manager.THREAD_STOP_SEC)
            except subprocess.TimeoutExpired:
                self.process.kill()

