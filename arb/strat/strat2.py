import json
from collections import OrderedDict

from arb import es, logger
from arb.core.models import AuditTradeModel
from arb.strat import helpers
from arb.utils import epoch


class Strat2(object):
    """
    Circular buffer
    """
    strategy_name = 'strategy02__circular_buffer'
    ticker = 'eth'

    def __init__(self, run_id, run_description, strategy_trading_accounts,
                 buy_threshold=0.020,
                 action_amount=10000.0,
                 capital_buffer_multiplier=1.01,
                 snap_repetition=5):
        self.run_id = run_id
        self.run_description = run_description
        self.trading_acc1 = strategy_trading_accounts[0]
        self.trading_acc2 = strategy_trading_accounts[1]

        self.buy_threshold = buy_threshold
        self.action_amount = action_amount
        self.capital_buffer_multiplier = capital_buffer_multiplier
        self.snap_repetition = snap_repetition


    def _strategy_info(self):
        accounts = []
        accounts.append(self.trading_acc1.get_account().js)
        accounts.append(self.trading_acc2.get_account().js)

        js = OrderedDict()
        js['strategy_name'] = self.strategy_name
        js['run_id'] = self.run_id
        js['buy_threshold'] = self.buy_threshold
        js['action_amount'] = self.action_amount
        js['accounts'] = accounts
        return js

    def __repr__(self):
        return json.dumps(self._strategy_info(), indent=2)

    def get_signal__arbitrage_delta(self, timestamp=-1):
        """
        Buy at GDAX, SELL at CEX => What is the delta?
        """
        ticker = self.ticker
        amount = self.action_amount
        threshold = self.buy_threshold

        gdax_ob = self.trading_acc1.get_order_book(ticker=ticker, timestamp=timestamp)
        cex_ob = self.trading_acc2.get_order_book(ticker=ticker, timestamp=timestamp)
        delta = helpers.compute_delta__withdraw_cash(amount, gdax_ob, cex_ob)

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'arbitrage delta'
        signal_js['arbitrage_delta'] = delta
        signal_js['signal'] = delta > threshold
        return signal_js

    def get_signal__gdax_has_usd(self, timestamp=-1):
        action_amount = self.action_amount
        gdax_account = self.trading_acc1.get_account()
        gdax_usd = gdax_account.js['usd__num']

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'gdax_has_usd'
        signal_js['gdax_usd'] = gdax_usd
        signal_js['gdax_eth'] = gdax_account.js['eth__num']
        signal_js['signal'] = gdax_usd > action_amount
        return signal_js

    def get_signal__gdax_has_eth(self, timestamp=-1):
        gdax_account = self.trading_acc1.get_account()
        gdax_usd = gdax_account.js['usd__num']
        gdax_eth = gdax_account.js['eth__num']

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'gdax_has_usd'
        signal_js['gdax_usd'] = gdax_usd
        signal_js['gdax_eth'] = gdax_eth
        signal_js['signal'] = gdax_eth > 0.5
        return signal_js

    def get_signal__cex_has_eth(self, timestamp=-1):
        cex_account = self.trading_acc2.get_account()
        cex_usd = cex_account.js['usd__num']
        cex_eth = cex_account.js['eth__num']

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'cex_has_eth'
        signal_js['cex_usd'] = cex_usd
        signal_js['cex_eth'] = cex_eth
        signal_js['signal'] = cex_usd > 0.3
        return signal_js

    def get_signal__arbitrage_delta(self, timestamp=-1):
        """
        Buy at GDAX, SELL at CEX => What is the delta?
        """
        ticker = self.ticker
        amount = self.action_amount
        threshold = self.buy_threshold

        gdax_ob = self.trading_acc1.get_order_book(ticker=ticker, timestamp=timestamp)
        cex_ob = self.trading_acc2.get_order_book(ticker=ticker, timestamp=timestamp)
        delta = helpers.compute_delta__withdraw_cash(amount, gdax_ob, cex_ob)

        signal_js = OrderedDict()
        signal_js['signal_name'] = 'arbitrage delta'
        signal_js['arbitrage_delta'] = delta
        signal_js['signal'] = delta > threshold
        return signal_js

    def exec_gdax_buy(self, timestamp=-1):
        ticker = self.ticker
        gdax_amount = self.action_amount / self.capital_buffer_multiplier
        gdax_trading_account = self.trading_acc1
        gdax_ob = gdax_trading_account.get_order_book(ticker=ticker, timestamp=timestamp)
        shares = helpers.compute_buy(gdax_amount, gdax_ob)
        buy_price_upperbound = helpers.compute_buy_upperbound(shares, gdax_ob)

        # trade
        gdax_trading_account \
            .place_limit_order('buy', ticker, buy_price_upperbound, shares, timestamp=timestamp)

        # audit info
        audit_info = {
            'ticker': ticker,
            'action_type': 'exec_gdax_buy',
            'shares': shares,
            'targeted_amount':  gdax_amount,
            'buy_price_upperbound': buy_price_upperbound,
        }
        return audit_info

    def exec_cex_sell(self, timestamp=-1):
        ticker = self.ticker
        cex_trading_account = self.trading_acc2
        cex_ob = cex_trading_account.get_order_book(ticker=ticker, timestamp=timestamp)
        shares = cex_trading_account.get_balance(ticker)
        sell_price_lowerbound = helpers.compute_sell_lowerbound(shares, cex_ob)

        # trade
        cex_trading_account \
            .place_limit_order('sell', ticker, sell_price_lowerbound, shares, timestamp=timestamp)

        # audit info
        audit_info = {
            'ticker': ticker,
            'action_type': 'exec_cex_sell',
            'shares': shares,
            'sell_price_lowerbound': sell_price_lowerbound
        }
        return audit_info

    def exec_eth_transfer(self, timestamp=-1):
        """
        Transfer the entire amount from GDAX to CEX
        """
        ticker = self.ticker
        gdax_trading_account = self.trading_acc1
        cex_trading_account = self.trading_acc2
        gdax_eth_amount = gdax_trading_account.get_balance(ticker)
        cex_deposit_address = cex_trading_account.get_crypto_deposit_address(ticker)

        # transfer
        gdax_trading_account.transfer_crypto(ticker, cex_deposit_address, gdax_eth_amount)

        # audit info
        audit_info = {
            'ticker': ticker,
            'action_type': 'exec_eth_transfer',
            'gdax_eth_amount': gdax_eth_amount,
            'cex_deposit_address': cex_deposit_address
        }
        return audit_info

    def market_snap(self, timestamp = -1):
        """
        Main logic about exactly what to do for each market interaction
        """
        # refresh account states
        self.trading_acc1.sync_account_with_exh()
        self.trading_acc2.sync_account_with_exh()

        signal__arbitrage_delta = self.get_signal__arbitrage_delta()
        signal__gdax_has_usd = self.get_signal__gdax_has_usd()
        signal__gdax_has_eth = self.get_signal__gdax_has_eth()
        signal__cex_has_eth = self.get_signal__cex_has_eth()

        def mk_audit_js():
            gdax_account = self.trading_acc1.get_account()
            cex_account = self.trading_acc2.get_account()
            transaction_t = epoch.current_milli_time() if timestamp == -1 else timestamp

            audit_js = OrderedDict()
            audit_js['strategy_run_id'] = self.run_id
            audit_js['timestamp'] = epoch.to_str(transaction_t)
            audit_js['timestamp__long'] = transaction_t
            audit_js['ticker'] = self.ticker
            audit_js['strategy_info'] = self._strategy_info

            audit_js['signal'] = OrderedDict()
            audit_js['signal']['signal__gdax_has_usd'] = signal__gdax_has_usd
            audit_js['signal']['signal__gdax_has_eth'] = signal__gdax_has_eth
            audit_js['signal']['signal__cex_has_eth'] = signal__cex_has_eth
            audit_js['signal']['signal__arbitrage_delta'] = signal__arbitrage_delta

            audit_js['total_usd__num'] = gdax_account.js['usd__num'] + cex_account.js['usd__num']
            audit_js['total_eth__num'] = gdax_account.js['eth__num'] + cex_account.js['eth__num']
            audit_js['gdax_account'] = gdax_account.js
            audit_js['cex_account'] = cex_account.js
            return audit_js

        snap_again = False  # Only repeat if we have an gdax buy action
        if signal__gdax_has_usd['signal'] and signal__arbitrage_delta['signal']:
            exec_context = self.exec_gdax_buy(timestamp)
            snap_again = True

            # Audit
            audit_js = mk_audit_js()
            audit_js['action'] = exec_context
            audit = AuditTradeModel.build(audit_js)
            logger.info('-----Executed GDAX Buy-----')
            logger.info(audit)
            logger.info('---------------------------')
            audit.db_save(es)

        if signal__gdax_has_eth['signal']:
            exec_context = self.exec_eth_transfer()

            # Audit
            audit_js = mk_audit_js()
            audit_js['action'] = exec_context
            audit = AuditTradeModel.build(audit_js)
            logger.info('-----Executed ETH TRANSFER-----')
            logger.info(audit)
            logger.info('---------------------------')
            audit.db_save(es)

        if signal__cex_has_eth['signal']:
            exec_context = self.exec_cex_sell(timestamp)

            # Audit
            audit_js = mk_audit_js()
            audit_js['action'] = exec_context
            audit = AuditTradeModel.build(audit_js)
            logger.info('-----Executed CEX Sell-----')
            logger.info(audit)
            logger.info('---------------------------')
            audit.db_save(es)

        # Extra logging
        audit_js = mk_audit_js()
        logger.info('post-snapping states: \n' + json.dumps(audit_js, indent=2))

        return snap_again


if __name__ == '__main__':
    pass

