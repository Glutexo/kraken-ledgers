__all__ = ["format_total", "format_totals", "format_trade_total", "format_trade_totals"]


def format_amount_with_fee(amount_with_fee):
    return f"{amount_with_fee.amount}, fees: {amount_with_fee.fee}"


def format_total_item(head, tail):
    return f"{head}: {tail}"


def format_total(total):
    asset, amount_with_fee = total

    formatted_amount = format_amount_with_fee(amount_with_fee)
    return format_total_item(asset, formatted_amount)


def format_totals(totals):
    for total in totals.items():
        formatted = format_total(total)
        yield formatted


def format_trade_pair(buy, sell):
    return f"{buy} for {sell}"


def format_trade_total(trade_total):
    key, value = trade_total
    head = format_trade_pair(f"{key[0]:4}", f"{key[1]:4}")
    tail = format_trade_pair(
        format_amount_with_fee(value.buy), format_amount_with_fee(value.sell)
    )
    return format_total_item(head, tail)


def format_trade_totals(trade_totals):
    for trade_total in trade_totals.items():
        formatted = format_trade_total(trade_total)
        yield formatted
