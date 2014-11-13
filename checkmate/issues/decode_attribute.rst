>>> import sample_app.application
>>> ap = sample_app.exchanges.AP(R=sample_app._data.R2['value'])
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

