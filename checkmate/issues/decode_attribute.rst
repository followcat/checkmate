>>> import sample_app.application
>>> r2 = sample_app.application.TestData.data_value['ActionRequest'][1]['R2']
>>> ap = sample_app.exchanges.AP(R=r2)
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

