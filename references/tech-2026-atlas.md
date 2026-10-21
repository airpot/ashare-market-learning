# 2026科技与高波动读图：先观察，再复盘

本图谱为当前主要技术读图材料；2024图谱仅作补充迁移。先从[安全离线入口](../assets/tech-2026/index.html)选一个专题。四组证券为中际旭创、寒武纪、中芯国际、天普股份，各8题，共32题、64张配对SVG。科技业务与高波动是教学分组，没有精确市值排名资格；天普股份须结合发行人风险提示，“妖股”并非官方分类。

全部原图窗口在2026-06-01至09-30内，避开已知寒武纪五月送转及中际旭创十月除息区间。各题观察30根，随后开放5根，价格均为元/股（CNY/share）、量均为股（shares）。这仍是未复权原始坐标；逐项公司行动资格以来源公告补充为准，原始缺口不等于技术破位、经济损失或投资者总收益。Sina原始日线经Tencent的OHLC交叉核对，量换算使用每证券自己的元数据，不能统一乘100。来源文件的公开可访问性不等于再分发许可。

## 授课顺序

1. 核对单位与截止，读开高低收；区分收盘相对开盘的阴阳与相对前收的涨跌。
2. 每次只选一个价量题：自己求此前20根均量（不含当日）与本课日量相对值（V/前20日均量，不是软件盘中量比），练四种价格/相对量组合。
3. 再练实体和影线、局部位置；形态须按数字条件检验，不能只凭外观或故事。
4. 画先前局部上/下沿带；比较越界、回到冻结旧带、失效和条件不满足的替代题。
5. 使用明确给出的全部风险假设，允许等待或跳过；作答后才看同题5根后续，逐项解释是否出现反证。

每张观察页列出六个可选问题。其余问题不是首轮必答项。

Tutor: Select only one question for this learner stage. Give the lesson for one short part. Do its comprehension check. Only after this check gives satisfactory results, continue.

Only at the applicable stage, give all assumptions with their labels. Then, give the question about the calculation of planned loss and position size.

Tutor routing: First, open ONLY one `t26-NN-decision.html` or its decision JSON. Before you open ONLY its matching outcome, keep the raw response without change. For the cutoff for this step, do not load these materials into learner context:

- The teacher manifest
- The generator
- Full source JSON
- Other outcomes.

Outcome HTML/JSON/SVG contains answers and observations after the cutoff. Links give a lesson sequence. They do not prevent access.

After hints, record the exercise with `assisted` status. Do not use these windows as evidence of proficiency without aid:

- Windows that you used previously
- Windows with some of the same observations.

Do not record these windows as market events that occur independently.

Before selection without aid, obey [exposure records](progress.md). When you show an observation, annotation, or outcome, record the full date range that the learner can see. If no applicable window without previous access is available, use the [reserved replay](holdout-replay.md). Unknown history stays unknown. After you record the raw response without change, open only the matching [topic plate](topic-plates.md) for the concept for this step.

## 事后选例算法与边界

从日期范围内枚举每个30根前缀，要求尚有5根后续。价量方向使用 C/前收−1，量比为 V/此前20根量的算术均值；严格涨/跌与量比≥1、<1组成四类，平收不强归类。四组形态题分别使用上影、下影、小实体、吞没条件：长影≥全振幅50%且≥实体2倍；小实体≤振幅15%且振幅>0；吞没须前后开收方向相反，今日实体两端严格跨过前实体，任何一端相等只记临界，影线无需包住。此口径与M08一致。条件只是本课程约定，不是普适预测法。

局部边界取此前10根最高/最低的最早同价日期为锚点，容差±0.5%；不是已证实的多次触碰区。收盘高于上带外缘/低于下带外缘才是越界候选；向上/下整根缺口跨越不准入对应候选，其他公司行动疑点仍须另核。回访题只查此前9根内已成立的非整根跳空上沿越界，冻结当时10根高点带；要求前收在旧带之上，今日高低区间与旧带相交且今日非整根缺口。首次符合的历史锚点优先；不要求今日收回上缘，因此可能失败。

先分配稀缺条件，缺失则明确记为边界核查替代题，绝不充作该形态阳性样本。每证券每题用不同截止；优先全局未用日期，再优先间隔至少3根，再接近8个均匀目标时点，最后按日期。算法只用当时前缀条件与后续长度，不以随后涨跌评分。事后选样与窗口重叠仍造成偏差；32题/64图不代表32/64个独立市场事件，也未回测获利率。每份复盘列实际数字、日期、位置、不同解释、预先可写下的失效线及真实5根后续；图线都是解释，不代表实际委托。

## 专题入口

| 编号 | 中性专题 | 观察截止 | 入口 |
| --- | --- | --- | --- |
| T26-01 | 中际旭创 · 价量观察一 | 2026-07-13 | [先看原图](../assets/tech-2026/t26-01-decision.html) |
| T26-02 | 中际旭创 · 价量观察二 | 2026-07-23 | [先看原图](../assets/tech-2026/t26-02-decision.html) |
| T26-03 | 中际旭创 · 价量观察三 | 2026-07-30 | [先看原图](../assets/tech-2026/t26-03-decision.html) |
| T26-04 | 中际旭创 · 价量观察四 | 2026-08-18 | [先看原图](../assets/tech-2026/t26-04-decision.html) |
| T26-05 | 中际旭创 · 实体与影线 | 2026-08-25 | [先看原图](../assets/tech-2026/t26-05-decision.html) |
| T26-06 | 中际旭创 · 前期边界一 | 2026-08-28 | [先看原图](../assets/tech-2026/t26-06-decision.html) |
| T26-07 | 中际旭创 · 前期边界二 | 2026-09-02 | [先看原图](../assets/tech-2026/t26-07-decision.html) |
| T26-08 | 中际旭创 · 边界与回看 | 2026-09-22 | [先看原图](../assets/tech-2026/t26-08-decision.html) |
| T26-09 | 寒武纪 · 价量观察一 | 2026-07-20 | [先看原图](../assets/tech-2026/t26-09-decision.html) |
| T26-10 | 寒武纪 · 价量观察二 | 2026-07-27 | [先看原图](../assets/tech-2026/t26-10-decision.html) |
| T26-11 | 寒武纪 · 价量观察三 | 2026-08-03 | [先看原图](../assets/tech-2026/t26-11-decision.html) |
| T26-12 | 寒武纪 · 价量观察四 | 2026-08-11 | [先看原图](../assets/tech-2026/t26-12-decision.html) |
| T26-13 | 寒武纪 · 实体与影线 | 2026-08-27 | [先看原图](../assets/tech-2026/t26-13-decision.html) |
| T26-14 | 寒武纪 · 前期边界一 | 2026-09-16 | [先看原图](../assets/tech-2026/t26-14-decision.html) |
| T26-15 | 寒武纪 · 前期边界二 | 2026-08-24 | [先看原图](../assets/tech-2026/t26-15-decision.html) |
| T26-16 | 寒武纪 · 边界与回看 | 2026-09-17 | [先看原图](../assets/tech-2026/t26-16-decision.html) |
| T26-17 | 中芯国际 · 价量观察一 | 2026-07-21 | [先看原图](../assets/tech-2026/t26-17-decision.html) |
| T26-18 | 中芯国际 · 价量观察二 | 2026-07-31 | [先看原图](../assets/tech-2026/t26-18-decision.html) |
| T26-19 | 中芯国际 · 价量观察三 | 2026-07-14 | [先看原图](../assets/tech-2026/t26-19-decision.html) |
| T26-20 | 中芯国际 · 价量观察四 | 2026-08-10 | [先看原图](../assets/tech-2026/t26-20-decision.html) |
| T26-21 | 中芯国际 · 实体与影线 | 2026-09-03 | [先看原图](../assets/tech-2026/t26-21-decision.html) |
| T26-22 | 中芯国际 · 前期边界一 | 2026-08-17 | [先看原图](../assets/tech-2026/t26-22-decision.html) |
| T26-23 | 中芯国际 · 前期边界二 | 2026-09-10 | [先看原图](../assets/tech-2026/t26-23-decision.html) |
| T26-24 | 中芯国际 · 边界与回看 | 2026-08-18 | [先看原图](../assets/tech-2026/t26-24-decision.html) |
| T26-25 | 天普股份 · 价量观察一 | 2026-09-21 | [先看原图](../assets/tech-2026/t26-25-decision.html) |
| T26-26 | 天普股份 · 价量观察二 | 2026-07-24 | [先看原图](../assets/tech-2026/t26-26-decision.html) |
| T26-27 | 天普股份 · 价量观察三 | 2026-07-16 | [先看原图](../assets/tech-2026/t26-27-decision.html) |
| T26-28 | 天普股份 · 价量观察四 | 2026-08-13 | [先看原图](../assets/tech-2026/t26-28-decision.html) |
| T26-29 | 天普股份 · 实体与影线 | 2026-09-08 | [先看原图](../assets/tech-2026/t26-29-decision.html) |
| T26-30 | 天普股份 · 前期边界一 | 2026-08-18 | [先看原图](../assets/tech-2026/t26-30-decision.html) |
| T26-31 | 天普股份 · 前期边界二 | 2026-09-14 | [先看原图](../assets/tech-2026/t26-31-decision.html) |
| T26-32 | 天普股份 · 边界与回看 | 2026-09-01 | [先看原图](../assets/tech-2026/t26-32-decision.html) |

本索引不汇总教师答案。

Builder: From the portable skill directory, use `python -B scripts/tech_2026_atlas.py`.

This task gives SVG. A different rendering step makes PNG files.
