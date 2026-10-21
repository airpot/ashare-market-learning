"""The script gives M11 observations and offline Chan lessons. The results are the same for the same observed prefix.

This module uses the course convention. It is not a Chan parser for all cases.
The worksheets show inputs for higher structures. They do not give qualification for a segment or a center.

In the portable skill directory, use ``python -B scripts/chan_atlas.py``.
"""

from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
import hashlib
import importlib.util
import json
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]


def price(value):
    """Read a finite positive price. Do not change the input value."""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("The price is incorrect.") from None
    if not number.is_finite() or number <= 0:
        raise ValueError("The price must be a finite positive number.")
    return number


def number(value):
    return format(value, "f").rstrip("0").rstrip(".") if "." in format(value, "f") else str(value)


def prefix(bars, cutoff=None):
    """Make a copy of only observed bars. The analysis does not read suffix prices."""
    if not bars:
        raise ValueError("The bars are empty.")
    cutoff = bars[-1]["date"] if cutoff is None else cutoff
    try:
        if type(cutoff) is not str or date.fromisoformat(cutoff).isoformat() != cutoff:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("The cutoff must be a canonical date.") from None
    dates = [bar["date"] for bar in bars]
    if cutoff not in dates:
        raise ValueError("The cutoff must be in the observations.")
    result = deepcopy(bars[:dates.index(cutoff) + 1])
    previous = ""
    for bar in result:
        day = bar["date"]
        if type(day) is not str or date.fromisoformat(day).isoformat() != day or day <= previous:
            raise ValueError("Each date must be after the last date.")
        previous = day
        low, high = price(bar["low"]), price(bar["high"])
        if low > high or not low <= price(bar["open"]) <= high or not low <= price(bar["close"]) <= high:
            raise ValueError("The OHLC range is incorrect.")
    return result


def contains(a, b):
    al, ah, bl, bh = (price(a["low"]), price(a["high"]), price(b["low"]), price(b["high"]))
    return al <= bl <= bh <= ah or bl <= al <= ah <= bh


def direction(a, b):
    if price(b["low"]) > price(a["low"]) and price(b["high"]) > price(a["high"]):
        return "up"
    if price(b["low"]) < price(a["low"]) and price(b["high"]) < price(a["high"]):
        return "down"
    return None


def decontain(bars):
    groups, unresolved = [], False
    for i, bar in enumerate(bars):
        group = dict(low=number(price(bar["low"])), high=number(price(bar["high"])),
                     source_indices=[i], first_date=bar["date"], last_date=bar["date"],
                     high_date=bar["date"], low_date=bar["date"], formed_at=bar["date"],
                     merge_direction=None, tentative=False)
        if groups and contains(groups[-1], group):
            trend = direction(groups[-2], groups[-1]) if len(groups) >= 2 else None
            if trend is None or unresolved:
                # Do not start the analysis with future data. Keep the calculation records.
                # Stop admission of structures for this window. The user must supply bars from before this window.
                unresolved = True
                group["unresolved_initial"] = True
                groups.append(group)
                continue
            target = groups[-1]
            for bound in ("low", "high"):
                old, new = price(target[bound]), price(group[bound])
                replace = new > old if trend == "up" else new < old
                if replace:
                    target[bound] = number(new)
                    target[bound + "_date"] = bar["date"]
            target["source_indices"].append(i)
            target["last_date"] = target["formed_at"] = bar["date"]
            target["merge_direction"] = trend
        else:
            groups.append(group)
    for i, group in enumerate(groups):
        group["index"] = i
        group["tentative"] = i == len(groups) - 1
        group["known_at"] = groups[i + 1]["first_date"] if i + 1 < len(groups) else None
    return groups, unresolved


def find_fractals(groups):
    result = []
    for i in range(1, len(groups) - 1):
        left, middle, right = groups[i - 1:i + 2]
        top = all(price(middle[key]) > max(price(left[key]), price(right[key])) for key in ("low", "high"))
        bottom = all(price(middle[key]) < min(price(left[key]), price(right[key])) for key in ("low", "high"))
        if not (top or bottom):
            continue
        bound = "high" if top else "low"
        result.append(dict(kind="top" if top else "bottom", center=i, span=[i - 1, i, i + 1],
                           price=middle[bound], date=middle[bound + "_date"],
                           formed_at=right["first_date"], right_group_updated_at=right["last_date"],
                           known_at=right["known_at"],
                           formation_source_indices=left["source_indices"] + middle["source_indices"] + right["source_indices"][:1],
                           source_indices=[j for g in (left, middle, right) for j in g["source_indices"]],
                           state="provisional_right_group" if right["tentative"] else "confirmed_at_cutoff"))
    return result


def stroke_reason(a, b, groups):
    if a["kind"] == b["kind"]:
        return "same_kind"
    if b["center"] - a["center"] < 4:
        return "spacing"
    span = groups[a["center"]:b["center"] + 1]
    bottom, top = (a, b) if a["kind"] == "bottom" else (b, a)
    if (price(bottom["price"]) >= price(top["price"]) or
            price(bottom["price"]) != min(price(g["low"]) for g in span) or
            price(top["price"]) != max(price(g["high"]) for g in span)):
        return "range_coverage"
    return None


def select_strokes(fractals, groups):
    endpoints, rejected, revisions = [], [], []
    for point in fractals:
        if not endpoints:
            endpoints.append(point)
            continue
        last = endpoints[-1]
        if point["kind"] == last["kind"]:
            p, q = price(point["price"]), price(last["price"])
            better = p > q if point["kind"] == "top" else p < q
            if better and (len(endpoints) < 2 or stroke_reason(endpoints[-2], point, groups) is None):
                revisions.append(dict(old=last, new=point, reason="same_kind_more_extreme",
                                      known_at=point["formed_at"],
                                      observed_at=point["formed_at"],
                                      endpoint_confirmed_at=point["known_at"]))
                endpoints[-1] = point
            else:
                reason = ("equal_keep_earlier" if p == q else
                          "same_kind_update_range_coverage" if better else "same_kind_not_extreme")
                rejected.append(dict(start=last, end=point, reason=reason))
        else:
            reason = stroke_reason(last, point, groups)
            if reason:
                rejected.append(dict(start=last, end=point, reason=reason))
            else:
                endpoints.append(point)
    strokes = []
    for i, (a, b) in enumerate(zip(endpoints, endpoints[1:])):
        tentative = a["state"] != "confirmed_at_cutoff" or b["state"] != "confirmed_at_cutoff"
        state = ("provisional_fractal" if tentative else
                 "latest_endpoint_revisable" if i == len(endpoints) - 2 else "accepted_at_cutoff")
        strokes.append(dict(index=i, start=a, end=b, direction="up" if a["kind"] == "bottom" else "down",
                            low=min((a["price"], b["price"]), key=price),
                            high=max((a["price"], b["price"]), key=price),
                            center_spacing=b["center"] - a["center"], state=state,
                            formed_at=max(a["formed_at"], b["formed_at"]),
                            known_at=max(a["known_at"], b["known_at"]) if not tentative else None))
    return endpoints, strokes, rejected, revisions


def _analyze_observed(observed):
    """Calculate one snapshot. The caller did the validation of its observed prefix."""
    groups, unresolved = decontain(observed)
    fractals = [] if unresolved else find_fractals(groups)
    endpoints, strokes, rejected, revisions = select_strokes(fractals, groups)
    tail = None
    if not unresolved and len(groups) > 1:
        trend = direction(groups[-2], groups[-1])
        if trend:
            bound = "high" if trend == "up" else "low"
            tail = dict(kind="top" if trend == "up" else "bottom", center=len(groups) - 1,
                        price=groups[-1][bound], date=groups[-1][bound + "_date"],
                        formed_at=groups[-1]["formed_at"], known_at=None, state="missing_right_group")
    return dict(cutoff=observed[-1]["date"], groups=groups, unresolved_initial=unresolved,
                fractals=fractals, endpoints=endpoints, strokes=strokes,
                rejections=rejected, revisions=revisions, tail_candidate=tail)


def analyze(bars, cutoff=None):
    """Keep the initial revision observation and the subsequent endpoint confirmation as different events.

    Do the analysis again for only observed prefixes to find the date of each revision event.
    The formation metadata of the last fractal does not show when the analysis first accepted the revision at a previous cutoff.
    The event key keeps the previous extrema and the new extrema.
    """
    observed = prefix(bars, cutoff)
    state = _analyze_observed(observed)
    def identity(revision):
        return tuple(revision[side][key] for side in ("old", "new")
                     for key in ("kind", "date", "price"))
    remaining = {identity(r) for r in state["revisions"]}
    first = {}
    for count in range(1, len(observed) + 1):
        if not remaining:
            break
        earlier = state if count == len(observed) else _analyze_observed(observed[:count])
        for revision in earlier["revisions"]:
            key = identity(revision)
            if key in remaining:
                first[key] = observed[count - 1]["date"]
                remaining.remove(key)
    for revision in state["revisions"]:
        revision["known_at"] = revision["observed_at"] = first[identity(revision)]
    return state


def higher_worksheet(state):
    """Show the inputs before the conclusions. Do not accept strokes as B0.

    The windows are hypotheses. They are not a recognizer for completed segments.
    The worksheet includes arithmetic for the first feature relation and gap to show the missing qualification records.
    The flags for segments and centers at each recursive level stay false.
    """
    strokes = state["strokes"]
    windows = []
    for start in range(max(0, len(strokes) - 2)):
        selected = strokes[start:start + 3]
        low = max(price(s["low"]) for s in selected)
        high = min(price(s["high"]) for s in selected)
        if low < high:
            windows.append(dict(stroke_indices=[s["index"] for s in selected],
                                low=number(low), high=number(high),
                                all_fractals_stable=all(s["state"] != "provisional_fractal" for s in selected)))
    hypotheses = []
    for start in range(len(strokes)):
        first = strokes[start]
        features = [dict(stroke_index=s["index"], low=s["low"], high=s["high"],
                         start_date=s["start"]["date"], end_date=s["end"]["date"], state=s["state"])
                    for s in strokes[start + 1:] if s["direction"] != first["direction"]]
        # Feature inclusion must have a seed and boundary for this feature sequence.
        # Do not merge the raw intervals. Do not show them as intervals after standardization.
        triple = features[:3]
        needs_inclusion = any(contains(a, b) for a, b in zip(triple, triple[1:]))
        relation = "insufficient_feature_elements"
        gap = None
        if len(triple) == 3:
            a, b, c = triple
            top = all(price(b[k]) > max(price(a[k]), price(c[k])) for k in ("low", "high"))
            bottom = all(price(b[k]) < min(price(a[k]), price(c[k])) for k in ("low", "high"))
            relation = "raw_top" if top else "raw_bottom" if bottom else "no_raw_fractal"
            gap = max(price(a["low"]), price(b["low"])) > min(price(a["high"]), price(b["high"]))
        initial_three = strokes[start:start + 3]
        start_overlap = (len(initial_three) == 3 and
                         max(price(s["low"]) for s in initial_three) < min(price(s["high"]) for s in initial_three))
        hypotheses.append(dict(start_stroke=start, direction=first["direction"], features=features,
                               first_three_overlap=start_overlap,
                               raw_relation=relation, feature_gap=gap, feature_inclusion_required=needs_inclusion,
                               qualified=False, reason="left_boundary_and_standardized_feature_completion_not_qualified"))
    return dict(qualified_segment=False, qualified_center=False, qualified_L1=False, qualified_L2=False,
                stroke_overlap_windows=windows, segment_hypotheses=hypotheses,
                prerequisites=['M11 strict strokes with cutoff evidence and revision evidence',
                               "The start boundary of an M11 segment from a previous context with qualification",
                               'Feature inclusion that uses the applicable direction, with source mapping',
                               'A feature fractal without a gap, or a gap plus a reverse feature fractal',
                               "For an L1 center, three B0 segments are necessary. They must be completed and have no other segment between them.",
                               'L1 blocks in the C12-F sealed state before each L2 exercise'])


def render_ranges(groups, title):
    """The processed intervals do not supply open prices, close prices, or volume."""
    width, height, left, top, bottom = 1120, 370, 65, 55, 290
    low = min(float(g["low"]) for g in groups)
    high = max(float(g["high"]) for g in groups)
    spread = high - low or 1
    low, high = low - spread * .08, high + spread * .08
    y = lambda p: top + (high - float(p)) / (high - low) * (bottom - top)
    step = (width - 110) / max(len(groups), 1)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}">',
           '<rect width="100%" height="100%" fill="#f8fafc"/>',
           f'<text x="25" y="28" font-size="18">{escape(title)}</text>',
           '<text x="25" y="350" font-size="13">竖线仅表示去包含后高低区间；无合成开收盘；橙色为末组待定。</text>']
    for tick in range(5):
        p = low + (high - low) * tick / 4
        out.append(f'<text x="3" y="{y(p):.3f}" font-size="11">{p:.2f}</text>')
    for i, group in enumerate(groups):
        x = left + (i + .5) * step
        color = "#c2410c" if group["tentative"] else "#0369a1"
        label = f'P{i}: [{group["low"]},{group["high"]}], raw {group["source_indices"]}; {group["first_date"]}—{group["last_date"]}'
        out.append(f'<line class="processed-range" data-index="{i}" data-low="{group["low"]}" data-high="{group["high"]}" x1="{x:.3f}" x2="{x:.3f}" y1="{y(group["high"]):.3f}" y2="{y(group["low"]):.3f}" stroke="{color}" stroke-width="5"><title>{escape(label)}</title></line>')
        if i % max(1, len(groups) // 12) == 0:
            out.append(f'<text x="{x - 12:.3f}" y="315" font-size="10">P{i}</text>')
    return "".join(out) + "</svg>"


def table(headers, rows):
    return '<table><thead><tr>' + ''.join(f'<th>{escape(str(h))}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(str(v))}</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table>'


def evidence_tables(bars, state):
    groups = state["groups"]
    raw_map = {j: g["index"] for g in groups for j in g["source_indices"]}
    raw = table(["原始号", "日期", "开", "高", "低", "收", "映射到"],
                [[i, b["date"], b["open"], b["high"], b["low"], b["close"], f'P{raw_map[i]}'] for i, b in enumerate(bars)])
    processed = table(["处理号", "原始号", "日期范围", "[低,高]", "低点实际日", "高点实际日", "合并方向", "形成/末次修改", "右边界已知日"],
                      [[f'P{g["index"]}', g["source_indices"], f'{g["first_date"]}—{g["last_date"]}', f'[{g["low"]},{g["high"]}]', g["low_date"], g["high_date"], g["merge_direction"] or "无合并", g["formed_at"], g["known_at"] or "末组仍可吸收"] for g in groups])
    fractals = table(["顶/底", "中心/三组", "极值日/价", "三组最早形成日", "右组末次吸收", "边界已知日", "截止状态"],
                     [[f["kind"], f'P{f["center"]}: {f["span"]}', f'{f["date"]}: {f["price"]}', f["formed_at"], f["right_group_updated_at"], f["known_at"] or "尚无独立后组", f["state"]] for f in state["fractals"]])
    strokes = table(["笔号/方向", "起点日/价", "终点日/价", "处理中心间距", "全范围", "分型证据齐备日", "状态"],
                    [[s["index"], f'{s["start"]["date"]}: {s["start"]["price"]}', f'{s["end"]["date"]}: {s["end"]["price"]}', s["center_spacing"], f'[{s["low"]},{s["high"]}]', s["known_at"] or "分型末组待定", s["direction"] + "; " + s["state"]] for s in state["strokes"]])
    rejects = table(["起点", "候选终点", "中心距", "拒绝原因"], [[r["start"]["date"], r["end"]["date"], r["end"]["center"] - r["start"]["center"], r["reason"]] for r in state["rejections"]])
    revisions = table(["旧端点", "新端点", "修订首次观察日", "新端点分型确认日", "原因"], [[f'{r["old"]["date"]}: {r["old"]["price"]}', f'{r["new"]["date"]}: {r["new"]["price"]}', r["observed_at"], r["endpoint_confirmed_at"] or "尚待确认", r["reason"]] for r in state["revisions"]])
    return '<h2>1 原始 K 线 → 处理区间</h2>' + raw + processed + '<h2>2 分型：发生与知道分列</h2>' + fractals + '<h2>3 严格笔与拒绝项</h2>' + strokes + rejects + '<h2>4 同类极值更新记录</h2>' + revisions


def annotations_for(state, focus):
    notes = []
    if focus in ("inclusion", "mapping"):
        for group in state["groups"]:
            if len(group["source_indices"]) > 1:
                notes.append(dict(kind="line", start_date=group["first_date"], end_date=group["last_date"],
                                  start_price=group["high"], end_price=group["high"],
                                  label=f'P{group["index"]} 合并后高{group["high"]}/低{group["low"]}'))
    elif focus == "fractals":
        for f in state["fractals"]:
            kind = "顶" if f["kind"] == "top" else "底"
            status = "本截止内条件满足" if f["state"] == "confirmed_at_cutoff" else "候选：右侧仍为末组"
            notes.append(dict(kind="marker", date=f["date"], price=f["price"], label=f'{kind} {f["price"]}；{status}'))
        if state["tail_candidate"]:
            t = state["tail_candidate"]
            notes.append(dict(kind="marker", date=t["date"], price=t["price"], label="末组候选，缺右区间"))
    elif focus == "spacing":
        rejects = [r for r in state["rejections"] if r["reason"] == "spacing"]
        for r in rejects[:3]:
            notes.append(dict(kind="line", start_date=r["start"]["date"], start_price=r["start"]["price"],
                              end_date=r["end"]["date"], end_price=r["end"]["price"],
                              label=f'反例：中心距{r["end"]["center"] - r["start"]["center"]}<4，不成笔'))
    else:
        feature_map = {}
        if focus == "feature":
            hypotheses = higher_worksheet(state)["segment_hypotheses"]
            if hypotheses:
                feature_map = {f["stroke_index"]: i + 1 for i, f in enumerate(hypotheses[0]["features"])}
        for s in state["strokes"]:
            status = ("候选：端点分型待定" if s["state"] == "provisional_fractal" else
                      "末端仍可更新" if s["state"] == "latest_endpoint_revisable" else "本截止内接受")
            label = f'笔{s["index"]}：{s["start"]["price"]}→{s["end"]["price"]}；{status}'
            if s["index"] in feature_map:
                label += f'；原始特征E{feature_map[s["index"]]}=[{s["low"]},{s["high"]}]'
            notes.append(dict(kind="line", start_date=s["start"]["date"], start_price=s["start"]["price"],
                              end_date=s["end"]["date"], end_price=s["end"]["price"],
                              label=label))
        if focus in ("revision_before", "revision_after") and state["tail_candidate"]:
            t = state["tail_candidate"]
            notes.append(dict(kind="marker", date=t["date"], price=t["price"], label="缺右组的末端观察，非确认分型"))
        if focus in ("center", "level"):
            windows = higher_worksheet(state)["stroke_overlap_windows"]
            if windows:
                w = windows[0]
                selected = [state["strokes"][i] for i in w["stroke_indices"]]
                for bound, name in (("low", "下沿"), ("high", "上沿")):
                    notes.append(dict(kind="line", start_date=selected[0]["start"]["date"], start_price=w[bound],
                                      end_date=selected[-1]["end"]["date"], end_price=w[bound],
                                      label=f'笔{w["stroke_indices"]}交集{name}{w[bound]}；不是中枢'))
                known = selected[-1]["known_at"]
                if known:
                    notes.append(dict(kind="marker", date=known, price=w["high"], label=f'三笔证据最早齐备{known}；缺B0资格'))
    return notes


STYLE = """body{font:16px/1.75 system-ui,'Microsoft YaHei',sans-serif;color:#172554;background:#f1f5f9;margin:0}main{max-width:1220px;margin:auto;padding:28px}h1{font-size:27px}h2{margin-top:36px;font-size:22px}img,svg{max-width:100%;height:auto;background:white}table{border-collapse:collapse;width:100%;background:white;font-size:13px;display:block;overflow:auto}th,td{border:1px solid #cbd5e1;padding:7px;text-align:left;white-space:nowrap}.notice{padding:16px;background:#fff7ed;border-left:5px solid #ea580c}a{color:#075985}code{overflow-wrap:anywhere}li{margin:8px 0}p{max-width:90ch}"""


def page(title, body):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + escape(title) + '</title><style>' + STYLE + '</style></head><body><main><h1>' + escape(title) + '</h1>' + body + '</main></body></html>\n'


TEACHING = {
    "inclusion": ("原图与逐根包含", "先只看每根最高与最低，别拿红绿、实体替代区间。记录前一对互不包含区间的共同方向，再与当前合成结果比较。合并可能抬高低点或降低高点；原交易仍在原始表。", ["找出一处包含：哪根装进哪根？", "此前最近一对非包含区间向哪边？按该方向算一次合并。"]),
    "mapping": ("处理区间与原始映射", "一条处理竖线可能对应多天；它不是某天真的开收盘。高点日、低点日、最后吸收日可能各不相同。原始号从 0 开始，P 号也从 0 开始，间距只数 P。", ["给一组合并区间列出全部原始号和高低实际日期。", "为什么不能替合成竖线虚构开盘、收盘和成交量？"]),
    "fractals": ("分型的已知与候选", "三组高低都满足严格关系才有分型。右区间虽有日 K 收盘，最后包含组仍可能吸收；本课额外记录后一独立组出现日，保守地区分形成与边界已知。末组缺右侧时只记方向极值候选。所有确认都限本次截止、起点及口径。", ["指出一组三组顶或底，写出极值日与最早可知日。", "最后一组缺右区间吗？哪些标记仍应待定？"]),
    "stroke": ("严格笔：三组之间再留一组", "底中心 a、顶中心 b 的跨度要达到 b−a≥4；两组三组分别占 a−1…a+1 与 b−1…b+1。两者之间至少剩一组，且端点包住中心到中心间全范围；只有顶底交替还不够。最后有效末端仍可被更极端同类分型更新。", ["选一对顶底，列出两组三组及中间独立 P 号。", "端点是否覆盖整笔范围？分型证据何日齐备？"]),
    "spacing": ("分型间距核查", "图中虚线式连线只说明被拒绝的尝试，不是一笔。两个分型中心相差 3 时，三组三组虽然可以不共用，却没有额外独立区间；相差 1 或 2 更不够。原始 K 根数不能补足处理后间距。", ["找一对异类分型，数处理后中心距。", "按本课间距与全范围条件判断是否成笔；列出证据或缺项。"]),
    "revision_before": ("末端修订：第一次观察", "先保存此页答案，再读下一观察包。把当前末端的价格、极值日、右组状态写下来；不能因后来有更高顶就把本页当时的顶价改掉，也不能把候选极值当可成交价。", ["截止此日，末端已知到哪一层？", "记录当前端点与失效条件，暂不打开下一包。"]),
    "revision_after": ("末端修订：第二次观察", "对照自己上一包的记录。只有新资料进入后才能追加更极端同类端点；若已经存在合格异类端点，不能跨过去把多笔拉成一笔。表内保留当时的旧、新端点以及首次可知日期。", ["先记录本包末端，再对照上一包的手写答案。", "变化来自末组吸收、同类极值更新，还是出现合格异类端点？"]),
    "feature": ("特征序列与线段候选", "先列实际笔，再按假设段方向抽反向笔区间。向上段取向下笔；向下段取向上笔。特征区间须另作包含、核对起始三笔重叠和左边界；有缺口还要反向特征分型。本图显示原始特征，不冒称已标准化。", ["假设一段向上或向下，选哪些笔作反向特征？", "列出至少三个特征区间；包含、缺口、反向确认分别核过了吗？"]),
    "center": ("中枢候选的资格清单", "先看三笔的交集，练最大低点与最小高点。即便正宽相交，它也只是笔区间算术；M12 最低教学中枢需要三个连续已确认 B0 线段。这里没有资格记录，故结论停在中枢构造候选与缺证单。", ["选连续三笔，计算共同区间与外围范围。", "这些是笔还是已确认 B0？还缺哪些资格，才能称 L1 中枢？"]),
    "level": ("取样周期与递归级别", "本页始终是日 K，处理区间、笔、B0、L1、L2 是不同结构层次。换成周 K 会改变输入，不能把本页三笔交集改名周线中枢。没有完成 B0 和按 C12-F 封口的 L1，便没有本课程 L2 输入。", ["把日线、处理区间、笔、B0、L1、L2 分别放到取样或结构链中。", "本图能够计算到哪一层？哪些层仅有候选、为什么？"]),
    "bootstrap": ("起始方向核查", "样本开头两根便有包含，而没有此前最近一对互不包含区间。按 M11 应补更早真实资料；本页保留原始区间作占位，停止分型与笔准入，不能拿后面涨跌倒推最初合并方向。", ["样本最初两根是否包含？已有此前方向证据吗？", "说明本包可以做到哪一步；若有缺项，如何处理？"]),
}


def higher_html(higher, state):
    parts = ['<h2>高层构造：先展示输入，再判断资格</h2>',
             '<p>以下均为可复查候选窗口。没有输出完成线段；样本左边界未绑定已确认前段，特征包含与有缺口时的反向确认尚未独立完成。</p>']
    for hyp in higher["segment_hypotheses"][:4]:
        start = hyp["start_stroke"]
        selected = state["strokes"][start:start + 7]
        parts.append(f'<h3>候选起点：笔 {start}，方向 {hyp["direction"]}</h3>')
        parts.append(table(["实际选笔", "方向", "起点→终点", "区间", "状态"],
                           [[s["index"], s["direction"], f'{s["start"]["date"]}/{s["start"]["price"]} → {s["end"]["date"]}/{s["end"]["price"]}', f'[{s["low"]},{s["high"]}]', s["state"]] for s in selected]))
        parts.append(table(["特征来自笔", "日期范围", "实际特征区间", "状态"],
                           [[f["stroke_index"], f'{f["start_date"]}—{f["end_date"]}', f'[{f["low"]},{f["high"]}]', f["state"]] for f in hyp["features"]]))
        parts.append(f'<p>起始三笔正宽重叠：{hyp["first_three_overlap"]}；原始三元素关系：{hyp["raw_relation"]}；存在包含待整理：{hyp["feature_inclusion_required"]}；首两特征缺口：{hyp["feature_gap"]}。这些只是原始区间检查，未宣告标准特征分型或段结束。还缺可绑定的左边界、特征包含处理完成记录；若有缺口，还缺候选端点之后反向标准特征分型的逐笔确认。</p>')
    if not higher["segment_hypotheses"]:
        parts.append('<p>当前严格笔尚不足以列出线段特征序列，继续等待真实资料。</p>')
    parts.append(table(["连续选笔", "最大低点", "最小高点", "资格结论"], [[w["stroke_indices"], w["low"], w["high"], "正宽笔区间交集；不是 B0 中枢"] for w in higher["stroke_overlap_windows"]]))
    parts.append(table(["M12 资格清单", "当前状态"], [
        ["固定日线、未复权、同一股票与截止", "已声明"],
        ["连续严格笔及端点、间距、范围证据", "见上表；末笔仍可修订"],
        ["M11 已确认 B0 线段与左边界", "未取得独立资格证据"],
        ["三个连续已完成 B0 正宽交集 → 最低教学中枢", "缺 B0；不能由三笔替代"],
        ["L1 完成与 C12-F 延迟封口", "未具备输入，未执行"],
        ["三个连续合格已完成 L1 → L2", "未具备输入，未执行"],
        ["背驰、三类买卖点与净收益", "未检验，不由本图推出"]]))
    return ''.join(parts)


def choose_lessons(series):
    'The script selects cases after the observations. The decision payloads contain only prefixes.'
    first = series[0]
    # Find a stable fractal and a pair with spacing that is not sufficient.
    fractal_case = spacing_case = stroke_case = None
    revision_case = None
    for stock in series:
        bars = stock["bars"]
        previous = None
        for n in range(8, len(bars) + 1):
            state = analyze(bars[:n])
            if fractal_case is None and any(f["state"] == "confirmed_at_cutoff" for f in state["fractals"]) and any(f["state"] == "provisional_right_group" for f in state["fractals"]):
                fractal_case = stock, n
            if spacing_case is None and any(r["reason"] == "spacing" for r in state["rejections"]):
                spacing_case = stock, n
            if stroke_case is None and any(s["known_at"] for s in state["strokes"]):
                stroke_case = stock, n
            if previous and revision_case is None and previous["strokes"] and state["strokes"]:
                old, new = previous["strokes"][-1], state["strokes"][-1]
                if (old["start"]["date"] == new["start"]["date"] and
                        old["end"]["kind"] == new["end"]["kind"] and
                        old["end"]["date"] != new["end"]["date"] and state["revisions"]):
                    revision_case = stock, n - 1, n
            previous = state
    if not all((fractal_case, spacing_case, stroke_case, revision_case)):
        raise ValueError("The sample does not supply the examples of lower structures in the request.")
    # Use different symbols and cutoffs for worksheets about higher levels. Do not make copies of views.
    definitions = [
        ("01-inclusion", first, 20, "inclusion"),
        ("02-mapping", series[1], 32, "mapping"),
        ("03-fractals", *fractal_case, "fractals"),
        ("04-strict-stroke", *stroke_case, "stroke"),
        ("05-spacing-check", series[1], 8, "spacing"),
        ("06-endpoint-before", revision_case[0], revision_case[1], "revision_before"),
        ("07-endpoint-after", revision_case[0], revision_case[2], "revision_after"),
        ("08-feature-sequence", first, 96, "feature"),
        ("09-center-qualification", series[1], 110, "center"),
        ("10-interval-level", series[1], 120, "level"),
        ("11-start-direction", series[2], 40, "bootstrap"),
    ]
    return [dict(slug=slug, stock=stock, count=count, focus=focus) for slug, stock, count, focus in definitions]


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def build():
    history_path = SKILL / "assets" / "chart-data" / "teacher-history.json"
    history = json.loads(history_path.read_text(encoding="utf-8"))
    renderer_path = Path(__file__).with_name("chart_atlas.py")
    spec = importlib.util.spec_from_file_location("chart_atlas", renderer_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    output = SKILL / "assets" / "chan-real"
    output.mkdir(parents=True, exist_ok=True)
    manifest = dict(schema_version=1, curation='The script selects cases for lessons after the observations. The cases do not show the frequency in the market.',
                    convention='M11 uses strict strokes. M12 has a B0 floor. This atlas gives no qualification for higher structures.',
                    source_sha256=hashlib.sha256(history_path.read_bytes()).hexdigest(),
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    renderer_sha256=hashlib.sha256(renderer_path.read_bytes()).hexdigest(), lessons=[])
    index_rows = []
    for item in choose_lessons(history["series"]):
        slug, stock, count, focus = (item[k] for k in ("slug", "stock", "count", "focus"))
        bars = deepcopy(stock["bars"][:count])
        cutoff = bars[-1]["date"]
        title, explanation, questions = TEACHING[focus]
        title = f'{stock["name"]}（{stock["symbol"]}）｜{title}'
        state = analyze(bars)
        higher = higher_worksheet(state)
        notes = annotations_for(state, focus)
        payload = dict(symbol=stock["symbol"], name=stock["name"], interval=stock["interval"],
                       adjustment=stock["adjustment"], cutoff=cutoff, bars=bars, questions=questions)
        write_json(output / f"{slug}-decision.json", payload)
        raw_svg = renderer.render_svg(bars, f'{title}｜截止 {cutoff}｜原始日线，未复权')
        (output / f"{slug}-decision.svg").write_text(raw_svg, encoding="utf-8", newline="\n")
        decision = f'<p class="notice">观察包截止 {cutoff} 收盘（Asia/Shanghai），只含截至此日的 {count} 根日 K。真实历史、未复权；样本为事后选题，不用于推断出现频率。先记录答案，记录后只打开同编号独立讲解页。</p>'
        decision += raw_svg + '<h2>先独立观察</h2><ol>' + ''.join(f'<li>{escape(q)}</li>' for q in questions) + '</ol><p>手写或另存：截止、原始号、价格区间、候选/确认、何时知道、仍缺证据。记录后返回目录，按相同编号打开讲解页。离线文件隔离只是教学顺序，不是访问控制。</p>'
        (output / f"{slug}-decision.html").write_text(page(title, decision), encoding="utf-8", newline="\n")
        annotated = renderer.render_svg(bars, f'{title}｜本次截止内的教师标注', notes)
        range_title = '起始方向待补：原始区间占位，不作为去包含结果' if state["unresolved_initial"] else '处理区间映射'
        ranges = render_ranges(state["groups"], f'{range_title}｜截止 {cutoff}')
        (output / f"{slug}-annotated.svg").write_text(annotated, encoding="utf-8", newline="\n")
        (output / f"{slug}-ranges.svg").write_text(ranges, encoding="utf-8", newline="\n")
        # Keep outcomes in their observed prefixes.
        # Before the raw response for case 07, do not show case 07 with the explanation for case 06.
        body = f'<p class="notice">仅本案例教师讲解；先保存同编号观察包答案。观察截止 {cutoff}；本页不扩展至下一观察包，不自动加载其他案例。</p><p>{explanation}</p>'
        if state["unresolved_initial"]:
            body += '<p class="notice">本窗口起始包含缺少方向，以下 P 号仅是原始区间占位映射，并非已经完成去包含的标准区间。分型、严格笔和所有高层结构均停止准入；补更早真实数据后才可重算。</p>'
        body += '<h2>原图与标注图</h2>' + raw_svg + annotated + ranges
        body += '<p>状态译名：confirmed_at_cutoff＝本截止内条件已满足；provisional_right_group＝右侧仍是末包含组；missing_right_group＝缺右组；latest_endpoint_revisable＝末端可被同类极值更新；accepted_at_cutoff＝本次资料内接受，均不表示永久确认。</p>'
        body += evidence_tables(bars, state)
        if focus in ("feature", "center", "level"):
            body += higher_html(higher, state)
        if focus == "revision_before":
            body += '<h2>下一观察包仍须先独立作答</h2><p>已保存本包答案后，可打开 <a href="07-endpoint-after-decision.html">下一份原始观察包</a>。先保存它自己的原图回答，再读它自己的教师讲解；本页不提供下一包结果。</p>'
        else:
            body += '<h2>保留本次记录</h2><p>本页只解释当前截止。后续资料须作为另一观察包先作答，再追加变化；不能回写原来的判断，也不能据此认定极值成交或收益。</p>'
        body += '<h2>定义与数据来源（作答后核对）</h2><p><a href="../../references/modules/module-11.md">M11 包含、分型、严格笔及线段条件</a>；<a href="../../references/modules/module-12.md">M12 B0、L1、C12-F 与 L2 资格</a>；<a href="../chart-data/teacher-history.json">教师完整历史及原始供应商入口</a>；<a href="../../scripts/chan_atlas.py">本图生成与筛选规则</a>。未复权，个股公司行为日历未逐一核准；缺口不能单独证明技术突破或投资损失。公开行情访问不等于再分发许可；仅本地教育复核。</p>'
        (output / f"{slug}-outcome.html").write_text(page(title + "｜本包讲解", body), encoding="utf-8", newline="\n")
        write_json(output / f"{slug}-evidence.json", dict(symbol=stock["symbol"], cutoff=cutoff, annotations=notes,
                                                       analysis=state, higher=higher))
        manifest["lessons"].append(dict(slug=slug, symbol=stock["symbol"], cutoff=cutoff, focus=focus,
                                         raw_count=count, processed_count=len(state["groups"]),
                                         fractal_count=len(state["fractals"]), stroke_count=len(state["strokes"])))
        index_rows.append(f'<tr><td>{escape(title)}</td><td>{cutoff}</td><td><a href="{slug}-decision.html">先看观察包</a></td><td><a href="{slug}-outcome.html">保存本包答案后只看本包讲解</a></td></tr>')
    write_json(output / "teacher-manifest.json", manifest)
    index = '<p>十一幅不同观察重点的真实日线课图。先打开观察包，保存自己的原答；再只打开同编号讲解页。06、07 为先后两个独立包，07 也须单独保存原答后再读它的讲解。观察包不内嵌未来 K 线或教师判断；每包讲解同样不越过本包截止。完整教师历史与清单是另一类来源核验材料，不用于未作答案例的上下文。</p><table><tr><th>课图</th><th>截止</th><th>第一步</th><th>第二步</th></tr>' + ''.join(index_rows) + '</table>'
    (output / "index.html").write_text(page("真实缠论课图：先观察，再核对", index), encoding="utf-8", newline="\n")
    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, ensure_ascii=True, indent=2))
