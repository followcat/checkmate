import time
import shlex
import pickle
import subprocess


def launch(command, args=[''], wait_sec=0):
    process = subprocess.Popen(command)
    time.sleep(wait_sec)
    return process

def launch_component(component):
    pickled_component = pickle.dumps(component)
    process = subprocess.Popen(shlex.split('python checkmate/runtime/_component_launcher.py'), stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write(pickled_component)
    return process

def end(process):
    process.terminate()
    process.communicate()

