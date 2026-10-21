"""Make 2026 technical-reading lessons with specified limits. The script selects lessons after the observations. The script does not use network I/O.

The script reads only the portable renderer in the same directory and chart-data/teacher-2026.json.
It writes assets/tech-2026 and references/tech-2026-atlas.md. It does not change a 2024 file.

Selection uses operands from cutoff prefixes and the available horizon length. It does not use future prices.
Different windows include the same observations. Lesson counts are not counts of independent events.
"""

from copy import deepcopy
from decimal import Decimal as D
from html import escape
import hashlib
import importlib.util
import json
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
START, END = "2026-06-01", "2026-09-30"
WINDOW, HORIZON = 30, 5
SYMBOLS = ("sz300308", "sh688256", "sh688981", "sh605255")
SHAPES = ("upper", "lower", "small", "engulf")
TOPICS = ("价量观察一", "价量观察二", "价量观察三", "价量观察四", "实体与影线", "前期边界一", "前期边界二", "边界与回看")
QUADS = ("up_high", "up_low", "down_high", "down_low")
LABELS = {"up_high": "收盘较前收上涨、量不低于此前20日均量", "up_low": "收盘较前收上涨、量低于此前20日均量",
          "down_high": "收盘较前收下跌、量不低于此前20日均量", "down_low": "收盘较前收下跌、量低于此前20日均量",
          "upper": "长上影条件", "lower": "长下影条件", "small": "小实体条件", "engulf": "相反方向实体吞没条件",
          "breakout": "局部上沿越界候选", "breakdown": "局部下沿越界候选", "retest": "冻结上沿带的回访候选",
          "boundary_review": "边界核查替代题"}
NOTICE = ("真实未复权日线；价格 CNY/share（元/股），成交量 shares（股），Asia/Shanghai。"
          "Sina 为原始 OHLCV；Tencent OHLC 交叉核对，量的换算仅按本证券来源元数据，不采用统一倍数。"
          "本案例只使用2026-06-01至09-30内的观测。个股公司行动仍须结合公告资格核查；"
          "原始缺口、收盘坐标变化不直接表示技术破位或投资者经济损益。"
          "科技业务角色与高波动教学分组不构成市值排名。天普股份仅作高波动观察，须结合发行人风险提示；"
          "“妖股”是市场俗称，并非官方分类。历史挑选有偏差，形态不证明获利模式、资金意图或派发。")
QUESTIONS = [
    "先核对代码、日期、未复权口径与单位。今日收盘相对前收怎样变化？阴阳线与这个方向是否相同？",
    "用今天之前的20根日线求成交量算术均值（排除今天），再求本课日量相对值（V/前20日均量，不是软件盘中量比）；写出价格方向与量的组合。",
    "把实体、上影、下影分别除以全日振幅；与前一日实体比较。单根外形能否支持多种解释？",
    "用此前10根的最高价、最低价作局部边界锚点，并各留±0.5%的教学容差。列出锚点日期；区分接近、穿越、收盘越界。",
    "若想核查回访，先找当时已经成立的上沿越界，再冻结那时的带，勿用今天的边界倒推。先写条件与反证，也可写未满足或跳过。",
    "依下列全部假设，计算每股计划风险和资金/风险双重约束下的教学股数；若开盘跳过假设停止价，为何不能保证风险上限？",
]


def num(value):
    return format(value, "f")


def pct(value):
    return f"{value:.4f}%"


def zone(bars, side):
    key = "high" if side == "resistance" else "low"
    extreme = (max if key == "high" else min)(D(b[key]) for b in bars)
    anchor = next(b for b in bars if D(b[key]) == extreme)
    return dict(anchor_price=num(extreme), anchor_date=anchor["date"],
                low=num(extreme*D(".995")), high=num(extreme*D("1.005")),
                start_date=bars[0]["date"], end_date=bars[-1]["date"])


def measure(bars):
    """Make an analysis of only the supplied prefix. Do not read a source file, suffix, or clock."""
    if len(bars) < WINDOW:
        raise ValueError("A minimum of 30 observed bars is necessary.")
    x, previous = bars[-1], bars[-2]
    o, h, l, c = (D(x[k]) for k in ("open", "high", "low", "close"))
    po, pc = D(previous["open"]), D(previous["close"])
    mean = sum(D(b["volume_shares"]) for b in bars[-21:-1])/20
    if mean <= 0:
        raise ValueError("A prior20 volume mean must be a positive number.")
    ratio, change = D(x["volume_shares"])/mean, (c/pc-1)*100
    body, span = abs(c-o), h-l
    upper, lower = h-max(o, c), min(o, c)-l
    shapes = []
    if span > 0:
        if upper >= span*D(".5") and upper >= 2*body:
            shapes.append("upper")
        if lower >= span*D(".5") and lower >= 2*body:
            shapes.append("lower")
        if body <= span*D(".15"):
            shapes.append("small")
    if (c-o)*(pc-po) < 0 and min(o, c) < min(po, pc) and max(o, c) > max(po, pc):
        shapes.append("engulf")
    resistance, support = zone(bars[-11:-1], "resistance"), zone(bars[-11:-1], "support")
    gap = "up" if l > D(previous["high"]) else "down" if h < D(previous["low"]) else "none"
    retest = None
    # The first anchor uses bars[-20:-10], in the 30-row window that the learner can see.
    for j in range(len(bars)-10, len(bars)-1):
        historical = zone(bars[j-10:j], "resistance")
        if (D(bars[j]["close"]) > D(historical["high"])
                and D(bars[j]["low"]) <= D(bars[j-1]["high"])
                and pc > D(historical["high"]) and l <= D(historical["high"])
                and h >= D(historical["low"]) and gap == "none"):
            retest = dict(historical, break_date=bars[j]["date"], break_close=bars[j]["close"])
            break
    return dict(prior20_mean_volume=num(mean), volume_ratio=num(ratio), return_pct=num(change),
                open_return_pct=num((c/o-1)*100), quad=("up" if change > 0 else "down" if change < 0 else "flat") + ("_high" if ratio >= 1 else "_low"),
                body=num(body), span=num(span), upper_wick=num(upper), lower_wick=num(lower),
                body_fraction=num(body/span) if span else "0", upper_fraction=num(upper/span) if span else "0",
                lower_fraction=num(lower/span) if span else "0", shapes=shapes, full_gap=gap,
                resistance=resistance, support=support,
                breakout=c > D(resistance["high"]) and gap != "up",
                breakdown=c < D(support["low"]) and gap != "down", retest=retest,
                prior20_start=bars[-21]["date"], prior20_end=previous["date"])


def matches(metrics, condition):
    if condition in QUADS:
        return metrics["quad"] == condition
    if condition in SHAPES:
        return condition in metrics["shapes"]
    if condition == "boundary_review":
        return True
    return bool(metrics[condition])


def risk(bars):
    entry = D(bars[-1]["close"])
    stop = entry*D(".97")
    shares = min(int(D(1000)/(entry-stop)/100)*100, int(D(100000)/entry/100)*100)
    premises = dict(capital_cny="100000", risk_budget_cny="1000", entry_cny_per_share=num(entry),
                    stop_cny_per_share=num(stop), unit_shares=100,
                    assumptions="【全部是假设】现金做多、无杠杆；10万元本金、1000元计划风险预算；入场价仅假设等于观察日收盘，"
                    "停止价假设为其97%；每100股为人为教学单位，非交易规则；忽略费用滑点；"
                    "先假设可在这两个价格成交。另问：若次日开盘仅为假设入场价94%，停止价成交假设会失效。"
                    "这些数不是建议委托；日线不能证明成交、触及先后或可卖出。")
    answer = dict(per_share_planned_risk_cny=num(entry-stop), maximum_hypothetical_shares=shares,
                  planned_capital_cny=num(entry*shares), planned_risk_cny=num((entry-stop)*shares),
                  hypothetical_gap_open_cny_per_share=num(entry*D(".94")),
                  warning="计划风险依赖成交假设，跳空、费用、流动性与制度约束均可能使实际结果不同。不是实际成交或收益。")
    return premises, answer


def explain(case):
    b, m = case["decision_bars"], case["metrics"]
    x, prev, later = b[-1], b[-2], case["outcome_bars"][WINDOW:]
    c = D(x["close"])
    r, s = m["resistance"], m["support"]
    location = (c-D(s["anchor_price"]))/ (D(r["anchor_price"])-D(s["anchor_price"])) * 100 if D(r["anchor_price"]) != D(s["anchor_price"]) else D(0)
    out = [f"观察截止 {case['cutoff']}；以下只在保存原答后开放。选择规则命中：{LABELS[case['selected_condition']]}。",
           f"量价核算：前收 {prev['date']} 为 {prev['close']} 元/股，今日开 {x['open']}、高 {x['high']}、低 {x['low']}、收 {x['close']} 元/股。"
           f"原始收盘较前收变化 {pct(D(m['return_pct']))}，收盘较开盘变化 {pct(D(m['open_return_pct']))}；前者判断涨跌，后者判断阴阳。"
           f"今日量 {x['volume_shares']} 股；此前20根 {m['prior20_start']}—{m['prior20_end']} 的均量 {m['prior20_mean_volume']} 股，"
           f"今日/均量={D(m['volume_ratio']):.6f}，比较线为1，等于1归入不低于均量。归类：{LABELS.get(m['quad'], '平收，非四组合')}。",
           f"形态核算：振幅 H−L={m['span']}，实体 |C−O|={m['body']}，上影 H−max(O,C)={m['upper_wick']}，"
           f"下影 min(O,C)−L={m['lower_wick']} 元/股；实体/振幅={D(m['body_fraction']):.6f}、"
           f"上影/振幅={D(m['upper_fraction']):.6f}、下影/振幅={D(m['lower_fraction']):.6f}。",
           f"位置核算：此前10根 {r['start_date']}—{r['end_date']}，最高价锚点 {r['anchor_date']} {r['anchor_price']}，"
           f"上沿教学带 [{r['low']}, {r['high']}]；最低价锚点 {s['anchor_date']} {s['anchor_price']}，"
           f"下沿教学带 [{s['low']}, {s['high']}] 元/股。今日收盘在两锚点间的线性位置={pct(location)}，可超出0—100%。"
           "容差均为锚点±0.5%，不是统计置信区间，也未证明多次成交密集的压力/支撑。"]
    kind = case["selected_condition"]
    if case["fallback_reason"]:
        out.append(f"替代说明：{case['fallback_reason']} 今日不是被强行标为{LABELS[case['requested_condition']]}。"
                   f"上沿严格比较为 C={x['close']} > {r['high']}：{m['breakout']}（还须排除向上整根跳空）；"
                   f"冻结历史带回访条件为 {bool(m['retest'])}。可只记录靠近、未越过或证据不足。")
    elif kind in SHAPES:
        body, span, u, lo = (D(m[k]) for k in ("body", "span", "upper_wick", "lower_wick"))
        if kind == "upper":
            out.append(f"长上影判据逐项：振幅>0；上影 {num(u)} ≥ 振幅×50%={num(span/2)}，且 ≥ 实体×2={num(body*2)}。只描述外形，不能推断派发或顶部。")
        elif kind == "lower":
            out.append(f"长下影判据逐项：振幅>0；下影 {num(lo)} ≥ 振幅×50%={num(span/2)}，且 ≥ 实体×2={num(body*2)}。只描述外形，不能据此宣布底部或资金承接意图。")
        elif kind == "small":
            out.append(f"小实体判据逐项：振幅>0；实体 {num(body)} ≤ 振幅×15%={num(span*D('.15'))}。实体小不等于振幅小，也不保证方向选择。")
        else:
            oldbody = abs(D(prev["close"])-D(prev["open"]))
            out.append(f"实体吞没判据逐项：前日 {prev['date']} 实体 [{min(D(prev['open']), D(prev['close']))}, {max(D(prev['open']), D(prev['close']))}]，"
                       f"今日实体 [{min(D(x['open']), c)}, {max(D(x['open']), c)}]；开收方向相反、两端严格跨过前实体且今日实体 {m['body']} > 前日 {num(oldbody)}。边界相等只记临界，不要求影线包住，不证明反转。")
    elif kind in ("breakout", "breakdown"):
        upper = kind == "breakout"
        z = r if upper else s
        out.append(f"越界核查：C={x['close']} {'>' if upper else '<'} {'上' if upper else '下'}沿带外缘 {z['high'] if upper else z['low']}；"
                   f"今日低 {x['low']} 与前日高 {prev['high']}、今日高 {x['high']} 与前日低 {prev['low']} 对照，整根跳空标志={m['full_gap']}。"
                   "只授予未复权坐标中的局部候选；发行人行动资格尚未全部核定，不能升级为已确认经济突破。")
    elif kind == "retest":
        z = m["retest"]
        out.append(f"回访逐项：以 {z['start_date']}—{z['end_date']} 的高点 {z['anchor_date']} {z['anchor_price']} 元/股冻结带 "
                   f"[{z['low']}, {z['high']}]；{z['break_date']} 收 {z['break_close']} > 当时带上缘 {z['high']}，且非向上整根跳空。"
                   f"今日之前收盘 {prev['close']} > 冻结上缘；今日低 {x['low']} ≤ 上缘、高 {x['high']} ≥ 下缘，且今日非整根缺口。"
                   "这是从上方回到旧带的区间交叠条件；不要求当日收回上缘，也不能自动叫回踩成功。")
    # At the cutoff, set a specified hypothetical invalidation for the topic.
    z = m["retest"] if kind == "retest" else s if kind == "breakdown" else r
    bearish = kind == "breakdown" or kind in ("down_high", "down_low", "upper") or (kind == "engulf" and c < D(x["open"]))
    if kind in QUADS or kind in SHAPES:
        level = D(x["high"] if bearish else x["low"])
        hypothesis = ("观察日低点以下延续或上冲受限" if bearish else "观察日低点保持并尝试延续或反弹")
        if kind == "small":
            hypothesis = "小实体后低点保持的上行分支（另有下行分支，形态本身不选方向）"
    else:
        level = D(z["high"] if bearish else z["low"])
        hypothesis = "下沿以下延续" if bearish else "收复或维持旧上沿"
    relation = ">" if bearish else "<"
    condition = f"后续收盘 {relation} 冻结阈值 {num(level)} 元/股"
    invalid = [v for v in later if (D(v["close"]) > level if bearish else D(v["close"]) < level)]
    path = "；".join(f"{v['date']} 开 {v['open']}、高 {v['high']}、低 {v['low']}、收 {v['close']}、量 {v['volume_shares']} 股，较观察收盘 {pct((D(v['close'])/c-1)*100)}" for v in later)
    out.append(f"实际随后5根（均为原始坐标变化，不是收益）：{path}。")
    out.append(f"失效与反证：若提出{hypothesis}这个假设，预先固定的反证是 {condition}。"
               + (f"本窗口首次在 {invalid[0]['date']} 收 {invalid[0]['close']} 出现该反证。" if invalid else f"截至 {later[-1]['date']}，这5根中未出现该反证，不能外推永久有效。")
               + "此阈值是读图检验线，不是成交停止指令；量价归类及实体外形的历史事实不会被随后变化推翻，失效的只能是附加方向假设。")
    above = next((v for v in later if D(v["close"]) > D(x["high"])), None)
    below = next((v for v in later if D(v["close"]) < D(x["low"])), None)
    out.append("与观察日整根区间比较：" + (f"随后首次收在当日高 {x['high']} 之上为 {above['date']} 收 {above['close']}；" if above else f"5根中没有收盘高于观察日高 {x['high']}；")
               + (f"首次收在当日低 {x['low']} 之下为 {below['date']} 收 {below['close']}。" if below else f"5根中没有收盘低于观察日低 {x['low']}。")
               + "这区分了日内触及与收盘越界；两边都未越过也可能继续整理，不把单根形态解释为保证反转。")
    if kind in QUADS:
        alternative = ("可能是活跃交易中的上涨，也可能是短期冲高后的波动" if kind == "up_high" else
                       "可能是低成交环境下的上涨，也可能缺少持续跟随" if kind == "up_low" else
                       "可能是剧烈分歧中的下跌，也可能继续走弱" if kind == "down_high" else
                       "可能是交投收缩，也可能是下跌暂缓后再延续")
        out.append(f"替代解释：{alternative}。这些解释需要后续价格与合格事件信息区分，成交量本身不识别买卖双方意图；下一日量比的变化只改变下一日归类。")
    else:
        out.append("替代解释：同一外形可能处于反弹、整理或延续阶段；局部越界也可能重新回带，回访也可能失守。先核对更早背景和公司行动，不把后续结果倒填为当时确定答案。")
    if kind == "boundary_review":
        action = "原定候选未达准入条件，跳过该形态或边界交易假设，只保留数字核查"
    elif invalid:
        action = f"原先方向假设在 {invalid[0]['date']} 已遇反证，纸上撤销该假设并回到等待"
    else:
        action = "只能在纸上继续观察已写出的条件，也可因行动、流动性或执行证据不足而跳过"
    out.append(f"假设行动/跳过：{action}。没有真实委托、成交或推荐；公司行动、涨跌幅状态与可交易性未由本日线核实。")
    a = case["risk_answer"]
    out.append(f"风险题答案（仅用先给假设）：每股计划风险 {a['per_share_planned_risk_cny']} 元；"
               f"100股教学单位向下取整，并同时受本金和预算约束，最多 {a['maximum_hypothetical_shares']} 股，"
               f"假设占用本金 {a['planned_capital_cny']} 元、计划风险 {a['planned_risk_cny']} 元。"
               f"若假设开盘为入场价94%={a['hypothetical_gap_open_cny_per_share']} 元/股，不能保证在97%停止价成交；{a['warning']}")
    return out


def make_cases(packet):
    'The script selects topics after the observations. It gives the same result for the same input. It does not put future prices in rank order.'
    sources = {v["symbol"]: v for v in packet["sources"]}
    series = {v["symbol"]: v for v in packet["series"]}
    cases, global_dates = [], set()
    for stock_index, symbol in enumerate(SYMBOLS):
        s = series[symbol]
        bars = [deepcopy(b) for b in s["bars"] if START <= b["date"] <= END]
        indices = list(range(WINDOW-1, len(bars)-HORIZON))
        measures = {i: measure(bars[i-WINDOW+1:i+1]) for i in indices}
        requests = (*QUADS, SHAPES[stock_index], "breakout", "breakdown", "retest")
        candidates = {slot: [i for i in indices if matches(measures[i], kind)] for slot, kind in enumerate(requests)}
        used, assignments = set(), {}
        # First select the conditions with the smallest number of cases. A missing condition is a specified alternative.
        # If the condition is missing, do not add a positive label. Tie-breaks use only dates.
        for slot in sorted(range(8), key=lambda k: (len(candidates[k]) or len(indices)+1, k)):
            pool = [i for i in candidates[slot] if i not in used]
            missing = not candidates[slot]
            if missing:
                pool = [i for i in indices if i not in used]
            if not pool:
                raise ValueError(f"A different cutoff is not available for {symbol} {requests[slot]}")
            target = indices[0] + (indices[-1]-indices[0]) * slot / 7
            # The first selection priority is dates that other securities do not use. The next priority is cutoffs with sufficient spacing.
            # The next priority is the eight target positions in date sequence. The script does not read the suffix.
            i = min(pool, key=lambda j: (bars[j]["date"] in global_dates,
                    min((abs(j-u) for u in used), default=99) < 3, abs(j-target), bars[j]["date"]))
            used.add(i)
            global_dates.add(bars[i]["date"])
            assignments[slot] = i, missing
        for slot, requested in enumerate(requests):
            i, missing = assignments[slot]
            ident = f"t26-{len(cases)+1:02d}"
            decision, outcome = deepcopy(bars[i-29:i+1]), deepcopy(bars[i-29:i+6])
            premises, answer = risk(decision)
            case = dict(id=ident, symbol=symbol, name=s["name"], slot=slot,
                        title=f"{s['name']} · {TOPICS[slot]}", cutoff=bars[i]["date"],
                        window_start=decision[0]["date"], window_end=outcome[-1]["date"], horizon_bars=HORIZON,
                        requested_condition=requested, selected_condition="boundary_review" if missing else requested,
                        eligible_count=len(candidates[slot]),
                        fallback_reason=f"在既定日期、30根先验窗口和5根后续约束下，未找到满足{LABELS[requested]}全部条件的样本；改为边界核查，不能充作阳性实例。" if missing else "",
                        decision_bars=decision, outcome_bars=outcome, metrics=measures[i],
                        risk_premises=premises, risk_answer=answer, source=deepcopy(sources[symbol]))
            for phase in ("decision", "outcome"):
                for ext in ("svg", "html", "json"):
                    case[f"{phase}_{ext}"] = f"{ident}-{phase}.{ext}"
            case["analysis"] = explain(case)
            cases.append(case)
    return cases


def decision_packet(case):
    """Make a copy of only the permitted fields. Do not include answers, metrics, annotated lines, or the store for future data."""
    return dict(id=case["id"], symbol=case["symbol"], name=case["name"], title=case["title"],
                cutoff=case["cutoff"], bars=deepcopy(case["decision_bars"]),
                price_unit="CNY/share", volume_unit="shares", adjustment="unadjusted",
                timezone="Asia/Shanghai", notice=NOTICE, source=deepcopy(case["source"]),
                questions=list(QUESTIONS), risk_premises=deepcopy(case["risk_premises"]))


def annotations(case):
    m = case["metrics"]
    notes = [dict(kind="zone", low=m[k]["low"], high=m[k]["high"],
                  label=f"先前10根{'上' if k == 'resistance' else '下'}沿带，锚点 {m[k]['anchor_date']}") for k in ("resistance", "support")]
    if case["selected_condition"] == "retest":
        z = m["retest"]
        notes.append(dict(kind="zone", low=z["low"], high=z["high"], label=f"{z['break_date']} 当时冻结的回访带"))
    notes.append(dict(kind="marker", date=case["cutoff"], price=case["decision_bars"][-1]["close"], label="观察截止，不是成交指令"))
    return notes


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def reference(cases):
    rows = "\n".join(f"| {c['id'].upper()} | {c['title']} | {c['cutoff']} | [先看原图](../assets/tech-2026/{c['decision_html']}) |" for c in cases)
    return f"""# 2026科技与高波动读图：先观察，再复盘

本图谱为当前主要技术读图材料；2024图谱仅作补充迁移。先从[安全离线入口](../assets/tech-2026/index.html)选一个专题。四组证券为中际旭创、寒武纪、中芯国际、天普股份，各8题，共32题、64张配对SVG。科技业务与高波动是教学分组，没有精确市值排名资格；天普股份须结合发行人风险提示，“妖股”并非官方分类。

全部原图窗口在2026-06-01至09-30内，避开已知寒武纪五月送转及中际旭创十月除息区间。各题观察30根，随后开放5根，价格均为元/股（CNY/share）、量均为股（shares）。这仍是未复权原始坐标；逐项公司行动资格以来源公告补充为准，原始缺口不等于技术破位、经济损失或投资者总收益。Sina原始日线经Tencent的OHLC交叉核对，量换算使用每证券自己的元数据，不能统一乘100。来源文件的公开可访问性不等于再分发许可。

## 授课顺序

1. 核对单位与截止，读开高低收；区分收盘相对开盘的阴阳与相对前收的涨跌。
2. 每次只选一个价量题：自己求此前20根均量（不含当日）与本课日量相对值（V/前20日均量，不是软件盘中量比），练四种价格/相对量组合。
3. 再练实体和影线、局部位置；形态须按数字条件检验，不能只凭外观或故事。
4. 画先前局部上/下沿带；比较越界、回到冻结旧带、失效和条件不满足的替代题。
5. 使用明确给出的全部风险假设，允许等待或跳过；作答后才看同题5根后续，逐项解释是否出现反证。

每张观察页列出六个可选问题。At the learner stage for this step, select only one question.
Give a short explanation.
Do a check of the learner explanation. Only after this check gives satisfactory results, continue.
The learner can give the first raw response without answers to the other questions.
Before you give a risk calculation task, give all the specified assumptions.
At the applicable stage only, give the risk calculation task.

Tutor routing: First, open only one `t26-NN-decision.html` or its decision JSON.
Before you open its related outcome, keep the raw response without changes.
For the learner context at this cutoff, do not load the teacher manifest, generator, full source JSON, or other outcomes.

Outcome HTML/JSON/SVG contains answers and future observations.
Links give a lesson sequence. They do not prevent file access.

After hints, record the exercise with `assisted` status.
Do not use reused or overlapping windows to show independent mastery.
Do not count reused or overlapping windows as independent market events.

Before selection without prior access, obey [exposure records](progress.md).
When you show an observation, annotation, or outcome, record the full date range that the learner can see.
If no eligible window without prior access is available, use the [reserved replay](holdout-replay.md).
Unknown history stays unknown.
After the raw response without changes, open only the related [topic plate](topic-plates.md) for the topic at this step.

## 事后选例算法与边界

从日期范围内枚举每个30根前缀，要求尚有5根后续。价量方向使用 C/前收−1，量比为 V/此前20根量的算术均值；严格涨/跌与量比≥1、<1组成四类，平收不强归类。四组形态题分别使用上影、下影、小实体、吞没条件：长影≥全振幅50%且≥实体2倍；小实体≤振幅15%且振幅>0；吞没须前后开收方向相反，今日实体两端严格跨过前实体，任何一端相等只记临界，影线无需包住。此口径与M08一致。条件只是本课程约定，不是普适预测法。

局部边界取此前10根最高/最低的最早同价日期为锚点，容差±0.5%；不是已证实的多次触碰区。收盘高于上带外缘/低于下带外缘才是越界候选；向上/下整根缺口跨越不准入对应候选，其他公司行动疑点仍须另核。回访题只查此前9根内已成立的非整根跳空上沿越界，冻结当时10根高点带；要求前收在旧带之上，今日高低区间与旧带相交且今日非整根缺口。首次符合的历史锚点优先；不要求今日收回上缘，因此可能失败。

先分配稀缺条件，缺失则明确记为边界核查替代题，绝不充作该形态阳性样本。每证券每题用不同截止；优先全局未用日期，再优先间隔至少3根，再接近8个均匀目标时点，最后按日期。算法只用当时前缀条件与后续长度，不以随后涨跌评分。事后选样与窗口重叠仍造成偏差；32题/64图不代表32/64个独立市场事件，也未回测获利率。每份复盘列实际数字、日期、位置、不同解释、预先可写下的失效线及真实5根后续；图线都是解释，不代表实际委托。

## 专题入口

| 编号 | 中性专题 | 观察截止 | 入口 |
| --- | --- | --- | --- |
{rows}

本索引不汇总教师答案。

Builder: From the portable skill directory, use `python -B scripts/tech_2026_atlas.py`.

This task makes SVG files. A different rendering step makes PNG files.
"""


def main():
    source = SKILL / "assets/chart-data/teacher-2026.json"
    raw = source.read_bytes()
    cases = make_cases(json.loads(raw))
    renderer_spec = importlib.util.spec_from_file_location("chart_renderer_2026", SKILL / "scripts/chart_atlas.py")
    renderer = importlib.util.module_from_spec(renderer_spec)
    renderer_spec.loader.exec_module(renderer)
    dest = SKILL / "assets/tech-2026"
    for case in cases:
        p = decision_packet(case)
        caption = NOTICE + "\n\n教师按学员当前阶段只选一问；其余问题不是首轮必答项。先讲一小段，确认理解再继续。\n" + "\n".join(f"{i+1}. {q}" for i, q in enumerate(QUESTIONS))
        caption += "\n\n风险题已标明全部假设：\n" + dump(case["risk_premises"])
        page = renderer.render_page(p["bars"], p["title"], caption)
        nav = (f'<nav class="card"><p>先在自己的笔记保存原答；本页不收集输入。</p>'
               f'<a href="{case["outcome_html"]}">仅在作答后：开放同题随后5根与解释</a> · '
               '<a href="index.html">返回专题入口</a></nav>')
        write(dest/case["decision_html"], page.replace("</main>", nav+"</main>"))
        write(dest/case["decision_svg"], renderer.render_svg(p["bars"], p["title"]))
        write(dest/case["decision_json"], dump(p))
        outcome = dict(id=case["id"], teacher_only=True, cutoff=case["cutoff"],
                       title=case["title"]+" · 作答后复盘", bars=case["outcome_bars"],
                       notice=NOTICE, metrics=case["metrics"], analysis=case["analysis"],
                       risk_premises=case["risk_premises"], risk_answer=case["risk_answer"], source=case["source"])
        notes = annotations(case)
        page = renderer.render_page(outcome["bars"], outcome["title"], NOTICE+"\n\n"+"\n\n".join(case["analysis"]), notes)
        detail = (f'<section class="card"><h2>同题专题细图：保存原答后逐层核对</h2>'
                  f'<img src="../topic-plates/{case["id"]}.svg" alt="同题截止内的专题放大与标注" style="width:100%;height:auto">'
                  '<p>细图只用本题截止前数据；每次解释一个标记，与上方随后行情分开。看过讲解记有辅助。</p></section>')
        nav = f'<nav class="card"><a href="{case["decision_html"]}">返回同题原始观察</a> · <a href="index.html">专题入口</a></nav>'
        write(dest/case["outcome_html"], page.replace("</main>", detail+nav+"</main>"))
        write(dest/case["outcome_svg"], renderer.render_svg(outcome["bars"], outcome["title"], notes))
        write(dest/case["outcome_json"], dump(outcome))
    manifest = dict(schema_version=1, teacher_only=True, source="../chart-data/teacher-2026.json",
                    source_sha256=hashlib.sha256(raw).hexdigest(), period=[START, END],
                    decision_bars=WINDOW, horizon_bars=HORIZON, topics=len(cases), svg_count=2*len(cases),
                    unique_symbol_cutoffs=len({(c["symbol"], c["cutoff"]) for c in cases}),
                    independent_events='There is no estimate. Different windows include the same observations. Topic count is not a count of independent events.',
                    notice="TEACHER ONLY: This source contains all answers and future observations. Before the raw response for this case at this cutoff, open only the selected decision packet.", cases=cases)
    write(dest/"teacher-manifest.json", dump(manifest))
    links = "\n".join(f'<li><a href="{c["decision_html"]}">{escape(c["id"].upper()+" · "+c["title"]+" · "+c["cutoff"])}</a></li>' for c in cases)
    write(dest/"index.html", '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
          '<title>2026技术读图 · 先观察</title><style>body{max-width:1000px;margin:32px auto;padding:20px;font:18px/1.8 sans-serif;background:#f6f8fb;color:#24354b}a{color:#245ca6}</style>'
          '<h1>2026技术读图 · 先观察</h1><p>2026为主要技术案例，2024只作补充。先读坐标，再看价量、形态、边界与风险；每次只选一题。'
          '每页问题由教师依当前阶段只选一问，其余不是首轮必答项；先讲一小段，确认理解再继续。'
          '先保存原答，再通过同题页面的明确链接打开复盘。这里没有预载教师答案。</p><p>'+escape(NOTICE)+'</p>'
          '<p>32题采用部分重叠窗口；64张图不代表64个独立事件。每题30根观察，作答后开放5根；纯离线，无脚本、登录、采集或外部依赖。</p><ol>'+links+'</ol></html>')
    write(SKILL/"references/tech-2026-atlas.md", reference(cases))
    print(f"The script made {len(cases)} topics, {len(cases)*2} SVG/HTML/JSON stages. There are {sum(bool(c['fallback_reason']) for c in cases)} specified alternatives.")


if __name__ == "__main__":
    main()
