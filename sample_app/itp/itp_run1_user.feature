Feature: First run AC
    In order to control component C1,C3
    User should be able to toggle C1.State,C1.AnotherState,C3.Acknowledge

    Scenario: Toggle C1 state with AC
        Given Component state C1.State at value State1
        And Component state C1.AnotherState at value AnotherState2()
        And Component state C3.Acknowledge at value Acknowledge1
        When Component USER sends exchange ExchangeButton PBAC()
        Then Component state C1.State should change to value State2
        And Component state C1.AnotherState should change to value AnotherState2()
        And Component state C3.Acknowledge should change to value Acknowledge2

