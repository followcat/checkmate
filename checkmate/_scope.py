import os
import yaml
import doctest


__all__ = ['check_backlog']


def check_backlog(filename):
    scope = Scope(filename=filename)
    runner = doctest.DocTestRunner()
    for feature in scope.backlog:
        scope.run_feature(feature, runner, filename)


class Scope(object):
    """"""
    def __init__(self, definition=None, filename=None):
        if filename:
            if not os.path.isfile(filename):
                filename = os.path.sep.join(
                                [os.getenv('CHECKMATE_HOME'), filename])
            with open(filename) as _f:
                definition = _f.read()
        assert definition
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

    def run_feature(self, feature, runner, filename):
        test = feature['example']
        runner.run(doctest.DocTestParser().get_doctest(test, locals(),
                          filename, None, None))

