from csv import DictReader
from collections import defaultdict
from collections import namedtuple
from decimal import Decimal
from enum import Enum
from sys import argv


zero = Decimal("0")


class EntryTypeError(KeyError):
    pass


class EntryValueError(ValueError):
    pass


class AmountWithFee(
    namedtuple(
        "AmountWithFee",
        ("amount", "fee"),
        defaults=(zero, zero)
    )
):
    def __add__(self, other):
        amount = self.amount + other.amount
        fee = self.fee + other.fee
        return AmountWithFee(amount, fee)

    def __abs__(self):
        amount = abs(self.amount)
        fee = abs(self.fee)
        return AmountWithFee(amount, fee)


def totaldict(**kwargs):
    return defaultdict(AmountWithFee, **kwargs)


EntryType = Enum("EntryType", ["deposits", "withdrawals", "buys", "sells"])
Trade = namedtuple("Trade", ("buy", "sell"), defaults=(None, None))
TradeTotal = namedtuple("TradeTotal", ("buys", "sells"), defaults=(AmountWithFee(), AmountWithFee()))


class Totals:
    def __init__(self):
        self.totals = defaultdict(totaldict)

    def add(self, entry):
        self.totals[entry.type][entry.asset] += abs(entry.amount)


class Trades:
    def __init__(self):
        self.trades = defaultdict(Trade)

    def add(self, entry):
        field = "buy" if entry.amount.amount > zero else "sell"
        existing = self.trades[entry.refid]._asdict()
        self.trades[entry.refid] = Trade(**{**existing, field: entry})


class Entry:
    def __init__(self, entry):
        self.refid = entry["refid"]
        self.asset = entry["asset"]
        self.amount = AmountWithFee(Decimal(entry["amount"]), Decimal(entry["fee"]))

        type = entry["type"]
        try:
            entry_type = entry_types[type]
        except KeyError:
            raise EntryTypeError()
        else:
            self.type = entry_type(self)

    def validate(self):
        valid = entry_validations[self.type](self)
        if not valid:
            raise EntryValueError()


entry_types = {
    "deposit": lambda entry: EntryType.deposits,
    "withdrawal": lambda entry: EntryType.withdrawals,
    "trade": lambda entry: EntryType.buys if entry.amount.amount > zero else EntryType.sells,
}

entry_validations = {
    EntryType.deposits: lambda entry: entry.amount.amount > zero,
    EntryType.withdrawals: lambda entry: entry.amount.amount < zero,
    EntryType.buys: lambda entry: entry.amount.amount > zero,
    EntryType.sells: lambda entry: entry.amount.amount < zero,
}


def _format_totals(total):
    lines = []
    for asset, amount_with_fee in total.items():
        lines += [
            f"{asset}: {amount_with_fee.amount}, "
            f"fees: {amount_with_fee.fee}"
        ]
    return lines


def _read_csv(file):
    for entry in DictReader(file):
        yield entry


def main(input_path):
    with open(input_path, "r") as input_file:
        unprocessed = []
        totals = Totals()
        trades = Trades()
        for raw_entry in _read_csv(input_file):
            try:
                entry = Entry(raw_entry)
            except EntryTypeError:
                unprocessed.append(entry)
            else:
                entry.validate()
                totals.add(entry)
                if entry.type in [EntryType.buys, EntryType.sells]:
                    trades.add(entry)

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    for description, totals in totals.totals.items():
        print(f"Total {description.name}:")
        for line in _format_totals(totals):
            print(line)
        print()

    buys = defaultdict(TradeTotal)

    for trade in trades.trades.values():
        buy_key = (trade.buy.asset, trade.sell.asset)

        buy = buys[buy_key].buys + abs(trade.buy.amount)
        sell = buys[buy_key].sells + abs(trade.sell.amount)
        buys[buy_key] = TradeTotal(buy, sell)

    print("Total buys by asset:")
    for key, value in buys.items():
        print(f"{key[0]:4} for {key[1]:4}: {value.buys.amount}, fees {value.buys.fee} for {value.sells.amount}, fees {value.sells.fee}")
    print()


if __name__ == "__main__":
    main(argv[1])
