from arb.core.exh.accounts import LiveTradingAccount
from arb.core.exh.backtest.accounts import BacktestingTradingAccount, MockTradingAccount
from arb.core.models import AccountModel
from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb import es, logger
from arb.utils.string import pretty_json
from arb.notebook import quick
import pandas as pd

print '\n\n\n'
print '------------------------'
print 'exchanges'
print '------------------------'

# view gdax
account_id = 'gdax'
exh = 'gdax'
sensitive_gdax_account = LiveTradingAccount(account_id, exh)
gdax_account = sensitive_gdax_account.sync_account_with_exh()

print '-' * 30
print 'gdax info'
print '-' * 30
print gdax_account

# view gdax
account_id = 'gdax'
exh = 'gdax'
sensitive_gdax_account = LiveTradingAccount(account_id, exh)
cex_account = sensitive_gdax_account.sync_account_with_exh()

print '-' * 30
print 'gdax info'
print '-' * 30
print cex_account

# # create accounts
# account_id = 'cex'
# exh = 'cex'
# cex_acc_js = {
#     "uid": account_id,
#     "timestamp__long": epoch.current_milli_time(),
#     "exchange": exh,
#     "country": "usa",
#     "usd__num": 0.0,
#     "eth__num": 0.0,
#     "btc__num": 0.0
# }
# cex_account = AccountModel.build(cex_acc_js)
# cex_account.db_save(es)


