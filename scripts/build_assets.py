"""Make the portable SVG figures and the offline replay with the Python standard library.

Use: python -B skills/ashare-market-learning/scripts/build_assets.py

The script does not use these resources:
- The network
- The clock at this time
- A random seed
- A market service
- An optional package.
The teacher data for reproduction is in a different file from frame-00.html. This HTML file is the learner entry.
If there are PNG copies, they are optional derivatives. SVG is the primary source.
"""

import json
from decimal import Decimal
from html import escape
from pathlib import Path

from case_tools import daily_return, size_position, validate_bar, visible_replay


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / 'assets' / 'figures'
REPLAY = ROOT / 'assets' / 'replay'
INK, MUTED, GRID = '#183044', '#4c6273', '#d4dee7'
RED, GREEN, BLUE = '#b83238', '#14745b', '#285f9d'


class SVG:
    def __init__(self, title, description, subtitle='合成教学示意 · 非真实证券或交易所参数 · 图中假设仅用于解释机制', height=760):
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" '
            f'viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            f'<rect width="1200" height="{height}" fill="#f7f9fb"/>',
            '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;'
            f'fill:{INK};font-size:21px}} .small{{font-size:17px;fill:{MUTED}}} '
            '.heading{font-size:32px;font-weight:700} .large{font-size:26px;font-weight:600}</style>',
        ]
        self.text(48, 58, title, cls='heading')
        self.text(48, 96, subtitle, cls='small')

    def text(self, x, y, value, *, cls='', color=None, anchor='start'):
        style = f' style="fill:{color}"' if color else ''
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{style}>{escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color=GRID, width=2, dash=False):
        dashed = ' stroke-dasharray="7 6"' if dash else ''
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{dashed}/>')

    def rect(self, x, y, width, height, fill='#ffffff', stroke=GRID):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="{stroke}"/>')

    def card(self, x, y, width, heading, lines, height=180):
        self.rect(x, y, width, height)
        self.text(x + 20, y + 38, heading, cls='large')
        for row, value in enumerate(lines):
            self.text(x + 20, y + 78 + row * 33, value)

    def arrow(self, x1, y1, x2, y2, color=BLUE):
        self.line(x1, y1, x2, y2, color, 3)
        if y1 == y2:
            d = 1 if x2 > x1 else -1
            self.line(x2 - d * 10, y2 - 6, x2, y2, color, 3)
            self.line(x2 - d * 10, y2 + 6, x2, y2, color, 3)
        else:
            self.line(x2 - 6, y2 - 10, x2, y2, color, 3)
            self.line(x2 + 6, y2 - 10, x2, y2, color, 3)

    def poly(self, points, color=BLUE, width=3):
        coords = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
        self.parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def candle(self, x, bar, y, width=38, tentative=False):
        values = validate_bar(bar)
        o, h, l, c = (float(values[k]) for k in ('open', 'high', 'low', 'close'))
        color = RED if c > o else GREEN if c < o else MUTED
        self.line(x, y(h), x, y(l), color, 3, tentative)
        if c == o:
            self.line(x - width / 2, y(c), x + width / 2, y(c), color, 5, tentative)
        else:
            self.rect(x - width / 2, min(y(o), y(c)), width, max(2, abs(y(o) - y(c))),
                      '#ffffff' if tentative else color, color)

    def finish(self, note):
        self.line(48, self.height - 73, 1152, self.height - 73)
        self.text(48, self.height - 39, note, cls='small')
        return '\n'.join(self.parts + ['</svg>']) + '\n'


def figures():
    output = {}
    s = SVG('市场资金与证券流向', '一级市场募集资金流向公司；二级市场买卖双方交换证券与资金。中介提供通道与服务，二级交易款一般不直接流入公司。')
    s.card(70, 160, 300, '一级市场：发行', ['投资者认购新发行证券', '资金 → 公司（示意）', '公司 → 投资者：证券'], 195)
    s.card(455, 160, 300, '公司与经营', ['资金用于经营等用途', '分红取决于决策与条件', '股东承担经营与价格风险'], 195)
    s.arrow(375, 255, 445, 255)
    s.card(70, 430, 300, '二级市场：买方', ['支付交易款', '取得既有证券'], 165)
    s.card(455, 430, 300, '二级市场：卖方', ['交付既有证券', '取得交易款'], 165)
    s.arrow(375, 480, 445, 480)
    s.text(400, 467, '款', cls='small', anchor='middle')
    s.arrow(445, 552, 375, 552)
    s.text(400, 580, '证券', cls='small', anchor='middle')
    s.card(825, 215, 320, '通道与服务', ['券商：委托入口与服务', '交易所：交易组织与撮合', '登记结算：登记与结算', '具体职责须查现行来源'], 240)
    output['market-flow'] = s.finish('示意省略税费和部分参与者；买到股票不等于公司直接收到这笔二级交易款。')

    s = SVG('从交易意图到成交与结算', '委托依次经过提交、受理、撮合和成交回报，可有拒单、部分成交、撤单待确认；结算及可用状态需另行核对。')
    for x, title, lines in [(50, '1 填写委托', ['价格、数量、方向', '先核对资金与规则']),
                            (430, '2 受理与校验', ['可能拒单或等待', '受理不等于成交']),
                            (810, '3 进入撮合', ['需有可成交对手方', '可能只成交一部分'])]:
        s.card(x, 165, 340, title, lines, 175)
    s.arrow(395, 250, 420, 250)
    s.arrow(775, 250, 800, 250)
    s.arrow(980, 350, 980, 420)
    s.card(810, 430, 340, '4 核对回报', ['实际成交价与数量', '未成交与剩余数量', '费用、结算、可用状态'], 210)
    s.card(50, 430, 665, '撤单有自己的状态', ['撤单申请 → 待确认 → 已撤 / 失败 / 已成交', '申请撤单时，订单仍可能发生撮合。', '以正式回报核对；不凭“按钮已按下”记账。'], 210)
    output['order-flow'] = s.finish('一般状态模型，非完整交易所时序；价格触及、提交委托、受理与成交是不同事实。')

    sample = {'open': '10', 'high': '11', 'low': '9.8', 'close': '10.8'}
    s = SVG('一根 K 线的四个价格', '合成完整日线：开盘10、最高11、最低9.8、收盘10.8元每股。实体由开收盘围成，上下影线延伸至最高最低；OHLC不规定日内先后路径。')
    y = lambda v: 555 - (v - 9.6) * 250
    for price in (9.8, 10, 10.8, 11):
        s.line(145, y(price), 600, y(price))
        s.text(120, y(price) + 7, f'{price:g}', anchor='end')
    s.text(70, 150, '价格（元 / 股）', cls='small')
    s.candle(350, sample, y, 95)
    for value, label in [(11, '最高 11.00：上影线顶端'), (10.8, '收盘 10.80：实体上沿'),
                         (10, '开盘 10.00：实体下沿'), (9.8, '最低 9.80：下影线底端')]:
        s.text(650, y(value) + 7, label)
    s.text(210, 625, '红色＋文字：收盘高于开盘（阳线）')
    output['candle-anatomy'] = s.finish('数据：合成普通完整日线；没有给出日内逐笔顺序，不据此画出唯一价格路径。')

    s = SVG('阳线，也可以是当日下跌', '开10、最高11、最低9.8、收10.8，前收11.2；收盘比开盘上涨8%，但相对前收下跌约3.57%。假设普通交易日且无除权除息等公司行动。',
            '合成普通日线 · 元 / 股 · 无除权除息等公司行动 · 阳阴与涨跌使用不同参照价')
    y = lambda v: 550 - (v - 9.6) * 210
    s.line(120, y(11.2), 570, y(11.2), BLUE, 2, True)
    s.text(110, y(11.2) - 15, '前收 11.20', color=BLUE)
    s.candle(330, sample, y, 80)
    s.text(120, 610, 'O 10.00 / H 11.00 / L 9.80 / C 10.80', cls='small')
    s.card(610, 170, 535, '实体方向：阳线（红）', ['收盘 10.80 > 开盘 10.00', '(10.8 − 10) ÷ 10 = +8.00%'], 175)
    s.card(610, 390, 535, '当日收益：下跌（绿）', ['收盘 10.80 < 前收 11.20', '(10.8 − 11.2) ÷ 11.2 ≈ −3.57%'], 175)
    s.text(610, 625, '日收益返回小数比例，百分数须再乘 100。', cls='small')
    output['candle-return'] = s.finish('实体颜色说明开收盘关系；当日涨跌说明本次收盘与前收盘关系。两者不可互换。')

    s = SVG('形态必须放回上下文', '两个面板包含完全相同的长下影线：开10、最高10.3、最低9、收10.2。在不同先行走势和位置下，不能仅凭这根线推定相同后果。')
    for x, title, prior in [(70, 'A：先行下行', [12, 11.5, 10.8, 10.2]),
                            (645, 'B：先行上行', [8, 8.7, 9.5, 10.2])]:
        s.rect(x, 150, 485, 405)
        s.text(x + 22, 190, title, cls='large')
        local_y = lambda v: 490 - (v - 8) * 60
        s.poly([(x + 45 + i * 70, local_y(v)) for i, v in enumerate(prior)], MUTED)
        s.candle(x + 380, {'open': 10, 'high': 10.3, 'low': 9, 'close': 10.2}, local_y)
        s.text(x + 22, 530, '末根同为阳线：O10 H10.3 L9 C10.2', cls='small')
    s.text(85, 610, '单位：元 / 股；横轴为合成观测序列。折线只连各期收盘，不表示日内路径。')
    s.text(85, 653, '共同待查：位置、先行趋势、量能、后续确认、失败条件与风险预算。')
    output['pattern-context'] = s.finish('状态：只有观察候选，尚未确认后果；任何单根形态都不是普遍买卖指令。')

    s = SVG('趋势与成交量：并列观察', '合成收盘价10、10.2、10.5、10.4、10.8、10.3元；对应成交量100、110、160、90、200、230千股。放量与价格变化只是观察，不证明原因或盈利能力。')
    prices, volumes = [10, 10.2, 10.5, 10.4, 10.8, 10.3], [100, 110, 160, 90, 200, 230]
    s.text(60, 145, '收盘价（元 / 股）', cls='small')
    for price in (10, 10.4, 10.8):
        yy = 340 - (price - 10) * 180
        s.line(165, yy, 1090, yy)
        s.text(145, yy + 6, f'{price:.1f}', cls='small', anchor='end')
    xs = [230 + i * 160 for i in range(6)]
    s.poly([(x, 340 - (v - 10) * 180) for x, v in zip(xs, prices)])
    s.text(60, 425, '成交量（千股）', cls='small')
    for v in (0, 100, 200):
        yy = 610 - v * .65
        s.line(165, yy, 1090, yy)
        s.text(145, yy + 6, str(v), cls='small', anchor='end')
    for i, (x, v, p) in enumerate(zip(xs, volumes, prices)):
        s.rect(x - 25, 610 - v * .65, 50, v * .65, '#8aa9c9')
        s.text(x, 610 - v * .65 - 12, str(v), cls='small', anchor='middle')
        s.text(x, 340 - (p - 10) * 180 - 15, f'{p:g}', anchor='middle')
        s.text(x, 652, f'S{i + 1}', cls='small', anchor='middle')
    output['trend-volume'] = s.finish('量价不单独构成完整规则；需预先写明观察周期、触发、失效、执行假设与成本。')

    sized = size_position('10', '9.5', '520', '8050', 100, '20')
    s = SVG('仓位：同时受损失与现金约束', '合成预算520元，现金8050元，入场10元，止损参考9.5元，每100股一档，固定预留总成本20元。损失约束1000股，现金约束800股，取800股，计划损失420元，所需现金8020元。')
    s.card(50, 150, 520, '合成输入（不是现行费率）', ['入场 10.00；止损参考 9.50 元 / 股', '损失预算 520 元；可用现金 8050 元', '每档 100 股；整笔预留总成本 20 元', '无杠杆做多；两项预算都先扣成本'], 240)
    s.card(620, 150, 530, '先计算两项股数上限', ['损失：⌊(520−20) ÷ 0.5 ÷ 100⌋', '        × 100 = 1000 股', '现金：⌊(8050−20) ÷ 10 ÷ 100⌋', '        × 100 = 800 股'], 240)
    s.card(50, 430, 1100, '取较小值并检查', [f"股数 {sized['shares']}；计划损失 800 × 0.5 + 20 = {sized['planned_loss']} 元",
                                                  f"所需现金 800 × 10 + 20 = {sized['cash_required']} 元 ≤ 8050 元",
                                                  '预算不足一档时取 0 股，模型成本与现金占用均为 0。'], 210)
    output['risk-sizing'] = s.finish('计划损失不是保证上限：跳空、滑点、不能成交与实际成本均可能使损失扩大。')

    s = SVG('顶分型：位置与确认时间分开', '教学约定不含包含处理，顶分型中间K线的高低点均高于左右两根。中间K线是位置；右侧K线完成后才能确认三根关系。右侧未完成时只能暂定。')
    bars = [dict(open=10.5, high=11, low=10, close=10.8), dict(open=11.5, high=12, low=11, close=11.8),
            dict(open=10.7, high=11.2, low=10.3, close=10.5)]
    for x, heading, tentative in [(65, '右侧未完成：暂定', True), (650, '右侧完成：确认三根关系', False)]:
        s.rect(x, 150, 490, 405)
        s.text(x + 20, 192, heading, cls='large')
        yy = lambda v: 470 - (v - 10) * 105
        for offset, bar, label in zip((90, 240, 390), bars, ('左', '中', '右')):
            s.candle(x + offset, bar, yy, 45, tentative and label == '右')
            s.text(x + offset, 515, label, anchor='middle')
        s.text(x + 240, 234, '位置在中间根', cls='small', anchor='middle')
    s.text(85, 609, '元 / 股；红：阳线，绿：阴线。左 H/L=11/10；中=12/11；右最终=11.2/10.3。', cls='small')
    s.text(85, 650, '约定：三根无包含关系；右侧未收完时高低点可变。图示的是局部分型条件。')
    output['fractal-confirmation'] = s.finish('中间位置 ≠ 当时已知；确认分型 ≠ 笔已完成 ≠ 通用交易信号。完整判定须遵循声明的流派约定。')

    s = SVG('中枢重叠：先声明次级别区间', '三个已声明的连续次级别走势区间A为[10,13]，B为[11,14]，C为[10.5,12.5]；共同交集是[11,12.5]。图不使用任意三根K线定义递归级别。')
    x = lambda v: 240 + (v - 9.5) * 160
    s.rect(x(11), 165, x(12.5) - x(11), 350, '#e3edf7', '#aac0d7')
    for price in (10, 10.5, 11, 12, 12.5, 13, 14):
        s.line(x(price), 165, x(price), 525, GRID, 1, True)
        s.text(x(price), 563, f'{price:g}', cls='small', anchor='middle')
    for yy, name, lo, hi in [(225, 'A', 10, 13), (345, 'B', 11, 14), (465, 'C', 10.5, 12.5)]:
        s.text(65, yy + 6, f'{name} [{lo:g}, {hi:g}]')
        s.line(x(lo), yy, x(hi), yy, BLUE, 9)
        s.line(x(lo), yy - 15, x(lo), yy + 15, BLUE, 3)
        s.line(x(hi), yy - 15, x(hi), yy + 15, BLUE, 3)
    s.text(65, 612, '交集下界 = max(10, 11, 10.5) = 11；上界 = min(13, 14, 12.5) = 12.5。')
    s.text(65, 654, '单位：元 / 股；教学假设：A、B、C 已按声明的次级别规则识别并完成。', cls='small')
    output['center-overlap'] = s.finish('此图只算区间交集；递归结构还需级别、走势连接及完成条件，不能用任意三根蜡烛替代。')

    s = SVG('决策时序：何时知道，何时行动', '中间根位置在D2，右侧根在D3收盘才完成并可确认局部分型；D3观察后制定计划，未来可交易时段方可提交，成交仍待正式回报。')
    s.line(100, 315, 1100, 315, BLUE, 4)
    for x, label in [(145, 'D2：中间根'), (455, 'D3：右根收完'), (765, '下一可交易时段'), (1070, '回报时刻')]:
        s.line(x, 295, x, 335, BLUE, 4)
        s.text(x, 275, label, cls='small', anchor='middle')
    s.card(50, 390, 310, '结构的位置', ['位置可标在 D2', 'D2 不知道 D3 全貌', '当时只能暂定'], 190)
    s.card(405, 390, 310, '信息与判断', ['D3 收完后才确认', '先检查完整规则', '记录信息截止时点'], 190)
    s.card(760, 390, 390, '委托与实际回报', ['是否能提交取决于可交易性', '成交价、数量、时间待核对', '无法成交也须记录'], 190)
    s.text(65, 190, '合成日线示例；箭头表示时间先后，不表示固定等待长度。')
    s.text(65, 650, '离线回放按完整日线开放；一次只使用该截止时点可得的价格与事件。')
    output['decision-timeline'] = s.finish('不把结构标记日期当成已知日期，不用未来确认反填过去委托或成交。')

    nav = [Decimal(v) for v in ('1.00', '1.10', '0.99', '1.20', '1.08', '0.90', '1.26')]
    peak, dd = nav[0], []
    for value in nav:
        peak = max(peak, value)
        dd.append((value / peak - 1) * 100)
    s = SVG('净值与回撤：用同一组数字', '合成期末净值依次1、1.1、0.99、1.2、1.08、0.9、1.26元每份，回撤依次0%、0%、负10%、0%、负10%、负25%、0%。截至S6的最大回撤为25%。',
            '合成期末净值 · 假设已计模型成本、无追加或提取资金 · 连线不代表期间最低净值')
    xs = [205 + i * 145 for i in range(len(nav))]
    s.text(55, 146, '净值（元 / 份）', cls='small')
    for v in (0.9, 1.0, 1.1, 1.2):
        yy = 330 - (v - .9) * 320
        s.line(160, yy, 1120, yy)
        s.text(140, yy + 5, f'{v:.1f}', cls='small', anchor='end')
    s.poly([(x, 330 - (float(v) - .9) * 320) for x, v in zip(xs, nav)])
    for x, v in zip(xs, nav):
        s.text(x, 330 - (float(v) - .9) * 320 - 13, f'{v:.2f}', cls='small', anchor='middle')
    s.text(55, 416, '回撤（%）', cls='small')
    for v in (0, -10, -25):
        yy = 450 - v * 5
        s.line(160, yy, 1120, yy)
        s.text(140, yy + 6, str(v), cls='small', anchor='end')
    s.poly([(x, 450 - float(v) * 5) for x, v in zip(xs, dd)], GREEN)
    for i, (x, v) in enumerate(zip(xs, dd)):
        s.text(x, 450 - float(v) * 5 + 27, f'{v:.0f}%', cls='small', anchor='middle')
        s.text(x, 639, f'S{i}', cls='small', anchor='middle')
    output['equity-drawdown'] = s.finish('回撤 = 当前净值 ÷ 截至当时峰值 − 1；S5：0.90 ÷ 1.20 − 1 = −25%。只覆盖列示期末观测。')
    return output


PROMPTS = (
    '目前还没有价格。你会先记录哪些信息，并选择观察还是行动？',
    '请读出今天的开、高、低、收。仅凭一根线，你还不知道什么？',
    '两根日线的范围有何重叠？请先列事实，再写仍待观察的条件。',
    '请写出目前可观察的区间；你的触发条件是否已完整定义？',
    '今天与前三根相比有何变化？若要写计划，还缺哪些风险和执行条件？',
    '当前观察是否改变你的计划？请写出继续观察与停止执行的条件。',
    '若事先关注 10.70 与 11.10 两个价位，本根能说明各价位是否触及、先后能否确定？',
    '本根与前收盘之间有何差异？原有计划应检查哪些执行和失效问题？',
    '新信息是否满足你预先写下的条件？若不足，请记录等待理由。',
    '请比较最近两根的区间和成交量。当前有足够依据执行你的完整规则吗？',
    '只按当时记录复盘：哪些判断有依据，哪些仍未知？请把过程与结果分开。',
)


def teacher_case():
    rows = [
        ('2026-01-05', '10', '10.2', '9.8', '10', 100000),
        ('2026-01-06', '10', '10.15', '9.85', '10.05', 90000),
        ('2026-01-07', '10.05', '10.2', '9.95', '10.15', 110000),
        ('2026-01-08', '10.15', '10.6', '10.1', '10.5', 180000),
        ('2026-01-09', '10.5', '11', '10.35', '10.85', 210000),
        ('2026-01-12', '10.85', '11.2', '10.6', '10.9', 160000),
        ('2026-01-13', '10.4', '10.55', '9.9', '10', 260000),
        ('2026-01-14', '10', '10.2', '9.95', '10.05', 85000),
        ('2026-01-15', '10.05', '10.1', '9.95', '10', 60000),
        ('2026-01-16', '10', '10.3', '9.9', '10.15', 70000),
    ]
    return {
        'title': '青禾制造：逐步观察练习（虚构、无真实代码）',
        'synthetic': True, 'symbol': 'SYNTHETIC-QINGHE',
        'source': '内置合成数据 synthetic-v1，由 scripts/build_assets.py 确定性生成',
        'timezone': 'Asia/Shanghai', 'interval': '完整日线，收盘后开放',
        'price_unit': '元 / 股', 'volume_unit': '股 / 日',
        'adjustment': '无公司行动，未复权合成价格',
        'assumptions': '现金账户、无杠杆做多的观察练习；未模拟撮合、真实费率、结算或涨跌幅参数。',
        'bars': [dict(index=i, date=date, open=o, high=h, low=l, close=c, volume=v)
                 for i, (date, o, h, l, c, v) in enumerate(rows, 1)],
        'events': [
            {'available_after_bar': 0, 'text': '本练习允许等待和不交易。先写观察条件，下一步只开放一根完整日线。'},
            {'available_after_bar': 3, 'date': '2026-01-07', 'text': '截至今日：已开放三个完整日线观测。'},
            {'available_after_bar': 6, 'date': '2026-01-12', 'text': '本练习仅有日线 OHLC 和日成交量，没有逐笔路径与成交回报。'},
            {'available_after_bar': 7, 'date': '2026-01-13', 'text': '今日开盘 10.40，前收盘 10.90；未提供开盘撮合细节。'},
        ],
        'teacher_only': True,
        'teacher_notice': 'TEACHER SOURCE: This source contains all future observations. Before the raw response for this case at this cutoff, do not load this source. Learner entry: frame-00.html.',
        'future_observations': [
            {'cutoff': 0, 'note': 'There are no bars. A no-trade observation is permitted. A forecast is not available.'},
            {'cutoff': 4, 'note': 'The observation shows a possible breakout from the previous range. It does not show that a rule gives a profit.'},
            {'cutoff': 5, 'note': 'The continuation agrees with a possible satisfactory result for the setup. It does not show an order or realized profit.'},
            {'cutoff': 6, 'note': 'The bar includes 10.70 and 11.10. The sequence of touches is unknown. Fills are unknown.'},
            {'cutoff': 7, 'note': 'The opening gap puts the open and close at prices less than the minimum of the previous range. These prices show failure of the local continuation assumption. They do not show a simulated fill.'},
            {'cutoff': 9, 'note': 'The overlap has a small width, and volume is lower. Thus, you can use this case for an exercise to wait. This is not a no-trade rule for all conditions.'},
        ],
    }


def replay_chart(packet):
    bars = packet['bars']
    s = SVG('已开放价格', '仅绘制当前截止时点已开放的合成完整日线。红色为收高于开，绿色为收低于开，平线为开收相同。',
            '合成日线 · 元 / 股 · 横轴为观测日 · 红：阳线；绿：阴线；横线：平线', height=480)
    if not bars:
        s.text(600, 260, '尚无价格观测；先记录你的观察条件。', cls='large', anchor='middle')
    else:
        lower = min(float(bar['low']) for bar in bars)
        upper = max(float(bar['high']) for bar in bars)
        padding = max(.1, (upper - lower) * .15)
        lower, upper = lower - padding, upper + padding
        y = lambda v: 340 - (v - lower) / (upper - lower) * 195
        for j in range(5):
            value = lower + (upper - lower) * j / 4
            s.line(145, y(value), 1130, y(value))
            s.text(130, y(value) + 6, f'{value:.2f}', cls='small', anchor='end')
        gap = 940 / max(len(bars), 1)
        for i, bar in enumerate(bars):
            x = 180 + (i + .5) * gap
            s.candle(x, bar, y, min(46, gap * .45))
            s.text(x, 380, bar['date'][5:], cls='small', anchor='middle')
    return s.finish(f"信息截止：已完成第 {packet['cutoff']} 根日线；不含未开放的后续价格或事件。")


def replay_html(packet, total):
    cutoff = packet['cutoff']
    rows = ''.join('<tr>' + ''.join(f'<td>{escape(str(bar[k]))}</td>' for k in
                                   ('index', 'date', 'open', 'high', 'low', 'close', 'volume')) + '</tr>'
                   for bar in packet['bars'])
    events = ''.join(f'<li>第 {e["available_after_bar"]} 根后已知：{escape(e["text"])}</li>'
                     for e in packet['events'])
    previous = f'<a href="frame-{cutoff - 1:02d}.html">← 返回上一步</a>' if cutoff else '<span>入口：尚未开放价格</span>'
    following = (f'<a href="frame-{cutoff + 1:02d}.html">下一步：开放下一根完整日线 →</a>'
                 if cutoff < total else '<span>本组观测已结束；可返回核对当时记录。</span>')
    date = packet['bars'][-1]['date'] + ' 收盘后' if packet['bars'] else '第一根观测开放前'
    # The snapshot has only the data that the learner can see. It has no script or JSON payload.
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>合成逐步观察 · 第 {cutoff:02d} 步</title>
<style>
body{{margin:0;background:#f7f9fb;color:{INK};font:18px/1.65 "Microsoft YaHei",sans-serif}}
main{{max-width:1120px;margin:auto;padding:24px}}h1{{font-size:29px;margin:0 0 12px}}
h2{{font-size:22px}}p{{margin:8px 0}}.meta{{font-size:15px;color:{MUTED}}}
section{{background:white;border:1px solid {GRID};border-radius:10px;padding:16px 22px;margin:18px 0}}
.chart svg{{display:block;width:100%;min-width:960px;height:auto}}.chart{{padding:0;overflow-x:auto}}
nav{{display:flex;gap:24px;justify-content:space-between;flex-wrap:wrap;margin:24px 0}}
a{{color:{BLUE};font-weight:600}}table{{width:100%;border-collapse:collapse;font-size:15px}}
th,td{{padding:8px;text-align:right;border-bottom:1px solid {GRID}}}th:first-child,td:first-child{{text-align:left}}
.scroll{{overflow-x:auto}}.question{{border-left:5px solid {BLUE}}}
@media(max-width:600px){{main{{padding:12px}}h1{{font-size:24px}}body{{font-size:16px}}section{{padding:12px}}}}
</style></head><body><main>
<h1>{escape(packet['title'])}</h1>
<p><strong>合成教学数据 · 第 {cutoff:02d} 步 · cutoff = {cutoff}</strong></p>
<p class="meta">来源：{escape(packet['source'])}</p>
<p class="meta">截止：{escape(date)}；时区 {packet['timezone']}；{packet['interval']}。</p>
<p class="meta">价格：{packet['price_unit']}；成交量：{packet['volume_unit']}；{packet['adjustment']}。</p>
<p class="meta">{escape(packet['assumptions'])}</p>
<section class="chart">{replay_chart(packet)}</section>
<section><h2>截至此刻已知的事件</h2><ul>{events}</ul></section>
<section class="question"><h2>先写观察，再继续</h2><p>{escape(PROMPTS[cutoff])}</p>
<p class="meta">可在自己的笔记中作答；本页面不收集也不保存输入。等待与不交易也是可记录的选择。</p></section>
<section><h2>已开放的数据</h2><div class="scroll"><table><thead><tr><th>序号</th><th>日期</th><th>开</th><th>高</th><th>低</th><th>收</th><th>量（股）</th></tr></thead>
<tbody>{rows}</tbody></table></div></section>
<p class="meta">图中只表示 OHLC 范围；不表示日内先后顺序、委托或保证成交。不得用后续信息改写此前记录。</p>
<nav aria-label="逐步开放观测">{previous}{following}</nav>
</main></body></html>
'''


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')


def main():
    for name, content in figures().items():
        write(FIGURES / f'{name}.svg', content)
    case = teacher_case()
    write(REPLAY / 'teacher-case.json', json.dumps(case, ensure_ascii=False, indent=2) + '\n')
    for cutoff in range(len(case['bars']) + 1):
        write(REPLAY / f'frame-{cutoff:02d}.html', replay_html(visible_replay(case, cutoff), len(case['bars'])))
    write(REPLAY / 'README.md', """# Offline synthetic replay

Learner entry: [frame-00.html](frame-00.html).

Open the file locally. Read the page. Record a raw response. Then open the link with the next label.

Each page contains only prices and events available at its cutoff.
Dates are labels for synthetic observations. They are not historical market records.
The replay does not use a network, login, script, analytics, or local storage.

The teacher source `teacher-case.json` contains the full future sequence and teacher observations.
The regeneration script also contains the full sequence.
Each next link shows a different observation. These steps give the instruction sequence. They do not prevent file access.

Before the raw response for this case at this cutoff, do not read the teacher source.
Do not give the teacher source or regeneration script as an observation packet to the learner model at this cutoff.

From the repository root, use:

```powershell
python -B skills/ashare-market-learning/scripts/build_assets.py
```

From a directory, you can also use this command with an absolute script path.

SVG files are the primary source. PNG files are optional.

All fee and share-increment examples are assumptions for lessons. They are not trading rules at this time.

OHLC touches do not show the sequence of fills. They do not show execution availability or realized profit.
""")
    assert daily_return({'open': 10, 'high': 11, 'low': 9.8, 'close': 10.8}, '11.2') < 0
    print(f"The script made 11 SVG figures, {len(case['bars']) + 1} learner HTML snapshots, a teacher source, and a replay README.")


if __name__ == '__main__':
    main()
