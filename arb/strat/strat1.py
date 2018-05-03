import json
from collections import OrderedDict

from arb import es, logger
from arb.core.models import AuditTradeModel
from arb.strat import helpers
from arb.utils import epoch


class Strat1(object):
    """
    Contain the trading logic at each moment in in time
    """
    strategy_name = 'strategy001'

    ticker = 'eth'
    CAPITAL_BUFFER_MULTIPLIER = 1.111
    THRESHOLD_WITHDRAW_DELTA = 0.030
    THRESHOLD_DEPOSIT_DELTA  = 0.005

    SNAP_REPETITION = 5  # How many times market_snap repeats
    WITHDRAW_ACTION_AMOUNT = 1000.0  # the USD amount for each action
    DEPOSIT_ACTION_AMOUNT = 1000.0 * 0.95  # the USD amount for each action

    def __init__(self, run_id, run_description, strategy_trading_accounts):
        self.run_id = run_id
        self.run_description = run_description
        self.trading_acc1 = strategy_trading_accounts[0]
        self.trading_acc2 = strategy_trading_accounts[1]

    def __repr__(self):
        accounts = []
        accounts.append(self.trading_acc1.get_account().js)
        accounts.append(self.trading_acc2.get_account().js)

        js = OrderedDict()
        js['strategy_name'] = 'strat1'
        js['accounts'] = accounts
        return json.dumps(js, indent=2)

    def get_signal__available_to_withdraw(self, timestamp=-1):
        ticker = self.ticker
        action_amount = self.WITHDRAW_ACTION_AMOUNT
        buffer_factor = self.CAPITAL_BUFFER_MULTIPLIER
        gdax_account = self.trading_acc1.get_account()
        cex_account = self.trading_acc2.get_account()
        gdax_ob = self.trading_acc1.get_order_book(ticker=ticker, timestamp=timestamp)

        gdax_usd = gdax_account.js['usd__num']
        cex_eth_shares_needed = helpers.compute_shares_needed(action_amount, gdax_ob)
        cex_eth_shares = cex_account.js['eth__num']

        signal = gdax_usd > action_amount and cex_eth_shares > cex_eth_shares_needed * buffer_factor

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'available to withdraw'
        signal_js['gdax_usd'] = gdax_account.js['usd__num']
        signal_js['gdax_eth'] = gdax_account.js['eth__num']
        signal_js['cex_usd'] = cex_account.js['usd__num']
        signal_js['cex_eth'] = cex_account.js['eth__num']
        signal_js['signal'] = signal
        return signal_js

    def get_signal__available_to_deposit(self, timestamp=-1):
        """
        Look at two accounts and see if we need to re-balance.
        """
        ticker = self.ticker
        action_amount = self.DEPOSIT_ACTION_AMOUNT
        buffer_factor = self.CAPITAL_BUFFER_MULTIPLIER
        gdax_account = self.trading_acc1.get_account()
        cex_account = self.trading_acc2.get_account()
        gdax_ob = self.trading_acc1.get_order_book(ticker=ticker, timestamp=timestamp)
        cex_ob = self.trading_acc2.get_order_book(ticker=ticker, timestamp=timestamp)

        gdax_eth_shares = gdax_account.js['eth__num']
        gdax_eth_shares_needed = helpers.compute_shares_needed(action_amount, gdax_ob)

        cex_usd = cex_account.js['usd__num']
        cex_usd_needed = helpers.compute_usd_spent(gdax_eth_shares_needed, cex_ob)

        signal_part_1 = gdax_eth_shares > gdax_eth_shares_needed * buffer_factor
        signal_part_2 = cex_usd > cex_usd_needed * buffer_factor
        signal = signal_part_1 and signal_part_2

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'available to deposit'
        signal_js['gdax_usd'] = gdax_account.js['usd__num']
        signal_js['gdax_eth'] = gdax_account.js['eth__num']
        signal_js['cex_usd'] = cex_account.js['usd__num']
        signal_js['cex_eth'] = cex_account.js['eth__num']
        signal_js['signal'] = signal
        return signal_js

    def get_signal__withdraw_delta(self, timestamp=-1):
        """
        Buy at GDAX, SELL at CEX => What is the delta?
        """
        ticker = self.ticker
        amount = self.WITHDRAW_ACTION_AMOUNT
        threshold = self.THRESHOLD_WITHDRAW_DELTA

        gdax_ob = self.trading_acc1.get_order_book(ticker=ticker, timestamp=timestamp)
        cex_ob = self.trading_acc2.get_order_book(ticker=ticker, timestamp=timestamp)
        delta = helpers.compute_delta__withdraw_cash(amount, gdax_ob, cex_ob)

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'withdraw delta'
        signal_js['withdraw_delta'] = delta
        signal_js['signal'] = delta > threshold
        return signal_js

    def get_signal__deposit_delta(self, timestamp=-1):
        """
        Sell at GDAX, Buy at CEX => What is the delta?
        """
        ticker = self.ticker
        amount = self.DEPOSIT_ACTION_AMOUNT
        threshold = self.THRESHOLD_DEPOSIT_DELTA

        gdax_ob = self.trading_acc1.get_order_book(ticker=ticker, timestamp=timestamp)
        cex_ob = self.trading_acc2.get_order_book(ticker=ticker, timestamp=timestamp)
        delta = helpers.compute_delta__deposit_cash(amount, gdax_ob, cex_ob)

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'deposit delta'
        signal_js['deposit_delta'] = delta
        signal_js['signal'] = delta < threshold
        return signal_js

    def exe_withdraw(self, timestamp=-1):
        """
        1. gdax buy withdraw amount --> shares
        2. cex sell "shares"
        """
        t0 = epoch.current_milli_time()
        ticker = self.ticker
        gdax_amount = self.WITHDRAW_ACTION_AMOUNT
        gdax_trading_account = self.trading_acc1
        cex_trading_account = self.trading_acc2
        gdax_ob = gdax_trading_account.get_order_book(ticker=ticker, timestamp=timestamp)
        cex_ob = cex_trading_account.get_order_book(ticker=ticker, timestamp=timestamp)
        gdax_balances_before = gdax_trading_account.get_balances()
        cex_balances_before = cex_trading_account.get_balances()

        # pre-calculation
        shares = helpers.compute_buy(gdax_amount, gdax_ob)
        buy_price_upperbound = helpers.compute_buy_upperbound(shares, gdax_ob)
        sell_price_lowerbound = helpers.compute_sell_lowerbound(shares, cex_ob)

        # trade
        gdax_trading_account\
            .place_limit_order('buy', ticker, buy_price_upperbound, shares, timestamp=timestamp)
        cex_trading_account\
            .place_limit_order('sell', ticker, sell_price_lowerbound, shares, timestamp=timestamp)

        # audit info
        gdax_balances_after = gdax_trading_account.get_balances()
        cex_balances_after = cex_trading_account.get_balances()
        t1 = epoch.current_milli_time()
        audit_info = build_audit_info(ticker, 'withdraw',
                                      buy_price_upperbound, sell_price_lowerbound,
                                      shares, gdax_amount,
                                      t0, t1,
                                      gdax_balances_before,
                                      gdax_balances_after,
                                      cex_balances_before,
                                      cex_balances_after)
        return audit_info

    def exe_deposit(self, timestamp=-1):
        """
        1. gdax sell deposit amount --> shares
        2. cex buy "shares"
        """
        t0 = epoch.current_milli_time()
        ticker = self.ticker
        gdax_amount = self.DEPOSIT_ACTION_AMOUNT
        gdax_trading_account = self.trading_acc1
        cex_trading_account = self.trading_acc2
        gdax_ob = gdax_trading_account.get_order_book(ticker=ticker, timestamp=timestamp)
        cex_ob = cex_trading_account.get_order_book(ticker=ticker, timestamp=timestamp)
        gdax_balances_before = gdax_trading_account.get_balances()
        cex_balances_before = cex_trading_account.get_balances()

        # pre-calculation
        shares = helpers.compute_shares_needed(gdax_amount, gdax_ob)
        buy_price_upperbound = helpers.compute_buy_upperbound(shares, cex_ob)
        sell_price_lowerbound = helpers.compute_sell_lowerbound(shares, gdax_ob)

        # trade
        gdax_trading_account \
            .place_limit_order('sell', ticker, sell_price_lowerbound, shares, timestamp=timestamp)
        cex_trading_account \
            .place_limit_order('buy', ticker, buy_price_upperbound, shares, timestamp=timestamp)

        # audit info
        gdax_balances_after = gdax_trading_account.get_balances()
        cex_balances_after = cex_trading_account.get_balances()
        t1 = epoch.current_milli_time()
        audit_info = build_audit_info(ticker, 'deposit',
                                      buy_price_upperbound, sell_price_lowerbound,
                                      shares, gdax_amount,
                                      t0, t1,
                                      gdax_balances_before,
                                      gdax_balances_after,
                                      cex_balances_before,
                                      cex_balances_after)
        return audit_info

    def market_snap(self, timestamp = -1):
        """
        Main logic about exactly what to do for each market interaction

        1. calculate account signals
        2. calculate market signals
        3. use signals to make decisions
        """
        # refresh account states
        self.trading_acc1.sync_account_with_exh()
        self.trading_acc2.sync_account_with_exh()

        signal_available_withdraw = self.get_signal__available_to_withdraw()
        signal_available_deposit = self.get_signal__available_to_deposit()
        signal_withdraw_delta = self.get_signal__withdraw_delta(timestamp)
        signal_deposit_delta = self.get_signal__deposit_delta(timestamp)

        def mk_audit_js():
            gdax_account = self.trading_acc1.get_account()
            cex_account = self.trading_acc2.get_account()
            transaction_t = epoch.current_milli_time() if timestamp == -1 else timestamp

            audit_js = OrderedDict()
            audit_js['strategy_run_id'] = self.run_id
            audit_js['timestamp'] = epoch.to_str(transaction_t)
            audit_js['timestamp__long'] = transaction_t
            audit_js['product'] = self.ticker
            audit_js['strategy_info'] = {
                'THRESHOLD_WITHDRAW_DELTA': self.THRESHOLD_WITHDRAW_DELTA,
                'THRESHOLD_DEPOSIT_DELTA': self.THRESHOLD_DEPOSIT_DELTA,
                'WITHDRAW_ACTION_AMOUNT': self.WITHDRAW_ACTION_AMOUNT,
                'DEPOSIT_ACTION_AMOUNT': self.DEPOSIT_ACTION_AMOUNT,
                'SNAP_REPETITION': self.SNAP_REPETITION
            }
            audit_js['signal'] = OrderedDict()
            audit_js['signal']['withdraw_delta'] = signal_withdraw_delta
            audit_js['signal']['available_withdraw'] = signal_available_withdraw
            audit_js['signal']['deposit_delta'] = signal_deposit_delta
            audit_js['signal']['available_deposit'] = signal_available_deposit
            audit_js['total_usd__num'] = gdax_account.js['usd__num'] + cex_account.js['usd__num']
            audit_js['total_eth__num'] = gdax_account.js['eth__num'] + cex_account.js['eth__num']
            audit_js['gdax_account'] = gdax_account.js
            audit_js['cex_account'] = cex_account.js
            return audit_js

        snap_again = False  # Only repeat if we have an execution
        if signal_available_withdraw['signal'] and signal_withdraw_delta['signal']:
            exec_context = self.exe_withdraw(timestamp)
            snap_again = True

            # Audit
            audit_js = mk_audit_js()
            audit_js['action'] = exec_context
            audit = AuditTradeModel.build(audit_js)
            logger.info('-----Executed Withdraw-----')
            logger.info(audit)
            logger.info('---------------------------')
            audit.db_save(es)

        if signal_available_deposit['signal'] and signal_deposit_delta['signal']:
            exec_context = self.exe_deposit(timestamp)
            snap_again = True

            # Audit
            audit_js = mk_audit_js()
            audit_js['action'] = exec_context
            audit = AuditTradeModel.build(audit_js)
            logger.info('-----Executed Deposit-----')
            logger.info(audit)
            logger.info('---------------------------')
            audit.db_save(es)

        # Extra logging
        audit_js = mk_audit_js()
        logger.info('Post snapping states: \n' + json.dumps(audit_js, indent=2))

        return snap_again

    def _snap_helper(self, snap_counter, timestamp=-1):
        snap_again = self.market_snap(timestamp)
        if snap_again and snap_counter < self.SNAP_REPETITION:
            snap_again = self._snap_helper(snap_counter + 1, timestamp)

        return snap_again

    def snap(self, timestamp=-1):
        # # Testing code only
        # if random.uniform(0, 1) < 0.9:
        #     raise RuntimeError('Deliberate runtime exception to test fail fast')

        return self._snap_helper(1, timestamp)


# ------------------------
# HELPERS
# ------------------------
def build_audit_info(ticker, action_type,
                     buy_price_upperbound, sell_price_lowerbound,
                     shares, action_amount,
                     t0, t1,
                     gdax_balances_before,
                     gdax_balances_after,
                     cex_balances_before,
                     cex_balances_after):
    t_delta = t1 - t0

    gdax_usd_diff = float(gdax_balances_after['usd']) - float(gdax_balances_before['usd'])
    gdax_eth_diff = float(gdax_balances_after['eth']) - float(gdax_balances_before['eth'])
    cex_usd_diff = float(cex_balances_after['usd']) - float(cex_balances_before['usd'])
    cex_eth_diff = float(cex_balances_after['eth']) - float(cex_balances_before['eth'])

    total_usd_before = float(gdax_balances_before['usd']) + float(cex_balances_before['usd'])
    total_usd_after = float(gdax_balances_after['usd']) + float(cex_balances_after['usd'])
    total_eth_before = float(gdax_balances_before['eth']) + float(cex_balances_before['eth'])
    total_eth_after = float(gdax_balances_after['eth']) + float(cex_balances_after['eth'])
    total_usd_diff = total_usd_after - total_usd_before
    total_eth_diff = total_eth_after - total_eth_before

    audit_info = OrderedDict()
    audit_info['method_execution_time'] = t_delta
    audit_info['ticker'] = ticker
    audit_info['action_type'] = action_type
    audit_info['total_usd_diff'] = total_usd_diff
    audit_info['total_eth_diff'] = total_eth_diff
    audit_info['shares'] = shares
    audit_info['action_amount'] = action_amount
    audit_info['buy_price_upperbound'] = buy_price_upperbound
    audit_info['sell_price_lowerbound'] = sell_price_lowerbound
    audit_info['gdax_balances_before'] = gdax_balances_before
    audit_info['gdax_balances_after'] = gdax_balances_after
    audit_info['gdax_usd_diff'] = gdax_usd_diff
    audit_info['gdax_eth_diff'] = gdax_eth_diff
    audit_info['cex_balances_before'] = cex_balances_before
    audit_info['cex_balances_after'] = cex_balances_after
    audit_info['cex_usd_diff'] = cex_usd_diff
    audit_info['cex_eth_diff'] = cex_eth_diff
    audit_info['total_usd_before'] = total_usd_before
    audit_info['total_eth_before'] = total_eth_before
    audit_info['total_usd_after'] = total_usd_after
    audit_info['total_eth_after'] = total_eth_after

    return audit_info


if __name__ == '__main__':
    pass

