import traceback

from arb import logger, sentry_client
from arb.utils import epoch

SIGNAL_CAPITAL_AVAILABLE = 'SIGNAL_CAPITAL_AVAILABLE'
SIGNAL_CAPITAL_IMBALANCE = 'SIGNAL_CAPITAL_IMBALANCE'
SIGNAL_WITHDRAW = 'SIGNAL_WITHDRAW'
SIGNAL_DEPOSIT = 'SIGNAL_DEPOSIT'


class StrategyRunner(object):
    """
    Run the strategies on specific trading accounts and environments
    """
    def __init__(self, execution_window, execution_interval,
                 strategy_cls,
                 strategy_run_id,
                 strategy_description,
                 strategy_trading_accounts,
                 **kwargs):
        """
        Examples
        1. strategy
        1. trading_accounts = [acc_gdax, acc_cex]
        2. window = None, [to_long('2017-08-28 09:00:00 PDT'), to_long(''2017-08-29 09:00:00 PDT'')]
                    [1503936000000, 1504022400000]

        1. Use trader's data and account state to determine actions.
        2. Execute actions by using trader
        3. Update results in accounts
        """
        self.execution_window = execution_window
        self.execution_interval = execution_interval
        self.strategy_cls = strategy_cls
        self.strategy = strategy_cls(strategy_run_id,
                                     strategy_description,
                                     strategy_trading_accounts,
                                     **kwargs)

    def __repr__(self):
        return str(self.strategy)

    def snap(self, timestamp=-1, fail_fast=True):
        snap_result = None
        if fail_fast:
            snap_result = self.strategy.snap(timestamp)
        else:
            try:
                snap_result = self.strategy.snap(timestamp)
            except:  # any Exception
                sentry_client.captureException()
                logger.error(traceback.format_exc())  # log traceback

        return snap_result

    def start(self, fail_fast=True):
        logger.info('Starting strategy: {0}'.format(str(self.strategy.strategy_name)))
        logger.info("Strategy withdraw threshold: " + str(self.strategy.THRESHOLD_WITHDRAW_DELTA))
        logger.info("Strategy deposit threshold: " + str(self.strategy.THRESHOLD_DEPOSIT_DELTA))

        # How long? How often?
        length = (self.execution_window[1] - self.execution_window[0]) # In millisecond
        interval = self.execution_interval # In millisecond

        # length = 86400000  # one day
        # interval = 600 # 5 minutes

        counter_limit = length / interval
        timestamp = self.execution_window[0]

        logger.info('====================================')
        logger.info('Starting time : {0}'.format(epoch.to_str(timestamp)))
        logger.info('Interval in seconds: {0}'.format(str(interval / 1000)))
        logger.info('====================================')

        counter = 0
        while counter <= counter_limit:
            counter += 1
            timestamp += interval
            snap_t = self.strategy.trading_acc1.get_snapping_timestamp(timestamp)
            self.snap(snap_t, fail_fast=fail_fast) # main execution path

            # logging info line
            execution_timestamp = '-1' if timestamp == -1 else epoch.to_str(timestamp)
            info_line = '{0} Runner snapping, current time: {1} | execution timestamp: {2}' \
                .format(str(counter), epoch.current_time(), str(execution_timestamp))
            logger.info(info_line)
            self.strategy.trading_acc1.sleep(interval / 1000) # Sleeping in seconds

        logger.info('Finished strategy runner : {0}'.format(epoch.current_time()))


if __name__ == '__main__':
    pass







