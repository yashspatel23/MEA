import unittest

from arb.core.exh.backtest.accounts import BacktestingTradingAccount
from arb.core.models import OrderBookModel
from arb.strat import helpers
from arb.utils import epoch


class TestComputingShares(unittest.TestCase):
    def test__001(self):
        timestamp = epoch.to_long('2017-08-21 13:00:00 PDT')
        amount = 1000.0
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        ob = trading_acc1.get_order_book(ticker='eth-usd', timestamp=timestamp)
        shares = helpers.compute_shares_needed(amount, ob)

        assert shares == amount / 330.2

    def test__002(self):
        timestamp = epoch.to_long('2017-08-23 20:00:00 PDT')
        amount = 20000.0
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        ob = trading_acc1.get_order_book(ticker='eth-usd', timestamp=timestamp)
        shares = helpers.compute_shares_needed(amount, ob)
        direct_calculation = 45.39426145+0.03269+(amount-45.39426145*316.17-0.03269*316.01)/316.0
        assert shares == direct_calculation

    def test__003(self):
        timestamp = epoch.to_long('2017-08-23 20:00:00 PDT')
        shares = 1
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        ob = trading_acc1.get_order_book(ticker='eth-usd', timestamp=timestamp)

        usd = helpers.compute_usd_spent(shares, ob)
        direct_calculation = 316.19
        assert usd == direct_calculation

    def test__004(self):
        timestamp = epoch.to_long('2017-08-23 20:00:00 PDT')
        shares = 25.86
        trading_acc1 = BacktestingTradingAccount(None, 'gdax')
        ob = trading_acc1.get_order_book(ticker='eth-usd', timestamp=timestamp)

        usd = helpers.compute_usd_spent(shares, ob)
        direct_calculation = 316.19 * 25.86
        assert usd == direct_calculation

    def test__005(self):
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "timestamp__long": 1503543603463,
            "sequence__long": 1036028392,
            "asks": [
                {
                    "price__num": 316.19,
                    "size__num": 25.86,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.2,
                    "size__num": 8.8439152,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.25,
                    "size__num": 7.45,
                    "num_orders__int": 2.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 30.0

        usd = helpers.compute_usd_spent(shares, ob)
        direct_calculation = 316.19 * 25.86 + 316.2 * (30 - 25.86)
        assert usd == direct_calculation

    def test__007(self):
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "asks": [
                {
                    "price__num": 316.19,
                    "size__num": 25.86,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.2,
                    "size__num": 8.8439152,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.25,
                    "size__num": 7.45,
                    "num_orders__int": 2.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 40.0

        usd = helpers.compute_usd_spent(shares, ob)
        direct_calculation = 316.19 * 25.86 + 316.2 * 8.8439152 + 316.25 * (shares - 25.86 - 8.8439152)
        assert usd == direct_calculation

    def test__008(self):
        """
        compute_sell
        """
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "bids": [
                {
                    "price__num": 316.17,
                    "size__num": 45.39426145,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.01,
                    "size__num": 0.03269,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.0,
                    "size__num": 22.6947,
                    "num_orders__int": 6.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 10.0

        usd = helpers.compute_sell(shares, ob)
        direct_calculation = 316.17 * shares
        assert usd == direct_calculation

    def test__009(self):
        """
        compute_sell
        """
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "bids": [
                {
                    "price__num": 316.17,
                    "size__num": 45.39426145,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.01,
                    "size__num": 0.03269,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.0,
                    "size__num": 22.6947,
                    "num_orders__int": 6.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 50.0

        usd = helpers.compute_sell(shares, ob)
        direct_calculation = 316.17 * 45.39426145 + 316.01 * 0.03269 + 316.0 * (shares - 45.39426145 - 0.03269)
        assert usd == direct_calculation

    def test__0010(self):
        """
        compute_by
        """
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "asks": [
                {
                    "price__num": 316.19,
                    "size__num": 25.86,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.2,
                    "size__num": 8.8439152,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.25,
                    "size__num": 7.45,
                    "num_orders__int": 2.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        amount = 3000

        shares = helpers.compute_buy(amount, ob)
        direct_calculation = amount / 316.19
        assert shares == direct_calculation

    def test__0011(self):
        """
        compute_buy
        """
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "asks": [
                {
                    "price__num": 316.19,
                    "size__num": 3.0,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.2,
                    "size__num": 8.8439152,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.25,
                    "size__num": 7.45,
                    "num_orders__int": 2.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        amount = 3000

        shares = helpers.compute_buy(amount, ob)
        direct_calculation = 3.0 + (amount - 316.19*3)/316.2
        assert shares == direct_calculation

    def test__computing_sell_eth_value__013(self):
        """
        computing sell value of some number of shares
        """
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "bids": [
                {
                    "price__num": 316.17,
                    "size__num": 45.39426145,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.01,
                    "size__num": 0.03269,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.0,
                    "size__num": 22.6947,
                    "num_orders__int": 6.0
                }
            ],
            "asks": [
                {
                    "price__num": 316.19,
                    "size__num": 3.0,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.2,
                    "size__num": 8.8439152,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.25,
                    "size__num": 7.45,
                    "num_orders__int": 2.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 2.0
        shares_value = helpers.compute_sell_value(shares, ob)

        direct_cal = shares * 316.17

        assert shares_value == direct_cal

    def test__computing_sell_eth_value__014(self):
        """
        computing sell value of some number of shares
        """
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "bids": [
                {
                    "price__num": 316.17,
                    "size__num": 2.39426145,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.01,
                    "size__num": 0.03269,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.0,
                    "size__num": 22.6947,
                    "num_orders__int": 6.0
                }
            ],
            "asks": [
                {
                    "price__num": 316.19,
                    "size__num": 3.0,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.2,
                    "size__num": 8.8439152,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.25,
                    "size__num": 7.45,
                    "num_orders__int": 2.0
                }
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 3.0
        shares_value = helpers.compute_sell_value(shares, ob)

        direct_cal = 2.39426145 * 316.17 + 0.03269 * 316.01 + (3 - 2.39426145 - 0.03269) * 316.0

        assert shares_value == direct_cal

    def test__compute_money_made__01(self):
        ob_js = {
            "uid": "71e689f5d4884dddb17f3f3b660b40f1",
            "created__long": 1503543603464,
            "modified__long": 1503543603468,
            "exchange": "gdax",
            "product": "eth-usd",
            "timestamp__long": 1503543603463,
            "sequence__long": 1036028392,
            "bids": [
                {
                    "price__num": 316.17,
                    "size__num": 2.39426145,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.01,
                    "size__num": 0.03269,
                    "num_orders__int": 1.0
                },
                {
                    "price__num": 316.0,
                    "size__num": 22.6947,
                    "num_orders__int": 6.0
                }
            ],
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 20

        usd = helpers.compute_usd_made(shares, ob)
        direct_calculation = 316.17*2.39426145 + 316.01*0.03269 + 316.0 * (shares - 2.39426145- 0.03269)
        assert usd == direct_calculation


if __name__ == '__main__':
    unittest.main()

    # pass


