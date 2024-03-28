from csv import DictReader
from collections import defaultdict
from decimal import Decimal
from sys import argv


def totaldict(**kwargs):
    return defaultdict(Decimal, **kwargs)


def _process_entry(
    entry,
    old_deposits,
    old_deposit_fees,
    old_withdrawals,
    old_withdrawal_fees
):
    new_deposits = totaldict(**old_deposits)
    new_deposit_fees = totaldict(**old_deposit_fees)
    new_withdrawals = totaldict(**old_withdrawals)
    new_withdrawal_fees = totaldict(**old_withdrawal_fees)

    if entry["type"] == "deposit":
        new_deposits[entry["asset"]] += Decimal(entry["amount"])
        new_deposit_fees[entry["asset"]] += Decimal(entry["fee"])
    elif entry["type"] == "withdrawal":
        new_withdrawals[entry["asset"]] += Decimal(entry["amount"])
        new_withdrawal_fees[entry["asset"]] += Decimal(entry["fee"])
    else:
        raise ValueError(f"Unknown entry type: {entry['type']}")

    return new_deposits, new_deposit_fees, new_withdrawals, new_withdrawal_fees


def _format_totals(deposits):
    lines = []
    for asset, amount in deposits.items():
        lines += [f"{asset}: {amount}"]
    return lines


def _read_csv(file):
    for entry in DictReader(file):
        yield entry


def main(input_path):
    with open(input_path, "r") as input_file:
        unprocessed = []
        deposits = totaldict()
        deposit_fees = totaldict()
        withdrawals = totaldict()
        withdrawal_fees = totaldict()
        for entry in _read_csv(input_file):
            try:
                deposits, deposit_fees, withdrawals, withdrawal_fees =\
                    _process_entry(
                        entry,
                        deposits,
                        deposit_fees,
                        withdrawals,
                        withdrawal_fees
                    )
            except ValueError:
                unprocessed.append(entry)

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    print("Total deposits:")
    for line in _format_totals(deposits):
        print(line)
    print()

    print("Total deposit fees:")
    for line in _format_totals(deposit_fees):
        print(line)
    print()

    print("Total withdrawals:")
    for line in _format_totals(withdrawals):
        print(line)
    print()

    print("Total withdrawal fees:")
    for line in _format_totals(withdrawal_fees):
        print(line)


if __name__ == "__main__":
    main(argv[1])
