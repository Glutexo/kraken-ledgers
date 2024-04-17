from enum import IntEnum
from sys import argv
from sys import stderr

__all__ = ["main"]

USAGE = "Usage: main.py <filename>"

ExitCode = IntEnum(
    "ExitCode",
    ["ok", "invalid_usage", "file_not_found", "unsufficent_permissions"],
    start=0,
)


def print_error(*args):
    print(*args, file=stderr)


def main(callback):
    try:
        filename = argv[1]
    except IndexError:
        print_error("No file specified.")
        print_error(USAGE)
        exit(ExitCode.invalid_usage)

    try:
        file = open(filename, "r")
    except FileNotFoundError:
        print_error("File not found.")
        exit(ExitCode.file_not_found)
    except PermissionError:
        print_error("Unsufficent permissions.")
        exit(ExitCode.unsufficent_permissions)

    callback(file)
    file.close()

    exit(ExitCode.ok)


if __name__ == "__main__":
    from main import main as main_main

    main(main_main)
