import json
import unittest
import uuid

from arb.core.exh.accounts import LiveTradingAccount
from arb.core.models import OrderBookModel, AuditTradeModel
from arb import logger
from arb import es
from arb.core.models.exception import ModelKeyValueException
from arb.strat import helpers
from arb.utils import epoch


class TestLiveTradingAccounts(unittest.TestCase):
    def test__run_main(self):
        trading_account = LiveTradingAccount('gdax', 'gdax')

        account = trading_account.sync_account_with_exh()
        logger.info('before')
        logger.info(account)

        # account_02 = trading_account.place_limit_order('buy', 'eth', 100.0, 0.01)
        account_02 = trading_account.place_limit_order('sell', 'eth', 500.0, 0.01)
        # ob = trading_account.get_order_book('eth')
        # shares = 20.0

        logger.info('before')
        logger.info('-'*30)
        logger.info(account)

        logger.info('after')
        logger.info('-'*30)
        logger.info(account_02)

        assert True

    def test__001(self):
        assert True


if __name__ == '__main__':
    unittest.main()
