from collections import namedtuple
from decimal import Decimal


zero = Decimal("0")


class AmountWithFee(
    namedtuple("AmountWithFee", ("amount", "fee"), defaults=(zero, zero))
):
    def __add__(self, other):
        raw_amount = self.amount + other.amount
        decimal_amount = Decimal(raw_amount)

        raw_fee = self.fee + other.fee
        decimal_fee = Decimal(raw_fee)

        return AmountWithFee(decimal_amount, decimal_fee)

    def __abs__(self):
        amount = abs(self.amount)
        fee = abs(self.fee)
        return AmountWithFee(amount, fee)
