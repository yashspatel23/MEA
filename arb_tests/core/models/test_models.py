import json
import unittest
import uuid

from arb.core.models import OrderBookModel, AuditTradeModel
from arb import logger
from arb import es
from arb.core.models.exception import ModelKeyValueException
from arb.utils import epoch


class TestComputingShares(unittest.TestCase):
    def test__build_order_book_model__001(self):
        js1 = {
            "uid": "5cdf981ca55344fc84f390faa10dbafb",
            "key1__bool": False,
            "key2__long": 343,
            "key3": "buy",
            "exchange": "gdax",
            "product": "sdfds"
        }
        uid = js1['uid']
        ob = OrderBookModel.build(js1)
        assert ob.js['uid'] == uid


    def test__build_order_book_model__002(self):
        js = {
            "key1__bool": False,
            "key2__long": 343,
            # "product": "usdeth",
            "exchange": "gdax",
            "key3": "buy"
        }

        got_error = False
        try:
            ob = OrderBookModel.build(js)
        except ModelKeyValueException as e:
            got_error = True

        assert got_error


    def test__parse_order_book_model_should_fail__001(self):
        """
        should fail due to missing key
        """
        js = {
            # "uid": "5cdf981ca55344fc84f390faa10dbafb",
            "key1__bool": False,
            "key2__long": 343,
            "product": "usdeth",
            "exchange": "gdax",
        }
        got_error = False
        try:
            ob = OrderBookModel.parse(js)
        except ModelKeyValueException as e:
            got_error = True
        assert got_error


    def test__parse_order_book_model_should_pass__001(self):
        js = {
            "uid": "5cdf981ca55344fc84f390faa10dbafb",
            "key1__bool": False,
            "key2__long": 343,
            "product": "usdeth",
            "exchange": "gdax",
        }
        ob = OrderBookModel.parse(js)


    def test__db_save__and_db_get(self):
        js = {
            "product": "usdeth",
            "exchange": "gdax",
        }
        ob = OrderBookModel.build(js)
        uid = ob.uid

        # saving data
        ob.db_save(es)

        # get data
        js = ob.db_get(es, uid)
        ob2 = OrderBookModel.parse(js)

        assert ob == ob2

    def test__audit_trade_model__building_001(self):
        js = {
            'strategy_run_id': uuid.uuid4().hex,
            'product': 'eth-usd',
            'action': 'withdraw',
            'timestamp__long': epoch.current_milli_time()
        }
        ob = AuditTradeModel.build(js)
        assert ob.uid is not None



if __name__ == '__main__':
    unittest.main()






