# 与完整规则对齐的交易案例

本案例配合[M10完整教学规则](modules/module-10.md#u03-p01)，不是该策略已有效的证明。青禾制造、21日价格、盘口、权限、成交回报和费用均为合成题设。日序S01等不是实际日期，没有真实代码。每股往返费用假定0.02元，与该规则相同；具体成交后的费用单独列明，不重复扣计划预留。

普通[10日观察回放](../assets/replay/frame-00.html)用于练习信息时点、形态和不交易选择。本案例另外提供21个已完成交易日，才能计算M10所需的前后MA20及前五日比较。两者用途不同。

## 分六次开放资料

Tutor: Each time, read only the packet for this step and packets that you opened previously. First, record the raw response. Then, continue with the next packet.

The index that follows identifies only material types. It does not show subsequent prices or results before their time. Packets divide lessons into parts. They do not prevent direct file access to other files.

| 次序 | 当时资料 | 先完成什么 |
| --- | --- | --- |
| 1 | [S21收盘后](../assets/strategy-replay/01-signal.json) | 按既定规则判断背景、触发与缺失信息 |
| 2 | [下一交易日观察窗口](../assets/strategy-replay/02-entry-quote.json) | 事前记录是否申报、数量、价格边界和风险 |
| 3 | [申报后的状态回报](../assets/strategy-replay/03-entry-reports.json) | 核对部分成交、撤单、余量、现金与持仓 |
| 4 | [买入日收盘](../assets/strategy-replay/04-buyday-close.json) | 更新策略状态，记录行动约束 |
| 5 | [下一次合法观察窗口](../assets/strategy-replay/05-exit-quote.json) | 说明持仓管理和所需委托，不预填成交 |
| 6 | [后续成交回报](../assets/strategy-replay/06-exit-report.json) | 对账、计算净结果，分别评价过程与方法证据 |

填写[日志](../assets/templates/journal.md)并保留规则版本。若你的动作不同于题设后续分支，保留原决定，另作分支比较；不把预设回报强加给你没有发出的委托。这个有限案例不是能响应所有订单的模拟撮合系统。

Tutor: Before the learner completes the raw response, do not read the applicable teacher answer. For each packet, use only the packet and previously opened material for feedback. Only after you record raw responses for all six packets, read the full case answer.

This page supplies no teacher answer links.
