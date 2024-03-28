from csv import DictReader
from decimal import Decimal
from sys import argv


def _process_entry(entry, old_deposits):
    new_deposits = {**old_deposits}
    if entry["type"] == "deposit":
        if entry["asset"] not in new_deposits:
            new_deposits[entry["asset"]] = Decimal("0")
        new_deposits[entry["asset"]] += Decimal(entry["amount"])
    else:
        raise ValueError(f"Unknown entry type: {entry['type']}")

    return new_deposits


def _format_deposits(deposits):
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
        deposits = {}
        for entry in _read_csv(input_file):
            try:
                deposits = _process_entry(entry, deposits)
            except ValueError:
                unprocessed.append(entry)

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    print("Total deposits:")
    for line in _format_deposits(deposits):
        print(line)


if __name__ == "__main__":
    main(argv[1])
