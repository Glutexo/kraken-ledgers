from csv import DictReader

from entry import Entry

__all__ = ["read"]


def read(file):
    for entry in DictReader(file):
        yield Entry(entry)
