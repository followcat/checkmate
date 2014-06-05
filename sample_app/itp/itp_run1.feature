Feature: First run AC
    In order to control component C1,C3
    User should be able to toggle C1.State,C1.AnotherState,C3.Acknowledge

    Scenario: Toggle C1 state with AC
        Given Component state C1.State at value __init__(True)
        And Component state C1.AnotherState at value Q0()
        And Component state C3.Acknowledge at value __init__(False)
        When Component C2 sends exchange Action AC()
        Then Component state C1.State should change to value __init__(False)
        And Component state C1.AnotherState should change to value Q0()
        And Component state C3.Acknowledge should change to value __init__(True)

