from arb.core.exh.accounts import LiveTradingAccount
from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb.utils.string import pretty_json

# Use the strategy to calculate deltas
account_id = 'gdax'
exh = 'gdax'
gdax_trading_account = LiveTradingAccount(account_id, exh)
gdax_account = gdax_trading_account.sync_account_with_exh()

# view cex
account_id = 'cex'
exh = 'cex'
cex_trading_account = LiveTradingAccount(account_id, exh)
cex_account = cex_trading_account.sync_account_with_exh()


strategy_running_id = 'live_trade_01'
strategy_desc = 'live trading with 500USD and 1.8ETH'

strat1 = Strat1(strategy_running_id, strategy_desc, gdax_trading_account, cex_trading_account)
strat1.THRESHOLD_WITHDRAW_DELTA = 0.02
strat1.THRESHOLD_DEPOSIT_DELTA = 0.01
strat1.CAPITAL_BUFFER_MULTIPLIER = 1.05
strat1.SNAP_REPETITION = 7
strat1.WITHDRAW_ACTION_AMOUNT = 100
strat1.DEPOSIT_ACTION_AMOUNT = 100 * 0.95

signal_available_withdraw = strat1.get_signal__available_to_withdraw()
signal_available_deposit = strat1.get_signal__available_to_deposit()
signal_withdraw_delta = strat1.get_signal__withdraw_delta()
signal_deposit_delta = strat1.get_signal__deposit_delta()

print epoch.current_milli_time(), epoch.current_milli_time()
print 'total usd: ' + str(gdax_account.js['usd__num'] + cex_account.js['usd__num'])
print 'total eth: ' + str(gdax_account.js['eth__num'] + cex_account.js['eth__num'])
print gdax_account
print cex_account

print pretty_json(signal_withdraw_delta)
print pretty_json(signal_available_withdraw)
print pretty_json(signal_deposit_delta)
print pretty_json(signal_available_deposit)

strat1.market_snap()
