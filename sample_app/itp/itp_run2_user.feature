Feature: Second run RL
    In order to control component C3
    User should be able to toggle C3.Acknowledge

    Scenario: Toggle C3 state with RL
        Given Component state C3.Acknowledge at value __init__(True)
        When Component USER sends exchange ExchangeButton PBRL()
        Then Component state C3.Acknowledge should change to value __init__(False)
