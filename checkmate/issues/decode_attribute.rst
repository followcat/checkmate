>>> import sample_app.application
>>> ap = sample_app.exchanges.AP(R=sample_app._data.R2['value'])
>>> ap.R.C.value
'AT2'
>>> import checkmate.runtime.encoder
>>> encode_exchange = checkmate.runtime.encoder.encode(ap)
>>> decode_exchange = checkmate.runtime.encoder.decode(encode_exchange)
>>> decode_exchange == ap
True
>>> decode_exchange.R.C.value
'AT2'

