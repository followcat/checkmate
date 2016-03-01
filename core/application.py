class Application(object):
    """"""
    def __init__(self, components, communication):
        """"""
        self.components = {}
        for _c in components:
            self.components[_c.name] = _c
        self.communication = communication

    def start(self):
        """"""
        self.communication.start()
        for _c in self.components.values():
            _c.start()

    def stop(self):
        """"""
        for _c in self.components.values():
            _c.stop()
        self.communication.close()
        
    def sut(self, system_under_test):
        """"""
        self.system_under_test = system_under_test
