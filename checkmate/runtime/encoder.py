import pickle


def encode(exchange):
    dump_data = pickle.dumps((type(exchange), exchange.value))
    return dump_data


def decode(message, exchange_module):
    exchange_type, exchange_value = pickle.loads(message)
    exchange = exchange_type(exchange_value)
    return exchange
