__all__ = ["format_total", "format_totals", "format_trade_total", "format_trade_totals"]


def format_amount_with_fee(amount_with_fee):
    return f"{amount_with_fee.amount}, fee: {amount_with_fee.fee}"


def format_total_item(head, tail):
    return f"{head}: {tail}"


def format_total(total):
    asset, amount_with_fee = total

    formatted_amount = format_amount_with_fee(amount_with_fee)
    return format_total_item(asset, formatted_amount)


def format_totals(totals):
    for total in totals.items():
        yield format_total(total)


def format_trade_asset(asset):
    return f"{asset:4}"


def format_trade(trade, format_trade_item):
    buy = format_trade_item(trade.buy)
    sell = format_trade_item(trade.sell)
    return f"{buy} for {sell}"


def format_trade_total(trade_total):
    key, value = trade_total
    head = format_trade(key, format_trade_asset)
    tail = format_trade(value, format_amount_with_fee)
    return format_total_item(head, tail)


def format_trade_totals(trade_totals):
    for trade_total in trade_totals.items():
        yield format_trade_total(trade_total)
