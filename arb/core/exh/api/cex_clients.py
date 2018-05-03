import collections
import hashlib
import hmac
import re
import time
import uuid

import requests

from arb import logger, EXCHANGE_API_TIMEOUT
from arb.utils.common import current_milli_time


class CexAuthClient(object):
    def __init__(self, api_url, api_user_id, api_key, api_secret):
        self.api_url = api_url
        self.api_user_id = api_user_id
        self.api_key = api_key
        self.api_secret = api_secret

    def __get_signature(self):
        nonce = '{:.10f}'.format(time.time() * 1000).split('.')[0]
        message = nonce + self.api_user_id + self.api_key
        signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
        data = {
            'key': self.api_key,
            'signature': signature,
            'nonce': nonce
        }
        return data

    def get_account(self):
        req_url = self.api_url + '/balance/'
        data = self.__get_signature()

        req = requests.post(req_url, data=data)
        return req.json()

    def place_order(self, side, product_id, price, size, order_type='limit'):
        req_url = self.api_url + '/place_order/{}'.format(product_id)

        data = self.__get_signature()
        data['amount'] = size
        data['type'] = side
        if order_type == 'market':
            data['order_type'] = order_type
        else:
            data['price'] = price

        req = requests.post(req_url, data=data)
        return req.json()

    def cancel_order(self, order_id):
        url = self.api_url + '/cancel_order/'
        data = self.__get_signature()
        data['id'] = order_id

        req = requests.post(url, data=data)
        return req.json()

        # def get_crypto_address(self, product='ETH'):
        #     data = self.__get_signature()
        #     data['currency'] = product
        #     req = requests.post(self.url + '/get_address', data=data)
        #     return req.json()


class CexPublicClient(object):
    timeout = EXCHANGE_API_TIMEOUT

    def __init__(self, api_url):
        self.api_url = api_url

    def get_product_ticker(self, product_id):
        product_id = re.sub('-', '/', product_id)
        req_url = self.api_url + '/ticker/{}'.format(product_id)
        req = requests.get(req_url, timeout=self.timeout)
        return req.json()

    def get_product_order_book(self, product_id, depth):
        product_id = re.sub('-', '/', product_id)
        req_url = self.api_url + '/order_book/{}/?depth={}'.format(product_id, depth)
        req = requests.get(req_url, timeout=self.timeout)
        js = req.json()
        data = self.__structure_product_order_book(js, product_id)
        return data

    # def get_product_trades(self, product_id='BTC/USD', since=0):
    #     req = requests.get(self.url + '/trade_history/{}/?since={}'.format(product_id, since), timeout=self.timeout)
    #     return req.json()

    def __structure_product_order_book(self, data, product_id):
        new_data = collections.OrderedDict()

        new_data['uid'] = uuid.uuid4().hex
        new_data['exchange'] = 'cex'
        new_data['product'] = re.sub('/', '-', product_id).lower()
        new_data['timestamp__long'] = current_milli_time()

        bids = []
        for b in data['bids']:
            bid = collections.OrderedDict()
            bid["price__num"] = b[0]
            bid["size__num"] = b[1]
            bids.append(bid)
        new_data['bids'] = bids

        asks = []
        for a in data['asks']:
            ask = collections.OrderedDict()
            ask["price__num"] = a[0]
            ask["size__num"] = a[1]
            asks.append(ask)
        new_data['asks'] = asks

        return new_data
