import pickle


def encode(exchange):
    pickle_dump = pickle.dumps((type(exchange), exchange.value))
    return pickle_dump


def decode(message, exchange_module):
    load = pickle.loads(message)
    exchange = load[0](load[1])
    return exchange
