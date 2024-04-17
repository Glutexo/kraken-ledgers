from collections import defaultdict
from collections import namedtuple

from amount import AmountWithFee


def totaldict(**kwargs):
    return defaultdict(AmountWithFee, **kwargs)


Trade = namedtuple("Trade", ("buy", "sell"), defaults=(None, None))
TradeTotal = namedtuple(
    "TradeTotal", ("buy", "sell"), defaults=(AmountWithFee(), AmountWithFee())
)


class Totals:
    def __init__(self):
        self.totals = defaultdict(totaldict)

    def add(self, entry):
        self.totals[entry.type][entry.asset] += entry.amount


class Trades:
    def __init__(self):
        self.trades = defaultdict(Trade)

    def add(self, entry):
        existing = self.trades[entry.refid]._asdict()
        type = entry.type.name
        self.trades[entry.refid] = Trade(**{**existing, type: entry})
