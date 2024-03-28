from csv import DictReader
from collections import defaultdict
from decimal import Decimal
from sys import argv


def totaldict(**kwargs):
    return defaultdict(Decimal, **kwargs)


def _process_entry(entry, old_deposits, old_withdrawals):
    new_deposits = totaldict(**old_deposits)
    new_withdrawals = totaldict(**old_withdrawals)
    if entry["type"] == "deposit":
        new_deposits[entry["asset"]] += Decimal(entry["amount"])
    elif entry["type"] == "withdrawal":
        new_withdrawals[entry["asset"]] += Decimal(entry["amount"])
    else:
        raise ValueError(f"Unknown entry type: {entry['type']}")

    return new_deposits, new_withdrawals


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
        withdrawals = totaldict()
        for entry in _read_csv(input_file):
            try:
                deposits, withdrawals = _process_entry(entry, deposits, withdrawals)
            except ValueError:
                unprocessed.append(entry)

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    print("Total deposits:")
    for line in _format_totals(deposits):
        print(line)
    print()

    print("Total withdrawals:")
    for line in _format_totals(withdrawals):
        print(line)


if __name__ == "__main__":
    main(argv[1])
