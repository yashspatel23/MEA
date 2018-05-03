import unittest

from arb import es
from arb.core.exh.account import BacktestingTradingAccount
from arb.core.models import AccountModel
from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb.utils.common import random_str
from arb_tests import remove_testing_data, ensure_test_data


class TestStratSignalCapitalRequirements(unittest.TestCase):
    @classmethod
    def setUp(cls):
        remove_testing_data(es)

    @classmethod
    def tearDown(cls):
        remove_testing_data(es)

    def test__001(self):
        """
        About capital signals
        """
        timestamp = epoch.to_long('2017-08-21 06:00:00 PDT')
        acc1_js = ensure_test_data({
            "uid": "backtesting_gdx_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "gdax",
            "country": "usa",
            "usd__num": 0.0,
            "eth__num": 100.0,
            "btc__num": 0.0
        })
        acc1 = AccountModel.build(acc1_js)
        acc1.db_save(es)

        acc2_js = ensure_test_data({
            "uid": "backtesting_cex_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "cex",
            "country": "gbr",
            "usd__num": 3001.0,
            "eth__num": 0.0,
            "btc__num": 0.0
        })
        acc2 = AccountModel.build(acc2_js)
        acc2.db_save(es)

        trading_acc1 = BacktestingTradingAccount(acc1.uid, 'gdax')
        trading_acc2 = BacktestingTradingAccount(acc2.uid, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__available_to_deposit(timestamp)
        assert signal['signal'] == True

    def test__002(self):
        """
        About capital signals
        """
        timestamp = epoch.to_long('2017-08-21 06:00:00 PDT')
        acc1_js = ensure_test_data({
            "uid": "backtesting_gdx_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "gdax",
            "country": "usa",
            "usd__num": 0.0,
            "eth__num": 100.0,
            "btc__num": 0.0
        })
        acc1 = AccountModel.build(acc1_js)
        acc1.db_save(es)

        acc2_js = ensure_test_data({
            "uid": "backtesting_cex_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "cex",
            "country": "gbr",
            "usd__num": 1700.0,
            "eth__num": 0.0,
            "btc__num": 0.0
        })
        acc2 = AccountModel.build(acc2_js)
        acc2.db_save(es)

        trading_acc1 = BacktestingTradingAccount(acc1.uid, 'gdax')
        trading_acc2 = BacktestingTradingAccount(acc2.uid, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__available_to_deposit(timestamp)
        assert signal['signal'] == True

    def test__003(self):
        """
        About capital signals
        """
        timestamp = epoch.to_long('2017-08-21 06:00:00 PDT')
        acc1_js = ensure_test_data({
            "uid": "backtesting_gdx_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "gdax",
            "country": "usa",
            "usd__num": 0.0,
            "eth__num": 0.0,
            "btc__num": 0.0
        })
        acc1 = AccountModel.build(acc1_js)
        acc1.db_save(es)

        acc2_js = ensure_test_data({
            "uid": "backtesting_cex_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "cex",
            "country": "gbr",
            "usd__num": 1700.0,
            "eth__num": 0.0,
            "btc__num": 0.0
        })
        acc2 = AccountModel.build(acc2_js)
        acc2.db_save(es)

        trading_acc1 = BacktestingTradingAccount(acc1.uid, 'gdax')
        trading_acc2 = BacktestingTradingAccount(acc2.uid, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__available_to_deposit(timestamp)
        assert signal['signal'] == False

    def test__004(self):
        """
        About capital signals
        """
        timestamp = epoch.to_long('2017-08-21 06:00:00 PDT')
        acc1_js = ensure_test_data({
            "uid": "backtesting_gdx_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "gdax",
            "country": "usa",
            "usd__num": 0.0,
            "eth__num": 100.0,
            "btc__num": 0.0
        })
        acc1 = AccountModel.build(acc1_js)
        acc1.db_save(es)

        acc2_js = ensure_test_data({
            "uid": "backtesting_cex_" + random_str(),
            "timestamp__long": timestamp,
            "exchange": "cex",
            "country": "gbr",
            "usd__num": 1200.0,
            "eth__num": 0.0,
            "btc__num": 0.0
        })
        acc2 = AccountModel.build(acc2_js)
        acc2.db_save(es)

        trading_acc1 = BacktestingTradingAccount(acc1.uid, 'gdax')
        trading_acc2 = BacktestingTradingAccount(acc2.uid, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__available_to_deposit(timestamp)
        assert signal['signal'] == False

if __name__ == '__main__':
    unittest.main()

    # pass


