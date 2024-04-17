from collections import namedtuple
from decimal import Decimal


zero = Decimal("0")


class AmountWithFee(
    namedtuple("AmountWithFee", ("amount", "fee"), defaults=(zero, zero))
):
    def __add__(self, other):
        amount = self.amount + other.amount
        fee = self.fee + other.fee
        return AmountWithFee(amount, fee)

    def __abs__(self):
        amount = abs(self.amount)
        fee = abs(self.fee)
        return AmountWithFee(amount, fee)
