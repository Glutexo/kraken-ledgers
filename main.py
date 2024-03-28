from csv import DictReader
from collections import defaultdict
from collections import namedtuple
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


def _process_entry(entry, old_deposits, old_withdrawals, old_trades):
    new_deposits = totaldict(**old_deposits)
    new_withdrawals = totaldict(**old_withdrawals)
    new_trades = totaldict(**old_trades)

    new_fee = Decimal(entry["fee"])
    if new_fee > 0:
        raise EntryValueError(f"Positive fee amount: {new_fee}")

    if entry["type"] == "deposit":
        new_amount = Decimal(entry["amount"])
        if new_amount < zero:
            raise EntryValueError(
                f"Negative deposit amount: {new_amount}"
            )
        old_deposit = new_deposits[entry["asset"]]
        amount = old_deposit.amount + new_amount
        fee = old_deposit.fee + Decimal(entry["fee"])
        new_deposits[entry["asset"]] = AmountWithFee(amount, fee)
    elif entry["type"] == "withdrawal":
        new_amount = Decimal(entry["amount"])
        if new_amount > zero:
            raise EntryValueError(
                f"Positive withdrawal amount: {new_amount}"
            )

        old_withdrawal = new_withdrawals[entry["asset"]]
        amount = old_withdrawal.amount + new_amount
        fee = old_withdrawal.fee + Decimal(entry["fee"])
        new_withdrawals[entry["asset"]] = AmountWithFee(amount, fee)
    elif entry["type"] == "trade":
        old_trade = new_trades[entry["asset"]]
        amount = old_trade.amount + Decimal(entry["amount"])
        fee = old_trade.fee + Decimal(entry["fee"])
        new_trades[entry["asset"]] = AmountWithFee(amount, fee)
    else:
        raise EntryTypeError(f"Unknown entry type: {entry['type']}")

    return new_deposits, new_withdrawals, new_trades


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
        deposits = totaldict()
        withdrawals = totaldict()
        trades = totaldict()
        for entry in _read_csv(input_file):
            try:
                deposits, withdrawals, trades = _process_entry(
                    entry, deposits, withdrawals, trades
                )
            except EntryTypeError:
                unprocessed.append(entry)

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    for totals, description in [
        (deposits, "deposits"),
        (withdrawals, "withdrawals"),
        (trades, "trades"),
    ]:
        print(f"Total {description}:")
        for line in _format_totals(totals):
            print(line)
        print()


if __name__ == "__main__":
    main(argv[1])
