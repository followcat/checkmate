the run transform application components' states to back to initial
will be all initial followed runs' previous run

>>> import checkmate.sandbox
>>> import checkmate.pathfinder
>>> import sample_app.application
>>> app = sample_app.application.TestData()
>>> app.reset()
>>> box = checkmate.sandbox.Sandbox(type(app), app)
>>> exchanges = app.origin_exchanges()
>>> pbac = sample_app.exchanges.ExchangeButton('PBAC')
>>> box([pbac])
True
>>> box.application.components['C1'].states[0].value
False
>>> box.application.components['C1'].states[1].value # doctest: +ELLIPSIS
[{'R': <sample_app.data_structure.ActionRequest object at ...
>>> pbrl = sample_app.exchanges.ExchangeButton('PBRL')
>>> box([pbrl])
True
>>> run_pbrl = box.blocks
>>> runs =[]
>>> gen = checkmate.pathfinder.followed_runs(box.application, exchanges)
>>> runs.append(next(gen))
>>> checkmate.pathfinder.filter_run(box.application, runs[0])
>>> checkmate.pathfinder.update_matrix(box.application, runs[0], runs)
>>> runs.append(next(gen))
>>> checkmate.pathfinder.filter_run(box.application, runs[1])
>>> checkmate.pathfinder.update_matrix(box.application, runs[1], runs)
>>> len(runs)
2
>>> run_ac_er = [_r for _r in runs if _r.exchanges[0].value == 'PBAC'][0]
>>> box(run_ac_er.exchanges)
True
>>> path = checkmate.pathfinder._find_runs(box.application, runs[0], run_ac_er)
>>> len(path)
1
>>> path[0].exchanges[0].value
'PBRL'
>>> path = checkmate.pathfinder._find_runs(box.application, runs[1], run_ac_er)
>>> len(path)
1
>>> path[0].exchanges[0].value
'PBRL'
>>> app.reset()

