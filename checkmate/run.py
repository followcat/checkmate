class Run(object):
    """"""
    def __init__(self, data):
        self.initial, self.incoming, self.final, self.outgoing = data


    def __eq__(self, other):
        return (self.initial == other.initial
                and self.incoming == other.incoming
                and self.final == other.final
                and self.outgoing == other.outgoing)
