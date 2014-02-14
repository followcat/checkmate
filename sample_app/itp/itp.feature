Feature: First run AC
    In order to control component C1
    User should be able to toggle C1.State

    Scenario: Toggle C1 state with AC
        Given Component state C1.State at value M0(True)
        When Component C2 sends exchange Action AC()
        Then Component state C1.State should change to value M0(False)

