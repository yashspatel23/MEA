import json
import time
from abc import abstractmethod
from collections import OrderedDict

from arb import es, EXCHANGE_NAME_GDAX, EXCHANGE_NAME_CEX, \
    GDAX_API_URL, CEX_API_URL, ES_GET_TIMEOUT, \
    ES_SEARCH_TIMEOUT, logger  # TODO: make this an explicit argument
from arb.core.exh.accounts import TradingAccount
from arb.core.exh.clients import GdaxClient, CexClient
from arb.core.models import OrderBookModel, AccountModel
from arb.strat import helpers
from arb.utils import epoch
from arb.utils.string import pretty_json


def default_es_get_params():
    return {
        'request_timeout': ES_GET_TIMEOUT,
    }


def default_es_search_params():
    return {
        'request_timeout': ES_SEARCH_TIMEOUT,
    }


class BacktestingTradingAccount(TradingAccount):
    def __init__(self, account_uid, exh):
        super(BacktestingTradingAccount, self).__init__(account_uid, exh)

    @classmethod
    def sleep(cls, seconds):
        """
        No need to sleep for backtesting
        """
        return None

    @classmethod
    def get_snapping_timestamp(cls, timestamp=-1):
        return timestamp

    def _buy_ticker(self, ticker, shares, timestamp=-1):
        if timestamp == -1:
            raise NotImplementedError()  # safety

        ob = self.get_order_book(ticker=ticker, timestamp=timestamp)
        amount = helpers.compute_usd_spent(shares, ob)

        # update account
        account = self.get_account()
        account.js['usd__num'] = account.js['usd__num'] - amount
        account.js['eth__num'] = account.js['eth__num'] + shares
        account.db_save(es)

        return amount

    def _sell_ticker(self, ticker, shares, timestamp=-1):
        if timestamp == -1:
            raise NotImplementedError()  # safety

        ob = self.get_order_book(ticker=ticker, timestamp=timestamp)
        amount = helpers.compute_sell(shares, ob)

        # update account
        account = self.get_account()
        account.js['usd__num'] = account.js['usd__num'] + amount
        account.js['eth__num'] = account.js['eth__num'] - shares
        account.db_save(es)

        return amount

    def _limit_buy_eth(self, shares, timestamp):
        self._buy_ticker('eth-usd', shares, timestamp)

    def _limit_sell_eth(self, shares, timestamp):
        self._sell_ticker('eth-usd', shares, timestamp)

    def get_order_book(self, product_id=None, ticker=None, timestamp=-1):
        """
        Search from timstamp, and work backward until one is found.

        :return: OrderbookModel
        """
        if timestamp == -1:
            timestamp = epoch.current_milli_time()

        search_window = 11000 # 11 seconds
        search_window = 15 * 60000 # 15 minutes
        search_window = 1000 * 60000 # 1000 minutes
        (t0, t1) = timestamp - search_window, timestamp + 500
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
                                "exchange.raw": self.exh
                            }
                        },
                        {
                            "match": {
                                "product.raw": 'eth-usd'
                            }
                        }
                    ]
                }
            }
        }
        params = default_es_get_params()
        result = es.search("order_book", "data", query, params=params)

        # validation
        if result['hits']['total'] == 0:
            logger.info(pretty_json(query))
            logger.info(timestamp)
            logger.info(epoch.to_str(timestamp))
            raise RuntimeError('Cannot find orderbook in backtesting')

        ob_js = result['hits']['hits'][0]['_source']
        ob = OrderBookModel.build(ob_js)
        return ob

    def place_limit_order(self, side, ticker, price, shares, timestamp=-1):
        if side == 'buy':
            self._limit_buy_eth(shares, timestamp=timestamp)
        elif side == 'sell':
            self._limit_sell_eth(shares, timestamp=timestamp)
        else:
            raise RuntimeError('unknown market side.')


class MockTradingAccount(TradingAccount):
    def __init__(self, account_uid, exh):
        self.gdax_client = GdaxClient(GDAX_API_URL, None, None, None)
        self.cex_client = CexClient(CEX_API_URL, None, None, None)
        super(MockTradingAccount, self).__init__(account_uid, exh)

    @classmethod
    def get_snapping_timestamp(cls, timestamp=-1):
        return -1

    @classmethod
    def sleep(cls, seconds):
        time.sleep(seconds)
        return None

    def _get_exh_client(self):
        if self.exh == EXCHANGE_NAME_GDAX:
            exh_client = self.gdax_client
        elif self.exh == EXCHANGE_NAME_CEX:
            exh_client = self.cex_client
        else:
            raise RuntimeError('unknown exchange')
        return exh_client

    def _buy_eth(self, shares, ob):
        amount = helpers.compute_usd_spent(shares, ob)

        # update account
        account = self.get_account()
        account.js['usd__num'] = account.js['usd__num'] - amount
        account.js['eth__num'] = account.js['eth__num'] + shares
        account.db_save(es)

        return amount

    def _sell_eth(self, shares, ob):
        amount = helpers.compute_sell(shares, ob)

        # update account
        account = self.get_account()
        account.js['usd__num'] = account.js['usd__num'] + amount
        account.js['eth__num'] = account.js['eth__num'] - shares
        account.db_save(es)

        return amount

    def get_order_book(self, product_id=None, ticker=None, timestamp=-1):
        if timestamp != -1:
            raise RuntimeError('should always be -1')

        exh_client = self._get_exh_client()
        ob_js = exh_client.get_order_book(product_id=product_id, ticker=ticker, level=2)
        ob = OrderBookModel.build(ob_js)
        return ob

    def place_limit_order(self, side, ticker, price, shares, timestamp=-1):
        """
        1. make a live query to get order book
        2. directly update accounts
        """
        ob = self.get_order_book(ticker, timestamp)

        if side == 'buy':
            self._buy_eth(shares, ob)
        elif side == 'sell':
            self._sell_eth(shares, ob)
        else:
            raise RuntimeError('unknown market side.')

