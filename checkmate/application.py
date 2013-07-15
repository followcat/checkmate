import checkmate.exchange
import checkmate.parser.doctree


class Application(object):
    def __init__(self, matrix, exchange_module=None):
        """
        """
        self.exchanges = []
        self.component_list = []
        global checkmate
        output = checkmate.parser.doctree.load_partitions(matrix, exchange_module)
        setattr(self, 'exchanges', output['exchanges'])

    def start(self):
        """
        """
        for component in self.component_list:
            component.start()
        

        

