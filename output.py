from collections import namedtuple
from csv import DictWriter
from itertools import product

from total import Trade

__all__ = ["TradeTotalsWriter"]


FIELD_FUNCTIONS = {
    "asset": lambda key, value: key,
    "amount": lambda key, value: value.amount,
    "fee": lambda key, value: value.fee,
}

Field = namedtuple("Field", ["trade_field", "trade_total_field"])


def populate_fields():
    fields = {}
    fields_product = product(Trade._fields, FIELD_FUNCTIONS.keys())

    for trade_field, trade_total_field in fields_product:
        key = "_".join([trade_field, trade_total_field])
        value = Field(trade_field, trade_total_field)
        fields[key] = value

    return fields


FIELDS = populate_fields()
del populate_fields


class TradeTotalsWriter:
    def __init__(self, file):
        field_names = FIELDS.keys()
        self.writer = DictWriter(
            file,
            fieldnames=field_names,
            delimiter=",",
            lineterminator="\n",
            doublequote=True,
        )
        self.writer.writeheader()

    def write(self, trade_total):
        row = {}
        for row_field, (trade_field, trade_total_field) in FIELDS.items():
            trade_total_key, trade_total_value = trade_total
            key = getattr(trade_total_key, trade_field)
            value = getattr(trade_total_value, trade_field)
            row[row_field] = FIELD_FUNCTIONS[trade_total_field](key, value)

        self.writer.writerow(row)
