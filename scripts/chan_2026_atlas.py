"""Make eight lessons with the M11 implementation from the review. Each lesson uses only its observed prefix.

The script selects cases after the observations. All lesson windows use June--September prices.
This script gives no qualification for these items:
- A completed segment
- A recursive center
- Satisfactory results from trading
- An action calendar.

From a directory, use this script with Python -B.
"""

from copy import deepcopy
from html import escape
import hashlib
import importlib.util
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
OUTPUT = SKILL / 'assets' / 'chan-2026'
HISTORY = SKILL / 'assets' / 'chart-data' / 'teacher-2026.json'


def load(name):
    spec = importlib.util.spec_from_file_location('chan2026_' + name, Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


chan = load('chan_atlas')
chart = load('chart_atlas')

# The windows have specified limits. They do not show an action adjustment or the frequency in the market.
CASES = [
    dict(slug='01-inclusion', symbol='sz300308', start='2026-06-01', cutoff='2026-06-15', focus='inclusion'),
    dict(slug='02-mapping', symbol='sh688256', start='2026-06-02', cutoff='2026-06-16', focus='mapping'),
    dict(slug='03-fractals', symbol='sh688981', start='2026-06-01', cutoff='2026-06-04', focus='fractals'),
    dict(slug='04-strict-stroke', symbol='sh688981', start='2026-06-01', cutoff='2026-06-29', focus='stroke'),
    dict(slug='05-spacing-check', symbol='sh605255', start='2026-06-01', cutoff='2026-07-07', focus='spacing'),
    dict(slug='06-endpoint-change', symbol='sz300308', start='2026-06-01', cutoff='2026-07-08', focus='revision', previous_cutoff='2026-07-07'),
    dict(slug='07-feature-sequence', symbol='sh688256', start='2026-06-05', cutoff='2026-09-30', focus='feature'),
    dict(slug='08-overlap-level-check', symbol='sh605255', start='2026-06-01', cutoff='2026-09-30', focus='center'),
]

TITLES = dict(inclusion='逐根包含与方向', mapping='高低来源与原始映射',
              fractals='分型发生与边界可知', stroke='严格笔的间距与范围',
              spacing='分型间距核查', revision='末端变化与旧记录',
              feature='真实笔的反向特征序列', center='交集与层级核查')
QUESTIONS = {
    'inclusion': ['找一处包含，列出前一对非包含区间的高低与共同方向。', '逐根算合并区间；下一根应与原始区间还是当前合成区间比较？'],
    'mapping': ['选一组合并区间，列出全部原始号、日期以及高低值各自的来源。', '原始号与 P 号各数什么？何时知道该组不再吸收，能否替它造开收盘？'],
    'fractals': ['分别比较相邻三组的高和低，判定顶底。', '把极值发生日、三组形成日、known_at 分开；最后右组是否仍可能吸收？'],
    'stroke': ['选一对端点，列三组分型及中间独立 P 号，检查中心距是否至少 4。', '端点能否覆盖中心到中心全范围？哪天证据齐备，末端是否还能更新？'],
    'spacing': ['找一对中心距为 3 的异类分型，列各自占用的三个 P 号。', '两组三组之间还有独立区间吗？原始 K 线更多能否补足？'],
    'revision': ['先独立记录本截止的末端，再用原始数据比较前一交易日截止。', '变化是同类极值更新还是合格反向笔？新端点分型的右边界是否已知？'],
    'feature': ['按候选段方向抽反向笔，列前三个特征区间与各笔状态。', '计算包含、首两元素交集或缺口；哪些左边界或标准化资格仍缺？'],
    'center': ['取连续三笔，计算最大低点、最小高点及外围范围。', '输入是笔还是已完成 B0？能否称 L1 中枢，L2 还需哪些输入？'],
}


def window(stock, start, cutoff):
    """Make a copy of only the specified window. Do not read suffix prices to find the direction."""
    if not '2026-06-01' <= start <= cutoff <= '2026-09-30':
        raise ValueError('The structural windows must stay in June--September.')
    rows = [b for b in stock['bars'] if start <= b['date'] <= cutoff]
    if len(rows) < 2 or rows[0]['date'] != start or rows[-1]['date'] != cutoff:
        raise ValueError('The window must have endpoints and an initial pair.')
    rows = chan.prefix(rows, cutoff)
    if chan.contains(rows[0], rows[1]):
        raise ValueError('Set a new start with a pair without containment. Do not use a direction from future data.')
    if chan.analyze(rows)['unresolved_initial']:
        raise ValueError('The initial direction is not known.')
    return rows


def interval(item):
    return f'[{item["low"]},{item["high"]}]'


def when(value):
    return value or '未可知，仍待独立后组'


def point_text(point):
    kind = '顶' if point['kind'] == 'top' else '底'
    return f'{kind} P{point["center"]}，{point["date"]} 的 {point["price"]} 元/股'


def merge_trace(rows, group, prior):
    """Show each operand from the inputs in one selected aggregate group."""
    direction = group['merge_direction']
    op = max if direction == 'up' else min
    indices = group['source_indices']
    low, high = (chan.price(rows[indices[0]][k]) for k in ('low', 'high'))
    steps = []
    for i in indices[1:]:
        raw = rows[i]
        next_low, next_high = op(low, chan.price(raw['low'])), op(high, chan.price(raw['high']))
        steps.append(f'当前 [{chan.number(low)},{chan.number(high)}] 与 raw {i}（{raw["date"]}）{interval(raw)} 合为 [{chan.number(next_low)},{chan.number(next_high)}]')
        low, high = next_low, next_high
    return [
        f'选 P{group["index"]}：此前 P{prior[0]["index"]}{interval(prior[0])} → P{prior[1]["index"]}{interval(prior[1])}，高低共同{ "抬高" if direction == "up" else "降低" }，采用{ "向上取两个较大值" if direction == "up" else "向下取两个较小值" }。',
        '；'.join(steps) + '。每步都与当前合成区间比较，不把包含关系当作可无限传递。',
        f'最终 P{group["index"]}={interval(group)}；高点实际日 {group["high_date"]}，低点实际日 {group["low_date"]}；最后吸收 {group["formed_at"]}，known_at={when(group["known_at"])}。',
    ]


def worked(case, rows, state, higher):
    """Before the full audit tables, give an explanation of a selected calculation from the inputs."""
    focus = case['focus']
    groups = state['groups']
    selected = {}
    if focus in ('inclusion', 'mapping'):
        # If it is possible, we recommend different dates of extrema for the mapping lesson.
        candidates = [g for g in groups if len(g['source_indices']) > 1 and g['known_at']]
        if focus == 'mapping':
            candidates.sort(key=lambda g: (g['high_date'] == g['low_date'], -len(g['source_indices'])))
        g = candidates[0]
        i = g['index']
        if i < 1:
            raise ValueError('The direction must be known before the merge.')
        # The direction seed contains the last group and the first raw member of this group.
        # The merged limits can be different from the limits of the first member.
        first = dict(rows[g['source_indices'][0]], index=i)
        seed = [groups[i - 1], first]
        paragraphs = merge_trace(rows, g, seed)
        selected = dict(group=i, raw_indices=g['source_indices'], direction_seed=[i - 1, g['source_indices'][0]])
        if focus == 'mapping':
            raw_desc = '；'.join(f'raw {j}={rows[j]["date"]}{interval(rows[j])}' for j in g['source_indices'])
            paragraphs.insert(0, f'这条处理竖线映射为 {raw_desc}。{len(g["source_indices"])} 根真实日 K 只形成一个 P 号，中心距只数 P。')
            paragraphs.append('合成高低各有真实来源，但不存在一笔真实交易同时给出这条竖线的开、收、量；原图保留每个交易日的股数成交量。')
        else:
            paragraphs.append('包含整理改变的是结构区间，不能抹去原始最低价或把合并区间解释为当天可成交路径。下一根仍须与最新合成值比较。')
    elif focus == 'fractals':
        stable = next(f for f in state['fractals'] if f['known_at'])
        pending = next(f for f in state['fractals'] if f['known_at'] is None)
        a, b, c = [groups[i] for i in stable['span']]
        relation = '>' if stable['kind'] == 'top' else '<'
        paragraphs = [
            f'选 {point_text(stable)}。相邻三组为 P{a["index"]}{interval(a)}、P{b["index"]}{interval(b)}、P{c["index"]}{interval(c)}；中间低 {b["low"]}{relation}左右 {a["low"]}/{c["low"]}，中间高 {b["high"]}{relation}左右 {a["high"]}/{c["high"]}，两项严格关系都满足。',
            f'极值发生 {stable["date"]}；右组首根到来、三组形成在 {stable["formed_at"]}；再有独立后组时，known_at={stable["known_at"]}，本截止状态 {stable["state"]}。不能把后知的确认回填到极值当日。',
            f'同页 {point_text(pending)} 的三组形成于 {pending["formed_at"]}，但右组仍在窗口末端，known_at={when(pending["known_at"])}，状态 {pending["state"]}。它与前者的可知程度不同；这只是局部关系，尚非买卖指令。',
        ]
        selected = dict(stable_center=stable['center'], provisional_center=pending['center'])
    elif focus in ('stroke', 'spacing'):
        if focus == 'stroke':
            s = next(s for s in state['strokes'] if s['known_at'])
            a, b = s['start'], s['end']
            selected = dict(stroke_index=s['index'])
        else:
            r = next(r for r in state['rejections'] if r['reason'] == 'spacing' and r['end']['center'] - r['start']['center'] == 3)
            a, b = r['start'], r['end']
            selected = dict(rejection_start=a['center'], rejection_end=b['center'])
        gap = list(range(a['center'] + 2, b['center'] - 1))
        span = groups[a['center']:b['center'] + 1]
        low = chan.number(min(chan.price(g['low']) for g in span))
        high = chan.number(max(chan.price(g['high']) for g in span))
        paragraphs = [
            f'所选两端为 {point_text(a)} → {point_text(b)}；三组分别占 {a["span"]} 与 {b["span"]}。处理中心距 {b["center"]}−{a["center"]}={b["center"]-a["center"]}，两组三组之间独立 P 号为 {gap}，共 {len(gap)} 组。',
            f'中心至中心真实处理范围为 [{low},{high}] 元/股；两端局部分型 formed_at 分别为 {a["formed_at"]}、{b["formed_at"]}，known_at 分别为 {when(a["known_at"])}、{when(b["known_at"])}。极值发生日不能替代这两项证据时刻。',
        ]
        if focus == 'stroke':
            paragraphs.append(f'本笔端点覆盖范围 {interval(s)}，中心距≥4，至少留一独立组；分型证据于 {s["known_at"]} 齐备，状态 {s["state"]}。这接受的是本窗口口径内的一笔；最后端点仍可由更极端同类分型更新，尚无已完成 B0 资格。')
        else:
            raw_count = sum(len(g['source_indices']) for g in groups[a['span'][0]:b['span'][-1] + 1])
            paragraphs.append(f'这两组三组虽不共用，却首尾相接，没有额外独立 P 组。覆盖这两分型的原始 K 线共有 {raw_count} 根，仍不能补足处理中心距≥4；拒绝原因 spacing。因此没有这条指定严格笔的 known_at，不能把局部分型知道的日期当成成笔日期。')
    elif focus == 'revision':
        before_rows = chan.prefix(rows, case['previous_cutoff'])
        before = chan.analyze(before_rows)
        old, new = before['strokes'][-1], state['strokes'][-1]
        if not (old['start']['date'] == new['start']['date'] and old['end']['date'] != new['end']['date']):
            raise ValueError('The selected cutoffs do not show an endpoint change.')
        a, b = old['end'], new['end']
        paragraphs = [
            f'只用截至 {case["previous_cutoff"]} 的同起点前缀，末笔从 {point_text(old["start"])} 连到 {point_text(a)}；当时端点三组 formed_at={a["formed_at"]}，known_at={when(old["known_at"])}，状态 {old["state"]}。保留这个旧观察。',
            f'新增至本包 {case["cutoff"]}，同类端点改为 {point_text(b)}。旧价 {a["price"]} → 新价 {b["price"]}，差 {chan.number(chan.price(b["price"])-chan.price(a["price"]))} 元/股；共同起点不变，属于同类更极端更新，未跨过合格反向端点。',
            f'新端点极值发生 {b["date"]}，右组首根使三组形成于 {b["formed_at"]}；本包首次看到这次更新，但新分型 known_at={when(b["known_at"])}，新笔 known_at={when(new["known_at"])}，状态 {new["state"]}。更新事件可见不等于端点已稳定。',
            '本课为一个当前截止包，前一截止由同包较短前缀计算；没有另一个可提前读取的后续答案包。应追加本次观察，不能改写旧记录或按后来极值回填成交。',
        ]
        selected = dict(previous_cutoff=case['previous_cutoff'], previous_stroke=old, current_stroke=new)
    elif focus == 'feature':
        hyp = next(h for h in higher['segment_hypotheses'] if len(h['features']) >= 3)
        features = hyp['features'][:3]
        pairs = [(a, b) for a, b in zip(features, features[1:])]
        paragraphs = [f'仅作假设：从笔 {hyp["start_stroke"]} 开始、方向 {hyp["direction"]}。抽取相反方向的笔作为原始特征：' + '；'.join(f'E{i+1}=笔 {f["stroke_index"]}{interval(f)}（{f["start_date"]}→{f["end_date"]}，{f["state"]}）' for i, f in enumerate(features)) + '。']
        a, b = features[:2]
        low, high = max(chan.price(a['low']), chan.price(b['low'])), min(chan.price(a['high']), chan.price(b['high']))
        paragraphs.append(f'前两元素 max(低)={chan.number(low)}，min(高)={chan.number(high)}，首两特征缺口={hyp["feature_gap"]}；相邻包含分别为 {[chan.contains(a,b) for a,b in pairs]}。前三原始元素关系={hyp["raw_relation"]}，需另作特征包含={hyp["feature_inclusion_required"]}；原始关系不能冒称标准化特征分型。')
        chosen = [state['strokes'][f['stroke_index']] for f in features]
        paragraphs.append('三条输入笔的 known_at 依次为 ' + '；'.join(f'笔 {s["index"]}={when(s["known_at"])}（{s["state"]}）' for s in chosen) + f'。候选起始三笔正宽重叠={hyp["first_three_overlap"]}；以上只是本截止内输入与算术，最末端仍可能更新。')
        paragraphs.append('本窗口左边界没有已确认前段的绑定，特征序列也没有独立完成标准化；若有特征缺口，还须候选界之后的反向标准特征分型。故本例不输出完成线段；不能凭原始元素看起来转向就补造 B0。')
        selected = dict(hypothesis_start=hyp['start_stroke'], feature_strokes=[f['stroke_index'] for f in features])
    else:
        w = higher['stroke_overlap_windows'][0]
        strokes = [state['strokes'][i] for i in w['stroke_indices']]
        outer_low = chan.number(min(chan.price(s['low']) for s in strokes))
        outer_high = chan.number(max(chan.price(s['high']) for s in strokes))
        width = chan.number(chan.price(w['high']) - chan.price(w['low']))
        paragraphs = [
            '选连续三笔：' + '；'.join(f'笔 {s["index"]}{interval(s)}，{s["start"]["date"]}→{s["end"]["date"]}' for s in strokes) + '。它们是笔，尚无 B0 线段资格。',
            f'max(各低)={w["low"]}，min(各高)={w["high"]}，交集 {interval(w)}，宽 {width} 元/股>0；外围范围 [{outer_low},{outer_high}]。外围范围与共同交集不能混用。',
            '三笔 known_at 分别为 ' + '；'.join(f'笔 {s["index"]}={when(s["known_at"])}，状态 {s["state"]}' for s in strokes) + '。这些日期只说明笔所用分型的证据时间，不能充作中枢确认时间。',
            'M12 最低教学中枢要求三个连续已完成 B0 正宽相交；本例缺前段左边界、标准特征及段完成证据，qualified_segment=False、qualified_center=False。故这里只有三笔交集，没有 L1 中枢的 known_at；没有合格 L1 与 C12-F 封口，也不能递归生成 L2。日线只是取样周期。',
        ]
        selected = dict(overlap_strokes=w['stroke_indices'], low=w['low'], high=w['high'], width=width)
    return dict(selected=selected, paragraphs=paragraphs)


def boundary_text(rows):
    a, b = rows[:2]
    direction = '向上' if chan.direction(a, b) == 'up' else '向下'
    return (f'声明起点 {a["date"]}，首对 raw 0={interval(a)}、raw 1（{b["date"]}）={interval(b)}，'
            f'互不包含，高低共同{direction}。只按本窗口启动，未补造更早热身资料，也未绑定此前已确认段；'
            '左边界限制仍保留，首个笔端点不能自动作为真实段起点。')


NOTICE = ('真实未复权日线；价格单位元/股（CNY/share），成交量单位股（shares），横轴按实际交易日顺序。'
          '窗口避开已知价格基准变化，其他公司行为及现金分红日历仍未穷尽核准；'
          '价格差不单独证明技术破位、经济损失或投资总回报。样本按教学需要事后选取，不用于估计模式频率。')
STATUS = ('known_at 是本窗口、给定口径下边界证据齐备之日，空值表示尚待；'
          'confirmed_at_cutoff＝本截止内分型满足；provisional_right_group＝右组尚可吸收；'
          'provisional_fractal＝笔端点仍待；latest_endpoint_revisable＝末端仍可修订；'
          'accepted_at_cutoff＝本次接受。所有状态均非永久确认。')


def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')


def write_json(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def build():
    history = json.loads(HISTORY.read_text(encoding='utf-8'))
    stocks = {s['symbol']: s for s in history['series']}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = dict(schema_version=1,
                    curation='The script selects cases for lessons after the observations. The cases do not show the frequency in the market.',
                    convention='M11 center spacing must be >=4. M12 makes completed B0 necessary. This atlas gives no qualification for segments and centers.',
                    source_sha256=hashlib.sha256(HISTORY.read_bytes()).hexdigest(),
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    analyzer_sha256=hashlib.sha256(Path(chan.__file__).read_bytes()).hexdigest(),
                    renderer_sha256=hashlib.sha256(Path(chart.__file__).read_bytes()).hexdigest(),
                    lessons=[])
    for idx, case in enumerate(CASES):
        stock = stocks[case['symbol']]
        rows = window(stock, case['start'], case['cutoff'])
        state = chan.analyze(rows)
        higher = chan.higher_worksheet(state)
        lesson = worked(case, rows, state, higher)
        focus = 'revision_after' if case['focus'] == 'revision' else case['focus']
        notes = chan.annotations_for(state, focus)
        if case['focus'] == 'revision':
            old = lesson['selected']['previous_stroke']
            notes.append(dict(kind='line', start_date=old['start']['date'], end_date=old['end']['date'],
                              start_price=old['start']['price'], end_price=old['end']['price'],
                              label='前一截止的旧笔端点；保留旧观察'))
        slug = case['slug']
        title = f'{idx+1:02d}｜{stock["name"]}（{stock["symbol"]}）｜{TITLES[case["focus"]]}'
        cutoff = case['cutoff']
        questions = deepcopy(QUESTIONS[case['focus']])
        if 'previous_cutoff' in case:
            questions.insert(0, f'本包内另取截至 {case["previous_cutoff"]} 的较短前缀；先作本包原答，再对照两个截止。')
        payload = dict(symbol=stock['symbol'], name=stock['name'], interval=stock['interval'],
                       timezone='Asia/Shanghai', adjustment=stock['adjustment'],
                       price_unit=stock['price_unit'], volume_unit=stock['volume_unit'],
                       start=case['start'], cutoff=cutoff, bars=rows, questions=questions,
                       left_boundary_limit='The packet has a local seed pair without containment. It gives no qualification for a segment before this window.')
        write_json(OUTPUT / (slug + '-decision.json'), payload)
        raw = chart.render_svg(rows, f'{title}｜截止 {cutoff} 收盘｜原始日线')
        write(OUTPUT / (slug + '-decision.svg'), raw)
        decision = f'<p class="notice">截止 {cutoff} 收盘（Asia/Shanghai），本包 {len(rows)} 根原始 K 线。先保存自己的回答，再只看本包讲解。</p>'
        decision += f'<p>{escape(NOTICE)}</p><p>{escape(boundary_text(rows))}</p>'
        decision += f'<img src="{slug}-decision.svg" alt="本截止原始OHLC与股数成交量">'
        decision += '<h2>本次只答这些问题</h2><ol>' + ''.join(f'<li>{escape(q)}</li>' for q in questions) + '</ol>'
        decision += '<p>另存原答：案例号、截止、raw/P 号、实际区间、候选或确认、何时知道、仍缺什么。文件隔离维护教学顺序，不是访问控制。</p>'
        decision += f'<p><a href="{slug}-decision.json">核对本包原始数值</a>；保存答案后，<a href="{slug}-outcome.html">只打开本包讲解</a>。</p>'
        write(OUTPUT / (slug + '-decision.html'), chan.page(title, decision))
        annotated = chart.render_svg(rows, f'{title}｜仅截至 {cutoff} 的教师标注', notes)
        ranges = chan.render_ranges(state['groups'], f'{title}｜截止 {cutoff}｜处理区间：元/股')
        write(OUTPUT / (slug + '-annotated.svg'), annotated)
        write(OUTPUT / (slug + '-ranges.svg'), ranges)
        evidence = dict(symbol=stock['symbol'], start=case['start'], cutoff=cutoff,
                        source_sha256=manifest['source_sha256'], bars=rows,
                        analysis=state, higher=higher, annotations=notes, worked=lesson,
                        corporate_action_calendar='The calendar does not include all cases. It does not show that a basis-break analysis is correct. It does not show that an investor total-return calculation is correct.')
        write_json(OUTPUT / (slug + '-evidence.json'), evidence)
        body = f'<p class="notice">教师讲解仅截止 {cutoff}；先保留同编号原答，逐小段核对、确认理解后再继续。</p>'
        body += f'<p>{escape(NOTICE)}</p><p>{escape(boundary_text(rows))}</p><h2>这一例实际算出了什么</h2>'
        body += ''.join(f'<p>{escape(p)}</p>' for p in lesson['paragraphs'])
        body += f'<p>{escape(STATUS)}</p><h2>对照原图、标注和处理区间</h2>'
        for suffix, alt in [('-decision.svg', '本包原始日线'), ('-annotated.svg', '本包标注图'), ('-ranges.svg', '处理高低区间，没有合成开收盘或量')]:
            body += f'<img src="{slug}{suffix}" alt="{alt}">'
        body += '<details><summary>展开本截止的逐根映射、分型、笔、拒绝与修订证据</summary>' + chan.evidence_tables(rows, state) + '</details>'
        if case['focus'] in ('feature', 'center'):
            body += '<details><summary>展开高层资格工作表：候选与缺证</summary>' + chan.higher_html(higher, state) + '</details>'
        body += f'<p><a href="{slug}-evidence.json">仅本包计算证据 JSON</a>；<a href="../../references/modules/module-11.md">M11</a>；<a href="../../references/modules/module-12.md">M12</a>。本图不产生已完成线段、中枢或收益证明。</p>'
        if idx + 1 < len(CASES):
            body += f'<p>本包核对完毕后，<a href="{CASES[idx+1]["slug"]}-decision.html">进入下一份原图；仍须先保存下一包自己的回答</a>。</p>'
        else:
            body += '<p>八课结束。保留所有原答与修订记录；未具备资格的高层结构继续待核。</p>'
        write(OUTPUT / (slug + '-outcome.html'), chan.page(title + '｜本包讲解', body))
        manifest['lessons'].append(dict(case, raw_count=len(rows), processed_count=len(state['groups'])))
    write_json(OUTPUT / 'teacher-manifest.json', manifest)
    index = '<p>八课从原始区间逐层观察到资格边界。样本为事后选题，不能估计频率；日线取样不等于递归级别。</p><p>每次只打开一包原图，保存当前原答，再读同包讲解。可按主题选课；每包都须独立作答。</p><p>Do not read teacher cases as a group. Do not load the teacher manifest into the learner context.</p><ol>'
    index += ''.join(f'<li><a href="{case["slug"]}-decision.html">{escape(TITLES[case["focus"]])}</a></li>' for case in CASES)
    index += '</ol>'
    write(OUTPUT / 'index.html', chan.page('2026 缠论图谱｜逐包观察', index))
    return manifest


if __name__ == '__main__':
    result = build()
    print(json.dumps(dict(lessons=len(result['lessons']), output=str(OUTPUT)), ensure_ascii=False))
