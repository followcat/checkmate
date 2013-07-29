import pickle

import sample_app.application


global my_data
my_data = None


def App(_application=sample_app.application.TestData):
    global my_data
    if my_data is None:
        my_data = _application()
        my_data = pickle.dumps(my_data)
    return pickle.loads(my_data)

