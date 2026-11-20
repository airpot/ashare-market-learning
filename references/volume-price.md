# 量价实训：从读图到检验条件

先学 [M06 行情字段](modules/module-06.md)、[M09 区域与突破](modules/module-09.md)与 [M10 量价证据](modules/module-10.md)。本实训分五步。每步先读图，回答一小题，再核对。

读的时候依次问三件事：**成交比平时多多少、价格走了多远、收盘落在什么位置。** 突破、破位和滞涨都需要一条先画好的边界。量柱记录已经成交的数量，不包括所有挂单和撤单。美国股票的[订单簿研究](https://arxiv.org/abs/1011.6402)把最佳买卖档的供需净变化称为订单流不平衡。研究样本里，同等幅度的不平衡在深度较低的盘口对应较大的价格变化。这里借它解释为什么还要看能成交的报价和档位数量；这个结果不能直接拿来预测 A 股涨跌。

| 顺序 | 练习 | 要做到什么 |
| --- | --- | --- |
| 1 | [同图双窗口](exercises/volume-price-window.md) | 区分阴阳、当日涨跌、日相对量与盘中量比 |
| 2 | [三组真图对照](exercises/volume-price-replay.md) | 从量、价格推进和事前位置写出可被推翻的判断 |
| 3 | [价格与成交量条件对照](exercises/volume-price-filter.md) | 只改变一个条件，区分信号、成交和净结果 |
| 4（按品种选做） | [场内产品量价迁移](exercises/volume-price-products.md) | 先补对应机制，再识别还缺净值、份额、正股或业务状态等哪类证据 |
| 5 | 回到[真图练习的 VP07](exercises/volume-price-replay.md#vp07) | 在不看后续的情况下，独立算量、写边界、给出行动或等待理由 |

已学 M12 的学员可做[量、MACD 与背驰](exercises/volume-price-window.md#vp-c)。只熟悉基础量价时先跳过这一题。全部活动按纸面练习记录，不从历史图推定成交或盈利。

第四步的每题先核[产品先备表](exercises/volume-price-products.md#做题前先补哪一课)。未学相应产品机制，可以先完成股票实训，再补课回来；ETF课的进度不代表已经学过可转债、REIT或货币基金。

## Tutor steps

Use [navigation](navigation.md). Show this five-step arrangement when the branch starts. Before a new part, identify its step and selected case without opening later data. Optional product and Chan items do not become prerequisites for every learner. Keep main-course progress separate. Give current-answer feedback before its permitted continuation.

### VP07: Check before you open the data

Use the [exposure check](progress.md). Use sh688981 from 2026-02-24 to 2026-04-01. Include the first and last dates. If a record for this stock has dates that overlap this interval, record `assisted`. If there is no overlap and the history is not complete, record `unknown`. If there is no overlap and the history is complete, record `independent`. Record this result for the attempt. Do not change the history status for this check.

When you show the VP07 decision data, make an exposure event for this display. Record its event ID in this attempt. If the learner gets a hint, record `hinted`.

<a id="vp07-score"></a>

### VP07: Check before you give a result

After you keep the raw response, do the exposure check again. Do this check before you open the outcome or give feedback.

1. Add external exposures from before the raw response. If the dates are unknown, record the history as `unknown`.
2. For this check only, do not include the event with the ID for this attempt's decision display. Include all other events. Keep all events in the history. If you cannot identify this event ID, do not give an independent pass.
3. Keep the higher support rank of the two checks and any hint. Use this order, from lowest to highest: `independent`, `unknown`, `assisted`, `hinted`.
4. Use the [transfer criteria](assessment/volume-price/vp07.md) with this result. If the result is `independent` and the answers are correct for all five criteria, give an independent pass.

### Teach and give feedback

Before step 1, use [lesson sequence](lesson-sequence.md). The route label M10 does not show which explanations the learner received. Teach missing methods with another example before opening a reserved case. Read no answer guide for this preparation.

1. Open the learner page for this case. Show its question and rules. For VP01 to VP07, show [the stock exercise rules](exercises/volume-price-replay.md) for the current group. For VP07, use the first group. For VP07, show only the data up to 2026-03-25. Show only the current decision PNG and table. Use the decision HTML for that table. Record the dates that you show.
2. Keep the raw response without changes. For VP07, do the second exposure check before you open the outcome. For VP-W, VP-C, VP01 to VP07, or a product case, open only its file in `references/assessment/volume-price/`. Use the lower-case case ID as the file name with `.md`. Do not open a different case file. Read the [stock group review](assessment/volume-price-replay.md) only after you keep all seven stock responses.
3. For the first filter sample, show only the signal data first. Keep the signal response. Then show the [fill data](exercises/volume-price-filter-fills.md). Keep the completed account record. Then use the [first answer page](assessment/volume-price-filter.md).
4. Before you open the second sample, get the learner's previous access status for its data or answers. Record `not seen`, `seen`, or `unknown`. Then use the [second sample](exercises/volume-price-filter-later.md). Keep the signal response. Then show its [fill data](exercises/volume-price-filter-later-fills.md). Keep the completed account record. Then use the [second answer page](assessment/volume-price-filter-later.md). Use the same rules for the two samples.

Show images with absolute local paths. Record the dates in each outcome that you show. The lesson sequence does not prevent access to files.
