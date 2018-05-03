import json
from abc import abstractmethod, ABCMeta
from collections import OrderedDict

from arb import logger, EXCHANGE_PRODUCT_ID__ETH_USD, EXCHANGE_NAME_CEX, EXCHANGE_NAME_GDAX, \
    EXCHANGE_TICKER__ETH, EXCHANGE_TICKER__BTC, EXCHANGE_TICKER__USD
from arb.core.exh.api.cex_clients import CexPublicClient, CexAuthClient
from arb.core.exh.api.gdax_clients import GdaxAuthClient, GdaxPublicClient
from arb.core.exh.exceptions import ExchangeExecutionException
from arb.core.models.exception import ModelException
from arb.utils.string import pretty_json


class ExhClient(object):
    """
    Client that talks to exchanges.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        if not self.exh:
            raise NotImplementedError()

    def __repr__(self):
        js = OrderedDict()
        js['exh'] = self.exh
        return json.dumps(js, indent=2)

    @abstractmethod
    def get_balance(self, ticker):
        raise NotImplementedError()

    @abstractmethod
    def get_balances(self):
        raise NotImplementedError()

    @abstractmethod
    def get_order_book(self, ticker=None, product_id=None, level=2):
        """
        ticker: See EXCHANGE_TICKER__*
        eth
        btc

        ticker: See EXCHANGE_PRODUCT_ID__*
        eth-usd
        btc-usd

        level:
        1 -> Only the best bid and ask
        2 -> Top 50 bids and asks
        3 -> Full order book, or as much as possible

        TODO: provide an example
        """
        raise NotImplementedError()

    @abstractmethod
    def place_limit_order(self, side, ticker, price, size):
        """
        Return True if successful
        """
        raise NotImplementedError()


class CexClient(ExhClient):
    exh = EXCHANGE_NAME_CEX
    cex_pid_from_product_id = {
        EXCHANGE_PRODUCT_ID__ETH_USD: 'ETH/USD',
    }
    cex_pid_from_ticker = {
        EXCHANGE_TICKER__ETH : 'ETH/USD',
    }
    cex_ticker_from_ticker = {
        EXCHANGE_TICKER__USD : 'USD',
        EXCHANGE_TICKER__ETH : 'ETH',
        EXCHANGE_TICKER__BTC : 'BTC',
    }
    ticker_from_cex_ticker = {
        'USD': EXCHANGE_TICKER__USD,
        'ETH': EXCHANGE_TICKER__ETH,
        'BTC': EXCHANGE_TICKER__BTC,
    }

    @classmethod
    def _get_pid(cls, product_id=None, ticker=None):
        if product_id and ticker:
            raise RuntimeError()

        if product_id:
            pid = cls.cex_pid_from_product_id[ticker]
        elif ticker:
            pid = cls.cex_pid_from_ticker[ticker]

        return pid

    def __init__(self, api_url, api_user_id, api_key, api_secret):
        if not self.exh == EXCHANGE_NAME_CEX:
            raise ModelException()

        self.api_url = api_url
        self.api_user_id = api_user_id
        self.api_key = api_key
        self.api_secret = api_secret

        self.public_client = CexPublicClient(api_url)
        self.auth_client = CexAuthClient(api_url, api_user_id, api_key, api_secret)
        super(CexClient, self).__init__()


    def get_balance(self, ticker):
        cex_ticker = self.cex_ticker_from_ticker[ticker]
        account = self.auth_client.get_account()
        balance = account[cex_ticker]['available']
        return balance

    def get_balances(self):
        cex_tickers = self.cex_ticker_from_ticker.values()
        account = self.auth_client.get_account()

        balances = OrderedDict()
        for cex_ticker in cex_tickers:
            ticker = self.ticker_from_cex_ticker[cex_ticker]
            balances[ticker] = account[cex_ticker]['available']

        return balances

    def get_order_book(self, product_id=None, ticker=None, level=2):
        """
        Return json that is compatible with OrderBookModel
        """
        # product id
        cex_pid = self._get_pid(product_id=product_id, ticker=ticker)

        # depth
        if level == 1:
            depth = 1
        elif level == 2:
            depth = 50
        elif level == 3:
            depth = ''  # get all
        else:
            raise RuntimeError('not supported level')

        result = self.public_client.get_product_order_book(cex_pid, depth=depth)
        return result

    def place_limit_order(self, side, ticker, price, size):
        """
        Raise ExchangeExecutionException when the action is not performed as expected
        """
        try:
            cex_pid = self._get_pid(ticker=ticker)
            order_response = self.auth_client.place_order(side, cex_pid, price, size)

            # Validation
            order_id = order_response['id']
            pending = float(order_response['pending'])
            if pending > 0.0:
                self.auth_client.cancel_order(order_id)  # cancel order
                logger.warn(json.dumps(order_response, indent=2))
                raise RuntimeError('pending amount > 0')
        except Exception as e:
            logger.warn('side:{}|ticker:{}|price:{}|size:{}'.format(side, ticker, price, size))
            logger.warn(json.dumps(order_response, indent=2))
            raise ExchangeExecutionException(e)

    def transfer_crypto(self, ticker, crypto_address, shares):
        """
        Raise ExchangeExecutionException when the action is not performed as expected

        see: https://docs.gdax.com/#crypto
        """
        raise NotImplementedError()


class GdaxClient(ExhClient):
    exh = EXCHANGE_NAME_GDAX
    gdax_pid_from_product_id = {
        EXCHANGE_PRODUCT_ID__ETH_USD: 'ETH-USD',
    }
    gdax_pid_from_ticker = {
        EXCHANGE_TICKER__ETH : 'ETH-USD',
    }
    gdax_ticker_from_ticker = {
        EXCHANGE_TICKER__USD : 'USD',
        EXCHANGE_TICKER__ETH : 'ETH',
        EXCHANGE_TICKER__BTC : 'BTC',
    }
    ticker_from_gdax_ticker = {
        'USD': EXCHANGE_TICKER__USD,
        'ETH': EXCHANGE_TICKER__ETH,
        'BTC': EXCHANGE_TICKER__BTC,
    }

    @classmethod
    def _get_pid(cls, product_id=None, ticker=None):
        if product_id and ticker:
            raise RuntimeError()

        if product_id:
            gdax_pid = cls.gdax_pid_from_product_id[ticker]
        elif ticker:
            gdax_pid = cls.gdax_pid_from_ticker[ticker]
        else:
            raise RuntimeError()

        return gdax_pid

    def __init__(self, api_url, api_key, api_secret, api_passphrase):
        if not self.exh == EXCHANGE_NAME_GDAX:
            raise ModelException()

        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.auth_client = GdaxAuthClient(api_url, api_key, api_secret, api_passphrase)
        self.public_client = GdaxPublicClient(api_url)
        super(GdaxClient, self).__init__()

    def get_balance(self, ticker):
        gdax_ticker = self.gdax_ticker_from_ticker[ticker]
        accounts = self.auth_client.get_accounts()

        balance = None
        for account in accounts:
            if gdax_ticker == account['currency']:
                balance = account['available']
                break

        # Validate an assumption: only one account per currency
        currencies = set([x['currency'] for x in accounts])
        if len(currencies) != len(accounts):
            logger.error(pretty_json(accounts))
            raise RuntimeError('There are too many accounts. Assumption is violated.')

        # Fail fast if some unknow thing happen
        if balance is None:
            logger.error(pretty_json(accounts))
            raise RuntimeError('Cannot get balance')

        return balance

    def get_balances(self):
        gdax_tickers = self.gdax_ticker_from_ticker.values()
        accounts = self.auth_client.get_accounts()

        balances = OrderedDict()
        for account in accounts:
            gdax_ticker = account['currency']
            if gdax_ticker in gdax_tickers:
                ticker = self.ticker_from_gdax_ticker[gdax_ticker]
                balances[ticker] = account['available']

        # Validate an assumption: only one account per currency
        currencies = set([x['currency'] for x in accounts])
        if len(currencies) != len(accounts):
            logger.error(pretty_json(accounts))
            raise RuntimeError('There are too many accounts. Assumption is violated.')

        # More validations
        if not balances:
            logger.error(pretty_json(accounts))
            raise RuntimeError('Cannot get balance')

        return balances

    def get_order_book(self, product_id=None, ticker=None, level=2):
        if level == 3:
            # TODO: there is an error with the parsing of the order book when level=3
            raise NotImplementedError()

        gdax_pid = self._get_pid(product_id=product_id, ticker=ticker)
        return self.public_client.get_product_order_book(gdax_pid, level)

    def place_limit_order(self, side, ticker, price, size):
        try:
            gdax_pid = self._get_pid(ticker=ticker)
            order_response_01 = self.auth_client.\
                place_order(gdax_pid, price, size, side, time_in_force='FOK', order_type='limit')
            order_response_02 = self.auth_client.get_order(order_response_01['id'])

            # Validation
            status_02 = order_response_02['status']
            if status_02 not in ['pending', 'done']:
                raise RuntimeError('unknown gdax order status')

        except Exception as e:
            logger.warn('side:{}|ticker:{}|price:{}|size:{}'.format(side, ticker, price, size))
            logger.warn(json.dumps(order_response_01, indent=2))
            raise ExchangeExecutionException(e)

    def get_crypto_deposit_address(self, ticker):
        """
        Raise ExchangeExecutionException when the action is not performed as expected

        see: https://docs.gdax.com/#crypto
        """
        raise NotImplementedError()


# TESTING
if __name__ == '__main__':
    pass

