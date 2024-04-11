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
        self.asset = entry["asset"]
        self.amount = Decimal(entry["amount"])
        self.fee = Decimal(entry["fee"])
        self.key = ...

    def validate(self):
        if self.amount == zero:
            raise EntryValueError("Zero amount.")

        if self.fee > 0:
            raise EntryValueError(f"Positive fee amount: {self.fee}")

    def process(self, old_totals):
        new_totals = copy(old_totals)
        old_trades = getattr(new_totals, self.key)

        old_trade = old_trades[self.asset]
        amount = old_trade.amount + abs(self.amount)
        fee = old_trade.fee - self.fee

        old_trades[self.asset] = AmountWithFee(amount,fee)
        return new_totals


class Deposit(Entry):
    def __init__(self, entry):
        super().__init__(entry)
        self.key = "deposits"

    def validate(self):
        super().validate()

        if self.amount < zero:
            raise EntryValueError(
                f"Negative deposit amount: {self.amount}"
            )

class Withdrawal(Entry):
    def __init__(self, entry):
        super().__init__(entry)
        self.key = "withdrawals"

    def validate(self):
        super().validate()

        if self.amount > zero:
            raise EntryValueError(
                f"Positive withdrawal amount: {self.amount}"
            )


class Trade(Entry):
    def __init__(self, entry):
        super().__init__(entry)
        self.key = "buys" if self.amount > zero else "sells"


entry_types = {
    "deposit": Deposit,
    "withdrawal": Withdrawal,
    "trade": Trade,
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
        for entry in _read_csv(input_file):
            try:
                entry = Entry(entry)
            except EntryTypeError:
                unprocessed.append(entry)
            else:
                entry.validate()
                totals = entry.process(totals)

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


if __name__ == "__main__":
    main(argv[1])
