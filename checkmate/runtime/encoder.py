import pickle


def encode(exchange):
    dump = (exchange.value, exchange.get_partition_attr())
    return pickle.dumps(dump)


def decode(message, exchange_module):
    load = pickle.loads(message)
    exchange = getattr(exchange_module, load[0])()
    return exchange
