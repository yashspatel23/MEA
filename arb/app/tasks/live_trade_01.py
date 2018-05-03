from arb import logger
from arb.core.exh.accounts import LiveTradingAccount
from arb.strat.runner import StrategyRunner
from arb.strat.strat1 import Strat1
from arb.utils import epoch


if __name__ == '__main__':
    strategy_desc = 'live trading with 500USD and 1.8ETH'
    strategy_running_id = 'live_trade_01'

    start_time = epoch.current_milli_time()
    execution_window = [start_time, start_time + 7884000000]  # three months
    execution_interval = 5 * 60 * 1000  # every five minutes

    trading_acc1 = LiveTradingAccount('gdax', 'gdax')
    trading_acc2 = LiveTradingAccount('cex', 'cex')
    accounts = [trading_acc1, trading_acc2]

    # run strategies
    runner = StrategyRunner(execution_window, execution_interval,
                            Strat1, strategy_running_id, strategy_desc, accounts)

    # Set Internal Settings
    # runner.strategy.THRESHOLD_WITHDRAW_DELTA = 0.042
    # runner.strategy.THRESHOLD_DEPOSIT_DELTA = 0.022

    runner.strategy.THRESHOLD_WITHDRAW_DELTA = 0.025
    runner.strategy.THRESHOLD_DEPOSIT_DELTA  = 0.003

    runner.strategy.CAPITAL_BUFFER_MULTIPLIER = 1.05
    runner.strategy.SNAP_REPETITION = 5
    runner.strategy.WITHDRAW_ACTION_AMOUNT = 1000
    runner.strategy.DEPOSIT_ACTION_AMOUNT = 1000 * 0.95

    runner.start(fail_fast=False)







