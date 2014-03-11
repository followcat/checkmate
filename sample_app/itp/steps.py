import fresher


@fresher.Before
def before(sc):
    fresher.scc.array_items = []

@fresher.Given(_("^Component state (?:(\w+).(\w+)) at value ([\w\(\)]+)$"))
def set_initial(component_name, state, value):
    fresher.scc.array_items.append([state, value, 'x'])

@fresher.When(_("^Component (\w+) sends exchange (\w+) ([\w\(\)]+)$"))
def set_incoming(component, exchange, action):
    fresher.scc.array_items.insert(0, [exchange, 'x', action])

@fresher.Then(_("^Component state (?:(\w+).(\w+)) should change to value ([\w\(\)]+)$"))
def set_final(component_name, state, value):
    for i in range(len(fresher.scc.array_items)):
        if fresher.scc.array_items[i][0] == state:
            fresher.scc.array_items[i][2] = value

@fresher.After
def after(sc):
    if fresher.ftc.scenarios is None:
        fresher.ftc.scenarios = []
    fresher.ftc.scenarios.append(fresher.scc.array_items)
