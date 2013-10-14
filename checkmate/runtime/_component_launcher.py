import sys
import pickle

import checkmate.runtime.component


if __name__ == '__main__':
    pickled_component = sys.stdin.read()
    try:
        component = pickle.loads(pickled_component)
    except Exception as e:
        sys.stderr.write(e)
        raise e
    
    checkmate.component.runtime.ThreadedComponent(component).start()

    while True:
        pass

