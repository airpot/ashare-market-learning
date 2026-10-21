# 连续测评 H01

本题是单独保留的合成训练：桥溪设备不对应真实证券。先核对看过哪些标的、哪些日期；记录不全就如实标未知。每次只领当前一包，把事实、解释、未知、行动与依据写下来。可选择等待，不必为了交卷交易。

收到原答后，教师才开放本包讲解及有限后续，再继续下一包。旧答案留存，修订另写；不要提前看后包或生成源码。看过示范行情不影响使用不同的保留题，但若 H01 自身也已暴露，只能用来复习。

Tutor route: Before selection, read [progress](progress.md). Use `scripts/holdout_replay.py` with a record in the learner's workspace, in a different location from the skill.

This helper gives three prefix files. For initial feedback, it does not read a subsequent teacher packet. Before the learner gives an answer, do not read its source or teacher folder. The start operation gives no future prices or outcomes. It gives an attempt ID and support status.

```powershell
python -B <skill>/scripts/holdout_replay.py start --record <workspace>/learning-record.json
python -B <skill>/scripts/holdout_replay.py open --record <workspace>/learning-record.json --run <returned-id> --step 1
python -B <skill>/scripts/holdout_replay.py answer --record <workspace>/learning-record.json --run <returned-id> --step 1 --raw-file <workspace>/raw-01.txt
python -B <skill>/scripts/holdout_replay.py reveal --record <workspace>/learning-record.json --run <returned-id> --step 1
```

Replace placeholders with local paths. Show only the `open` output or its related [first raw chart](../assets/holdout-replay/01.html). For step 2:

1. Do `open`.
2. Do `answer`.
3. Do `reveal`.

For step 3:

1. Do `open`.
2. Do `answer`.
3. Do `reveal`.

Do not change the response file. The helper keeps response text and the course cursor.

Before you give a hint, do `hint` with the same record and attempt ID. For the remaining part of this attempt, support stays `hinted`.

For instruction with figures, show only the PNG for this step, `assets/holdout-replay/NN.png`, in the reply. Use a local image path in Markdown. Use an absolute path for this image. If a PNG is not available, use the SVG with the same basename. These images contain only the raw prefix for this step. Before the sequence opens a step, do not show the image with this step number.

At each step, add other observations to `exposure_history.events`. The runtime does a check of the full reserved interval for the instrument and dates. It does not include events that this attempt makes in the specified sequence. This is the only exception. Thus, its specified previous prefixes and related feedback let the attempt continue.

A previous attempt, alternative case ID, alias for the same instrument or external future exposure prevents independent credit. Unless a person finds the missing history and records it, keep it unknown. The runtime does not complete history automatically. During an attempt, the runtime does not decrease the support rank.

If Python is not available, use the same sequence without the helper:
1. Open only `assets/holdout-replay/01.json` or its HTML.
2. Record the raw response and exposure event.
3. Then read only `references/assessment/holdout-replay/01.json`.
4. Do these steps with 02 and 03 in sequence.
5. Keep different raw responses and date ranges that include their first and last dates.

If an exposure check is not available, set it to unknown. Packets in different files keep the teaching sequence. They do not prevent filesystem access. For the route without the helper, do not give a statement that a computer controls the gate.

H01 is one finite case for transfer. It includes price reading, an M11 connection check with its specified rule, quantity/risk arithmetic, outstanding orders, reports and revision timing. It does not give sufficient information for a conclusion about profitability, learner mastery, high-level Chan qualification or broker execution.

If exposure to the reserve occurred, give a report of the missing evidence for unseen assessment. Continue as assisted practice. Do not change the name of the reserve. Do not erase history.
