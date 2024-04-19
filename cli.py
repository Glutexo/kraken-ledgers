from argparse import ArgumentParser
from argparse import FileType

__all__ = ["main"]


def main(callback):
    parser = ArgumentParser(description="Parse Kraken ledgers file.")
    parser.add_argument("--ledgers", type=FileType("r"), default="ledgers.csv")
    args = parser.parse_args()

    callback(args.ledgers)
    args.ledgers.close()


if __name__ == "__main__":
    from main import main as main_main

    main(main_main)
