from csv import DictReader
from collections import defaultdict
from collections import namedtuple
from decimal import Decimal
from enum import Enum

from cli import main as cli
from numbers import AmountWithFee


class EntryTypeError(KeyError):
    pass


class EntryAmountError(ValueError):
    pass


def totaldict(**kwargs):
    return defaultdict(AmountWithFee, **kwargs)


EntryType = Enum("EntryType", ["deposit", "withdrawal", "buy", "sell"])
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


class Entry:
    def __init__(self, entry):
        self.refid = entry["refid"]
        self.asset = entry["asset"]

        type = entry["type"]
        try:
            entry_type = entry_types[type]
        except KeyError:
            raise EntryTypeError()

        amount = Decimal(entry["amount"])
        fee = Decimal(entry["fee"])
        amount_with_fee = AmountWithFee(amount, fee)
        self.type = entry_type(amount_with_fee)

        valid = entry_validations[self.type](amount_with_fee)
        if not valid:
            raise EntryAmountError()

        self.amount = abs(amount_with_fee)


entry_types = {
    "deposit": lambda amount: EntryType.deposit,
    "withdrawal": lambda amount: EntryType.withdrawal,
    "trade": lambda amount: EntryType.buy if amount.amount > zero else EntryType.sell,
    "spend": lambda amount: EntryType.sell,
    "receive": lambda amount: EntryType.buy,
}

entry_validations = {
    EntryType.deposit: lambda amount: amount.amount > zero,
    EntryType.withdrawal: lambda amount: amount.amount < zero,
    EntryType.buy: lambda amount: amount.amount > zero,
    EntryType.sell: lambda amount: amount.amount < zero,
}


def _format_totals(total):
    lines = []
    for asset, amount_with_fee in total.items():
        lines += [f"{asset}: {amount_with_fee.amount}, " f"fees: {amount_with_fee.fee}"]
    return lines


def _read_csv(file):
    for entry in DictReader(file):
        yield entry


def main(input_file):
    unprocessed = []
    totals = Totals()
    trades = Trades()
    for raw_entry in _read_csv(input_file):
        try:
            entry = Entry(raw_entry)
        except EntryTypeError:
            unprocessed.append(entry)
        else:
            totals.add(entry)
            if entry.type in [EntryType.buy, EntryType.sell]:
                trades.add(entry)
    input_file.close()

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    for description, totals in totals.totals.items():
        print(f"Total {description.name}:")
        for line in _format_totals(totals):
            print(line)
        print()

    trade_totals = defaultdict(TradeTotal)

    for trade in trades.trades.values():
        pair = (trade.buy.asset, trade.sell.asset)

        buy = trade_totals[pair].buy + trade.buy.amount
        sell = trade_totals[pair].sell + trade.sell.amount
        trade_totals[pair] = TradeTotal(buy, sell)

    print("Total trades by asset:")
    for key, value in trade_totals.items():
        print(
            f"{key[0]:4} for {key[1]:4}: {value.buy.amount}, fees {value.buy.fee} for {value.sell.amount}, fees {value.sell.fee}"
        )
    print()


if __name__ == "__main__":
    cli(main)
