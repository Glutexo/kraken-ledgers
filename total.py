from collections import defaultdict
from collections import namedtuple

from amount import AmountWithFee


__all__ = ["totaldict", "Trade", "TradeTotal", "Totals", "Trades", "TradeTotals"]


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


class TradeTotals:
    def __init__(self):
        self.totals = defaultdict(TradeTotal)

    def add(self, trade):
        pair = Trade(trade.buy.asset, trade.sell.asset)

        buy = self.totals[pair].buy + trade.buy.amount
        sell = self.totals[pair].sell + trade.sell.amount
        self.totals[pair] = TradeTotal(buy, sell)
