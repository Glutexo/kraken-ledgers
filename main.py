from entry import EntryType
from format import format_totals
from format import format_trade_totals
from ledgers import read
from total import Totals
from total import Trades
from total import TradeTotals


def main(input_file):
    totals = Totals()
    trades = Trades()

    for entry in read(input_file):
        totals.add(entry)
        if entry.type in [EntryType.buy, EntryType.sell]:
            trades.add(entry)
    input_file.close()

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
