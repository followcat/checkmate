import checkmate.block


class Engine(object):
    """"""
    def __init__(self, name=None, blocks=None):
        if blocks:
            assert isinstance(blocks, list)
            self.blocks = blocks
        else:
            self.blocks = []
        if name:
            self.name = name

    def add_blocks(self, blocks):
        assert isinstance(blocks, list)
        for _b in blocks:
            if _b not in self.blocks:
                self.blocks.append(_b)
    
    def process(self, exchanges, states, block):
        assert isinstance(block, checkmate.block.Block)
        return block.process(states, exchanges)

