The encoder is loading the exchange with attributes:
    >>> import sample_app.application
    >>> r2 = sample_app.application.TestData.data_value['ActionRequest'][1]['R2']
    >>> ap = sample_app.exchanges.Action('AP', R=r2)
    >>> ap.R.C.value
    'AT2'
    >>> import checkmate.runtime.communication
    >>> encoder = checkmate.runtime.communication.Encoder()
    >>> encode_exchange = encoder.encode(ap)
    >>> decode_exchange = encoder.decode(encode_exchange)
    >>> decode_exchange == ap
    True
    >>> decode_exchange.R.C.value
    'AT2'

The encoder is loading the exchange with origin and destination:
    >>> import sample_app.application
    >>> import checkmate.runtime.communication
    >>> app = sample_app.application.TestData()
    >>> encoder = checkmate.runtime.communication.Encoder()
    >>> app.start()
    >>> c2 = app.components['C2']
    >>> out = c2.process([sample_app.exchanges.ExchangeButton('PBAC')])
    >>> encode_exchange = encoder.encode(out[0])
    >>> decode_exchange = encoder.decode(encode_exchange)
    >>> decode_exchange.origin, decode_exchange.destination
    ('C2', ['C1'])

