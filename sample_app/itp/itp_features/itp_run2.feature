Feature: Second run RL
    In order to control component C3
    User should be able to toggle C3.Acknowledge

    Scenario: Toggle C3 state with RL
        Given Component state C3.Acknowledge at value A0(True)
        When Component C2 sends exchange Action RL()
        Then Component state C3.Acknowledge should change to value A0(False)
