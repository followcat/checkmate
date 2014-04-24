import checkmate.application

import sample_app.exchanges
import sample_app.data_structure

import pytango.checkmate.runtime.communication


class Application(checkmate.application.Application, metaclass=checkmate.application.ApplicationMeta):
    """
        >>> import pytango.checkmate.application
        >>> import time
        >>> import sample_app.exchanges
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> ac = pytango.checkmate.application.Application
        >>> cc = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(ac, cc, threaded=True)
        >>> r.setup_environment(['C3'])
        >>> time.sleep(1)
        >>> r.start_test()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> o = c2.simulate(sample_app.exchanges.AC())
        >>> time.sleep(1)
        >>> c1.validate(o[0])
        True
        >>> r.stop_test()

    """
    #database = 'tango'
    data_structure_module = sample_app.data_structure
    exchange_module = sample_app.exchanges

    def __init__(self, full_python=False):
        super(Application, self).__init__(full_python)

        import pytango.checkmate.component.component_1
        import pytango.checkmate.component.component_2
        import pytango.checkmate.component.component_3
        self.components = {'C1': pytango.checkmate.component.component_1.Component_1,
                           'C2': pytango.checkmate.component.component_2.Component_2,
                           'C3': pytango.checkmate.component.component_3.Component_3,
                          }

        for name in list(self.components.keys()):
            self.components[name] = self.components[name](name, full_python)

        self.communication_list = (pytango.checkmate.runtime.communication.Communication,)

        #db = PyTango.Database()
        #for name in list(self.components.keys()):
        #    db.add_device(self.components[name].device_info())

