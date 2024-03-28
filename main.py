from csv import DictReader
from collections import defaultdict
from collections import namedtuple
from decimal import Decimal
from sys import argv


class AmountWithFee(
    namedtuple(
        "AmountWithFee",
        ("amount", "fee"),
        defaults=(Decimal("0"), Decimal("0"))
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

    if entry["type"] == "deposit":
        old_deposit = new_deposits[entry["asset"]]
        amount = old_deposit.amount + Decimal(entry["amount"])
        fee = old_deposit.fee + Decimal(entry["fee"])
        new_deposits[entry["asset"]] = AmountWithFee(amount, fee)
    elif entry["type"] == "withdrawal":
        old_withdrawal = new_withdrawals[entry["asset"]]
        amount = old_withdrawal.amount + Decimal(entry["amount"])
        fee = old_withdrawal.fee + Decimal(entry["fee"])
        new_withdrawals[entry["asset"]] = AmountWithFee(amount, fee)
    elif entry["type"] == "trade":
        old_trade = new_trades[entry["asset"]]
        amount = old_trade.amount + Decimal(entry["amount"])
        fee = old_trade.fee + Decimal(entry["fee"])
        new_trades[entry["asset"]] = AmountWithFee(amount, fee)
    else:
        raise ValueError(f"Unknown entry type: {entry['type']}")

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
            except ValueError:
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
