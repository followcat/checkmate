Feature: Always run AP(R)
    In order to control component C1
    User should be able to toggle C1.State

    Scenario: Toggle C1 state with AP(R)
        Given Component state C1.AnotherState at value Q0()
        When Component C2 sends exchange Action AP(R)
        Then Component state C1.AnotherState should change to value Q0(R)
