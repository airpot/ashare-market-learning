"""These synthetic calculations give the same results for the same inputs. They are for lessons, not order execution.

All amounts use Decimal. The reserve_cost allowance is a fixed allowance for the full position and includes a margin for costs.
The calculation subtracts this allowance from cash and from the planned-loss allowance.
A stop price does not show a fill. An OHLC touch does not show a fill.
"""

from collections.abc import Mapping
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction


def _number(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(f"{name} must be a finite number. A bool is not permitted.")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name} must be a finite number") from None
    if not result.is_finite() or (result <= 0 if positive else result < 0):
        raise ValueError(f"{name} must be {'a positive finite number' if positive else 'a nonnegative finite number'}.")
    return result


def _precision(*values):
    # The digits are sufficient for exact additions and products, also for inputs with different scales.
    return max(28, sum(len(v.as_tuple().digits) + abs(v.as_tuple().exponent)
                       for v in values) + 16)


def validate_bar(bar):
    'Return OHLC values as Decimal. Reject missing values and incorrect geometry.'
    if not isinstance(bar, Mapping):
        raise ValueError("The bar must be a mapping.")
    try:
        values = {k: _number(bar[k], k, positive=True)
                  for k in ('open', 'high', 'low', 'close')}
    except KeyError as error:
        raise ValueError(f"Missing OHLC field: {error.args[0]}") from None
    if not (values['low'] <= min(values['open'], values['close'])
            <= max(values['open'], values['close']) <= values['high']):
        raise ValueError("The prices must agree with low <= open/close <= high.")
    return values


def candle_direction(bar):
    values = validate_bar(bar)
    return ('up' if values['close'] > values['open'] else
            'down' if values['close'] < values['open'] else 'flat')


def daily_return(bar, previous_close):
    """For an unadjusted trading session without a corporate action, the return is (C - prev) / prev."""
    close = validate_bar(bar)['close']
    previous = _number(previous_close, 'previous_close', positive=True)
    with localcontext() as context:
        context.prec = _precision(close, previous)
        return (close - previous) / previous


def size_position(entry, stop, loss_budget, available_cash, lot_size, reserve_cost):
    """Calculate the size of an unleveraged long position as integer lots with downward rounding. A zero position has zero costs.

    This allowance for lessons is not an exchange fee schedule.
    Gaps, slippage, nonfills, and other costs can be more than the planned loss.
    """
    entry = _number(entry, 'entry', positive=True)
    stop = _number(stop, 'stop', positive=True)
    budget = _number(loss_budget, 'loss_budget')
    cash = _number(available_cash, 'available_cash')
    cost = _number(reserve_cost, 'reserve_cost')
    if type(lot_size) is not int or lot_size <= 0:
        raise ValueError("lot_size must be an exact positive integer.")
    if stop >= entry:
        raise ValueError("For a long position, stop < entry is necessary.")
    with localcontext() as context:
        context.prec = _precision(entry, stop, budget, cash, cost)
        distance = entry - stop
        # The rational floor prevents upward division rounding at a lot boundary.
        lots = min(Fraction(max(Decimal(0), budget - cost)) // Fraction(distance * lot_size),
                   Fraction(max(Decimal(0), cash - cost)) // Fraction(entry * lot_size))
        shares = int(lots) * lot_size
        loss = distance * shares + cost if shares else Decimal(0)
        required = entry * shares + cost if shares else Decimal(0)
    return {'shares': shares, 'planned_loss': str(loss),
            'cash_required': str(required), 'loss_is_guaranteed': False}


def _learner_fields(record, keys):
    # Values are scalars only. The function does not make copies of nested teacher material.
    result = {}
    for key in keys:
        value = record.get(key)
        if type(value) in (str, int, float, bool):
            result[key] = value
        elif isinstance(value, Decimal) and value.is_finite():
            result[key] = str(value)
    return result


def visible_replay(case, cutoff):
    """After cutoff bars, make a copy of only the specified learner fields that are known. Do not make copies of more bars.

    The cutoff is a count from zero to N, with zero and N as permitted limits. Bar indexes must be 1..N.
    Availability is event-time metadata. Availability is not a prediction or an execution time.
    The function does not include unknown keys at each level. It also does not include teacher metadata.
    """
    if not isinstance(case, Mapping) or not isinstance(case.get('bars'), list):
        raise ValueError("The case must contain a bars list.")
    count = len(case['bars'])
    if type(cutoff) is not int or not 0 <= cutoff <= count:
        raise ValueError("The cutoff must be an exact integer from 0 to N, with 0 and N as permitted limits.")
    visible = _learner_fields(case, ('title', 'synthetic', 'symbol', 'source',
                                    'timezone', 'interval', 'price_unit',
                                    'volume_unit', 'adjustment', 'assumptions'))
    visible['cutoff'] = cutoff
    visible['bars'] = []
    for index, bar in enumerate(case['bars'][:cutoff], 1):
        if not isinstance(bar, Mapping) or type(bar.get('index')) is not int or bar['index'] != index:
            raise ValueError("The bars must have exact integer indexes in sequence from 1.")
        validate_bar(bar)
        visible['bars'].append(_learner_fields(bar, ('index', 'date', 'open', 'high',
                                                     'low', 'close', 'volume')))
    visible['events'] = []
    events = case.get('events', [])
    if not isinstance(events, list):
        raise ValueError("The events must be a list.")
    for event in events:
        if not isinstance(event, Mapping):
            raise ValueError("The event must be a mapping.")
        available = event.get('available_after_bar')
        if type(available) is not int or not 0 <= available <= count:
            raise ValueError("Event availability must be an exact integer from 0 to N, with 0 and N as permitted limits.")
        if available <= cutoff:
            visible['events'].append(_learner_fields(event, ('available_after_bar', 'date', 'text')))
    return visible


def intrabar_exit(bar, stop, target):
    """Give information only about level touches. OHLC does not show their time sequence."""
    values = validate_bar(bar)
    stop = _number(stop, 'stop', positive=True)
    target = _number(target, 'target', positive=True)
    if stop >= target:
        raise ValueError("For a long position, stop < target is necessary.")
    stopped = values['low'] <= stop <= values['high']
    targeted = values['low'] <= target <= values['high']
    if stopped and targeted:
        return 'ambiguous'
    return 'stop_touched' if stopped else 'target_touched' if targeted else 'neither_touched'
