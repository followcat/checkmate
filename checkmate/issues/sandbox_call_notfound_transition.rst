If run has no transition to match outgoing, the Sandbox should run
this run and return True.

>>> import sample_app.application
>>> import checkmate.sandbox
>>> app = sample_app.application.TestData()
>>> runs = app.run_collection()
>>> sandbox = checkmate.sandbox.Sandbox(type(app))
>>> voda = runs[0].nodes[0].nodes[0].nodes[2].nodes[0].nodes[1].\
... nodes.pop()
>>> voda.root.incoming[0].code
'VODA'
>>> sandbox(runs[0])
True

