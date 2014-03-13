import checkmate.runtime.test_plan


def get_path_from_pathfinder(application_class, application, target):
    """
        >>> import zope.interface
        >>> import checkmate.sandbox
        >>> import checkmate.paths_finder
        >>> import checkmate.runtime.registry    
        >>> import checkmate.runtime.pathfinder
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import sample_app.runtime.test_procedure
        >>> cc = checkmate.runtime.communication.Communication
        >>> _class = sample_app.application.TestData
        >>> runs = checkmate.paths_finder.RunCollection(_class)
        >>> r = checkmate.runtime._runtime.Runtime(_class, cc)
        >>> box = checkmate.sandbox.Sandbox(_class)
        >>> ex1 = sample_app.exchanges.AC()
        >>> ex1.origin_destination('C2', 'C1')
        >>> box.generate([ex1])
        >>> app = box.application
        >>> app.components['C3'].states[0].value
        'True'
        >>> checkmate.runtime.registry.global_registry.registerUtility(app, checkmate.application.IApplication)
        >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> generator = checkmate.runtime.pathfinder.get_path_from_pathfinder(_class, app, proc.initial)
        >>> for setup in generator:
        ...     print(setup[0].exchanges.root.action, setup[0].compare_states(setup[0].initial))
        RL True
        PP False
    """
    setup = []
    for proc in checkmate.runtime.test_plan.TestProcedureInitialGenerator(application_class):
        setup.append(proc)

    for proc in setup[2:]:
        yield proc
