import yaml


class Scope(object):
    """"""
    def __init__(self, definition):
        self.definition = yaml.load(definition)

    @property
    def description(self):
        try:
            return self.definition['description']
        except ValueError:
            return ""

    @property
    def backlog(self):
        yield from self.definition['backlog']

