import unittest

from arb import logger
from arb.core.models import OrderBookModel
from arb.strat import helpers
from arb.utils import epoch


class TestComputingShares(unittest.TestCase):
    def test__01(self):
        """
        buy stopping price
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
        shares = 11
        stopping_price = helpers.compute_buy_stopping_price(shares, ob)
        direct_calculation = 316.2
        assert stopping_price == direct_calculation

    def test__02(self):
        """
        sell stopping price
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
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 10
        stopping_price = helpers.compute_sell_stopping_price(shares, ob)
        direct_calculation = 316.0
        assert stopping_price == direct_calculation

    def test__03(self):
        """
        sell stopping price
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
            ]
        }
        ob = OrderBookModel.parse(ob_js)
        shares = 10
        stopping_price = helpers.compute_sell_stopping_price(shares, ob)

        logger.info(stopping_price * 0.999)

        lowerbound = helpers.compute_sell_lowerbound(shares, ob)
        logger.info(ob)
        logger.info(stopping_price)
        logger.info(lowerbound)

        # direct_calculation = 316.0
        # assert stopping_price == direct_calculation



    # def test__computing_sell_eth_value__014(self):
    #     """
    #     computing sell value of some number of shares
    #     """
    #     ob_js = {
    #         "uid": "71e689f5d4884dddb17f3f3b660b40f1",
    #         "created__long": 1503543603464,
    #         "modified__long": 1503543603468,
    #         "exchange": "gdax",
    #         "product": "eth-usd",
    #         "bids": [
    #             {
    #                 "price__num": 316.17,
    #                 "size__num": 2.39426145,
    #                 "num_orders__int": 1.0
    #             },
    #             {
    #                 "price__num": 316.01,
    #                 "size__num": 0.03269,
    #                 "num_orders__int": 1.0
    #             },
    #             {
    #                 "price__num": 316.0,
    #                 "size__num": 22.6947,
    #                 "num_orders__int": 6.0
    #             }
    #         ],
    #         "asks": [
    #             {
    #                 "price__num": 316.19,
    #                 "size__num": 3.0,
    #                 "num_orders__int": 1.0
    #             },
    #             {
    #                 "price__num": 316.2,
    #                 "size__num": 8.8439152,
    #                 "num_orders__int": 1.0
    #             },
    #             {
    #                 "price__num": 316.25,
    #                 "size__num": 7.45,
    #                 "num_orders__int": 2.0
    #             }
    #         ]
    #     }
    #     ob = OrderBookModel.parse(ob_js)
    #     shares = 3.0
    #     shares_value = helpers.compute_sell_value(shares, ob)
    #
    #     direct_cal = 2.39426145 * 316.17 + 0.03269 * 316.01 + (3 - 2.39426145 - 0.03269) * 316.0
    #
    #     assert shares_value == direct_cal


if __name__ == '__main__':
    unittest.main()

    # pass


