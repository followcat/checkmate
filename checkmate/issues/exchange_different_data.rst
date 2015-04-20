Init a new Action AP from transition incoming storage and modify it's arguments from 'R':None to 'R2', it's R should be ['AT2', 'HIGH'].   
>>> import sample_app.application
>>> a = sample_app.application.TestData()
>>> c1 = a.components['C1']
>>> incoming = c1.engine.transitions[1].incoming[0]
>>> incoming.code
'AP'
>>> incoming.arguments.update({'attribute_values':{}, 'values':('R2', )})
>>> incoming.factory().R.C.value, incoming.factory().R.P.value 
('AT2', 'HIGH')

Restore incoming.arguments
>>> del incoming.arguments['attribute_values']
>>> del incoming.arguments['values']
