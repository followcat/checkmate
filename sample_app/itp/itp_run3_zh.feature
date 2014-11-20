功能:第三运行PP
    为了能够控制组件C1, C3
    用户需要能切换C1, C3的状态

    场景:通过PP切换C1的状态
        假如组件的状态C1.State的值是State2
        而且组件的状态C1.AnotherState的值是AnotherState2()
        而且组件的状态C3.Acknowledge的值是Acknowledge1
        当组件C2发出信号Action PP()
        那么组件的状态C1.State的值变成State1
        而且组件的状态C1.AnotherState的值变成AnotherState1
        而且组件的状态C3.Acknowledge的值变成Acknowledge1
