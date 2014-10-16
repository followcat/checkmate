import pickle


def encode(exchange):
    dump = (exchange.action, exchange.get_partition_attr())
    return pickle.dumps(dump)


def decode(message, exchange_module):
    load = pickle.loads(message)
    exchange = getattr(exchange_module, load[0])()
    if exchange.partition_attribute:
        setattr(exchange, dir(exchange)[0], load[1])
    return exchange
