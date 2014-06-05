功能:首先运行AC
    为了能够控制组件C1, C3
    用户需要能切换C1, C3的状态

    场景:通过AC切换C1的状态
        假如组件的状态C1.State的值是__init__(True)
        而且组件的状态C1.AnotherState的值是Q0()
        而且组件的状态C3.Acknowledge的值是__init__(False)
        当组件C2发出信号Action AC()
        那么组件的状态C1.State的值变成__init__(False)
        而且组件的状态C1.AnotherState的值变成Q0()
        而且组件的状态C3.Acknowledge的值变成__init__(True)

