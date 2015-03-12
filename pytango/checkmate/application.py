# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate.application

import sample_app.exchanges
import sample_app.data_structure


class Application(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    #database = 'tango'
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges

    def __init__(self):
        super(Application, self).__init__()

        import pytango.checkmate.component_1.component
        import pytango.checkmate.component_2.component
        import pytango.checkmate.component_3.component
        self.components = {'C1': pytango.checkmate.component_1.component.Component_1,
                           'C2': pytango.checkmate.component_2.component.Component_2,
                           'C3': pytango.checkmate.component_3.component.Component_3,
                          }

        for name in list(self.components.keys()):
            self.components[name] = self.components[name](name)

        #db = PyTango.Database()
        #for name in list(self.components.keys()):
        #    db.add_device(self.components[name].device_info())

