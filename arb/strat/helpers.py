from arb import logger, LIMIT_PRICE_BUFFER_IN_FRACTION, LIMIT_PRICE_BUFFER_IN_USD


def compute_buy(amount, ob):
    """
    compute the number of shares we get for this amount of usd

    :return number of shares or None
    """
    remaining = 1.0 * amount
    shares = 0.0
    for ask in ob.js['asks']:
        if remaining == 0: # only walk the order book if remaining > 0
            break

        price = ask['price__num']
        size = ask['size__num']
        max_amount = 1.0 * price * size
        if max_amount >= remaining: # we can fill it up here
            shares += 1.0 * remaining / price
            remaining = 0
        elif max_amount < remaining: # we take the whole block
            shares += size
            remaining = remaining - 1.0 * price * size

    if remaining != 0: # cannot use up all the money
        shares = None # TODO
        raise RuntimeError('Cannot compute buy')

    return shares


def compute_sell(shares, ob):
    """
    how much money we got for the number of shares we are selling
    against an order book
    """
    amount = 0
    remaining_shares = shares
    for bid in ob.js['bids']:
        if remaining_shares == 0: # only walk the order book if remaining > 0
            break

        price = bid['price__num']
        size = bid['size__num']
        if size >= remaining_shares: # we can sell all the remaining shares
            amount += 1.0 * price * remaining_shares
            remaining_shares = 0
        else: # we take the whole block
            amount += 1.0 * price * size
            remaining_shares = remaining_shares - size

    if remaining_shares != 0: # cannot sell all the tickers
        amount = None # TODO
        raise RuntimeError('Cannot compute sell')

    return amount


def compute_shares_needed(amount, ob):
    """
    Number of shares needed to create the necessary cash.
    """
    remaining = 1.0 * amount
    shares = 0.0

    # attempting to sell shares
    for bid in ob.js['bids']:
        if remaining == 0: # only walk the order book if remaining > 0
            break

        price = bid['price__num']
        size = bid['size__num']
        max_amount = 1.0 * price * size
        if max_amount >= remaining: # we finish selling
            shares += 1.0 * remaining / price
            remaining = 0
        elif max_amount < remaining: # we take the whole block
            shares += size
            remaining = remaining - 1.0 * price * size

    if remaining != 0: # cannot use up all the money
        shares = None # TODO
        raise RuntimeError('Computation fails.')

    return shares


def compute_usd_spent(shares, ob):
    """
    USD needed to buy shares
    """
    amount = 0.0
    remaining_shares = shares
    for ask in ob.js['asks']:
        if remaining_shares == 0: # only walk the order book if remaining > 0
            break

        price = ask['price__num'] * 1.0
        size = ask['size__num'] * 1.0

        if size >= remaining_shares: # we buy all we needed
            amount += 1.0 * price * remaining_shares
            remaining_shares = 0
        else: # we take the whole block
            amount += 1.0 * price * size
            remaining_shares = remaining_shares - size

    if remaining_shares != 0: # cannot sell all the shares
        amount = None # TODO
        raise RuntimeError('Cannot compute buy')

    return amount


def compute_usd_made(shares, ob):
    """
    USD made from selling shares
    """
    amount = 0.0
    remaining_shares = shares
    for ask in ob.js['bids']:
        if remaining_shares == 0: # only walk the order book if remaining > 0
            break

        price = ask['price__num'] * 1.0
        size = ask['size__num'] * 1.0

        if size >= remaining_shares: # we sell all the remaining_shars
            amount += 1.0 * price * remaining_shares
            remaining_shares = 0
        else: # we take the whole block
            amount += 1.0 * price * size
            remaining_shares = remaining_shares - size

    if remaining_shares != 0: # cannot sell all the shares
        raise RuntimeError('Cannot compute sell')

    return amount


def compute_delta__withdraw_cash(amount, base_exh_ob, foreign_exh_ob):
    shares = compute_buy(amount, base_exh_ob)
    usd_got = compute_sell(shares, foreign_exh_ob)
    delta = (usd_got - amount) / amount
    return delta


def compute_delta__deposit_cash(amount, base_exh_ob, foreign_exh_ob):
    shares = compute_shares_needed(amount, base_exh_ob)
    usd_spent = compute_usd_spent(shares, foreign_exh_ob)
    delta = (usd_spent - amount) / amount
    return delta


def compute_sell_value(shares, ob, more_than=200000):
    """
    If it is at least max, return the value of more_than.

    """
    # TODO: need to write the logic for the max
    return compute_sell(shares, ob)


def compute_buy_stopping_price(shares, ob):
    stopping_price = None
    remaining_shares = shares
    for ask in ob.js['asks']:
        if remaining_shares == 0: # only walk the order book if remaining > 0
            break

        size = ask['size__num']
        if size >= remaining_shares:  # we can fill it up here
            remaining_shares = 0
            stopping_price = ask['price__num']
        else:  # we take the whole block
            remaining_shares = remaining_shares - size

    if remaining_shares != 0:
        raise RuntimeError('insufficient orderbook depth or liquidity')
    if stopping_price is None:
        raise RuntimeError('unknown calculation error')

    return stopping_price


def compute_sell_stopping_price(shares, ob):
    stopping_price = None
    remaining_shares = shares
    for ask in ob.js['bids']:
        if remaining_shares == 0: # only walk the order book if remaining > 0
            break

        size = ask['size__num']
        if size >= remaining_shares:  # we can fill it up here
            remaining_shares = 0
            stopping_price = ask['price__num']
        else:  # we take the whole block
            remaining_shares = remaining_shares - size

    if remaining_shares != 0:
        raise RuntimeError('insufficient orderbook depth or liquidity')
    if stopping_price is None:
        raise RuntimeError('unknown calculation error')

    return stopping_price


def compute_buy_upperbound(shares, ob):
    """
    What should be the appropriate limit price?

    Whichever is higher:
    -- stopping price for (2 * shares) * 1.001     (+ 0.1%)
    -- stopping price for (2 * shares) + 0.3       (+ USD 0.1)
    """
    buffer_multiply = 1.0 + LIMIT_PRICE_BUFFER_IN_FRACTION
    buffer_add = LIMIT_PRICE_BUFFER_IN_USD
    shares = 2.0 * shares
    stopping_price = compute_buy_stopping_price(shares, ob)

    upperbounds = [stopping_price * buffer_multiply, stopping_price + buffer_add]
    upperbound = max(upperbounds)
    return upperbound


def compute_sell_lowerbound(shares, ob):
    """
    What should be the appropriate limit price?

    Whichever is lower:
    -- stopping price for (2 * shares) *  0.009   (- 0.1%)
    -- stopping price for (2 * shares) - 0.3      (- USD 0.1)
    """
    buffer_multiply = 1.0 - LIMIT_PRICE_BUFFER_IN_FRACTION
    buffer_subtract = LIMIT_PRICE_BUFFER_IN_USD
    shares = 2.0 * shares
    stopping_price = compute_sell_stopping_price(shares, ob)

    lowerbounds = [stopping_price * buffer_multiply, stopping_price - buffer_subtract]
    lowerbound = min(lowerbounds)
    return lowerbound


if __name__ == '__main__':
    pass

