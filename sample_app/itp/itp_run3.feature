Feature: Third run PP
    In order to control component C1,C3
    User should be able to toggle C1.State,C1.AnotherState,C3.Acknowledge

    Scenario: Toggle C1 state with PP
        Given Component state C1.State at value M0(False)
        When Component C2 sends exchange Action PP()
        Then Component state C1.State should change to value M0(True)

    Scenario: Toggle C1 state with PP
        Given Component state C1.AnotherState at value Q0()
        When Component C2 sends exchange Action PP()
        Then Component state C1.AnotherState should change to value Q0(None)

    Scenario: Toggle C3 state with PP
        Given Component state C3.Acknowledge at value A0(False)
        When Component C2 sends exchange Action PP()
        Then Component state C3.Acknowledge should change to value A0(False)