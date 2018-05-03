import unittest

from arb import logger
from arb.core.models import OrderBookModel
from arb.strat import helpers
from arb.utils import epoch


from arb.core.exh.backtest.accounts import BacktestingTradingAccount, MockTradingAccount
from arb.core.exh.accounts import LiveTradingAccount
from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb import es, logger
from arb.utils.string import pretty_json
from arb.notebook import quick
import pandas as pd

# Use the strategy to calculate deltas
_id = 'server_mock_live__004'

gdax_t_account = MockTradingAccount(_id + '__gdax', 'gdax')
cex_t_account = MockTradingAccount(_id + '__cex', 'cex')
strategy001 = Strat1(None, None, gdax_t_account, cex_t_account)

withdraw_signal = strategy001.get_signal__withdraw_delta()
deposit_signal = strategy001.get_signal__deposit_delta()


print '------------------------'
print 'signals'
print '------------------------'
print pretty_json(withdraw_signal)
print pretty_json(deposit_signal)

# if __name__ == '__main__':
#     unittest.main()
#
    # pass
