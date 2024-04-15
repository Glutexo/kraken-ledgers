from csv import DictReader
from collections import defaultdict
from collections import namedtuple
from copy import copy
from decimal import Decimal
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


class Totals(namedtuple(
    "Totals",
    ("deposits", "withdrawals", "buys", "sells"),
    defaults=(totaldict(), totaldict(), totaldict(), totaldict())
)):
    def __copy__(self):
        return Totals(
            totaldict(**self.deposits),
            totaldict(**self.withdrawals),
            totaldict(**self.buys),
            totaldict(**self.sells),
        )


Trade = namedtuple("Trade", ("buy", "sell"), defaults=(None, None))
TradeTotal = namedtuple("TradeTotal", ("buys", "sells"), defaults=(AmountWithFee(), AmountWithFee()))


class Trades:
    def __init__(self):
        self.trades = defaultdict(Trade)

    def add(self, entry):
        field = "buy" if entry.amount.amount > zero else "sell"
        existing = self.trades[entry.refid]._asdict()
        self.trades[entry.refid] = Trade(**{**existing, field: entry})


class Entry:
    def __new__(cls, entry):
        if cls is not Entry:
            return super().__new__(cls)

        try:
            entry_type = entry_types[entry["type"]]
        except KeyError:
            raise EntryTypeError(f"Unknown entry type: {entry['type']}")

        return entry_type(entry)

    def __init__(self, entry):
        self.refid = entry["refid"]
        self.asset = entry["asset"]
        self.amount = AmountWithFee(Decimal(entry["amount"]), Decimal(entry["fee"]))
        self.key = ...

    def validate(self):
        if self.amount == zero:
            raise EntryValueError("Zero amount.")

        if self.amount.fee > 0:
            raise EntryValueError(f"Positive fee amount: {self.amount.fee}")

    def process(self, old_totals):
        new_totals = copy(old_totals)
        old_trades = getattr(new_totals, self.key)
        old_trades[self.asset] += abs(self.amount)
        return new_totals


class DepositEntry(Entry):
    def __init__(self, entry):
        super().__init__(entry)
        self.key = "deposits"

    def validate(self):
        super().validate()

        if self.amount.amount < zero:
            raise EntryValueError(
                f"Negative deposit amount: {self.amount}"
            )


class WithdrawalEntry(Entry):
    def __init__(self, entry):
        super().__init__(entry)
        self.key = "withdrawals"

    def validate(self):
        super().validate()

        if self.amount.amount > zero:
            raise EntryValueError(
                f"Positive withdrawal amount: {self.amount}"
            )


class TradeEntry(Entry):
    def __init__(self, entry):
        super().__init__(entry)
        self.key = "buys" if self.amount.amount > zero else "sells"


entry_types = {
    "deposit": DepositEntry,
    "withdrawal": WithdrawalEntry,
    "trade": TradeEntry,
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
                totals = entry.process(totals)
                if entry.key in ["buys", "sells"]:
                    trades.add(entry)

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    for totals, description in [
        (totals.deposits, "deposits"),
        (totals.withdrawals, "withdrawals"),
        (totals.buys, "buys"),
        (totals.sells, "sells"),
    ]:
        print(f"Total {description}:")
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
