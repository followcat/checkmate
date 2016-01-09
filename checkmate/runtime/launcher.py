# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import shlex
import argparse
import importlib
import subprocess

import checkmate.runtime._pyzmq
import checkmate.runtime._runtime
import checkmate.runtime.component


class Launcher(object):
    def __init__(self, component=None, command=None, command_env=None, runtime=None, *args):
        self.command = command
        self.runtime = runtime
        self.component = component
        self.command_env = command_env
        if self.command is not None:
            pass
        elif self.component is not None:
            self.runtime_component = checkmate.runtime.component.ThreadedComponent(self.component)
            self.runtime_component.setup(self.runtime)
        else:
            raise Exception("No command nor component")

    def initialize(self):
        if self.command is not None:
            command_env = dict(os.environ)
            if self.command_env is not None:
                command_env.update(self.command_env) 
            CLASSPATH = os.getenv('CHECKMATE_CLASSPATH', os.getenv('CLASSPATH'))
            self.process = subprocess.Popen(shlex.split(self.command.format(classpath=CLASSPATH, component=self.component)),
                                            env=command_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            self.runtime_component.initialize()

    def start(self):
        if self.command is None:
            self.runtime_component.start()

    def end(self):
        if self.command is not None:
            self.process.terminate()
            try:
                outs, errs = self.process.communicate(timeout=0.5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        else:
            self.runtime_component.stop()


def get_option_value(value):
    if len(value) == 0:
        return
    try:
        module, classname = value[0: value.rindex('.')], value[value.rindex('.')+1:]
        option_value = getattr(importlib.import_module(module), classname)
    except:
        raise ValueError("either env or command option is not properly specified")
    return option_value


def start_component(*args, **kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('--component', dest='component_name', action='store',
                        help='name of the component')
    parser.add_argument('--application', dest='application_callable', action='store',
                        default="sample_app.application.TestData",
                        help='application to find the component')
    parser.add_argument('--communication', dest='communication_callable', action='store',
                        default="checkmate.runtime._pyzmq.Communication",
                        help='communication to use with the component')
    args = parser.parse_args()

    component_name = vars(args)['component_name']
    application_callable = get_option_value(vars(args)['application_callable'])
    communication_callable = get_option_value(vars(args)['communication_callable'])
    
    runtime = checkmate.runtime._runtime.Runtime(application_callable, communication_callable, threaded=True)
    runtime.setup_environment([component_name])
    component = runtime.application.components[component_name]
    runtime_component = Launcher(component=component)
    while True:
        pass
    

if __name__ == '__main__':
    start_component()
    
