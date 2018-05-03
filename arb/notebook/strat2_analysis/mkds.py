from arb.core.exh.accounts import LiveTradingAccount
from arb.core.exh.backtest.accounts import BacktestingTradingAccount
from arb.strat import helpers
from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb import es, logger
from arb.utils.string import pretty_json
from arb.notebook import quick
import pandas as pd


# search_window = 10000 # 10 seconds
MILLIS_IN_MINUTE = 1000 * 60
MILLIS_IN_HOUR = 1000 * 60 * 60


def trade_result(amount, holding_period, timestamp,
                 gdax_trading_account, cex_trading_account):
    """
    - trade an amount
    - max out on the number of eth
    - sell after the holding_period
    - how much did it made

    holding_period in Minutes
    """
    # print gdax_ob
    # print cex_ob
    t0 = timestamp
    t1 = timestamp + holding_period * 60 * 1000
    gdax_ob_t0 = gdax_trading_account.get_order_book(ticker='eth', timestamp=t0)
    cex_ob_t1 = cex_trading_account.get_order_book(ticker='eth', timestamp=t1)

    shares = helpers.compute_buy(amount, gdax_ob_t0)

    money_used = helpers.compute_usd_spent(shares, gdax_ob_t0)
    money_gotten = helpers.compute_usd_made(shares, cex_ob_t1)
    diff = money_gotten - money_used

    return diff / amount


def get_ds_trading_result(check_window, check_interval, amount, holding_period, threshold_delta,
                          gdax_trading_account, cex_trading_account):
    """
    data series in dates that:
    1. show trading results

    """
    window = tuple(epoch.to_long(x) for x in check_window)
    interval = MILLIS_IN_MINUTE * check_interval
    x = []
    y1 = []
    y2 = []

    # Use the strategy to calculate deltas
    strategy001 = Strat1(None, None, [gdax_trading_account, cex_trading_account])
    n = (window[1] - window[0]) / interval

    timestamp = window[0]
    for i in range(n):
        withdraw_signal = strategy001.get_signal__withdraw_delta(timestamp)
        withdraw_delta = withdraw_signal['withdraw_delta']

        if withdraw_delta > threshold_delta:
            result = trade_result(amount, holding_period, timestamp, gdax_trading_account, cex_trading_account)

            x.append(timestamp)
            y1.append(withdraw_delta)
            y2.append(result)

            # print i, timestamp, epoch.to_str(timestamp), withdraw_delta, result

        # next timestamp
        timestamp += interval

        # checking progress
        if i % 50 == 0:
            logger.info("[{}] timestamp:{}|date:{}".format(str(i), str(timestamp), epoch.to_str(timestamp)))

    x_index = pd.to_datetime(x, unit='ms')
    ds1 = pd.Series(index=x_index, data=y1)
    ds2 = pd.Series(index=x_index, data=y2)

    logger.info(check_window)
    logger.info(window)
    logger.info(ds1.head())
    logger.info(ds1.head())

    return ds1, ds2


def get_results_for_a_mock_strategy(check_window, check_interval, amount, holding_period, threshold_delta,
                                    gdax_trading_account, cex_trading_account):
    """
    keep track of how we we are doing with one trade at a time
    """
    window = tuple(epoch.to_long(x) for x in check_window)
    interval = MILLIS_IN_MINUTE * check_interval
    x = []
    y1 = []
    y2 = []

    # Use the strategy to calculate deltas
    strategy001 = Strat1(None, None, [gdax_trading_account, cex_trading_account])
    n = (window[1] - window[0]) / interval

    ONE_DAY_IN_MINUTES =1440
    cash = amount
    eth = 0.0
    waiting_liquidate_ticks = 0
    waiting_capital_ticks = ONE_DAY_IN_MINUTES

    # def signal__has_eth():
    #     return eth > 0.0

    timestamp = window[0]
    for i in range(n):
        waiting_liquidate_ticks += check_interval
        waiting_capital_ticks += check_interval
        withdraw_signal = strategy001.get_signal__withdraw_delta(timestamp)
        withdraw_delta = withdraw_signal['withdraw_delta']

        # handling gdax
        if withdraw_delta >= threshold_delta and eth == 0.0 and waiting_capital_ticks >= ONE_DAY_IN_MINUTES:
            gdax_ob = gdax_trading_account.get_order_book(ticker='eth', timestamp=timestamp)
            shares = helpers.compute_buy(amount, gdax_ob)
            usd_used = helpers.compute_usd_spent(shares, gdax_ob)

            # accounting
            cash = cash - usd_used
            eth = eth + shares * (1 - 0.003)  # Including fees
            waiting_liquidate_ticks = 0
            waiting_capital_ticks = 0

            # x.append(timestamp)
            # y1.append(cash)
            # y2.append(eth)

        if eth > 0.0 and waiting_liquidate_ticks >= holding_period:
            cex_ob = cex_trading_account.get_order_book(ticker='eth', timestamp=timestamp)
            shares = eth
            usd_gotten = helpers.compute_usd_made(shares, cex_ob) * (1 - 0.002)  # Including fees

            # accounting
            cash = cash + usd_gotten
            eth = 0

            x.append(timestamp)
            y1.append(cash)
            y2.append(eth)

            print i, epoch.to_str(timestamp)
            print "cash: {} | eth: {}".format(str(cash), str(eth))
            print "capital tick: {} | liquidate tick: {}".format(waiting_capital_ticks, waiting_liquidate_ticks)


        # next timestamp
        timestamp += interval

        # checking progress
        # print i, epoch.to_str(timestamp)
        # print "cash: {} | eth: {}".format(str(cash), str(eth))
        # print "capital tick: {} | liquidate tick: {}".format(waiting_capital_ticks, waiting_liquidate_ticks)

        if i % 50 == 0:
            print i, epoch.to_str(timestamp)
            print "cash: {} | eth: {}".format(str(cash), str(eth))
            print "capital tick: {} | liquidate tick: {}".format(waiting_capital_ticks, waiting_liquidate_ticks)

    x_index = pd.to_datetime(x, unit='ms')
    ds1 = pd.Series(index=x_index, data=y1)
    ds2 = pd.Series(index=x_index, data=y2)

    logger.info(check_window)
    logger.info(window)
    logger.info(ds1.head())

    return ds1, ds2






if __name__ == '__main__':
    # -------------------
    # Signals Environment
    # -------------------
    # check_window = ("2017-09-13 00:00:00 PDT", "2017-09-18 08:00:00 PDT")
    # check_interval = 30  # In minutes
    #
    # ds1, ds2 = do_work(check_window, check_interval)

    timestamp = epoch.to_long("2017-10-01 00:00:00 PDT")
    gdax_trading_account = BacktestingTradingAccount('gdax', 'gdax')
    cex_trading_account = BacktestingTradingAccount('cex', 'cex')

    # gdax_ob = gdax_trading_account.get_order_book(ticker='eth', timestamp=timestamp)
    # cex_ob = cex_trading_account.get_order_book(ticker='eth', timestamp=timestamp)

    one_result = trade_result(10000.0, 40, timestamp, gdax_trading_account, cex_trading_account)

    print one_result

# def get_ds_trading_result(check_window, check_interval, amount, holding_period, threshold_delta,
#                           gdax_trading_account, cex_trading_account):

    check_window = ("2017-09-13 00:00:00 PDT", "2017-09-14 08:00:00 PDT")
    check_interval = 30  # In minutes

    delta_ds, diff_ds = get_ds_trading_result(check_window, check_interval, 10000.0, 40.0, 0.03,
                                              gdax_trading_account, cex_trading_account)


