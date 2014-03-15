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
        >>> import checkmate.runtime.registry
        >>> ac = pytango.checkmate.application.Application
        >>> cc = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(ac, cc, threaded=True)
        >>> r.setup_environment(['C3'])
        >>> time.sleep(1)
        >>> r.start_test()
        >>> c1 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C1')
        >>> c2 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
        >>> o = c2.simulate(sample_app.exchanges.AC())
        >>> time.sleep(1)
        >>> c1.validate(o[0])
        True
        >>> r.stop_test()

    """
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

        self.communication_list = (pytango.checkmate.runtime.communication.Communication,)

        #db = PyTango.Database()
        #for name in list(self.components.keys()):
        #    db.add_device(self.components[name].device_info())

