import json
import time
from abc import abstractmethod
from collections import OrderedDict

from arb import EXCHANGE_NAME_GDAX, EXCHANGE_NAME_CEX, ES_GET_TIMEOUT, logger
from arb import GDAX_API_URL, GDAX_API_SECRET, GDAX_API_PASSPHRASE, CEX_API_URL, \
    CEX_API_KEY, CEX_API_SECRET, CEX_API_USER_ID, GDAX_API_KEY, es
from arb.core.exh.clients import GdaxClient, CexClient
from arb.core.models import OrderBookModel, AccountModel


def default_es_get_params():
    return {
        'request_timeout': ES_GET_TIMEOUT,
    }


class TradingAccount(object):
    """
    Generic type for all trading accounts
    """
    def __init__(self, account_uid, exh):
        self.account_uid = account_uid
        self.exh = exh

    def __repr__(self):
        js = OrderedDict()
        js['exh'] = self.exh
        js['account_uid'] = self.account_uid
        return json.dumps(js, indent=2)

    @classmethod
    def sleep(cls, seconds):
        raise NotImplementedError()

    @classmethod
    def get_snapping_timestamp(cls, timestamp=-1):
        raise NotImplementedError()

    def get_account(self):
        """
        :return: AccountModel
        """
        params = default_es_get_params()
        result = es.get('account', self.account_uid, params=params)
        account_js = result['_source']
        account = AccountModel.build(account_js)
        return account

    @abstractmethod
    def get_order_book(self, product_id=None, ticker=None, timestamp=-1):
        """
        :param timestamp: Only useful for backtesting
        :return: OrderBookModel
        """
        raise NotImplementedError()

    @abstractmethod
    def place_limit_order(self, side, ticker, price, shares, timestamp=-1):
        """
        :param timestamp: Only useful for backtesting
        :return: AcccountModel
        """
        raise NotImplementedError()


class LiveTradingAccount(TradingAccount):
    def __init__(self, account_uid, exh):
        self.gdax_client = GdaxClient(GDAX_API_URL, GDAX_API_KEY, GDAX_API_SECRET, GDAX_API_PASSPHRASE)
        self.cex_client = CexClient(CEX_API_URL, CEX_API_USER_ID, CEX_API_KEY, CEX_API_SECRET)
        super(LiveTradingAccount, self).__init__(account_uid, exh)

    @classmethod
    def get_snapping_timestamp(cls, timestamp=-1):
        return -1

    @classmethod
    def sleep(cls, seconds):
        time.sleep(seconds)

    def _get_exh_client(self):
        if self.exh == EXCHANGE_NAME_GDAX:
            exh_client = self.gdax_client
        elif self.exh == EXCHANGE_NAME_CEX:
            exh_client = self.cex_client
        else:
            raise RuntimeError('unknown exchange')
        return exh_client

    def get_balance(self, ticker):
        exh_client = self._get_exh_client()
        return exh_client.get_balance(ticker)

    def get_balances(self):
        return self._get_exh_client().get_balances()

    def sync_account_with_exh(self):
        exh_client = self._get_exh_client()
        balances = exh_client.get_balances()
        account_js = self.get_account().js
        account_js['eth__num'] = float(balances['eth'])
        account_js['btc__num'] = float(balances['btc'])
        account_js['usd__num'] = float(balances['usd'])

        account = AccountModel.build(account_js)
        account.db_save(es)
        return account

    def get_order_book(self, product_id=None, ticker=None, timestamp=-1):
        if timestamp != -1:
            raise RuntimeError('should always be -1')

        exh_client = self._get_exh_client()
        ob_js = exh_client.get_order_book(product_id=product_id, ticker=ticker, level=2)
        ob = OrderBookModel.build(ob_js)
        return ob

    def place_limit_order(self, side, ticker, price, shares, timestamp=-1):
        if timestamp != -1:
            raise RuntimeError('should always be -1')

        # fix size precision
        shares = float("{0:.1f}".format(shares))

        exh_client = self._get_exh_client()
        if side == 'buy':
            exh_client.place_limit_order('buy', ticker, price, shares)
            account = self.sync_account_with_exh()
        elif side == 'sell':
            exh_client.place_limit_order('sell', ticker, price, shares)
            account = self.sync_account_with_exh()
        else:
            msg = 'side:{}|ticker:{}|price:{}|shares:{}'.format(side, ticker, price, shares)
            logger.error(msg)
            raise RuntimeError('unknown market execution')

        # TODO: create an audit trails for transactions

        return account
