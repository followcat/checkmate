Init a new Action AP from transition incoming storage and modify it's arguments from 'R':None to 'R2', it's R should be ['AT2', 'HIGH'].   
>>> import sample_app.application
>>> a = sample_app.application.TestData()
>>> c1 = a.components['C1']
>>> incoming = c1.state_machine.transitions[1].incoming[0]
>>> incoming.code
'AP'
>>> incoming.arguments.update({'attribute_values':{}, 'values':('R2', )})
>>> incoming.factory().R
['AT2', 'HIGH']
