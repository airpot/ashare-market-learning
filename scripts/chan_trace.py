"""This synthetic C12-F trace has a finite length. The script does not call the network or a shared generator."""

import argparse
from html import escape
import json
from pathlib import Path


ENDPOINTS = [50,58,53,59,51,57, 49,52,48,56,50,
             60,54,61,51,58, 47,53,46,56,48,
             62,54,63,49,60, 45,53,44,55]


def interval(a, b):
    return [min(a, b), max(a, b)]


def overlap(ranges):
    low, high = max(r[0] for r in ranges), min(r[1] for r in ranges)
    return [low, high] if low < high else None


def connected(items):
    return all(a['end'] == b['start'] and a['end_at'] == b['start_at']
               for a, b in zip(items, items[1:]))


def qualify_b0(strokes, start, cutoff):
    six = strokes[start:start+6]
    if len(six) != 6 or not connected(six):
        return None
    if any(s.get('admitted_strict') is not True or s['known_at'] > cutoff
           or s['known_at'] <= s['end_at'] for s in six):
        return None
    direction = [1 if s['end'] > s['start'] else -1 if s['end'] < s['start'] else 0
                 for s in six]
    if 0 in direction or any(a == b for a,b in zip(direction,direction[1:])):
        return None
    features = [interval(s['start'], s['end']) for s in six[1::2]]
    left, middle, right = features
    sign = direction[0]
    if not all(sign*(middle[j]-other[j]) > 0 for j in (0,1) for other in (left,right)):
        return None
    if overlap([left,middle]) is None:
        return None
    member_ranges = [interval(s['start'],s['end']) for s in six[:3]]
    if overlap(member_ranges) is None:
        return None
    full = [min(r[0] for r in member_ranges), max(r[1] for r in member_ranges)]
    if interval(six[0]['start'],six[2]['end']) != full:
        return None
    return dict(id=f'B{start//3+1}', start=six[0]['start'], end=six[2]['end'],
                range=full, start_at=six[0]['start_at'], end_at=six[2]['end_at'],
                known_at=max(s['known_at'] for s in six),
                member_strokes=[s['id'] for s in six[:3]],
                feature_strokes=[s['id'] for s in six[1::2]], features=features,
                first_three_overlap=overlap(member_ranges),
                no_gap_overlap=overlap([left,middle]),
                rule='M11 first case: The strict strokes have admission. There is no feature inclusion.')


def seal_block(b0, start, cutoff):
    available = b0[start:]
    if len(available) < 6:
        return None
    core = overlap([b['range'] for b in available[:3]])
    if core is None:
        return None
    for count in range(3, len(available)-2, 2):
        members, witnesses = available[:count], available[count:count+3]
        used = members+witnesses
        if not connected(used) or any(b['known_at'] > cutoff for b in used):
            continue
        directions = [1 if b['end'] > b['start'] else -1 if b['end'] < b['start'] else 0
                      for b in used]
        if 0 in directions or any(a == b for a,b in zip(directions,directions[1:])):
            continue
        if any(max(b['range'][0],core[0]) > min(b['range'][1],core[1]) for b in members):
            continue
        moving = [overlap([b['range'] for b in members[i:i+3]]) for i in range(count-2)]
        if any(r is None or max(r[0],core[0]) > min(r[1],core[1]) for r in moving):
            continue
        d,r,e = [b['end'] for b in witnesses]
        sign = directions[count-1]
        separated = (d < core[0] and r < core[0] and e < d) if sign == 1 else (
                     d > core[1] and r > core[1] and e > d)
        witness_core = overlap([b['range'] for b in witnesses])
        if not separated or witness_core is None:
            continue
        if not (witness_core[1] < core[0] if sign == 1 else witness_core[0] > core[1]):
            continue
        return dict(members=[b['id'] for b in members], witnesses=[b['id'] for b in witnesses],
                    core=core, moving_cores=moving, witness_core=witness_core,
                    range=[min(b['range'][0] for b in members),max(b['range'][1] for b in members)],
                    start=members[0]['start'], end=members[-1]['end'],
                    start_at=members[0]['start_at'], boundary_at=members[-1]['end_at'],
                    known_at=max(b['known_at'] for b in used), convention='C12-F',
                    branch='downward_seal' if sign==1 else 'upward_seal_mirror')
    return None


def make_strokes():
    turns = []
    for i,(a,b) in enumerate(zip(ENDPOINTS,ENDPOINTS[1:])):
        previous = ENDPOINTS[i-1] if i else b
        turns.append(round(min(b,previous)-.1 if b>a else max(b,previous)+.1,2))
    prices = [ENDPOINTS[0]]
    for i,(a,b) in enumerate(zip(ENDPOINTS,ENDPOINTS[1:])):
        next_turn = turns[i+1] if i+1<len(turns) else turns[i]
        retreat = round((a+min(turns[i],next_turn))/2 if b>a else
                        (a+max(turns[i],next_turn))/2,3)
        prices.extend([turns[i],retreat,b])
    return [dict(id=f'S{i+1}', start=a, end=b, start_at=2*i, end_at=2*i+2,
                 known_at=2*i+3, admitted_strict=True)
            for i,(a,b) in enumerate(zip(prices,prices[1:]))]


def classify_return(l2, departure, returned):
    result = dict(status='pending_departure')
    if departure['end'] >= l2['core'][0] or returned['start'] != departure['end']:
        return result
    high, boundary = returned['range'][1], l2['core'][0]
    status = ('failed_third_sell' if high > boundary else 'boundary_no_trade'
              if high == boundary else 'finite_third_sell_conditions_met')
    return dict(status=status, departure=departure['id'], departure_end=departure['end'],
                departure_known_at=departure['known_at'], first_return=returned['id'],
                return_range=returned['range'], overlap=overlap([returned['range'],l2['core']]),
                decision_at=max(l2['known_at'],departure['known_at'],returned['known_at']),
                scope='This classification is only for lessons with finite C12-F inputs.')


def build_trace(cutoff=175, strokes=None):
    strokes = make_strokes() if strokes is None else strokes
    b0 = []
    for i in range(0,len(strokes)-5,3):
        item = qualify_b0(strokes,i,cutoff)
        if item is None:
            break
        b0.append(item)
    l1, start = [], 0
    while True:
        block = seal_block(b0,start,cutoff)
        if block is None:
            break
        block['id'] = f'T{len(l1)+1}'
        l1.append(block)
        start += len(block['members'])
    l2 = None
    if len(l1)>=3:
        l2 = dict(inputs=[b['id'] for b in l1[:3]],
                  core=overlap([b['range'] for b in l1[:3]]),
                  range=[min(b['range'][0] for b in l1[:3]),max(b['range'][1] for b in l1[:3])],
                  known_at=max(b['known_at'] for b in l1[:3]),
                  status='formed_core_only_not_sealed_L2_type')
    classification = dict(status='pending_departure')
    if len(l1)>=4 and l2 is not None:
        departure = l1[3]
        classification = dict(status='pending_return', departure=departure['id'],
                              departure_known_at=departure['known_at'])
        if len(l1)>=5:
            classification = classify_return(l2,departure,l1[4])
    return dict(convention='C12-F', synthetic=True, cutoff=cutoff,
                input_boundary='The input contains completed strict strokes with admission and a left start with qualification. These inputs do not show that raw K-lines give these strokes.',
                b0=b0,l1=l1,l2=l2,classification=classification)


class Svg:
    def __init__(self, title, height):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="{height}" viewBox="0 0 1160 {height}" role="img">',
                      f'<title>{escape(title)}</title>',
                      '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;fill:#18283b;font-size:17px}.small{font-size:14px}</style>',
                      f'<rect width="1160" height="{height}" fill="#fbfcff"/>']
        self.text(28,32,title,22)

    def text(self,x,y,value,size=17,color='#18283b'):
        self.parts.append(f'<text x="{x:.2f}" y="{y:.2f}" style="font-size:{size}px;fill:{color}">{escape(str(value))}</text>')

    def line(self,x1,y1,x2,y2,color='#264b75',dash=False,width=2):
        self.parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="6 4"' if dash else '')+'/>')

    def rect(self,x,y,width,height,color,opacity=.14):
        self.parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" fill="{color}" fill-opacity="{opacity}" stroke="{color}"/>')

    def save(self,path):
        path.write_text('\n'.join(self.parts+['</svg>'])+'\n',encoding='utf-8')


def b0_svg(target, strokes):
    chart=Svg('合成教学 · B1 的 M11 无缺口证据（严格笔资格作为输入）',560)
    x=lambda q:95+q*72
    y=lambda p:395-(p-50)*30
    for p in (50,52,54,56,58):
        chart.line(85,y(p),1040,y(p),'#d8e1ed',True,1)
        chart.text(35,y(p)+5,p,14)
    for s in strokes[:6]:
        color='#205ea6' if int(s['id'][1:])<=3 else '#bc5e16'
        chart.line(x(s['start_at']),y(s['start']),x(s['end_at']),y(s['end']),color,width=3)
        chart.text((x(s['start_at'])+x(s['end_at']))/2-10,440,s['id'],15,color)
        chart.text(x(s['end_at'])-22,y(s['end'])-12,s['end'],14)
    chart.text(65,y(50)+23,'50',14)
    for q in range(0,14,2):
        chart.text(x(q)-8,465,f'q{q}',14)
    chart.line(x(6),100,x(6),410,'#205ea6',True)
    chart.text(x(6)-55,88,'q6 端点 58',16)
    chart.line(x(13),100,x(13),410,'#bc5e16',True)
    chart.text(x(13)-98,88,'q13 资料齐备',16)
    chart.text(28,500,'E1=S2 [51.55,57.9]；E2=S4 [53.1,58]；E3=S6 [53,57.95]；中间高低均更高。',16)
    chart.text(28,531,'E1∩E2=[53.1,57.9] 无缺口；S6 到 q13 才确认 → B1 范围 [50,58]，不是 q6 可用。',16)
    chart.save(target/'00.svg')


def block_svg(target, block, all_b0, number):
    chart=Svg(f'合成教学 · {block["id"]}：成员、核心与延迟封口（C12-F）',565)
    used=[b for b in all_b0 if b['id'] in block['members']+block['witnesses']]
    start,finish=block['start_at'],block['known_at']
    x=lambda q:90+(q-start)/(finish-start)*990
    y=lambda p:375-(p-44)*14
    lo,hi=block['range']; zd,zg=block['core']
    chart.text(28,65,f'原核心 [{zd},{zg}]；全范围 [{lo},{hi}]；边界 q{block["boundary_at"]}；最早可用 q{finish}',17)
    chart.rect(x(start),y(hi),x(block['boundary_at'])-x(start),y(lo)-y(hi),'#71849d',.06)
    chart.rect(x(start),y(zg),x(block['boundary_at'])-x(start),y(zd)-y(zg),'#246cb1')
    wl,wh=block['witness_core']
    chart.rect(x(block['boundary_at']),y(wh),x(used[-1]['end_at'])-x(block['boundary_at']),y(wl)-y(wh),'#be661e')
    for p in (44,48,52,56,60,64):
        chart.line(80,y(p),1095,y(p),'#d8e1ed',True,1)
        chart.text(37,y(p)+4,p,14)
    for i,b in enumerate(used):
        color='#205ea6' if b['id'] in block['members'] else '#bc5e16'
        chart.line(x(b['start_at']),y(b['start']),x(b['end_at']),y(b['end']),color,width=3)
        chart.text(x(b['end_at'])-13,y(b['end'])-9,b['end'],14)
        chart.text((x(b['start_at'])+x(b['end_at']))/2-12,401,b['id'],15,color)
        chart.text(x(b['end_at'])-13,426,f'q{b["end_at"]}',14)
    for q,color in ((block['boundary_at'],'#205ea6'),(finish,'#bc5e16')):
        chart.line(x(q),85,x(q),435,color,True)
    chart.text(x(finish)-58,455,f'q{finish} 才封口',15,'#bc5e16')
    chart.text(28,490,f'蓝色成员 {"—".join((block["members"][0],block["members"][-1]))}；橙色见证 {"、".join(block["witnesses"])} 属于下一块，不计入本块范围。',16)
    chart.text(28,521,f'见证交集 [{wl},{wh}] 与原核心严格分离；须等三个见证各自的 M11 确认，不能只看橙线末端。',16)
    chart.text(28,550,'灰框=全范围；蓝带=固定原核心；橙带=封口见证交集。横轴为顺序资料时刻，不是分钟级别。',15)
    chart.save(target/f'{number:02d}.svg')


def l2_svg(target, result):
    chart=Svg('合成教学 · 同一记录形成 L2 核心，再检查首次返回',720)
    x=lambda q:110+q*5.5
    y=lambda p:380-(p-44)*13
    chart.rect(x(0),y(57),x(150)-x(0),y(50)-y(57),'#327e66')
    for p in (44,48,50,57,60,64):
        chart.line(100,y(p),1100,y(p),'#d8e1ed',True,1)
        chart.text(45,y(p)+5,p,14)
    for i,b in enumerate(result['l1']):
        left,right=x(b['start_at']),x(b['boundary_at'])
        chart.rect(left,y(b['range'][1]),right-left,y(b['range'][0])-y(b['range'][1]),'#205ea6' if i<3 else '#bc5e16',.09)
        chart.line(left,y(b['start']),right,y(b['end']),'#205ea6' if i<3 else '#bc5e16',width=3)
        chart.text(left+8,92,f'{b["id"]} {b["range"]}',15)
        chart.text(left+4,420,f'q{b["start_at"]}—q{b["boundary_at"]}',14)
        chart.line(right,442,x(b['known_at']),442,'#8a5090',True)
        chart.text(left+5,472,f'封口 q{b["known_at"]}',15,'#8a5090')
    for q,label in ((115,'L2 核心可用'),(145,'T4 离开可用'),(175,'T5 返回可用')):
        chart.line(x(q),100,x(q),393,'#8a5090',True)
        chart.text(x(q)-55,505,f'q{q}',15,'#8a5090')
        chart.text(x(q)-65,529,label,14,'#8a5090')
    chart.text(28,573,'L2=[max(50,48,50), min(59,57,61)]=[50,57]；输入为 T1—T3 的全范围，不是三个内部核心。',17)
    chart.text(28,608,'T4：58→48，q145 完成向下离开。T5：48→60，全范围 [48,63]，q175 完成首次返回。',17)
    chart.text(28,643,'返回范围与旧核心相交 [50,57]，高点 63>50 → 本次有限三卖条件失败。',17)
    chart.text(28,678,'T5 最早一笔到 q123 已显示越过 50；q175 是完整返回分类时刻，不是首次发现越界的时刻。',16)
    chart.text(28,707,'绿带=固定 L2 核心；各灰蓝框=完整 L1 范围；斜线只连接块端点，不能替代框内波动。',15)
    chart.save(target/'06.svg')


def export(target):
    target=Path(target)
    target.mkdir(parents=True,exist_ok=True)
    strokes=make_strokes()
    full=build_trace(strokes=strokes)
    def write(name,data):
        (target/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write('teacher-record.json',dict(strokes=strokes,**full))
    for index,cutoff in enumerate((13,55,85,115,174,175),1):
        write(f'step-{index:02d}.json',dict(synthetic=True,convention='C12-F',cutoff=cutoff,
              input_boundary=full['input_boundary'],left_start=dict(price=50,at=0,admitted=True),
              strokes=[s for s in strokes if s['known_at']<=cutoff],
              pending_strokes=[dict(id=s['id'],start=s['start'],end=s['end'],
                                    start_at=s['start_at'],end_at=s['end_at'],
                                    state='observed_not_confirmed') for s in strokes
                               if s['end_at']<=cutoff<s['known_at']]))
    b0_svg(target,strokes)
    for i,b in enumerate(full['l1'],1):
        block_svg(target,b,full['b0'],i)
    l2_svg(target,full)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Write only the new assets for the synthetic Chan trace.')
    parser.parse_args()
    destination=Path(__file__).resolve().parents[1]/'assets'/'chan-trace'
    export(destination)
    print(json.dumps(dict(output=str(destination),l1=5,l2_core=[50,57],decision_at=175)))
