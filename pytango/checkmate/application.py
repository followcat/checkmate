import checkmate.application


class Application(checkmate.application.Application):
    #database = 'tango'

    def __init__(self):
        super(Application, self).__init__()

        import pytango.checkmate.component_1.component
        import pytango.checkmate.component_2.component
        self.components = {'C1': pytango.checkmate.component_1.component.Component_1,
                           'C2': pytango.checkmate.component_2.component.Component_2,
                          }

        for name in list(self.components.keys()):
            self.components[name] = self.components[name](name)

        #db = PyTango.Database()
        #for name in list(self.components.keys()):
        #    db.add_device(self.components[name].device_info())

