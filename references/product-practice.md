# 六类产品的分步纸面练习

本练习以六组虚构材料练完整过程：识别与核查、计划或不交易、委托与事件管理、对账与复盘。适用于先学共同基础、M15、所选产品模块，再进入M20的路径；不要求先学缠论。保留原有课程游标，临时查词后回到当前问题。

ETF、LOF、CB、REIT、MONEY、CLOSED是六条教学轨。MONEY可与ETF等法律包装重叠；封闭状态须看有效条款，不能只看基金名称。所有报价、资格、日期、成交、费用、分派与结算均为明示的合成假设。真实图谱只提供历史观察，OHLC不能证明委托成交。

## 一次只做当前一步

Tutor procedure:

1. Start a run. Record the run ID and product track.
2. Open only the learner packet for this step. Give the lesson for one short part. Give the explanation of units and times. Then, wait for the raw response.
3. Record the raw response without change, with all its parts. An empty entry is not a response.
4. Only after you record the raw response, show feedback for the step. Give feedback about the misconception that the response shows. Record revisions as different records.
5. Only after you complete feedback for this step, continue to the next step.

A new run prevents continuation with the entry for the previous run. The runtime keeps the previous records and raw responses.

Each track has four steps with question IDs `PRODUCT-<TRACK>-01` to `04`. The runtime records each response with a record key: `run_id`, `track`, and `step`. Each record key identifies only one response.

The run can have only one active step at a time. The runtime rejects more than one `open_step`, `answer`, or `reveal` call for a step. If a step is not next in the sequence, the runtime rejects it. Each of these calls must have the run ID for this attempt. Before it reads a packet for feedback, the runtime makes sure that the matching raw response is available. The answer interface reads no teacher material.

The learner directory contains raw responses and feedback. The installed skill keeps its lesson material without change. All six tracks include explanations, hints, or access to material. Thus, record all tracks as `assisted`. Do not give `independent` status.

With unknown access history, do not give `independent` status. Record access to related indices, underlying stocks, and products only as information about this access. This practice is not evidence of assessment without previous access. From this practice, you cannot be sure that the lessons give the necessary results. You also cannot be sure that the investment method gives the necessary results.

## Optional tutor commands

The tutor can complete this practice directly in chat. The commands that follow are optional for the tutor. They are not necessary before the lessons.

Optional tutor CLI: You can use the commands from this skill directory. Use an external learner record. Put the run ID from the command output in subsequent commands. The example uses a directory that the learner can change.

```powershell
python -B scripts/product_practice.py start --record D:/learning/product-record.json --track ETF
python -B scripts/product_practice.py open --record D:/learning/product-record.json --run <run_id> --step 1
python -B scripts/product_practice.py answer --record D:/learning/product-record.json --run <run_id> --step 1 --raw-file D:/learning/answer-01.txt
python -B scripts/product_practice.py reveal --record D:/learning/product-record.json --run <run_id> --step 1
```

`start` can make a new response record or add an attempt to `product_runs` in a record from before this command. Exposure history is the record of price data and other material that the learner saw, with or without answers. The command keeps the course cursor, holdout records, and exposure history without change.

Continue with steps 2, 3, and 4 in sequence. Use one writer for each record.

The CLI rejects paths in these locations:

- This skill
- Standard directories for installed skills
- A different directory with `SKILL.md`.

After a completed operation, the CLI replaces the external record with a temporary file.

Tutor procedure:

- Use `start(record, track)` to make one attempt for this run. Keep the run ID that `start` gives.
- Use `open_step(record, run_id, step)` one time for the learner packet for this step.
- Use `answer(record, run_id, step, raw)` to keep the raw response without change.
- Only after you record the raw response, use `reveal(record, run_id, step)`.
- Before the raw response, read only the learner packet that `open_step` gives for this step.
- Only after you record the matching raw response, read only teacher feedback from `reveal` for this step. Before the learner gives a response, do not load all packets, teacher files, generators, or full worksheets into learner context.
- Keep each response in `assisted` status. Do not give `independent` status from this practice.
- Use the gate as a control for the local lesson sequence.

The gate does not prevent direct file access or record edits.

## Arithmetic helper limits

The arithmetic helper is an optional program for these calculations. External fees are the fee values that you give to the helper as inputs.

| Interface | Input and result | Limit |
| --- | --- | --- |
| `premium(price, nav)` | The helper gives a Decimal percentage. The denominator is the supplied NAV or conversion value. | It does not examine historical availability. Do not identify previous NAV as NAV for the same time. |
| `conversion_value(stock, conversion_price, par)` | Formula: `面值÷转股价×正股价` | This is a value from the formula only. The helper does not calculate conversion results as integer numbers of shares or remaining face value. It does not do or simulate stock receipt or sale. |
| `size_position(cash, budget, entry, stop, lot, buyfee, sellfee)` | The result must obey the cash limit and the planned-loss budget. It rounds the number of units down to an integer multiple of the lot size. | Only long cash purchases are possible. The exit price is more than zero and less than the entry price. For this calculation, external buy/sell fees do not change. The helper does not simulate market fees. |
| `reconcile(opening_cash, events, mark=None)` | The helper calculates the cash flows in sequence. It gives `cash`, integer `quantity`, and Decimal `total_pnl`. | Initial holdings must be zero. If holdings are not zero, the mark price must be more than zero. |

This cash-flow ledger has zero initial holdings, but it can have initial cash. Zero initial cash is applicable only without expenses or with permitted cash receipts before expenses. This does not give permission for credit purchases.

Prices, NAV, face value, and risk budget must have finite values more than zero. Fees and initial cash can be zero. The helper rejects booleans, nonfinite numbers, negative numbers, and incorrect lot values. `lot` and the numbers of units in fills must be positive integers. `100.0` is not an integer order unit.

Cash-flow events are the entries in the supplied list. Keep their initial sequence. Do not use dates to change their sequence. Each `buy` or `sell` contains `quantity`, cash `price` for each unit, and the external-fee field `fee`. A `distribution` contains only the cash receipt value in `amount`.

An optional `event_id` must be a string that is not empty and is different from all other event IDs. Optional dates are record labels. They do not make the helper calculate calendars or settlement. The list position identifies each cash-flow event. Do not add the same report more than one time.

The helper rejects overselling, expenses more than cash before this operation, events with a type that is not permitted, and more fee fields.

External fees accept numeric values, for example, Decimal values. The helper rounds each fee one time to a cent with `ROUND_HALF_UP`. It then uses the fee for the budget and cash flows.

Before you calculate cash flows for partial fills, divide the fee with the rules of the question. The total must be equal to the fee for the full order. Do not subtract the full fee for each partial fill and then subtract the total fee again.

Do not use more rounding rules for prices or distribution quantities. We recommend that you use quantities that you calculated with the question's cash rules. Fund management fees change the price or NAV. Do not give them again in the external-fee field `fee`. The helper includes no tax rate.

First, calculate the total cash quantity for the bonds with `张数×每张面值÷报价分母×报价`. In this exercise, CB face value for each bond and the quote denominator are each `100元`. Thus, the cash price for each bond is equal to its quote. This equation is not applicable to all products.

Do not record conversion, allotment of product units, refunds, redemption, or liquidation as buy/sell events or distribution events.

In [产品工作表](product-worked-sheets.md), do different checks of these items:

- Frozen cash
- Available cash and cash available for withdrawal
- All units, units available for sale, and frozen units
- Settlement
- Registration eligibility
- Distribution receivables
- Stocks from the conversion
- Remaining face value
- Cutoff dates
- Credit amounts with no cash receipt.

From a calculated number without other evidence, you cannot be sure of permission for the operation, the applicable rule, or a fill.

Tutor: Use only the worksheet section for this step. Before you record the applicable raw response, do not open sections with solutions.

## 结束一轮

先核过程和数据，再看净损益；无交易也需依据与补证动作。完成四步仅说明这轮辅助练习走完。真实产品扩展可在原答和本轮反馈结束后选读[产品历史图谱](product-atlas.md)，另记接触范围和截止。

Tutor: Do not put full source data, subsequent observations, or teacher materials into the context for a previous decision.

Before it replaces the record, the optional CLI prepares its JSON output and does an encoding check. For GBK terminals, JSON escapes identify characters that the terminal cannot encode. The decoded feedback is the same.

A subsequent output failure does not cancel the record that the program wrote. After the failure, get only the feedback that the record contains for the same attempt. Do not read teacher packets that you did not open previously. Do not replace the raw response.
