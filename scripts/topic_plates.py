"""Make SVG plates for the tutor from observed bars. Do not use network access.

The caller supplies cases from the primary teacher manifest or make_cases().
The selected topic uses requested_condition. Arithmetic reads only decision_bars.
The script does not use a suffix, precomputed metrics, model output, a shared renderer, or an external package.
"""
import argparse
from copy import deepcopy
from decimal import Decimal as D
from html import escape
import hashlib
import json
from pathlib import Path
import re
import unicodedata

SKILL = Path(__file__).resolve().parents[1]
QUADS = ('up_high', 'up_low', 'down_high', 'down_low')
SHAPES = ('upper', 'lower', 'small', 'engulf')
BLUE, AMBER, PURPLE, TEAL = '#2463a0', '#b66c08', '#8255a6', '#087d80'
INK, MUTED = '#20344b', '#52677d'


def verdict(value):
    return '符合' if value else '不符合'


GAP_LABEL = {'none': '无', 'up': '向上', 'down': '向下'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def number(value):
    return format(D(value), 'f')


def short(value, places=3):
    return f'{D(str(value)):.{places}f}'.rstrip('0').rstrip('.') or '0'


def validate(case):
    bars = deepcopy(case['decision_bars'])
    if len(bars) < 21 or bars[-1]['date'] != case['cutoff']:
        raise ValueError('There must be a minimum of 21 observed bars. The last bar must be at the cutoff.')
    dates = [b['date'] for b in bars]
    if dates != sorted(set(dates)) or any(d > case['cutoff'] for d in dates):
        raise ValueError('Observed dates must increase. They must not be after the cutoff.')
    for b in bars:
        o, h, l, c, v = (D(b[k]) for k in ('open','high','low','close','volume_shares'))
        if not all(x.is_finite() for x in (o,h,l,c,v)) or not (0 < l <= min(o,c) <= max(o,c) <= h and v >= 0):
            raise ValueError('The OHLCV observation is incorrect.')
    if case['requested_condition'] not in (*QUADS, *SHAPES, 'breakout', 'breakdown', 'retest'):
        raise ValueError('The script cannot use the requested condition.')
    return bars


def band(bars, upper=True):
    key = 'high' if upper else 'low'
    value = (max if upper else min)(D(b[key]) for b in bars)
    return dict(anchor_price=number(value), anchor_date=next(b['date'] for b in bars if D(b[key])==value),
                low=number(value*D('.995')), high=number(value*D('1.005')),
                window_dates=[b['date'] for b in bars])


def gap(b, prev):
    return 'up' if D(b['low'])>D(prev['high']) else 'down' if D(b['high'])<D(prev['low']) else 'none'


def find_retest(bars):
    """Use the first frozen historical band that has qualification in the primary course."""
    last, prev = bars[-1], bars[-2]
    for j in range(len(bars)-10, len(bars)-1):
        z = band(bars[j-10:j])
        lo, hi = D(z['low']), D(z['high'])
        if (D(bars[j]['close'])>hi and D(bars[j]['low'])<=D(bars[j-1]['high'])
                and D(prev['close'])>hi and D(last['low'])<=hi and D(last['high'])>=lo
                and gap(last, prev)=='none'):
            z.update(break_date=bars[j]['date'], break_close=bars[j]['close'],
                     previous_close=prev['close'], return_date=last['date'],
                     overlap_low=number(max(D(last['low']),lo)), overlap_high=number(min(D(last['high']),hi)),
                     break_without_up_gap=True, return_without_full_gap=True,
                     subsequent_confirmation=None)
            return z
    return None


def scale(values, top=220, bottom=580, zero=False):
    low, high = min(values), max(values)
    if zero:
        low, high = D(0), high*D('1.12')
    else:
        pad = (high-low)*D('.12') or D(1)
        low, high = low-pad, high+pad
    return dict(minimum=number(low), maximum=number(high), top=top, bottom=bottom,
                pixels_per_unit=number(D(bottom-top)/(high-low)))


def y_at(value, s):
    return float(D(s['bottom'])-(D(value)-D(s['minimum']))*D(s['pixels_per_unit']))


class Drawing:
    'SVG text uses fixed widths from measurement and different lanes for labels.'
    def __init__(self):
        self.parts = []
        self.boxes = []

    def element(self, tag, **attrs):
        pairs = ' '.join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k,v in attrs.items())
        self.parts.append(f'<{tag} {pairs}/>')

    def line(self, x1, y1, x2, y2, color=MUTED, ident=None, dashed=False, width=1.5):
        attrs = dict(x1=f'{x1:.6f}', y1=f'{y1:.6f}', x2=f'{x2:.6f}', y2=f'{y2:.6f}', stroke=color, stroke_width=width)
        if ident:
            attrs['id'] = ident
        if dashed:
            attrs['stroke_dasharray'] = '7 5'
        self.element('line', **attrs)

    def rect(self, x, y, w, h, fill, ident=None, **attrs):
        attrs.update(x=f'{x:.6f}', y=f'{y:.6f}', width=f'{w:.6f}', height=f'{h:.6f}', fill=fill)
        if ident:
            attrs['id'] = ident
        self.element('rect', **attrs)

    @staticmethod
    def text_width(value, size):
        return sum(size*(1.0 if unicodedata.east_asian_width(c) in ('W','F') else .64) for c in value)

    def text(self, x, y, value, size=20, width=1500, color=INK):
        """Wrap text to the width. The textLength attribute makes the saved boxes agree with the specified dimensions."""
        tokens = re.findall(r'[A-Za-z0-9_.:/%+\-]+|[^\n]|\n', str(value))
        joined = []
        for token in tokens:
            if token in '。；，、：）】' and joined and joined[-1] != '\n':
                joined[-1] += token
            else:
                joined.append(token)
        lines, line = [], ''
        for token in joined:
            if token=='\n' or self.text_width(line+token,size)>width:
                if line:
                    lines.append(line)
                line = '' if token=='\n' else token.lstrip()
            else:
                line += token
        if line:
            lines.append(line)
        for i, value in enumerate(lines):
            top = y+i*size*1.5
            w = min(self.text_width(value,size), width)
            self.parts.append(f'<text x="{x}" y="{top+size}" font-size="{size}" fill="{color}" '
                              f'textLength="{w:.4f}" lengthAdjust="spacingAndGlyphs">{escape(value)}</text>')
            self.boxes.append(dict(x=x,y=top,width=round(w,4),height=size*1.25,text=value))
        return y+len(lines)*size*1.5

    def candle(self, b, x, s, ident, width=30):
        x=round(x,6)
        ys = {k:round(y_at(b[k],s),6) for k in ('open','high','low','close')}
        color = '#bd4548' if D(b['close'])>=D(b['open']) else '#167e67'
        self.line(x,ys['high'],x,ys['low'],color,ident+'-wick',width=2)
        self.rect(x-width/2,min(ys['open'],ys['close']),width,abs(ys['open']-ys['close']),color,ident+'-body')
        if ys['open']==ys['close']:
            self.line(x-width/2,ys['open'],x+width/2,ys['close'],color,width=2)
        return dict(id=ident,date=b['date'],x=x,y=ys,width=width)

    def bracket(self, x, y1, y2, color):
        self.line(x,y1,x,y2,color,width=3)
        self.line(x-7,y1,x+7,y1,color,width=2)
        self.line(x-7,y2,x+7,y2,color,width=2)


def anatomy(d, meta, bars):
    shown = bars[-2:]
    s = scale([D(b[k]) for b in shown for k in ('open','high','low','close')],220,560)
    meta['scale'] = s
    meta['anatomy'] = []
    p, t = shown
    prevclose = p['close']
    yy = y_at(prevclose,s)
    d.text(80,150,'双烛共用线性价格轴；右侧四价标签以引线对应真实高度。红：C≥O；绿：C<O。',20)
    for i,b in enumerate(shown):
        left, x = (80,260) if i==0 else (880,1060)
        d.rect(left,198,720,510,'#ffffff')
        d.text(left+22,200,('前一交易日  ' if i==0 else '目标日  ')+b['date'],21,width=650)
        d.line(left+50,yy,left+315,yy,TEAL,'previous-close' if i==0 else 'previous-close-target',True)
        g = d.candle(b,x,s,f'candle-{i}',64)
        meta['candles'].append(g)
        o,h,l,c = (D(b[k]) for k in ('open','high','low','close'))
        a = dict(date=b['date'],body=number(abs(c-o)),upper_wick=number(h-max(o,c)),lower_wick=number(min(o,c)-l))
        for key in ('body','upper_wick','lower_wick'):
            a[key+'_pixels'] = round(float(D(a[key])*D(s['pixels_per_unit'])),6)
        meta['anatomy'].append(a)
        endpoints = sorted(('high','open','close','low'),key=lambda k:-D(b[k]))
        labels = dict(high='H 最高',open='O 开盘',close='C 收盘',low='L 最低')
        for j,key in enumerate(endpoints):
            dock_y = 270+j*62
            d.line(x+32,g['y'][key],x+150,dock_y+12,'#a9b5c0',width=1)
            d.text(x+162,dock_y,f'{labels[key]}  {b[key]}',19,width=350)
        d.bracket(x+80,g['y']['high'],min(g['y']['open'],g['y']['close']),BLUE)
        d.bracket(x+80,min(g['y']['open'],g['y']['close']),max(g['y']['open'],g['y']['close']),AMBER)
        d.bracket(x+80,max(g['y']['open'],g['y']['close']),g['y']['low'],PURPLE)
        for j,(key,label,color) in enumerate((('upper_wick','蓝：上影',BLUE),('body','金：实体',AMBER),('lower_wick','紫：下影',PURPLE))):
            d.text(left+22,592+j*34,f'{label} {short(a[key])} 元/股',19,width=675,color=color)
    meta['previous_close'] = dict(date=p['date'],price=p['close'],y=round(yy,6))
    po,pc,o,c = (D(v) for v in (p['open'],p['close'],t['open'],t['close']))
    strict = dict(opposite_direction=(c-o)*(pc-po)<0,lower_strict=min(o,c)<min(po,pc),upper_strict=max(o,c)>max(po,pc))
    strict['admitted'] = all(strict.values())
    meta['strict_engulfing'] = strict
    body,up,lo = (D(meta['anatomy'][-1][k]) for k in ('body','upper_wick','lower_wick'))
    span = D(t['high'])-D(t['low'])
    conditions = dict(upper=span>0 and up>=span/2 and up>=body*2,
                      lower=span>0 and lo>=span/2 and lo>=body*2,
                      small=span>0 and body<=span*D('.15'),engulf=strict['admitted'])
    meta['requested_positive'] = conditions[meta['requested_condition']]
    a = meta['anatomy'][-1]
    explanation = [
        f"目标 {t['date']}：H−L={t['high']}−{t['low']}={number(span)}；|C−O|=|{t['close']}−{t['open']}|={a['body']} 元/股。",
        f"上影 H−max(O,C)={a['upper_wick']}；下影 min(O,C)−L={a['lower_wick']}。三段相加={number(span)}，与全幅相等。",
        '两根蜡烛共用价格刻度，右侧蓝、金、紫括线分别对应上影、实体、下影；长度可以直接比较。',
        f"青色虚线是 {p['date']} 前收 {prevclose}，不是目标日开盘 {t['open']}。收盘减开盘={number(c-o)} 判断阴阳；收盘减前收={number(c-pc)} 判断日涨跌。",
    ]
    if meta['requested_condition']=='engulf':
        explanation.append(f"只比实体：目标下端 {number(min(o,c))} < 前实体下端 {number(min(po,pc))}：{verdict(strict['lower_strict'])}；目标上端 {number(max(o,c))} > 前实体上端 {number(max(po,pc))}：{verdict(strict['upper_strict'])}；方向相反：{verdict(strict['opposite_direction'])}。相等只记临界，不能充作严格吞没；影线不用包住。")
    else:
        label = {'upper':'上影≥全幅50%且≥实体2倍','lower':'下影≥全幅50%且≥实体2倍','small':'实体≤全幅15%且全幅>0'}[meta['requested_condition']]
        explanation.append(f"本题条件为{label}，截止本日：{verdict(meta['requested_positive'])}。比例：实体 {short(body/span if span else 0,6)}，上影 {short(up/span if span else 0,6)}，下影 {short(lo/span if span else 0,6)}；外形不证明资金意图或反转。")
    prompt = '请指着目标实体与两条影线，逐一报出各自的价格差；再指出前收虚线，说明阴阳与相对前收涨跌为何要分别判断。'
    return explanation,prompt,760


def volume(d,meta,bars):
    shown = bars[-21:]
    prior,last,prev = shown[:-1],shown[-1],shown[-2]
    values = [D(b['volume_shares'])/10000 for b in shown]
    mean = sum(D(b['volume_shares']) for b in prior)/20
    ratio = D(last['volume_shares'])/mean
    s = scale(values,240,610,zero=True)
    meta['scale'] = s
    d.text(100,155,'成交量（万股）；蓝色20柱是基准窗口，金色最后一柱是目标日；每柱为完整交易日。',20)
    step = 930/21
    d.rect(112,230,step*20,380,'#eef4fb')
    vbars=[]
    for i,(b,value) in enumerate(zip(shown,values)):
        x=112+step*(i+.5)
        y=y_at(value,s)
        ident=f'volume-{i}'
        d.rect(x-13,y,26,610-y,AMBER if i==20 else '#7093b7',ident)
        vbars.append(dict(id=ident,date=b['date'],x=x,y=round(y,6),height=round(610-y,6),shares=b['volume_shares']))
    for value in (D(0),D(s['maximum'])/2,D(s['maximum'])):
        y=y_at(value,s)
        d.line(110,y,1045,y,'#d8e1eb',width=1)
        d.text(15,y-10,short(value,1),16,width=90)
    my=y_at(mean/10000,s)
    d.line(110,my,1045,my,TEAL,'prior20-mean',True,width=2.5)
    d.line(vbars[-1]['x'],230,vbars[-1]['x'],615,AMBER,'cutoff',True)
    d.line(112,666,112+20*step,666,BLUE,width=2)
    d.line(112,659,112,674,BLUE,width=2)
    d.line(112+20*step,659,112+20*step,674,BLUE,width=2)
    d.text(112,685,f"基准20根：{prior[0]['date']} 至 {prior[-1]['date']}（排除目标日）",19,width=930)
    d.text(vbars[-1]['x']-66,628,last['date'],18,width=140)
    pd='up' if D(last['close'])>D(prev['close']) else 'down' if D(last['close'])<D(prev['close']) else 'flat'
    quad=pd+('_high' if ratio>=1 else '_low')
    meta['requested_positive']=quad==meta['requested_condition']
    meta['volume']=dict(window_dates=[b['date'] for b in prior],mean_shares=number(mean),mean_wan_shares=number(mean/10000),
                        last_shares=last['volume_shares'],last_ratio=number(ratio),price_direction=pd,
                        axis_unit='wan shares (10000 shares)',bars=vbars,mean_y=round(my,6),quad=quad)
    notes=[('青色虚线：前20根均量',TEAL),
           (f"{number(mean)} 股 = {short(mean/10000,6)} 万股",INK),
           ('今日量 / 此前20根均量',AMBER),
           (f"{last['volume_shares']} / {number(mean)} = {short(ratio,6)}",INK),
           (f"今日量 {'≥' if ratio>=1 else '<'} 均量；等于归入不低于均量。",INK),
           (f"前收 {prev['date']}：{prev['close']} 元/股",INK),
           (f"今日 {last['date']}：O {last['open']}；C {last['close']}",INK),
           (f"C−前收 = {number(D(last['close'])-D(prev['close']))} 元/股",INK),
           ('本课日量相对值不是软件盘中量比。',MUTED)]
    end=notes_column(d,notes)
    explanation=[
        f"基准窗口 {prior[0]['date']}—{prior[-1]['date']} 共20根；原始量合计 {number(mean*20)} 股，除以20得 {number(mean)} 股。目标量 {last['volume_shares']} 股未进入分母。",
        f"纵轴用万股：股数÷10000。青色虚线为此前均量 {short(mean/10000,6)} 万股；金柱高于虚线表示今日量更大，低于则更小。单位换成万股不改变两者的大小关系。",
        f"目标收盘 {last['close']} 与前收 {prev['close']} 比，{'上涨' if pd=='up' else '下跌' if pd=='down' else '持平'}；今日量/此前均量={short(ratio,6)}，{'不低于' if ratio>=1 else '低于'}1。价格方向与相对成交量需要分别判断。",
        '先指出蓝色比较窗口、青色均量线与金色今日柱，再谈量价组合；每笔交易有买卖双方，柱高不证明资金身份、意图或后续涨跌。']
    return explanation,'请在图上指出排除今日的20根窗口；用股与万股各算一次均量，说明今日柱与虚线的比较为何不受单位换算影响。',max(790,end+40)


def notes_column(d,notes):
    y=210
    for value,color in notes:
        y=d.text(1120,y,value,19,width=480,color=color)+14
    return y


def price_plot(d,meta,shown,z,ret=False):
    vals=[D(b[k]) for b in shown for k in ('high','low')]+[D(z['low']),D(z['high'])]
    s=scale(vals,240,600)
    meta['scale']=s
    left,right=120,1040
    step=(right-left)/len(shown)
    d.rect(left,232,right-left-step,368,'#f0f4f8')
    high,low=y_at(z['high'],s),y_at(z['low'],s)
    d.rect(left,high,right-left,low-high,'#ebe3f5' if ret else '#e0edf8','frozen-band' if ret else 'anchor-band')
    d.line(left,high,right,high,PURPLE if ret else BLUE,width=1.5)
    d.line(left,low,right,low,PURPLE if ret else BLUE,width=1.5)
    for value in (D(s['minimum']), (D(s['minimum'])+D(s['maximum']))/2,D(s['maximum'])):
        yy=y_at(value,s)
        d.text(15,yy-10,short(value,2),16,width=95)
    for i,b in enumerate(shown):
        x=left+step*(i+.5)
        g=d.candle(b,x,s,f'candle-{i}',min(32,step*.48))
        meta['candles'].append(g)
        if b['date']==z['anchor_date']:
            anchor_y=y_at(z['anchor_price'],s)
            d.element('circle',cx=x,cy=anchor_y,r=6,fill='white',stroke=BLUE,stroke_width=2,id='anchor-point')
        if ret and b['date']==z['break_date']:
            d.line(x,232,x,600,AMBER,'break-day',True,width=2)
    last=meta['candles'][-1]
    d.line(last['x'],232,last['x'],610,TEAL,'cutoff',True,width=2)
    d.text(left,632,shown[0]['date'],18,width=160)
    d.text(last['x']-68,632,shown[-1]['date'],18,width=160)
    start=next(g['x'] for g in meta['candles'] if g['date']==z['window_dates'][0])-step/2
    end=next(g['x'] for g in meta['candles'] if g['date']==z['window_dates'][-1])+step/2
    d.line(start,683,end,683,BLUE,width=2)
    d.line(start,676,start,690,BLUE,width=2)
    d.line(end,676,end,690,BLUE,width=2)
    d.text(left,707,f"锚点取样10根：{z['window_dates'][0]}—{z['window_dates'][-1]}；空心蓝点为锚点。",18,width=950)
    return s


def boundary(d,meta,bars):
    upper=meta['requested_condition']!='breakdown'
    z=band(bars[-11:-1],upper)
    last,prev=bars[-1],bars[-2]
    edge=D(z['high' if upper else 'low'])
    close_ok=D(last['close'])>edge if upper else D(last['close'])<edge
    fullgap=gap(last,prev)
    admitted=close_ok and fullgap!=('up' if upper else 'down')
    z.update(side='resistance' if upper else 'support',close_strict=close_ok,
             cutoff_close=last['close'],full_gap=fullgap,candidate_admitted=admitted,
             relation='>' if upper else '<')
    meta['boundary']=z
    meta['requested_positive']=admitted if meta['requested_condition']!='retest' else False
    d.text(100,155,'局部边界核查；元/股。蓝带是锚点±0.5%的教学容差，青虚线为截止；未绘制后续。',20)
    s=price_plot(d,meta,bars[-11:],z)
    relation='>' if upper else '<'
    notes=[('先前10根的'+('最高价上沿' if upper else '最低价下沿'),BLUE),
           (f"锚点 {z['anchor_date']}：{z['anchor_price']}",INK),
           (f"带 [{short(z['low'],6)}, {short(z['high'],6)}] 元/股",INK),
           (f"截止 {last['date']}：C={last['close']}",TEAL),
           (f"严格比较 C {relation} {number(edge)}：{verdict(close_ok)}",INK),
           (f"H={last['high']}；L={last['low']}；触及与收盘越界分开。",INK),
           (f"整根缺口：{GAP_LABEL[fullgap]}；该方向越界候选：{verdict(admitted)}",INK)]
    if meta['fallback_reason']:
        notes.append(('请求条件未获选例资格；这里只核查，不当阳性示范。',AMBER))
    end=notes_column(d,notes)
    explanation=[
        f"只用此前10根 {z['window_dates'][0]}—{z['window_dates'][-1]}；锚点为最早同价日 {z['anchor_date']} 的 {z['anchor_price']}。低缘=锚点×0.995={z['low']}，高缘=锚点×1.005={z['high']}。",
        f"蓝带上边是 {short(z['high'],6)}，下边是 {short(z['low'],6)} 元/股。先用引线和价格轴找到两条边，再看目标收盘在带内、带外还是恰等于边界。",
        f"只在 {last['date']} 收盘截止核查：C={last['close']} {relation} 带外缘 {number(edge)}：{verdict(close_ok)}；相等不满足严格关系。整根缺口：{GAP_LABEL[fullgap]}；排除该方向整根跳空后，局部候选条件{verdict(admitted)}。",
        'H、L表示当日触及范围，C表示收盘位置；两者不能互换。容差不是置信区间，也未证明多次成交密集或经济突破；权益事件与可交易性须另核。']
    if meta['fallback_reason']:
        explanation.append('替代说明：'+meta['fallback_reason'])
        if meta['requested_condition']=='retest':
            explanation.append('截至本题，未取得合格的冻结旧带回访链；图中蓝带只是今日之前10根的上沿，不是捏造的旧突破带。不得把靠近它说成回访成功。')
    return explanation,'请指出锚点日、取样10根和截止日；比较当日最高/最低触及与收盘严格越界。若收盘恰等于带外缘，条件是否成立？',max(790,end+40)


def retest(d,meta,bars,z):
    meta['retest']=z
    meta['requested_positive']=True
    shown=[b for b in bars if b['date']>=z['window_dates'][0]]
    last=bars[-1]
    d.text(100,155,'冻结旧带回访核查；元/股。紫带保持旧值，金虚线为旧突破日，青虚线为本题截止。',20)
    s=price_plot(d,meta,shown,z,True)
    x=meta['candles'][-1]['x']
    high,low=y_at(z['overlap_high'],s),y_at(z['overlap_low'],s)
    d.rect(x+23,high,12,low-high,TEAL,'return-overlap')
    notes=[('冻结的是突破当时的旧上沿带',PURPLE),
           (f"旧锚点 {z['anchor_date']}：{z['anchor_price']}",INK),
           (f"旧带 [{short(z['low'],6)}, {short(z['high'],6)}]",INK),
           (f"突破日 {z['break_date']}：C={z['break_close']} > {short(z['high'],6)}",AMBER),
           (f"前收 {z['previous_close']} > 旧上缘 {short(z['high'],6)}",INK),
           (f"返回日 {z['return_date']}",TEAL),
           (f"最低 {last['low']} ≤ 旧上缘 {short(z['high'],6)}",TEAL),
           (f"最高 {last['high']} ≥ 旧下缘 {short(z['low'],6)}",TEAL),
           (f"交叠 [{short(z['overlap_low'],6)}, {short(z['overlap_high'],6)}]；右侧青条为交叠高度。",INK),
           ('只确认区间交叠；未用随后数据，不能称回踩成功。',MUTED)]
    end=notes_column(d,notes)
    explanation=[
        f"旧带只取 {z['window_dates'][0]}—{z['window_dates'][-1]} 的10根；高点 {z['anchor_date']} 为 {z['anchor_price']}，乘0.995与1.005得 [{z['low']}, {z['high']}]。随后不滚动改带。",
        f"{z['break_date']} 收 {z['break_close']} 严格高于旧上缘 {z['high']}，且非向上整根缺口；返回前收 {z['previous_close']} 仍在旧上缘之上。返回日 {last['date']} 不是整根缺口。",
        f"返回区间 [{last['low']}, {last['high']}] 与旧带交叠：下端=max(L,旧下缘)={z['overlap_low']}，上端=min(H,旧上缘)={z['overlap_high']}。下端≤上端才有交叠。",
        '紫带保持历史锚点不动；目标蜡烛右侧的青条只画出它与旧带共有的价格范围，青条与紫带等高表示整条旧带都在当日触及范围内。',
        f"本日 C={last['close']}；此条件不要求收回旧上缘。尚无随后确认，不能把区间接触、收回上缘、后续守住混为一事；将来确认须另定规则并等新完整日线。"]
    return explanation,'请依次指出旧锚点、突破日、返回日和交叠青条；说明哪一项只证明接触旧带，为什么今天还不能宣布回踩成功？',max(790,end+40)


def build_plate(case):
    """Return (SVG text, teacher metadata). Do not change the input case."""
    bars=validate(case)
    requested=case['requested_condition']
    selected=case['selected_condition']
    z=find_retest(bars) if requested=='retest' and selected=='retest' else None
    focus='volume' if requested in QUADS else 'anatomy' if requested in SHAPES else 'retest' if z else 'boundary'
    input_data=dict(id=case['id'],symbol=case['symbol'],name=case['name'],cutoff=case['cutoff'],
                    requested_condition=requested,selected_condition=selected,
                    fallback_reason=case.get('fallback_reason',''),observed_bars=bars)
    meta=dict(schema_version=1,teacher_only=True,opens_after='saved_raw_answer',**input_data,
              observed_bars_sha256=digest(bars),svg_input_sha256=digest(input_data),
              hash_serialization='UTF-8 JSON, ensure_ascii=False, sort_keys=True, separators=(comma,colon)',
              source=deepcopy(case.get('source',{})),
              price_unit='CNY/share',volume_unit='shares',adjustment='unadjusted',timezone='Asia/Shanghai',
              focus=focus,width=1680,candles=[],retest=None,boundary=None,requested_positive=False)
    d=Drawing()
    titles=dict(anatomy='实体与影线：双烛放大',volume='价量：固定20根比较',boundary='边界：锚点与收盘',retest='回访：冻结旧带')
    d.text(70,32,f"{case['id'].upper()} · {case['name']} · {titles[focus]}",30,width=1540)
    d.text(70,90,f"教师专用 · 保存原答后开放 · 截止 {case['cutoff']} · 真实未复权日线 · Asia/Shanghai",20,width=1540,color=MUTED)
    if focus=='anatomy':
        explanation,prompt,fy=anatomy(d,meta,bars)
    elif focus=='volume':
        explanation,prompt,fy=volume(d,meta,bars)
    elif focus=='retest':
        explanation,prompt,fy=retest(d,meta,bars,z)
    else:
        explanation,prompt,fy=boundary(d,meta,bars)
    meta['explanation_zh']=explanation
    meta['checking_prompt_zh']=prompt
    fy=d.text(80,fy,'把数值对应到图上',23,width=1500,color=BLUE)+16
    for row in explanation:
        fy=d.text(80,fy,row,19,width=1510)+12
    fy=d.text(80,fy+8,'检查一问：'+prompt,20,width=1510,color=TEAL)+18
    fy=d.text(80,fy,'来源：同题观察前缀（Sina OHLCV，Tencent OHLC交叉核对）；只画截止前数据。图形不是委托、成交或收益证明。',17,width=1510,color=MUTED)
    meta['height']=int(fy+55)
    meta['text_boxes']=d.boxes
    binding=dict(teacher_only=True,opens_after=meta['opens_after'],id=meta['id'],
                 observed_bars_sha256=meta['observed_bars_sha256'],svg_input_sha256=meta['svg_input_sha256'])
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="{meta["height"]}" viewBox="0 0 1680 {meta["height"]}" role="img" aria-labelledby="plate-title plate-desc">\n'
         f'<title id="plate-title">{escape(case["id"].upper()+" 教师专题图版")}</title>\n'
         '<desc id="plate-desc">仅在保存学员原答后开放；真实观察前缀的局部放大图，详细数值解释在图下方。</desc>\n'
         f'<metadata>{escape(json.dumps(binding,sort_keys=True))}</metadata>\n'
         '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif}line{stroke-linecap:round}</style>\n'
         f'<rect width="1680" height="{meta["height"]}" fill="#f7f9fc"/>\n'+ '\n'.join(d.parts)+'\n</svg>\n')
    meta['svg_sha256']=hashlib.sha256(svg.encode('utf-8')).hexdigest()
    return svg,meta


def routing_reference():
    return """# 专题图版：先原答，再按题开放

本页只作安全分流，不含逐题答案。原始观察材料与作答步骤仍由[2026主图谱](tech-2026-atlas.md)负责。实体与影线衔接[M07](modules/module-07.md)、[M08](modules/module-08.md)；边界与回访衔接[M09](modules/module-09.md)；量价衔接[M10](modules/module-10.md)。读坐标的方法见[读图手册](chart-reading.md)。

Tutor routing: Before the learner gives a raw response, use only one primary decision packet.
First, keep the raw response (`saved_raw_answer`). Then open only the related `assets/topic-plates/t26-NN.svg` and `t26-NN.json`.
Find NN from the exercise ID for this step.
Do not browse the plate directory, teacher manifest, generator, or other plate metadata in the learner context.
Before the raw response, do not load a plate.

The links and teacher flags give the instruction sequence. They do not prevent file access.

Record the annotated view as assisted exposure. This exposure is prior access to an answer.
Then continue from the lesson cursor from before this step.

Tutor display: After the saved raw response, find the related PNG with the same basename.
If the PNG is available, embed it in the response.
After path resolution, use Markdown image syntax with the absolute path to the local file.
Find the installed skill root and the case ID for this step.

Do not use a placeholder or a relative path.
If there is no PNG, embed the related SVG with its absolute path to the local file.
After the raw response, load only the related teacher JSON.
Before the answer, do not replace the raw observation with the annotated plate.

每题教师 JSON 有 `explanation_zh`（真实数值与图形部位的对应）、`checking_prompt_zh`（一个检查问句）、取样日期和图源哈希。Read only the explanation for the same exercise.
Give an explanation of one relation at a time.
Before you continue, wait for the learner to give a raw response.
Do not give all topic explanations to the learner together.
If the learner saw a figure, do not use it to show independent mastery without prior access.

图版按该题原请求选焦点：实体题采用前一根与目标根共用刻度的双烛放大，四价标签以引线连到真实位置；量价题画此前20根和今日量、固定均量线与窗口；边界题画带、锚点、取样区间与截止；回访题保持旧带不动，分别画突破日、返回日与交叠。若原选例为替代题，只作条件核查，解释为何不足；不把偶然出现的其他形态充作请求主题的正例。

数值与长度均由该题截止前行情重算。价格用元/股；量图显示万股，先由原始股数除以10000；今日不进入此前20根均量。实体像素高度不设人为最小值，小实体或零实体仍按真实差值呈现。标签另设固定栏，避免紧邻四价时互相覆盖。未复权坐标不证明经济突破，区间交叠不证明回踩成功。

Builder: After regeneration of the primary atlas, use `python -B scripts/topic_plates.py` from the skill directory.
The parent script can call `build(cases)` with the new `make_cases()` result.
The builder writes only this reference and `assets/topic-plates/` SVG/JSON files.
It does not change decision packets or make PNG files.

Each JSON has bindings to the observed bars without changes.
It also has a canonical input hash (`svg_input_sha256`) and the output SVG hash (`svg_sha256`).
The parent has different checks for PNG rendering and acceptance after a visual check.
"""


def build(cases, output=None, reference=None):
    'Write the plates and a reference that gives the instruction sequence without answers. Return the inventory.'
    output=Path(output) if output is not None else SKILL/'assets/topic-plates'
    reference=Path(reference) if reference is not None else SKILL/'references/topic-plates.md'
    output.mkdir(parents=True,exist_ok=True)
    inventory=[]
    for case in cases:
        svg,meta=build_plate(case)
        stem=case['id']
        (output/(stem+'.svg')).write_text(svg,encoding='utf-8',newline='\n')
        (output/(stem+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        inventory.append(dict(id=stem,cutoff=meta['cutoff'],svg=stem+'.svg',metadata=stem+'.json',
                              svg_sha256=meta['svg_sha256'],svg_input_sha256=meta['svg_input_sha256']))
    index=dict(schema_version=1,teacher_only=True,opens_after='saved_raw_answer',plates=inventory)
    (output/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    reference.parent.mkdir(parents=True,exist_ok=True)
    reference.write_text(routing_reference(),encoding='utf-8',newline='\n')
    return index


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=SKILL/'assets/tech-2026/teacher-manifest.json')
    parser.add_argument('--output',type=Path,default=SKILL/'assets/topic-plates')
    parser.add_argument('--reference',type=Path,default=SKILL/'references/topic-plates.md')
    args=parser.parse_args()
    cases=json.loads(args.manifest.read_text(encoding='utf-8'))['cases']
    # Do a check of the related raw observation. An outcome file is not necessary.
    for case in cases:
        decision=json.loads((args.manifest.parent/(case['id']+'-decision.json')).read_text(encoding='utf-8'))
        if decision['bars']!=case['decision_bars']:
            raise ValueError('The observed packet is different from the manifest: '+case['id'])
    index=build(cases,args.output,args.reference)
    print(f"The script made {len(index['plates'])} SVG/JSON plates for the tutor. It did not render PNG files.")


if __name__=='__main__':
    main()
