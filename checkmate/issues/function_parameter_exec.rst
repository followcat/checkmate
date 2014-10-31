
        >>> import checkmate._exec_tools
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> checkmate._exec_tools.method_arguments("Action(R = ActionRequest(['AT2', 'HIGH']))", sample_app.exchanges.IAction)
        ((), {'R': ActionRequest(['AT2', 'HIGH'])})
