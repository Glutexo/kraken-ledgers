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
    ("deposits", "withdrawals", "trades"),
    defaults=(totaldict(), totaldict(), totaldict())
)):
    def __copy__(self):
        return Totals(
            totaldict(**self.deposits),
            totaldict(**self.withdrawals),
            totaldict(**self.trades),
        )


def _process_deposit(entry, old_totals):
    new_amount = Decimal(entry["amount"])
    if new_amount < zero:
        raise EntryValueError(
            f"Negative deposit amount: {new_amount}"
        )

    new_totals = copy(old_totals)
    old_deposit = new_totals.deposits[entry["asset"]]

    amount = old_deposit.amount + new_amount
    fee = old_deposit.fee - Decimal(entry["fee"])
    new_totals.deposits[entry["asset"]] = AmountWithFee(amount, fee)

    return new_totals


def _process_withdrawal(entry, old_totals):
    new_amount = Decimal(entry["amount"])
    if new_amount > zero:
        raise EntryValueError(
            f"Positive withdrawal amount: {new_amount}"
        )

    new_totals = copy(old_totals)
    old_withdrawal = new_totals.withdrawals[entry["asset"]]

    amount = old_withdrawal.amount - new_amount
    fee = old_withdrawal.fee - Decimal(entry["fee"])
    new_totals.withdrawals[entry["asset"]] = AmountWithFee(amount, fee)

    return new_totals


def _process_trade(entry, old_totals):
    new_totals = copy(old_totals)
    old_trade = new_totals.trades[entry["asset"]]

    amount = old_trade.amount + Decimal(entry["amount"])
    fee = old_trade.fee - Decimal(entry["fee"])
    new_totals.trades[entry["asset"]] = AmountWithFee(amount, fee)

    return new_totals


entry_type_processors = {
    "deposit": _process_deposit,
    "withdrawal": _process_withdrawal,
    "trade": _process_trade,
}


def _process_entry(entry, old_totals):
    new_totals = Totals()

    new_fee = Decimal(entry["fee"])
    if new_fee > 0:
        raise EntryValueError(f"Positive fee amount: {new_fee}")

    try:
        processor = entry_type_processors[entry["type"]]
    except KeyError:
        raise EntryTypeError(f"Unknown entry type: {entry['type']}")

    new_totals = processor(entry, old_totals)
    return new_totals


def _format_totals(deposits):
    lines = []
    for asset, amount_with_fee in deposits.items():
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
        (totals.trades, "trades"),
    ]:
        print(f"Total {description}:")
        for line in _format_totals(totals):
            print(line)
        print()


if __name__ == "__main__":
    main(argv[1])
