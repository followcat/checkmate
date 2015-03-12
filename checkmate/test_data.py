# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import pickle

import sample_app.application


global my_data
my_data = {}


def App(_application=sample_app.application.TestData):
    global my_data
    if _application.__name__ not in iter(my_data):
        my_data[_application.__name__] = _application()
        my_data[_application.__name__] = pickle.dumps(my_data[_application.__name__])
    return pickle.loads(my_data[_application.__name__])

