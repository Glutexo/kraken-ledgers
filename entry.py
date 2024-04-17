from enum import Enum

from amount import AmountWithFee
from amount import zero


class EntryTypeError(KeyError):
    pass


class EntryAmountError(ValueError):
    pass


class Entry:
    def __init__(self, entry):
        self.refid = entry["refid"]
        self.asset = entry["asset"]

        type = entry["type"]
        try:
            entry_type = entry_types[type]
        except KeyError:
            raise EntryTypeError()

        amount_with_fee = AmountWithFee(entry["amount"], entry["fee"])
        self.type = entry_type(amount_with_fee)

        valid = entry_validations[self.type](amount_with_fee)
        if not valid:
            raise EntryAmountError()

        self.amount = abs(amount_with_fee)


EntryType = Enum("EntryType", ["deposit", "withdrawal", "buy", "sell"])

entry_types = {
    "deposit": lambda amount: EntryType.deposit,
    "withdrawal": lambda amount: EntryType.withdrawal,
    "trade": lambda amount: EntryType.buy if amount.amount > zero else EntryType.sell,
    "spend": lambda amount: EntryType.sell,
    "receive": lambda amount: EntryType.buy,
}

entry_validations = {
    EntryType.deposit: lambda amount: amount.amount > zero,
    EntryType.withdrawal: lambda amount: amount.amount < zero,
    EntryType.buy: lambda amount: amount.amount > zero,
    EntryType.sell: lambda amount: amount.amount < zero,
}