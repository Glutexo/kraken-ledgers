from collections import namedtuple

class Trade(namedtuple("Trade", ("buy", "sell"))):
    def __init__(self, trade, entry):
        print(super())
        super().__init__("b2", "s2")


if __name__ == "__main__":
    trade = Trade("b1", "s1")
    trade = Trade(trade, "x")
    print(trade)