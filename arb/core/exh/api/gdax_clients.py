import base64
import collections
import hashlib
import hmac
import json
import time
import uuid

import requests
from requests.auth import AuthBase

from arb import EXCHANGE_API_TIMEOUT
from arb.utils.common import current_milli_time


class GdaxPublicClient(object):
    timeout = EXCHANGE_API_TIMEOUT

    def __init__(self, api_url):
        self.api_url = api_url

    def get_product_order_book(self, product_id, level):
        req_url = self.api_url + '/products/{}/book'.format(product_id)
        params = {'level': level}
        req = requests.get(req_url, params=params, timeout=self.timeout)
        data = self.__structure_product_order_book(req.json(), product_id)
        return data

    # def get_products(self):
    #     req = requests.get(self.url + '/products', timeout=self.timeout)
    #     return req.json()

    # def get_product_ticker(self, product_id):
    #     req = requests.get(self.url + '/products/{}/ticker'.format(product_id), timeout=self.timeout)
    #     return req.json()

    # def get_product_trades(self, product_id):
    #     req = requests.get(self.url + '/products/{}/trades'.format(product_id), timeout=self.timeout)
    #     return req.json()

    def __structure_product_order_book(self, data, product_id):
        new_data = collections.OrderedDict()

        new_data['uid'] = uuid.uuid4().hex
        new_data['exchange'] = 'gdax'
        new_data['product'] = product_id.lower()
        new_data['timestamp__long'] = current_milli_time()
        new_data['sequence__long'] = data['sequence']

        bids = []
        for b in data['bids']:
            bid = collections.OrderedDict()
            bid["price__num"] = float(b[0])
            bid["size__num"] = float(b[1])
            bid["num_orders__int"] = float(b[2])
            bids.append(bid)
        new_data['bids'] = bids

        asks = []
        for a in data['asks']:
            ask = collections.OrderedDict()
            ask["price__num"] = float(a[0])
            ask["size__num"] = float(a[1])
            ask["num_orders__int"] = float(a[2])
            asks.append(ask)
        new_data['asks'] = asks

        return new_data


class GdaxAuthClient(object):
    timeout = EXCHANGE_API_TIMEOUT

    def __init__(self, api_url, api_key, api_secret, api_passphrase):
        self.api_url = api_url
        self.auth = GdaxAuthenticate(api_key, api_secret, api_passphrase)

    # def cancel_order(self, order_id):
    #     req_url = self.api_url + '/orders/' + order_id
    #     req = requests.delete(req_url, auth=self.auth, timeout=self.timeout)
    #     return req.json()

    # def withdraw_crypto(self, amount="", currency="", crypto_address=""):
    #     payload = {
    #         "amount": amount,
    #         "currency": currency,
    #         "crypto_address": crypto_address
    #     }
    #     req = requests.post(self.url + "/withdrawals/crypto", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
    #     return req.json()

    # def get_account(self, account_id):
    #     req_url = self.api_url + '/accounts/' + account_id
    #     req = requests.get(req_url, auth=self.auth, timeout=self.timeout)
    #     return req.json()

    def get_accounts(self):
        req_url = self.api_url + '/accounts'
        req = requests.get(req_url, auth=self.auth, timeout=self.timeout)
        return req.json()

    def get_order(self, order_id):
        req_url = self.api_url + '/orders/' + order_id
        req = requests.get(req_url, auth=self.auth, timeout=self.timeout)
        return req.json()

    def place_order(self, product_id, price, size, side, time_in_force='GTC', order_type='limit'):
        req_url = self.api_url + '/orders'
        payload = {
            'side': side,
            'price': price,
            'size': size,
            'product_id': product_id,
            'time_in_force': time_in_force,
            'type': order_type
        }
        req = requests.post(req_url, data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        return req.json()


class GdaxAuthenticate(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase
        })
        return request
