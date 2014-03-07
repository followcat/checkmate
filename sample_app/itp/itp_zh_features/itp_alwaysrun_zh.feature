Using step definitions from: '../steps'

功能:总是运行AP(R)
    为了能够控制组件C1
    用户需要能切换C1的状态

    场景:通过AP(R)切换C1的状态
        假如组件的状态C1.AnotherState的值是Q0()
        当组件C2发出信号Action AP(R)
        那么组件的状态C1.AnotherState的值变成Q0(R)
