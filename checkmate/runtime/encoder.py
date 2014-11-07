import pickle


def encode(exchange):
    dump_data = pickle.dumps((type(exchange), exchange.value))
    return dump_data


def decode(message):
    """
    >>> import sample_app.application
    >>> import checkmate.runtime.encoder
    >>> ac = sample_app.exchanges.AC()
    >>> encode_exchange = checkmate.runtime.encoder.encode(ac)
    >>> decode_exchange = checkmate.runtime.encoder.decode(encode_exchange)
    >>> ac == decode_exchange
    True
    """
    exchange_type, exchange_value = pickle.loads(message)
    exchange = exchange_type(exchange_value)
    return exchange
