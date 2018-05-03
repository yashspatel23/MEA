import time
import traceback

from arb import es, logger, sentry_client
from arb.core.models import AccountModel
from arb.strat.strat1 import Strat1
from arb.utils import epoch


# def run_task(interval, length, task_name, task, args=[], kwargs={}):
#     def runner():
#         counter_limit = length / interval
#         counter = 0
#         # accumulation = 0
#         # going = True
#         while counter <= counter_limit:
#             threading.Timer(0, task, args=args, kwargs=kwargs).start()
#
#             # timing and stop loop
#             time.sleep(interval)
#             counter += 1
#             logger.info('Ran task {0}: {1}'.format(task_name, str(counter)))
#         logger.info('Finish executing task: {0}'.format(task_name))
#     threading.Timer(0, runner).start()
#     logger.info('Scheduled: {0}'.format(task_name))


# def run_mock_live(strategy_running_id, strategy_description):
#     start_time = epoch.current_milli_time()
#
#     execution_window = [start_time, start_time + 7884000000]  # three months
#     execution_interval = 5 * 60 * 1000  # every five minutes
#
#     # execution_window = [start_time, start_time + 30000]  # testing, 30 seconds
#     execution_interval = 10000  # testing, every 10 secoonds
#
#     strategy_desc = strategy_description
#     gdax_account_name = strategy_desc + '__gdax'
#     cex_account_name = strategy_desc + '__cex'
#
#     # set accounts
#     gdax_acc_js = {
#         "uid": gdax_account_name,
#         "timestamp__long": start_time,
#         "exchange": "gdax",
#         "country": "usa",
#         "usd__num": 20000.0,
#         "eth__num": 3.0,
#         "btc__num": 0.0
#     }
#     cex_acc_js = {
#         "uid": cex_account_name,
#         "timestamp__long": start_time,
#         "exchange": "cex",
#         "country": "gbr",
#         "usd__num": 0.0,
#         "eth__num": 50.0,
#         "btc__num": 0.0
#     }
#
#     gdax = AccountModel.build(gdax_acc_js)
#     cex = AccountModel.build(cex_acc_js)
#     gdax.db_save(es)
#     cex.db_save(es)
#
#     trading_acc1 = MockTradingAccount(gdax.uid, 'gdax')
#     trading_acc2 = MockTradingAccount(cex.uid, 'cex')
#     accounts = [trading_acc1, trading_acc2]
#
#     # run strategies
#     runner = StrategyRunner(execution_window, execution_interval,
#                             Strat1, strategy_running_id, strategy_desc, accounts)
#     runner.start()


# def run_back_testing():
#     logger.info("...backtesting...")
#     execution_window = ("2017-09-13 00:00:00 PDT", "2017-09-14 08:00:00 PDT")
#     execution_interval = 60  # In minutes
#     strategy_run_id = 'backtesting__001'
#     strategy_description = 'backtesting'
#     fail_fast = False
#
#     window = tuple(epoch.to_long(x) for x in execution_window)
#     interval = execution_interval * 60 * 1000
#
#     acc1_js = {
#         "uid": "backtesting_gdx_001",
#         "timestamp__long": window[0],
#         "exchange": "gdax",
#         "country": "usa",
#         "usd__num": 20000.0,
#         "eth__num": 3.0,
#         "btc__num": 0.0
#     }
#     acc2_js = {
#         "uid": "backtesting_cex_001",
#         "timestamp__long": window[0],
#         "exchange": "cex",
#         "country": "gbr",
#         "usd__num": 0.0,
#         "eth__num": 50.0,
#         "btc__num": 0.0
#     }
#     acc1 = AccountModel.build(acc1_js)
#     acc2 = AccountModel.build(acc2_js)
#
#     acc1.db_save(es)
#     acc2.db_save(es)
#     # logger.info('-------------------------------')
#     # logger.info(acc1)
#     # logger.info(acc2)
#     # logger.info('-------------------------------')
#
#     trading_acc1 = BacktestingTradingAccount(acc1.uid, 'gdax')
#     trading_acc2 = BacktestingTradingAccount(acc2.uid, 'cex')
#     accounts = [trading_acc1, trading_acc2]
#
#     # run strategies
#     runner = StrategyRunner(window, interval,
#                             Strat1, strategy_run_id, strategy_description, accounts)
#     runner.start(fail_fast=fail_fast)
#
#     logger.info('----------------------------------')
#     logger.info('    END                           ')
#     logger.info('----------------------------------')
#     logger.info(trading_acc1.get_account())
#     logger.info(trading_acc2.get_account())


if __name__ == '__main__':
    # run_mock_live()
    # run_back_testing()
    pass







