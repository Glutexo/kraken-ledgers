from decimal import Decimal

__all__ = ["zero", "AmountWithFee"]

zero = Decimal("0")


class AmountWithFee:
    def __init__(self, amount=zero, fee=zero):
        self.amount = Decimal(amount)
        self.fee = Decimal(fee)

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
