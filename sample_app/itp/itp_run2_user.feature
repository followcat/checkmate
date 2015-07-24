Feature: Second run RL
    In order to control component C3
    User should be able to toggle C3.Acknowledge

    Scenario: USER press Button PBRL
        Given Component state C3.Acknowledge at value Acknowledge2
        When Component USER sends exchange ExchangeButton PBRL()
        Then Component state C3.Acknowledge should change to value Acknowledge1

