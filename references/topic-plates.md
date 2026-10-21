# 专题图版：先原答，再按题开放

本页只作安全分流，不含逐题答案。原始观察材料与作答步骤仍由[2026主图谱](tech-2026-atlas.md)负责。实体与影线衔接[M07](modules/module-07.md)、[M08](modules/module-08.md)；边界与回访衔接[M09](modules/module-09.md)；量价衔接[M10](modules/module-10.md)。读坐标的方法见[读图手册](chart-reading.md)。

Tutor routing: Before the learner gives the raw response, use only one primary decision packet. First, keep the raw response (`saved_raw_answer`). Then, open only the matching `assets/topic-plates/t26-NN.svg` and `t26-NN.json`. Get NN from the exercise ID for this step. Do not browse the plate directory, teacher manifest, generator, or other plate metadata in learner context. Before the raw response, do not load a plate.

The links and teacher flags give a lesson sequence. They do not prevent access.

Record each view with teacher explanations as access with `assisted` status. Then, continue from the course cursor.

Tutor display: If the matching PNG is available, show it in chat after the raw response. Use the same basename. Use Markdown image syntax with the absolute local path. Get the root of the installed skill and case ID for this step. Do not use a placeholder or relative path. If no PNG is available, show the matching SVG with its absolute local path in the chat.

After the raw response, load only the matching teacher JSON. Before the raw response, do not replace the observation without teacher explanations with the plate that contains teacher explanations.

Each teacher JSON contains `explanation_zh` (values that the image shows and their locations) and `checking_prompt_zh` (one learning question). It also contains sample dates and image source hashes.

Tutor: Read only the explanation for the same question. Give one relation at a time. After the learner gives the raw response, continue. Do not give all topic explanations to the learner together. Do not use charts that the learner saw previously as evidence sufficient to show proficiency with material without previous access.

图版按该题原请求选焦点：实体题采用前一根与目标根共用刻度的双烛放大，四价标签以引线连到真实位置；量价题画此前20根和今日量、固定均量线与窗口；边界题画带、锚点、取样区间与截止；回访题保持旧带不动，分别画突破日、返回日与交叠。若原选例为替代题，只作条件核查，解释为何不足；不把偶然出现的其他形态充作请求主题的正例。

数值与长度均由该题截止前行情重算。价格用元/股；量图显示万股，先由原始股数除以10000；今日不进入此前20根均量。实体像素高度不设人为最小值，小实体或零实体仍按真实差值呈现。标签另设固定栏，避免紧邻四价时互相覆盖。未复权坐标不证明经济突破，区间交叠不证明回踩成功。

Builder: After regeneration of the primary atlas, use `python -B scripts/topic_plates.py` from the skill directory.

The parent can use `build(cases)` with the new `make_cases()` result. The builder writes only this reference and SVG/JSON files in `assets/topic-plates/`. It does not change decision packets or make PNG files. Each JSON records the bars without change, a canonical input hash (`svg_input_sha256`), and the hash of the SVG result (`svg_sha256`). PNG rendering and visual acceptance are different parent checks.
