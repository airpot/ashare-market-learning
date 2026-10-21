# 产品阶段练习入口

先完成共同基础与M15，再选已学的产品轨进入M20。

Tutor: Give the lesson for one step of the selected track at a time. Do not show questions from all six tracks, the full answer table, or all worksheets together. During a temporary term lookup, keep the course cursor without change.

| 轨 | 本轮重点 |
| --- | --- |
| ETF | 估值时点、两项仓位约束、部分成交、未成交与撤单 |
| LOF | 旧NAV、申购暂停、有依据的不交易与条件二级买入 |
| CB | 每张面值与报价分母、转股价值、日期与权益路径 |
| REIT | 项目现金和债务、登记、除息、到账及含分派总收益 |
| MONEY | 资金用途、可取日期、外部费用与短期价差 |
| CLOSED | 有效封闭条款、旧NAV折价、剩余期限与不保证兑现 |

当前步只做一件事：第一步识别并核资料；第二步写计划或有依据地不交易；第三步管理给定委托或事件；第四步对账并复盘。问题与所需数据由[产品练习运行时](../product-practice.md)的 `open` 返回。不要从目录遍历提前读下一包。

每次回答保留自己的原话，写明已知、推断与未知。价格触及不是成交，计划退出不是已成交退出，预计分派不是现金到账。若资料不足，指出具体缺项、阻断的操作与补证动作；只说“不交易”不足以证明理解。

Tutor procedure:

1. Start one track. Keep its run ID in the external learner record.
2. Open only the learner packet for this step. Give the explanation for one short part. Then, wait for the raw response.
3. With `answer`, record the raw response without change. Keep its run, track, and step binding.
4. Show only the step. Give feedback about the misconception that the learner response shows. Record revisions as different records.
5. Only after the feedback for this step, continue to the next step. Keep the aid status `assisted` during all steps.

Before the applicable raw response, do not read these materials:

- Teacher packets
- Full answer templates
- Outcome suffixes
- Full source manifests.

The exercise gate does not replace this instruction or filesystem access controls.
