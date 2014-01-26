import time
import shlex
import argparse
import importlib
import subprocess

import checkmate.test_data
import checkmate.runtime._pyzmq
import checkmate.runtime._runtime
import checkmate.runtime.component


class Launcher(object):
    def __init__(self, command=None, args=[''], component=None, wait_sec=0):
        if command is not None:
            self.process = subprocess.Popen(shlex.split(command))
            time.sleep(wait_sec)
        elif component is not None:
            self.process = None
            self.runtime_component = checkmate.runtime.component.ThreadedComponent(component)
        else:
            raise Exception("No command nor component")

    def initialize(self):
        if self.process is None:
            self.runtime_component.initialize()

    def start(self):
        if self.process is None:
            self.runtime_component.start()

    def end(self):
        if self.process is not None:
            self.process.terminate()
            self.process.communicate()
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
                        default="checkmate.test_data.App",
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
    
