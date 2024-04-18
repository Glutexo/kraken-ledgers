from csv import DictWriter
from itertools import product

from total import Trade


def make_field_functions():
    entry_field_functions = {
        "asset": lambda key, value: key,
        "amount": lambda key, value: value.amount,
        "fee": lambda key, value: value.fee,
    }

    def make_product_function(trade_fld, entry_fld):
        def product_func(trade_total):
            base_field_function = entry_field_functions[entry_fld]

            trade_total_key, trade_total_value = trade_total
            key = getattr(trade_total_key, trade_fld)
            value = getattr(trade_total_value, trade_fld)

            return base_field_function(key, value)

        return product_func

    product_functions = {}
    fields_product = product(Trade._fields, entry_field_functions.keys())
    for trade_field, entry_field in fields_product:
        product_field_name = f"{trade_field}_{entry_field}"
        product_function = make_product_function(trade_field, entry_field)
        product_functions[product_field_name] = product_function

    return product_functions


FIELD_FUNCTIONS = make_field_functions()
del make_field_functions


class TradeTotalsWriter:
    def __init__(self, file):
        fieldnames = FIELD_FUNCTIONS.keys()
        self.writer = DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter=",",
            lineterminator="\n",
            doublequote=True,
        )
        self.writer.writeheader()

    def write(self, trade_total):
        row = {}
        for field, function in FIELD_FUNCTIONS.items():
            row[field] = function(trade_total)

        self.writer.writerow(row)
