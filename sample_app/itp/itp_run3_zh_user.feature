功能:第三运行PP
    为了能够控制组件C1, C3
    用户需要能切换C1, C3的状态

    场景:通过PP切换C1的状态
        假如组件的状态C1.State的值是__init__(False)
        而且组件的状态C1.AnotherState的值是__init__()
        而且组件的状态C3.Acknowledge的值是__init__(False)
        当组件USER发出信号Action PBPP()
        那么组件的状态C1.State的值变成__init__(True)
        而且组件的状态C1.AnotherState的值变成__init__(None)
        而且组件的状态C3.Acknowledge的值变成__init__(False)