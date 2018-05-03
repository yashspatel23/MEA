import json
import time
import traceback

import pytz
import datetime

from arb.utils import epoch
from arb import es, logger
from arb.utils.string import pretty_json


MILLIS_IN_MINUTE = 1000 * 60
MILLIS_IN_HOUR = 1000 * 60 * 60


def get_by_time(s, xh, search_window):
    """
    :param s: "2017-08-21 20:00:00 PDT"
    :param xh: "gdax"
    :param search_window: Milliseconds
    """
    return get_by_timestamp(epoch.to_long(s), xh, search_window)


def get_by_timestamp(t, xh, search_window):
    (t0, t1) = t - search_window, t + search_window
    query = {
        "size": 1,
        "sort": [
            {
                "timestamp__long": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "timestamp__long": {
                                "gte": t0,
                                "lte": t1
                            }
                        }
                    },
                    {
                        "match": {
                            "exchange.raw": xh
                        }
                    },
                    {
                        "match": {
                            "product.raw": "eth-usd"
                        }
                    }
                ]
            }
        }
    }
    result = es.search("order_book", "data", query)

    # print pretty_json(result)
    # def search(self, index=None, doc_type=None, body=None, params=None):

    return result['hits']['hits'][0]['_source']


def buy(amount, ob):
    """
    amount is primarily used to referred to USD.
    More generally, whatever we use to buy the shares with.

    number of shares or None
    """
    remaining = 1.0 * amount
    shares = 0.0
    for ask in ob['asks']:
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
        shares = None

    return shares


def sell(shares, ob):
    """

    (money we got from selling, remaining shares)
    """
    amount = 0
    remaining_shares = shares
    for bid in ob['bids']:
        if remaining_shares == 0: # only walk the order book if remaining > 0
            break

        price = bid['price__num']
        size = bid['size__num']
        max_transaction = 1.0 * price * size
        if max_transaction >= remaining_shares: # we can sell all we got
            amount += 1.0 * price * remaining_shares
            remaining_shares = 0
        else: # we take the whole block
            amount += 1.0 * price * size
            remaining_shares = remaining_shares - size

    if remaining_shares != 0: # cannot sell all the tickers
        amount = None

    return amount


def delta(before_amount, buy_ob, sell_ob):
    shares = buy(before_amount, buy_ob)
    after_amount = sell(shares, sell_ob)

    return (after_amount - before_amount) / before_amount


def delta_buy_gdax_sell_cex(amount, timestamp, search_window):
    gdax_ob = get_by_timestamp(timestamp, 'gdax', search_window)
    cex_ob = get_by_timestamp(timestamp, 'cex', search_window)
    return delta(amount, gdax_ob, cex_ob)


def try_delta_buy_gdax_sell_cex(amount, timestamp, search_window, default = None):
    ans = default
    try:
        gdax_ob = get_by_timestamp(timestamp, 'gdax', search_window)
        cex_ob = get_by_timestamp(timestamp, 'cex', search_window)
        ans = delta(amount, gdax_ob, cex_ob)
    except TypeError:
        stacktrace = traceback.format_exc()
        logger.error(stacktrace)

    return ans


if __name__ == '__main__':
    # earliest time
    "2017-08-20 16:27:09 PDT"
    1503271629989

    search_window = 11000 # 11 seconds
    starting_amount = 1000
    starting_time = 1503271629989
    for i in range(48):
        t = i * MILLIS_IN_HOUR + starting_time
        ts = epoch.to_str(t)
        diff = delta_buy_gdax_sell_cex(starting_amount, t, search_window)

        print 'time is {0}: {1}'.format(ts, str(diff))










