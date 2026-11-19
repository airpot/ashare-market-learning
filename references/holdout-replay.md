# 连续测评 H01

本题是单独保留的合成训练：桥溪设备不对应真实证券。先核对看过哪些标的、哪些日期；记录不全就如实标未知。每次只领当前一包，把事实、解释、未知、行动与依据写下来。可选择等待，不必为了交卷交易。

收到原答后，教师先判定并解释本次所选问题的回答，再衔接后续学习。你无须重抄正确答案；若主动重答，另存修订，不覆盖原答。本包讲解及有限后续只在相应答题条件满足后开放，不要提前看后包或生成源码。看过示范行情不影响使用不同的保留题，但若 H01 自身也已暴露，只能用来复习。

Tutor route: Before selection, read [progress](progress.md). Use `scripts/holdout_replay.py` with a record in the learner's workspace, in a different location from the skill.

## Select the assessment scope

Before the first packet, record the selected scope and question numbers in the checkpoint. Use actual instruction and response evidence. A route or cursor does not establish M11 instruction.

| Scope | Step 1 questions | Step 2 questions | Step 3 questions |
| --- | --- | --- | --- |
| `price_risk` | 1, 3 | 2, 3 | 1, 2, 3 |
| `chan_structure` | 1, 2, 3 | 1, 2, 3 | 1, 2, 3 |

Use `price_risk` when M11 is not yet taught. Do not show or ask the omitted M11 questions. They are excluded from this attempt; they are neither incorrect nor passed. Before `chan_structure`, teach the missing M11-U01 to U03 concepts with different examples. Do not make Chan necessary for the first-trade-cycle route.

The helper controls steps, exposure and raw-response storage. It does not select questions or score their content. Show only the selected questions, current bars, rules and reports. Save every selected raw answer for this step before `answer` and `reveal`. Use only the matching feedback numbers for the selected scope. Do not score an omitted structure criterion as missing or satisfied. Keep the selected scope with the result; price/risk completion is not evidence of Chan competence.

Keep all exposure events and support ranks for either scope. If this window or its full feedback was seen, do not later use it as an unseen structure assessment. Use another eligible case, or keep the later work assisted.

This helper gives three prefix files. For initial feedback, it does not read a subsequent teacher packet. Before the learner gives an answer, do not read its source or teacher folder. The start operation gives no future prices or outcomes. It gives an attempt ID and support status.

```powershell
python -B <skill>/scripts/holdout_replay.py start --record <workspace>/learning-record.json
python -B <skill>/scripts/holdout_replay.py open --record <workspace>/learning-record.json --run <returned-id> --step 1
python -B <skill>/scripts/holdout_replay.py answer --record <workspace>/learning-record.json --run <returned-id> --step 1 --raw-file <workspace>/raw-01.txt
python -B <skill>/scripts/holdout_replay.py reveal --record <workspace>/learning-record.json --run <returned-id> --step 1
python -B <skill>/scripts/holdout_replay.py feedback --record <workspace>/learning-record.json --run <returned-id> --step 1 --feedback-file <workspace>/feedback-01.txt --evidence "assistant message after H01-01"
```

Replace placeholders with local paths. For `price_risk`, show only the selected JSON questions, rules, reports and raw PNG/SVG. Do not send the unfiltered `open` output or an H01 HTML page. The first two H01 HTML pages contain the excluded structural questions. Keep the uniform `price_risk` restriction for all three steps. After M11 instruction, `chan_structure` can also use the [first HTML page](../assets/holdout-replay/01.html). Keep the selected-step gate for either scope.

`reveal` returns teacher material; it does not record a delivered judgment or explanation. Give feedback for every selected response under [response feedback](lesson-sequence.md#after-response). After the visible message, the tutor records its exact text and message reference with `feedback`. The tutor creates the feedback file. Do not ask the learner to create it, copy a correction or say that they understand. Only then open the next packet. The helper records the tutor's statement of delivery; it cannot verify actual delivery, message quality or understanding.

For an explicit learner decline, use `feedback --declined` with the actual request and its message reference. A requested hint/retry is not completed feedback. Older packet access alone does not clear pending feedback. Recover using the existing raw answer and preserve support/exposure. See [feedback records](progress.md#feedback-records). For step 2:

1. Do `open`.
2. Do `answer`.
3. Do `reveal`.
4. Give visible feedback for the selected responses. Then do `feedback`.

For step 3:

1. Do `open`.
2. Do `answer`.
3. Do `reveal`.
4. Give visible feedback for the selected responses. Then do `feedback`.

Do not change the response file. The helper keeps response text and the course cursor.

Before you give a hint, do `hint` with the same record and attempt ID. For the remaining part of this attempt, support stays `hinted`.

For instruction with figures, show only the PNG for this step, `assets/holdout-replay/NN.png`, in the reply. Use a local image path in Markdown. Use an absolute path for this image. If a PNG is not available, use the SVG with the same basename. These images contain only the raw prefix for this step. Before the sequence opens a step, do not show the image with this step number.

At each step, add other observations to `exposure_history.events`. The runtime does a check of the full reserved interval for the instrument and dates. It does not include events that this attempt makes in the specified sequence. This is the only exception. Thus, its specified previous prefixes and related feedback let the attempt continue.

A previous attempt, alternative case ID, alias for the same instrument or external future exposure prevents independent credit. Unless a person finds the missing history and records it, keep it unknown. The runtime does not complete history automatically. During an attempt, the runtime does not decrease the support rank.

If Python is not available, use the same sequence without the helper:
1. Open only `assets/holdout-replay/01.json`. For `price_risk`, present its selected fields with the raw PNG/SVG, without HTML. Only `chan_structure` can use the HTML alternative after its prerequisites.
2. Record all selected raw answers and the exposure event.
3. Then read only `references/assessment/holdout-replay/01.json`. Present only feedback for the selected scope.
4. Do these steps with 02 and 03 in sequence.
5. Keep different raw responses and date ranges that include their first and last dates.

If an exposure check is not available, set it to unknown. Packets in different files keep the teaching sequence. They do not prevent filesystem access. For the route without the helper, do not give a statement that a computer controls the gate.

H01 is one finite case for transfer. It includes price reading, an M11 connection check with its specified rule, quantity/risk arithmetic, outstanding orders, reports and revision timing. It does not give sufficient information for a conclusion about profitability, learner mastery, high-level Chan qualification or broker execution.

If exposure to the reserve occurred, give a report of the missing evidence for unseen assessment. Continue as assisted practice. Do not change the name of the reserve. Do not erase history.
