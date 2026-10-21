"""This renderer makes SVG/HTML documents for daily OHLCV observations with only the standard library. It gives the same output for the same input.

Public API (no I/O, imports from build_assets, clock, or network access):
    render_svg(bars, title, annotations=None) -> str
    render_page(bars, title, caption='', annotations=None) -> str

The bars input is a nonempty iterable of mappings. Its dates increase, with no duplicates.
Each row must have date, open, high, low, close, and volume_shares.
The date field has type datetime.date (not datetime) without subclasses, or is a string in canonical YYYY-MM-DD format.
The caller supplies this date as a UTC+8 trading day. It is not a timestamp for conversion.

Numeric fields accept Decimal, decimal strings, int, or finite float (with str).
The values bool, None, NaN, and infinities are incorrect inputs.
All numeric fields, and numeric annotation fields, have a limit of 34 significant digits.
The renderer ignores coefficient zeros at the end of the number when it counts significant digits.

Nonzero values must have an adjusted base-10 exponent in [-100, 100] (1e-100 <= value < 1e101).
If the precision or range is not permitted, validation raises ValueError before the renderer makes the chart.
The renderer sets zero to Decimal(0).

These limits keep guard digits in the 50-digit context for the drawing.
Thus, the scale padding cannot make different permitted price limits equal.

Prices agree with 0 < low <= open/close <= high. Volume is a nonnegative number, and zero is permitted.
If amount_cny is in the input, it is a finite nonnegative number.

The renderer ignores other row fields. It does not serialize these fields.
It makes copies of inputs. It does not put inputs in a different sequence.
It does not add missing inputs or change the inputs.

The annotations input is None or an iterable of mappings.
Each mapping has an optional label of type string and one of these structures:
    {'kind': 'zone', 'low': number, 'high': number}
    {'kind': 'line', 'start_date': date, 'start_price': number,
                     'end_date': date, 'end_price': number}
    {'kind': 'marker', 'date': date, 'price': number}
    {'kind': 'polyline', 'points': [{'date': date, 'price': number}, ...]}

All annotation prices must be finite numbers and >= 0. For zones, low <= high.
Dates for lines and polylines must be in a nondecreasing sequence of trading dates. Polylines must have >= 2 points.
Each annotation date must be in bars. This date must be <= the last date in bars.

The renderer rejects unknown annotation keys, point keys, and kinds. Incorrect input raises ValueError.
The title, caption, and labels must be strings with XML-compatible characters.

SVG uses a 1440-wide viewBox. The height increases when the renderer wraps the title and legend text.
Observations from trading days have equal spaces between their x positions. The renderer does not add bars for holidays without observations.

Price limits include annotations, with padding and a nonnegative lower limit. Volume starts at zero.
OHLC geometry uses Decimal arithmetic and pixel coordinates with six decimals.
The renderer does not set a minimum height for bodies or wicks.

Colors show the relation of close to open:
- Red for a close that is more than the open
- Green for a close that is less than the open
- Gray for no change.
The units are CNY/share and shares.
Price-axis labels show two decimals.
Volume-axis labels show integer shares, with commas between groups (ROUND_HALF_EVEN).
This display rounding does not change geometry, annotation legends, tooltips, or table values without rounding.
The renderer gives no means, indicators, Chan structures, or outcomes.

HTML includes CSS and SVG. It has the initial chart, an optional <details> panel with annotations, and an OHLCV/amount table.
The table values do not change.
The table contains only the supplied rows.

The HTML has no JavaScript, external assets, source objects after serialization, or store for future data.
A hidden annotation panel changes the presentation. It does not prevent access to observations after a cutoff.

For files at the decision stage, supply only the applicable bars.
Do not include outcome annotations, captions, or titles in these files.

The renderer escapes text. It does not interpret text as HTML.
The caller must make sure that provenance, adjustment basis, and historical qualification are correct.
The caller must also make sure that the facts and lesson content in the text are correct.
"""

from collections.abc import Mapping
from datetime import date
from decimal import Context, Decimal, InvalidOperation, localcontext
from html import escape
from unicodedata import east_asian_width


_FONT = "Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif"
_UP, _DOWN, _FLAT = "#c53643", "#087f5b", "#667085"
_INK, _GRID, _NOTE = "#24354b", "#dde5ed", "#7757b5"
_OHLC = ("open", "high", "low", "close")
_MAX_SIGNIFICANT_DIGITS = 34
_MAX_ADJUSTED_EXPONENT = 100
_SCHEMA = {
    "zone": {"low", "high"},
    "line": {"start_date", "start_price", "end_date", "end_price"},
    "marker": {"date", "price"},
    "polyline": {"points"},
}


def _text(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    if any(not (c in "\t\n\r" or "\x20" <= c <= "\ud7ff" or
                "\ue000" <= c <= "\ufffd" or "\U00010000" <= c <= "\U0010ffff") for c in value):
        raise ValueError(f"{field} contains incorrect XML characters")
    return value


def _number(value, field, positive=False):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(f"{field} must be a finite number")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field} must be a finite number") from None
    if not number.is_finite() or number < 0 or (positive and number == 0):
        raise ValueError(f"{field} must be {'a positive finite number' if positive else 'a nonnegative finite number'}")
    if number == 0:
        return Decimal(0)
    digits = number.as_tuple().digits
    significant = len(digits)
    while digits[significant - 1] == 0:
        significant -= 1
    if significant > _MAX_SIGNIFICANT_DIGITS:
        raise ValueError(f"{field} has a significant digit count of more than {_MAX_SIGNIFICANT_DIGITS}, the precision limit.")
    if not -_MAX_ADJUSTED_EXPONENT <= number.adjusted() <= _MAX_ADJUSTED_EXPONENT:
        raise ValueError(f"{field} is not in the permitted range. The nonzero adjusted exponent must be in [-100, 100].")
    return number


def _day(value, field):
    if type(value) is date:
        return value.isoformat()
    if isinstance(value, str):
        try:
            parsed = date.fromisoformat(value)
            if parsed.isoformat() == value:
                return value
        except ValueError:
            pass
    raise ValueError(f"{field} must be a daily UTC+8 date in YYYY-MM-DD format")


def _items(values, field):
    if isinstance(values, (str, bytes, Mapping)):
        raise ValueError(f"{field} must be an iterable of mappings")
    try:
        return list(values)
    except TypeError:
        raise ValueError(f"{field} must be an iterable of mappings") from None


def _bars(values):
    rows = []
    for i, raw in enumerate(_items(values, "bars")):
        if not isinstance(raw, Mapping):
            raise ValueError(f"bars[{i}] must be a mapping")
        row = {"date": _day(raw.get("date"), f"bars[{i}].date")}
        if rows and row["date"] <= rows[-1]["date"]:
            raise ValueError("Each bar date must be after the last bar date. Duplicates are not permitted.")
        for key in (*_OHLC, "volume_shares", "amount_cny"):
            if key == "amount_cny" and key not in raw:
                continue
            row[key] = _number(raw.get(key), f"bars[{i}].{key}", key in _OHLC)
        if not (row["low"] <= min(row["open"], row["close"]) <=
                max(row["open"], row["close"]) <= row["high"]):
            raise ValueError(f"bars[{i}] does not agree with low <= open/close <= high")
        rows.append(row)
    if not rows:
        raise ValueError("The bars must not be empty.")
    return rows


def _annotations(values, rows):
    days = {row["date"] for row in rows}

    def trading_day(value):
        day = _day(value, "annotation date")
        if day > rows[-1]["date"]:
            raise ValueError("The annotation date is after the last bar.")
        if day not in days:
            raise ValueError("The annotation date is not in the bars.")
        return day

    notes = []
    for raw in _items([] if values is None else values, "annotations"):
        if not isinstance(raw, Mapping) or not isinstance(raw.get("kind"), str):
            raise ValueError("The annotation must have a string kind.")
        kind = raw["kind"]
        if kind not in _SCHEMA or set(raw) - (_SCHEMA[kind] | {"kind", "label"}):
            raise ValueError("The annotation kind or fields are unknown.")
        note = {"kind": kind, "label": _text(raw.get("label", ""), "annotation label")}
        if kind == "zone":
            note.update((key, _number(raw.get(key), f"zone.{key}")) for key in ("low", "high"))
            if note["low"] > note["high"]:
                raise ValueError("For the zone, low must be <= high.")
        else:
            if kind == "polyline":
                points = _items(raw.get("points"), "polyline points")
                if len(points) < 2:
                    raise ValueError("The polyline must have a minimum of two points.")
            elif kind == "line":
                points = [dict(date=raw.get(f"{end}_date"), price=raw.get(f"{end}_price"))
                          for end in ("start", "end")]
            else:
                points = [dict(date=raw.get("date"), price=raw.get("price"))]
            normalized = []
            for point in points:
                if not isinstance(point, Mapping) or set(point) != {"date", "price"}:
                    raise ValueError("The annotation points must have only date and price.")
                normalized.append(dict(date=trading_day(point["date"]),
                                       price=_number(point["price"], "annotation price")))
            if any(a["date"] > b["date"] for a, b in zip(normalized, normalized[1:])):
                raise ValueError("The annotation points must have dates in a nondecreasing sequence.")
            note["points"] = normalized
        notes.append(note)
    return notes


def _wrap(value, columns=112):
    """Wrap full-width Chinese and Latin text. Keep all text other than newline characters."""
    lines = []
    for paragraph in value.splitlines() or [""]:
        line, width = "", 0
        for char in paragraph:
            size = 2 if east_asian_width(char) in "WF" else 1
            if width + size > columns:
                lines.append(line)
                line, width = "", 0
            line += char
            width += size
        lines.append(line)
    return lines


def _n(number):
    """The pixel serialization is stable. It does not change with the Decimal context of the caller."""
    result = format(number, ".6f").rstrip("0").rstrip(".")
    return "0" if result in ("", "-0") else result


def _value(number):
    if number == 0:
        return "0"
    # Keep market values easy to read. Prevent decimal expansions with too many decimal places.
    if -6 <= number.adjusted() <= 14:
        result = format(number, "f")
        return result.rstrip("0").rstrip(".") if "." in result else result
    return str(number)


def _svg(rows, title, notes):
    # A new Context also keeps rounding and traps isolated from application settings.
    with localcontext(Context(prec=50)):
        return _draw(rows, title, notes)


def _draw(rows, title, notes):
    title_lines = _wrap(title, 86)
    shift = (len(title_lines) - 1) * 32
    left, right = Decimal(112), Decimal(1320)
    top, bottom = Decimal(150 + shift), Decimal(570 + shift)
    vtop, vbottom = Decimal(640 + shift), Decimal(780 + shift)
    legend_y = 900 + shift
    note_lines = []
    kind_names = {"zone": "水平区", "line": "连线", "marker": "观察点", "polyline": "折线"}
    for i, note in enumerate(notes, 1):
        if note["kind"] == "zone":
            scope = f'{_value(note["low"])}–{_value(note["high"])} 元/股'
        else:
            scope = " → ".join(f'{p["date"]} / {_value(p["price"])}' for p in note["points"])
        label = f'{i}. {kind_names[note["kind"]]}：{note["label"]}（{scope}）'
        note_lines.extend(_wrap(label))
    height = max(940 + shift, legend_y + len(note_lines) * 25 + 30)
    prices = [r[key] for r in rows for key in ("low", "high")]
    for note in notes:
        prices.extend((note["low"], note["high"]) if note["kind"] == "zone"
                      else (p["price"] for p in note["points"]))
    low, high = min(prices), max(prices)
    padding = (high - low) * Decimal("0.08") if high != low else high * Decimal("0.08")
    # If a zero-price annotation is with a positive bar that has no other errors,
    # the high price stays more than zero. Thus, the scale calculation is possible.
    pmin, pmax = max(Decimal(0), low - padding), high + padding
    vmax = max(r["volume_shares"] for r in rows) * Decimal("1.12") or Decimal(1)
    step = (right - left) / len(rows)
    width = min(Decimal(18), step * Decimal("0.62"))
    day_x = {r["date"]: left + (Decimal(i) + Decimal("0.5")) * step
             for i, r in enumerate(rows)}

    def y(price):
        return bottom - (price - pmin) / (pmax - pmin) * (bottom - top)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 {height}" '
           f'role="img" aria-label="{escape(title, quote=True)}" '
           f'font-family="{_FONT}" font-size="17" fill="{_INK}">',
           f'<title>{escape(title)}</title>',
           '<desc>日线开高低收与成交量；交易观察等距排列，红涨绿跌灰平（收盘对开盘）。'
           '标注为调用方给定的解释，未推断未来走势。</desc>',
           f'<rect width="1440" height="{height}" rx="20" fill="#ffffff"/>']

    def text(x, y_pos, content, extra=""):
        out.append(f'<text x="{_n(Decimal(x))}" y="{_n(Decimal(y_pos))}" {extra}>'
                   f'{escape(content)}</text>')

    def line(x1, y1, x2, y2, color=_GRID, extra=""):
        out.append(f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" '
                   f'y2="{_n(y2)}" stroke="{color}" {extra}/>')

    for i, title_line in enumerate(title_lines):
        text(left, 43 + i * 32, title_line, 'font-size="26" font-weight="700"')
    text(left, 82 + shift, f'{rows[0]["date"]} 至 {rows[-1]["date"]} · UTC+8 · 日线 · {len(rows)} 根')
    text(left, 115 + shift, "价格（元/股）", 'font-weight="600"')
    out.append(f'<g class="price-axis" data-min="{pmin}" data-max="{pmax}" '
               f'data-top="{top}" data-bottom="{bottom}">')
    for i in range(6):
        price = pmin + (pmax - pmin) * i / 5
        y_pos = y(price)
        line(left, y_pos, right, y_pos)
        text(left - 14, y_pos + 6, format(price, ".2f"), 'text-anchor="end" font-size="14"')
    line(left, top, left, bottom)
    out.append('</g>')
    text(left, 618 + shift, "成交量（股）", 'font-weight="600"')
    out.append(f'<g class="volume-axis" data-min="0" data-max="{vmax}" '
               f'data-top="{vtop}" data-bottom="{vbottom}">')
    for i in range(3):
        value = vmax * i / 2
        y_pos = vbottom - (vbottom - vtop) * i / 2
        line(left, y_pos, right, y_pos)
        text(left - 14, y_pos + 6, format(value, ",.0f"), 'text-anchor="end" font-size="14"')
    out.append('</g>')
    for row in rows:
        x = day_x[row["date"]]
        color = _UP if row["close"] > row["open"] else _DOWN if row["close"] < row["open"] else _FLAT
        out.append(f'<g class="candle" data-date="{row["date"]}">')
        tooltip = f'{row["date"]} 开 {_value(row["open"])} 高 {_value(row["high"])} '
        tooltip += f'低 {_value(row["low"])} 收 {_value(row["close"])} 元/股；量 {_value(row["volume_shares"])} 股'
        out.append(f'<title>{tooltip}</title>')
        line(x, y(row["high"]), x, y(row["low"]), color, 'class="wick" stroke-width="1.6"')
        if row["close"] == row["open"]:
            line(x - width / 2, y(row["open"]), x + width / 2, y(row["close"]),
                 color, 'class="doji" stroke-width="1.6"')
        else:
            out.append(f'<rect class="body" x="{_n(x - width / 2)}" '
                       f'y="{_n(y(max(row["open"], row["close"])))}" width="{_n(width)}" '
                       f'height="{_n(abs(y(row["open"]) - y(row["close"])))}" fill="{color}"/>')
        out.append('</g>')
        vh = row["volume_shares"] / vmax * (vbottom - vtop)
        out.append(f'<rect class="volume-bar" data-date="{row["date"]}" '
                   f'x="{_n(x - width / 2)}" y="{_n(vbottom - vh)}" '
                   f'width="{_n(width)}" height="{_n(vh)}" fill="{color}">'
                   f'<title>{row["date"]} 成交量 {_value(row["volume_shares"])} 股</title></rect>')
    tick_count = min(7, len(rows))
    indices = [i * (len(rows) - 1) // max(1, tick_count - 1) for i in range(tick_count)]
    for i in indices:
        x = day_x[rows[i]["date"]]
        line(x, vbottom, x, vbottom + 8, _INK)
        # Dates at the ends have inward anchors, also for windows with one or two bars.
        anchor = "start" if x < left + 75 else "end" if x > right - 75 else "middle"
        text(x, vbottom + 36, rows[i]["date"], f'text-anchor="{anchor}" font-size="15"')
    text(left, 856 + shift, "红：收＞开　绿：收＜开　灰：收＝开；成交量以股计。标注编号见下方说明。", 'font-size="16"')

    for i, note in enumerate(notes, 1):
        kind = note["kind"]
        out.append(f'<g class="annotation {kind}" stroke="{_NOTE}" stroke-width="2" fill="none">')
        if kind == "zone":
            y_top, y_bottom = y(note["high"]), y(note["low"])
            if note["high"] == note["low"]:
                out.append(f'<line x1="{left}" y1="{_n(y_top)}" x2="{right}" y2="{_n(y_top)}"/>')
            else:
                out.append(f'<rect x="{left}" y="{_n(y_top)}" width="{right-left}" '
                           f'height="{_n(y_bottom-y_top)}" fill="{_NOTE}" fill-opacity="0.10"/>')
            bx, by = right - 23, (y_top + y_bottom) / 2
        else:
            points = [(day_x[p["date"]], y(p["price"])) for p in note["points"]]
            if kind == "marker":
                bx, by = points[0]
                out.append(f'<circle cx="{_n(bx)}" cy="{_n(by)}" r="7"/>')
            else:
                serialized = " ".join(f'{_n(x)},{_n(yp)}' for x, yp in points)
                out.append(f'<polyline points="{serialized}" stroke-linejoin="round"/>')
                bx, by = points[-1]
            bx, by = bx + 18, by - 18
        bx, by = max(left + 14, min(right - 14, bx)), max(top + 14, min(bottom - 14, by))
        out.append(f'<circle cx="{_n(bx)}" cy="{_n(by)}" r="12" fill="#ffffff"/>')
        text(bx, by + 5, str(i), f'text-anchor="middle" font-size="14" stroke="none" fill="{_NOTE}"')
        out.append('</g>')
    for i, label in enumerate(note_lines):
        text(left, legend_y + i * 25, label, 'font-size="17"')
    out.append('</svg>')
    return "\n".join(out)


def render_svg(bars, title, annotations=None):
    """Return an SVG without dependencies. Refer to the module contract for input and cutoff rules."""
    rows = _bars(bars)
    return _svg(rows, _text(title, "title"), _annotations(annotations, rows))


def render_page(bars, title, caption="", annotations=None):
    """Return a UTF-8 HTML document with all resources with native details controls."""
    rows = _bars(bars)
    title, caption = _text(title, "title"), _text(caption, "caption")
    notes = _annotations(annotations, rows)
    original = _svg(rows, title, [])
    panel = (f'<details class="card"><summary>展开标注图与说明（解释性标注）</summary>'
             f'<div class="chart">{_svg(rows, title, notes)}</div></details>') if notes else ""
    columns = ("date", *_OHLC, "volume_shares", "amount_cny")
    table_rows = []
    for row in rows:
        cells = "".join(f'<td>{escape(row[key] if key == "date" else _value(row[key])) if key in row else "—"}</td>'
                        for key in columns)
        table_rows.append(f'<tr>{cells}</tr>')
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#edf2f7;color:{_INK};font:17px/1.65 {_FONT}}}
main{{max-width:1480px;margin:24px auto;padding:0 18px 36px}}h1{{font-size:28px;line-height:1.4;overflow-wrap:anywhere}}
.card{{background:white;border:1px solid #dce4ee;border-radius:18px;margin:18px 0;padding:18px;box-shadow:0 4px 18px #24354b08}}
.chart{{overflow:auto}}svg{{display:block;width:100%;height:auto;min-width:760px}}
summary{{cursor:pointer;font-weight:600;padding:6px}}summary:focus-visible{{outline:3px solid #7757b5}}
.caption{{white-space:pre-wrap;overflow-wrap:anywhere}}.muted{{color:#526176;font-size:15px}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;white-space:nowrap}}
th,td{{text-align:right;border-bottom:1px solid #e4eaf1;padding:9px 13px}}th:first-child,td:first-child{{text-align:left}}
@media(max-width:700px){{main{{padding:0 10px}}.card{{padding:10px}}h1{{font-size:23px}}}}
</style></head><body><main><header><h1>{escape(title)}</h1>
<p class="muted">UTC+8 日线 · 截至 {rows[-1]["date"]} · 价格：元/股 · 成交量：股 · 成交额：元</p>
<p class="caption">{escape(caption)}</p></header>
<section class="card" aria-label="原始行情图"><h2>原始行情图</h2><div class="chart">{original}</div></section>
{panel}
<details class="card"><summary>展开同一窗口的逐日 OHLCV 数据</summary><div class="chart"><table>
<caption>已传入的日线数据；成交额未提供时显示 —</caption>
<thead><tr><th scope="col">日期（UTC+8）</th><th scope="col">开盘（元/股）</th><th scope="col">最高（元/股）</th>
<th scope="col">最低（元/股）</th><th scope="col">收盘（元/股）</th><th scope="col">成交量（股）</th><th scope="col">成交额（元）</th></tr></thead>
<tbody>{''.join(table_rows)}</tbody></table></div></details>
</main></body></html>'''
