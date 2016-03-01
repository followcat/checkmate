class Component(object):
    """"""
    def __init__(self, name, engine):
        """"""
        self.name = name
        self.engine = engine

    def start(self):
        """"""
        self.engine.start()

    def process(self):
        """"""
        self.engine.process()

    def validate(self):
        """"""
        self.engine.validate()
