import copy
import json
import uuid
from abc import ABCMeta, abstractmethod

from elasticsearch.exceptions import NotFoundError

from arb import ES_DATA_TYPE
from arb import ES_INDEX__account
from arb import ES_INDEX__order_book, ES_INDEX__audit_trading, ES_GET_TIMEOUT, ES_SEARCH_TIMEOUT
from arb import MODEL_KEY__created
from arb import MODEL_KEY__modified
from arb import MODEL_KEY__timestamp
from arb import MODEL_KEY__uid
from arb.core.models.fixer import fix_ordered_keys, fix_json_key_value
from arb.core.models.validator import validate_required_keys, validate_json_attribute_key_value
from arb.utils.common import current_milli_time


def default_es_get_params():
    return {
        'request_timeout': ES_GET_TIMEOUT,
    }


def default_es_search_params():
    return {
        'request_timeout': ES_SEARCH_TIMEOUT,
    }


class BaseModel(object):
    __metaclass__ = ABCMeta  # abstract class

    @property
    def uid(self):
        return self.js[MODEL_KEY__uid]

    @property
    def ordered_js(self):
        return fix_ordered_keys(self.js, self.key_order)

    def __init__(self, js):
        """
        Parameters
        ----------------------------------------
        js: dict, prefer OrderedDict over vanilla dict
        """
        # required class properties
        if not self.index:
            raise NotImplementedError('require class property: index')
        if not self.doctype:
            raise NotImplementedError('require class property: doctype')
        if not self.required_keys:
            raise NotImplementedError('require class property: required_keys')
        if not self.key_order:
            raise NotImplementedError('require class property: key_order')

        # validations
        validate_required_keys(js, self.required_keys)
        validate_json_attribute_key_value(js)

        # defensive copy
        self.js = copy.deepcopy(js)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return dict(self.js) == dict(other.js)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return json.dumps(self.ordered_js, indent=2)

    def __unicode__(self):
        return unicode(self.__repr__(), "utf-8")

    def __str__(self):
        return unicode(self).encode('utf-8')

    @classmethod
    @abstractmethod
    def build(cls, js):
        raise NotImplementedError('build an instance from a json')

    @classmethod
    @abstractmethod
    def parse(cls, js):
        raise NotImplementedError('deserialize instance from a proper json')

    @classmethod
    def db_get(cls, es, uid):
        """
        Return a dict holding the data

        None if it does not exist
        """
        js = None
        try:
            params = default_es_get_params()
            js = es.get(index=cls.index, doc_type=cls.doctype, id=uid, params=params)['_source']
        except NotFoundError:
            pass
        return js

    def db_save(self, es):
        index = self.index
        doctype = self.doctype

        add_modified(self.js)

        # save entity
        es.index(index, doctype, self.ordered_js, self.uid)


class OrderBookModel(BaseModel):
    index = ES_INDEX__order_book
    doctype = ES_DATA_TYPE
    required_keys = [
        MODEL_KEY__uid,
        "exchange",
        "product"
    ]
    key_order = [
        MODEL_KEY__uid,
        MODEL_KEY__created,
        MODEL_KEY__modified,
        "exchange",
        "product"
    ]

    @classmethod
    def build(cls, js):
        add_uuid(js)
        add_created(js)
        return OrderBookModel(js)

    @classmethod
    def parse(cls, js):
        return OrderBookModel(js)


class AccountModel(BaseModel):
    """
    {
      "uid": "gdx",
      "created__long": 1504112182975,  // only useful for db
      "modified__long": 1504112182975, // only useful for db
      "timestamp__long": "1504112155203",
      "exchange": "gdax",
      "country": "usa",
      "usd__num": 123.2,
      "eth__num": 10.12311232,
      "btc__num": 2.35784354
    }
    """
    index = ES_INDEX__account
    doctype = ES_DATA_TYPE
    required_keys = [
        MODEL_KEY__uid,
        MODEL_KEY__timestamp,
        "exchange"
    ]
    key_order = [
        MODEL_KEY__uid,
        MODEL_KEY__created,
        MODEL_KEY__modified,
        MODEL_KEY__timestamp,
        "exchange",
        "country"
    ]

    @classmethod
    def build(cls, js):
        add_uuid(js)
        add_created(js)
        return AccountModel(js)

    @classmethod
    def parse(cls, js):
        return AccountModel(js)


class AuditTradeModel(BaseModel):
    """
    {
      "uid": "2b2fe34600ce465fbf5b438f94e41928",
      "created__long": 1504112182975,
      "modified__long": 1504112182975,

      "strategy_run_id": 'ce251b1c602f4b129706ba681e22b2e1',
      "timestamp__long": "1504112155203",
      "product": "eth-usd",
      "action": "withdraw",
      "withdraw_delta": 0.043,

      "total_eth": 20000.0
      "total_usd": 53.0

      "gdax_account__map": {
        "uid": "backtesting_gdx_001",
        "created__long": 1504843047710,
        "modified__long": 1504843089125,
        "timestamp__long": 1503277200000,
        "exchange": "gdax",
        "country": "usa",
        "btc__num": 0.0,
        "usd__num": 4990.043303669622,
        "eth__num": 50.65081482893356
      },
      "cex_account__map": {
        "uid": "backtesting_cex_001",
        "created__long": 1504843047710,
        "modified__long": 1504843089125,
        "timestamp__long": 1503277200000,
        "exchange": "cex",
        "country": "usa",
        "btc__num": 0.0,
        "usd__num": 4990.043303669622,
        "eth__num": 50.65081482893356
      }
    }
    """
    index = ES_INDEX__audit_trading
    doctype = ES_DATA_TYPE
    required_keys = [
        MODEL_KEY__uid,
        'timestamp',
        'timestamp__long',
        'strategy_run_id',
        'product',
        'action',
    ]
    key_order = [
        MODEL_KEY__uid,
        MODEL_KEY__created,
        MODEL_KEY__modified,

        'strategy_run_id',
        'timestamp',
        'timestamp__long',
        'product',
        'action',

        'signal',

        "total_usd__num",
        "total_eth__num",
        'gdax_account',
        'cex_account',
    ]

    @classmethod
    def build(cls, js):
        add_uuid(js)
        add_created(js)
        return AuditTradeModel(js)

    @classmethod
    def parse(cls, js):
        return AuditTradeModel(js)


# ------------
# HELPERS
# ------------
def add_uuid(js):
    if MODEL_KEY__uid not in js:
        js[MODEL_KEY__uid] = uuid.uuid4().hex


def add_created(js):
    if MODEL_KEY__created not in js:
        js[MODEL_KEY__created] = current_milli_time()


def add_modified(js):
    js[MODEL_KEY__modified] = current_milli_time()

