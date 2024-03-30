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
    def __init__(self, entry):
        self.entry = entry

    def validate(self):
        amount = Decimal(self.entry["amount"])
        if amount == zero:
            raise EntryValueError("Zero amount.")

        new_fee = Decimal(self.entry["fee"])
        if new_fee > 0:
            raise EntryValueError(f"Positive fee amount: {new_fee}")

    def process(self, _old_totals):
        raise NotImplementedError("Entry can’t be processed.")


class Deposit(Entry):
    def validate(self):
        super().validate()

        amount = Decimal(self.entry["amount"])
        if amount < zero:
            raise EntryValueError(
                f"Negative deposit amount: {amount}"
            )

    def process(self, old_totals):
        new_totals = copy(old_totals)
        old_deposit = new_totals.deposits[self.entry["asset"]]

        amount = old_deposit.amount + Decimal(self.entry["amount"])
        fee = old_deposit.fee - Decimal(self.entry["fee"])
        new_totals.deposits[self.entry["asset"]] = AmountWithFee(amount, fee)

        return new_totals


class Withdrawal(Entry):
    def validate(self):
        super().validate()

        amount = Decimal(self.entry["amount"])
        if amount > zero:
            raise EntryValueError(
                f"Positive withdrawal amount: {amount}"
            )

    def process(self, old_totals):
        new_totals = copy(old_totals)
        old_withdrawal = new_totals.withdrawals[self.entry["asset"]]

        amount = old_withdrawal.amount - Decimal(self.entry["amount"])
        fee = old_withdrawal.fee - Decimal(self.entry["fee"])
        new_totals.withdrawals[self.entry["asset"]] = AmountWithFee(amount, fee)

        return new_totals


class Trade(Entry):
    def process(self, old_totals):
        new_amount = Decimal(self.entry["amount"])
        new_totals = copy(old_totals)
        if new_amount > zero:
            return self._process_buy(new_totals)
        else:
            return self._process_sell(new_totals)

    def _process_buy(self, new_totals):
        old_buys = new_totals.buys[self.entry["asset"]]

        amount = old_buys.amount + Decimal(self.entry["amount"])
        fee = old_buys.fee - Decimal(self.entry["fee"])
        new_totals. buys[self.entry["asset"]] = AmountWithFee(amount, fee)

        return new_totals

    def _process_sell(self, new_totals):
        old_sells = new_totals.sells[self.entry["asset"]]

        amount = old_sells.amount - Decimal(self.entry["amount"])
        fee = old_sells.fee - Decimal(self.entry["fee"])
        new_totals. sells[self.entry["asset"]] = AmountWithFee(amount, fee)

        return new_totals


entry_types = {
    "deposit": Deposit,
    "withdrawal": Withdrawal,
    "trade": Trade,
}


def _process_entry(raw_entry, old_totals):
    try:
        entry_type = entry_types[raw_entry["type"]]
    except KeyError:
        raise EntryTypeError(f"Unknown entry type: {raw_entry['type']}")

    entry = entry_type(raw_entry)
    entry.validate()

    new_totals = entry.process(old_totals)
    return new_totals


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
                totals = _process_entry(entry, totals)
            except EntryTypeError:
                unprocessed.append(entry)

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
