import re
import yaml
import os.path
import doctest
import importlib


__all__ = ['check_backlog', 'check_feature']


def test_scope_definition():
    scope_definition_path = "checkmate/documentation/scopes"
    for root, dirs, files in os.walk(scope_definition_path):
        for filename in [os.path.join(root, entry) for entry in files if
                os.path.isfile(os.path.join(root, entry))]:
            if os.path.splitext(filename)[-1] == '.yaml':
                yield check_backlog, filename

def check_backlog(filename):
    scope = Scope(filename=filename)
    runner = doctest.DocTestRunner(verbose=False)
    for feature in scope.backlog:
        try:
            failures = feature['failures']
        except KeyError:
            failures = 0
        example = scope.example(feature, filename)
        if not example:
            continue
        result = runner.run(example)
        if result.failed != failures:
            runner.run(example)
            if failures == 0:
                print("Expected: success, got: %d failures" % result.failed)
            else:
                print("Expected: %d failures, got: %d" % (failures, result.failed))

def check_feature(filename, feature_name, verbose=True):
    """
        >>> import checkmate._scope
        >>> feature = "Definition of scope using yaml"
        >>> name = "checkmate/documentation/scopes/scope_definition.yaml"
        >>> checkmate._scope.check_feature(name, feature, verbose=False)
    """
    scope = Scope(filename=filename)
    for feature in scope.backlog:
        if feature['feature'] == feature_name:
            runner = doctest.DocTestRunner(verbose=verbose)
            try:
                failures = feature['failures']
            except KeyError:
                failures = 0
            example = scope.example(feature, filename)
            if not example:
                break
            result = runner.run(example)
            if result.failed != failures:
                runner.run(example)
                if failures == 0:
                    print("Expected: success, got: %d failures" % result.failed)
                else:
                    print("Expected: %d failures, got: %d" % (failures, result.failed))
            break
        assert not feature_name


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

    @property
    def suite(self):
        """
            >>> import os
            >>> import doctest
            >>> import itertools
            >>> import checkmate._scope
            >>> name = 'checkmate/documentation/scopes/scope_definition.yaml'
            >>> with open(name) as _f:
            ...     definition = _f.read()
            >>> sco = checkmate._scope.Scope(definition)
            >>> runner = doctest.DocTestRunner(verbose=False)
            >>> for f in itertools.islice(sco.suite, 2):
            ...     assert runner.run(f)
        """
        for feature in self.backlog:
            example = self.example(feature)
            if example:
                yield example

    def example(self, feature, filename=''):
        try:
            reference = feature['reference']

            index = 1
            last_index = 0
            max_index = len(reference.split('.'))
            while True:
                assert index > last_index and index <= max_index
                if index < max_index:
                    name = '.'.join(reference.split('.', index)[:-1])
                else:
                    name = '.'.join(reference.split('.', index))
                try:
                    module = importlib.import_module(name)
                    last_index = index
                    index += 1
                except ImportError:
                    obj = module
                    for i in range(index-1, max_index):
                        obj = getattr(obj, reference.split('.')[i])
                    test = obj.__doc__
                    break
        except KeyError:
            try:
                test = feature['example']
                test = re.subn(" >>> ", "\n >>> ", test)[0]
                test = re.subn(" \.\.\. ", "\n ... ", test)[0]
            except KeyError:
                return
        return doctest.DocTestParser().get_doctest(test, locals(),
                  filename, None, None)

