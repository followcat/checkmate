import pickle

import sample_app.application


global my_data
my_data = {}


def App(_application=sample_app.application.TestData, full_python=False):
    global my_data
    if _application.__name__ not in iter(my_data):
        my_data[_application.__name__] = _application(full_python)
        my_data[_application.__name__] = pickle.dumps(my_data[_application.__name__])
    return pickle.loads(my_data[_application.__name__])

