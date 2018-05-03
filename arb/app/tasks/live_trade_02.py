from arb import logger
from arb.core.exh.accounts import LiveTradingAccount
from arb.strat.runner import StrategyRunner
from arb.strat.strat1 import Strat1
from arb.strat.strat2 import Strat2
from arb.utils import epoch


if __name__ == '__main__':
    strategy_running_id = 'live_trade_02'
    strategy_desc = 'live trading with circular buffer strategy'

    start_time = epoch.current_milli_time()
    execution_window = [start_time, start_time + 7884000000]  # three months
    execution_interval = 5 * 60 * 1000  # every five minutes

    trading_acc1 = LiveTradingAccount('gdax002', 'gdax')
    trading_acc2 = LiveTradingAccount('cex002', 'cex')
    accounts = [trading_acc1, trading_acc2]

    # run strategies
    runner = StrategyRunner(execution_window, execution_interval,
                            Strat2, strategy_running_id, strategy_desc, accounts,
                            buy_threshold=0.020,
                            action_amount=10000.0,
                            capital_buffer_multiplier=1.01,
                            snap_repetition=5)

    runner.start(fail_fast=False)







