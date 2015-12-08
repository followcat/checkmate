import os
import yaml
import doctest


__all__ = ['check_backlog']


def check_backlog(filename):
    if os.path.isfile(filename):
        _f = open(filename)
    else:
        _f = open(os.path.sep.join([os.getenv('CHECKMATE_HOME'), filename]))
    definition = _f.read()
    _f.close()
    scope = Scope(definition)
    runner = doctest.DocTestRunner()
    for feature in scope.backlog:
        scope.run_feature(feature, runner, filename)


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

    def run_feature(self, feature, runner, filename):
        test = feature['example']
        runner.run(doctest.DocTestParser().get_doctest(test, locals(),
                          filename, None, None))

