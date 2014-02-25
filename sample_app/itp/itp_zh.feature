Feature: 首先运行AC
    为了能够控制组件C1
    用户需要能切换C1的状态

    Scenario: 通过AC切换C1的状态
        Given 组件的状态C1.State的值是M0(True)
        When 组件C2发出信号Action AC()
        Then 组件的状态C1.State的值变成M0(False)

