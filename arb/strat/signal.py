import json
from abc import ABCMeta, abstractmethod
from collections import OrderedDict


# SIGNAL_CAPITAL_AVAILABLE = 'SIGNAL_CAPITAL_AVAILABLE'
# SIGNAL_CAPITAL_IMBALANCE = 'SIGNAL_CAPITAL_IMBALANCE'
# SIGNAL_WITHDRAW = 'SIGNAL_WITHDRAW'
# SIGNAL_DEPOSIT = 'SIGNAL_DEPOSIT'


class SignalBase(object):
    __metaclass__ = ABCMeta  # abstract class

    def __init__(self, signal_nme):
        self.signal_name = signal_nme

    def __repr__(self):
        js = OrderedDict()
        js['signal_name'] = self.signal_name
        js['signal'] = self.get_signal()
        return json.dumps(js, indent=2)

    @abstractmethod
    def get_signal(self):
        raise NotImplementedError()


class SignalCapitalWithdraw(SignalBase):
    def __init__(self, signal_name, base_account, foreign_account, action_amount, buffer_factor):
        self.base_account = base_account
        self.foreign_account = foreign_account
        self.action_amount = action_amount
        self.buffer_factor = buffer_factor
        super(SignalCapitalWithdraw, self).__init__(signal_name)

    def get_signal(self):
        action_amount = self.action_amount
        eth_price = self.get_eth_price()

        gdax_account = self.trading_acc1.get_account()
        cex_account = self.trading_acc2.get_account()

        buffer_factor = self.CAPITAL_BUFFER_MULTIPLIER
        usd = gdax_account.js['usd__num']
        eth_value = cex_account.js['eth__num'] * eth_price

        signal = usd > action_amount and eth_value > action_amount * buffer_factor

        signal_js = OrderedDict()
        signal_js['signal'] = signal
        return signal_js


if __name__ == '__main__':
    pass






