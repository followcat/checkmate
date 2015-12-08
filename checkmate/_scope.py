import os
import yaml
import doctest
import importlib


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
        """
            >>> import os
            >>> import doctest
            >>> import itertools
            >>> import checkmate._scope
            >>> name = 'checkmate/documentation/scopes/scope_definition.yaml'
            >>> with open(name) as _f:
            ...     definition = _f.read()
            >>> sco = checkmate._scope.Scope(definition)
            >>> runner = doctest.DocTestRunner()
            >>> for f in itertools.islice(sco.backlog, 2):
            ...     assert not sco.run_feature(f, runner, name)
        """
        yield from self.definition['backlog']


    def run_feature(self, feature, runner, filename):
        try:
            reference = feature['reference']

            index = 1
            last_index = 0
            max_index = len(reference.split('.'))
            while True:
                assert index > last_index
                name = '.'.join(reference.split('.', index)[:-1])
                try:
                    module = importlib.import_module(name)
                    last_index = index
                    index += 1
                except ImportError:
                    obj = module
                    for i in range(index, max_index+1):
                        obj = getattr(obj, reference.split('.')[i-1])
                    test = obj.__doc__
                    break
        except KeyError:
            try:
                test = feature['example']
            except KeyError:
                return
        runner.run(doctest.DocTestParser().get_doctest(test, locals(),
                          filename, None, None))

