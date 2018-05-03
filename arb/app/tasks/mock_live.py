from arb import logger, es
from arb.core.exh.backtest.accounts import MockTradingAccount
from arb.core.models import AccountModel
from arb.strat.runner import StrategyRunner
from arb.strat.strat1 import Strat1
from arb.utils import epoch


if __name__ == '__main__':
    logger.info("Starting a mock live strategy...")

    strategy_desc = 'mock live 00, 2007/09/23, Saturday'
    strategy_running_id = 'server_mock_live__004'
    gdax_account_name = strategy_running_id + '__gdax'
    cex_account_name = strategy_running_id + '__cex'

    start_time = epoch.current_milli_time()
    execution_window = [start_time, start_time + 7884000000]  # three months
    execution_interval = 5 * 60 * 1000  # every five minutes

    # execution_window = [start_time, start_time + 60000]  # testing, 30 seconds
    # execution_interval = 10000  # testing, every 10 seconds

    # set accounts
    gdax_acc_js = {
        "uid": gdax_account_name,
        "timestamp__long": start_time,
        "exchange": "gdax",
        "country": "usa",
        "usd__num": 20000.0,
        "eth__num": 3.0,
        "btc__num": 0.0
    }
    cex_acc_js = {
        "uid": cex_account_name,
        "timestamp__long": start_time,
        "exchange": "cex",
        "country": "gbr",
        "usd__num": 0.0,
        "eth__num": 60.0,
        "btc__num": 0.0
    }

    gdax = AccountModel.build(gdax_acc_js)
    cex = AccountModel.build(cex_acc_js)
    gdax.db_save(es)
    cex.db_save(es)

    trading_acc1 = MockTradingAccount(gdax.uid, 'gdax')
    trading_acc2 = MockTradingAccount(cex.uid, 'cex')
    accounts = [trading_acc1, trading_acc2]

    # run strategies
    runner = StrategyRunner(execution_window, execution_interval,
                            Strat1, strategy_running_id, strategy_desc, accounts)
    runner.start(fail_fast=False)






