import unittest

from arb import es
from arb.core.exh.account import BacktestingTradingAccount
from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb_tests import remove_testing_data


class TestStra1(unittest.TestCase):
    @classmethod
    def setUp(cls):
        remove_testing_data(es)

    @classmethod
    def tearDown(cls):
        remove_testing_data(es)

    def test__001(self):
        """
        go
        """
        timestamp = epoch.to_long('2017-08-20 23:00:00 PDT')
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        trading_acc2 = BacktestingTradingAccount(None, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__deposit_delta(timestamp)
        assert signal['signal'] == True

    def test__002(self):
        """
        go
        """
        timestamp = epoch.to_long('2017-08-21 13:00:00 PDT')
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        trading_acc2 = BacktestingTradingAccount(None, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__deposit_delta(timestamp)
        assert signal['signal'] == True

    def test__003(self):
        """
        no go
        """
        timestamp = epoch.to_long('2017-08-21 19:00:00 PDT')
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        trading_acc2 = BacktestingTradingAccount(None, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__deposit_delta(timestamp)
        assert signal['signal'] == False

    def test__004(self):
        """
        no go
        """
        timestamp = epoch.to_long('2017-08-21 07:00:00 PDT')
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        trading_acc2 = BacktestingTradingAccount(None, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__deposit_delta(timestamp)
        assert signal['signal'] == False

    def test__005(self):
        """
        no go
        """
        timestamp = epoch.to_long('2017-08-22 06:00:00 PDT')
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        trading_acc2 = BacktestingTradingAccount(None, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__deposit_delta(timestamp)
        assert signal['signal'] == False

    def test__006(self):
        """
        go
        """
        timestamp = epoch.to_long('2017-08-21 17:00:00 PDT')
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        trading_acc2 = BacktestingTradingAccount(None, 'cex')
        strat = Strat1(trading_acc1, trading_acc2)
        signal = strat.get_signal__deposit_delta(timestamp)

        assert signal['signal'] == True

if __name__ == '__main__':
    unittest.main()

    # pass


