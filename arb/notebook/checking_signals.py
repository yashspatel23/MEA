from arb.core.exh.backtest.accounts import BacktestingTradingAccount
from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb import es, logger
from arb.utils.string import pretty_json
from arb.notebook import quick
import pandas as pd


# search_window = 10000 # 10 seconds
MILLIS_IN_MINUTE = 1000 * 60
MILLIS_IN_HOUR = 1000 * 60 * 60


epoch.current_time()
epoch.current_milli_time()
def get_two_deltas(check_window, check_interval):
    window = tuple(epoch.to_long(x) for x in check_window)
    interval = MILLIS_IN_MINUTE * check_interval
    x = []
    y1 = []
    y2 = []

    # Use the strategy to calculate deltas
    gdax_t_account = BacktestingTradingAccount('backtesting_gdx_001', 'gdax')
    cex_t_account = BacktestingTradingAccount('backtesting_cex_001', 'cex')
    strategy001 = Strat1(None, None, [gdax_t_account, cex_t_account])
    n = (window[1] - window[0]) / interval

    timestamp = window[0]
    for i in range(n):
        withdraw_signal = strategy001.get_signal__withdraw_delta(timestamp)
        deposit_signal = strategy001.get_signal__deposit_delta(timestamp)
        withdraw_delta = withdraw_signal['withdraw_delta']
        deposit_delta = deposit_signal['deposit_delta']

        x.append(timestamp)
        y1.append(withdraw_delta)
        y2.append(deposit_delta)

        # print i, timestamp, epoch.to_str(timestamp)

        # next timestamp
        timestamp += interval

        # checking progress
        if i % 50 == 0:
            logger.info("timestamp:{0}|date:{1}".format(str(timestamp), epoch.to_str(timestamp)))


    x_index = pd.to_datetime(x, unit='ms')
    ds1 = pd.Series(index=x_index, data=y1)
    ds2 = pd.Series(index=x_index, data=y2)

    logger.info(check_window)
    logger.info(window)
    logger.info(ds1.head())
    logger.info(ds1.head())

    return ds1, ds2


if __name__ == '__main__':
    # -------------------
    # Signals Environment
    # -------------------
    check_window = ("2017-09-13 00:00:00 PDT", "2017-09-18 08:00:00 PDT")
    check_interval = 30  # In minutes

    ds1, ds2 = get_two_deltas(check_window, check_interval)


