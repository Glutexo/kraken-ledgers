from csv import DictReader

from entry import Entry
from entry import EntryType
from entry import EntryTypeError
from format import format_totals
from format import format_trade_totals
from total import Totals
from total import Trades
from total import TradeTotals


def _read_csv(file):
    for entry in DictReader(file):
        yield entry


def main(input_file):
    unprocessed = []
    totals = Totals()
    trades = Trades()
    for raw_entry in _read_csv(input_file):
        try:
            entry = Entry(raw_entry)
        except EntryTypeError:
            unprocessed.append(raw_entry)
        else:
            totals.add(entry)
            if entry.type in [EntryType.buy, EntryType.sell]:
                trades.add(entry)
    input_file.close()

    if unprocessed:
        print(f"WARNING: {len(unprocessed)} unprocessed entries")
        print()

    for description, totals in totals.totals.items():
        print(f"Total {description.name}:")
        for line in format_totals(totals):
            print(line)
        print()

    trade_totals = TradeTotals()
    for trade in trades.trades.values():
        trade_totals.add(trade)

    print("Total trade:")
    for line in format_trade_totals(trade_totals.totals):
        print(line)
    print()


if __name__ == "__main__":
    from cli import main as cli_main
    cli_main(main)
