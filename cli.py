from argparse import ArgumentParser
from argparse import FileType

__all__ = ["main"]


def main(callback):
    parser = ArgumentParser(
        description="Parse Kraken ledgers file. See "
        "https://tinyurl.com/kraken-ledgers for more details."
    )
    parser.add_argument("--ledgers", type=FileType("r"), default="ledgers.csv")
    parser.add_argument("--trades", type=FileType("w"), default="trades.csv")
    args = parser.parse_args()

    callback(args.ledgers, args.trades)
    args.ledgers.close()


if __name__ == "__main__":
    from main import main as main_main

    main(main_main)
