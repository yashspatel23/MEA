# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
import inspect
import json
import logging
import os
import uuid
import requests

from elasticsearch import Elasticsearch
from elasticsearch.compat import string_types
from elasticsearch.exceptions import SerializationError, ElasticsearchException
from raven import Client as SentryClient


# --------------------------------
# Helpers
# --------------------------------
class InitializationException(Exception):
    """
    Exception that the backend database is not setup properly.
    """


class OrderedDictJsonSerializer(object):
    """The serializer used by the Elasticsearch
    client to serialized results.
    """
    mimetype = 'application/json'

    def default(self, data):
        if isinstance(data, (date, datetime)):
            return data.isoformat()
        elif isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, uuid.UUID):
            return str(data)
        raise TypeError("Unable to serialize %r (type: %s)" % (data, type(data)))

    def loads(self, s):
        try:
            return json.loads(s, object_pairs_hook=OrderedDict)
        except (ValueError, TypeError) as e:
            raise SerializationError(s, e)

    def dumps(self, data):
        # don't serialize strings
        if isinstance(data, string_types):
            return data

        try:
            return json.dumps(data, default=self.default, ensure_ascii=False)
        except (ValueError, TypeError) as e:
            raise SerializationError(data, e)


def get_bool(s, default=False):
    """
    'True' --> True; 'False' --> False

    Default is False
    """
    if s and s.lower() == 'true':
        result = True
    elif s and s.lower() == 'false':
        result = False
    elif isinstance(default, bool):
        result = default
    else:
        result = False

    return result


def setup_index(es, index, doctype, mapping, setting):
    try:
        if not es.indices.exists(index):
            payload_body = OrderedDict()
            payload_body['settings'] = setting
            payload_body['mappings'] = {
                doctype: mapping
            }
            es.indices.create(index, payload_body)
    except ElasticsearchException as e:
        logger.error('Encountering an unexpected elasticsearch error')
        raise e


def makedir(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

# --------------------------------
# Envs
# --------------------------------
FLASK_DEBUG_MODE = get_bool(os.environ.get('SERVER_DEBUG', False))
FLASK_SERVER_PORT = int(os.environ['SERVER_PORT'])

ES_HOST = os.environ['BACKEND_ES_HOST']
ES_PORT = int(os.environ['BACKEND_ES_PORT'])

LOG_FILE_NAME = os.environ['LOG_FILE_NAME']
APP_NAME = os.environ['APP_NAME']

GDAX_API_URL = os.environ['GDAX_API_URL']
GDAX_API_KEY = os.environ['GDAX_API_KEY']
GDAX_API_SECRET = os.environ['GDAX_API_SECRET']
GDAX_API_PASSPHRASE = os.environ['GDAX_API_PASSPHRASE']

CEX_API_URL = os.environ['CEX_API_URL']
CEX_API_USER_ID = os.environ['CEX_API_USER_ID']
CEX_API_KEY = os.environ['CEX_API_KEY']
CEX_API_SECRET = os.environ['CEX_API_SECRET']

TWILIO_ACCOUNT = os.environ['TWILIO_ACCOUNT']
TWILIO_TOKEN = os.environ['TWILIO_TOKEN']

SENTRY_URL = os.environ['SENTRY_URL']

# --------------------------------
# Paths and working dir
# --------------------------------
# The project root directory should look something like:
# The working directory is {ROOT_PATH}
# The PYTHONPATH includes {ROOT_PATH}/source
# ---------------------------------------
# ├── conf
# ├── credentialed-conf
# ├── arb
# │   ├── api
# │   ├── common
# │   ├── core
# ├── wsgi.py
# ---------------------------------------
try:
    script_path = os.path.abspath(os.path.dirname(__file__))
except NameError:  # ipython
    script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
ROOT_PATH = os.path.abspath(os.path.join(script_path, '..'))
LOG_FILE_DIR = os.path.abspath(os.path.join(ROOT_PATH, 'logs'))
LOG_FILE_PATH = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)

os.chdir(ROOT_PATH)
makedir(LOG_FILE_DIR)

# --------------------------------
# Const and Conf
# --------------------------------
ES_INDEX__order_book = 'order_book'
ES_INDEX__trade_hist = 'trade_hist'
ES_INDEX__account = 'account'
ES_INDEX__tx = 'tx'
ES_INDEX__audit_trading = 'audit_trading'
ES_INDICES = [
    ES_INDEX__order_book,
    ES_INDEX__trade_hist,
    ES_INDEX__account,
    ES_INDEX__tx,
    ES_INDEX__audit_trading
]
ES_DATA_TYPE = 'data'

EXCHANGE_NAME_GDAX = 'gdax'
EXCHANGE_NAME_CEX = 'cex'

EXCHANGE_PRODUCT_ID__BTC_USD = 'btc-usd'
EXCHANGE_PRODUCT_ID__ETH_USD = 'eth-usd'
EXCHANGE_PRODUCT_ID__LTC_USD = 'ltc-usd'

EXCHANGE_TICKER__USD = 'usd'
EXCHANGE_TICKER__ETH = 'eth'
EXCHANGE_TICKER__BTC = 'btc'

# timeout
EXCHANGE_API_TIMEOUT = 10  # In Seconds
ES_GET_TIMEOUT = 5  # In Seconds
ES_SEARCH_TIMEOUT = 30  # In Seconds

# limit price
LIMIT_PRICE_BUFFER_IN_FRACTION = 0.002  # 0.2%
LIMIT_PRICE_BUFFER_IN_USD = 1.0  # 1 usd


# models
# -----------------------
MODEL_KEY__uid = 'uid'  # mostly hex uuid, sometimes unique identifier (gdx account)
MODEL_KEY__created = 'created__long'  # long
MODEL_KEY__modified = 'modified__long'  # long
MODEL_KEY__timestamp = 'timestamp__long'  # long

MODEL_KEY_RE_PATTERN__BOOL = '__bool$'
MODEL_KEY_RE_PATTERN__LONG = '__long$'
MODEL_KEY_RE_PATTERN__NUM = '__num$'
MODEL_KEY_RE_PATTERN__MAP = '__map$'

MODEL_INDEX__book_order = "book_order"



_file_path = 'conf/elasticsearch/mapping__data.json'
with open(_file_path) as data_file:
    es_mapping = json.load(data_file)

_file_path = 'conf/elasticsearch/setting__data.json'
with open(_file_path) as data_file:
    es_setting = json.load(data_file)

_file_path = 'conf/elasticsearch/template__all.json'
with open(_file_path) as data_file:
    es_template = json.load(data_file)


# --------------------------------
# Logger
# --------------------------------
fh_formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(pathname)s|%(lineno)d|%(message)s',
                                 datefmt='%m/%d/%Y %I:%M:%S %p')
ch_formatter = logging.Formatter('%(levelname)s|%(module)s|%(lineno)d|%(message)s',
                                 datefmt='%m/%d/%Y %I:%M:%S %p')
fh = logging.FileHandler(LOG_FILE_PATH)
fh.setLevel(logging.DEBUG)
fh.setFormatter(fh_formatter)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(ch_formatter)

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.addHandler(fh)

elasticsearch_logger = logging.getLogger('elasticsearch')
elasticsearch_logger.setLevel(logging.ERROR)

# --------------------------------
# Backend services
# --------------------------------
es = Elasticsearch(
    hosts=[{
        'host': ES_HOST,
        'port': ES_PORT
    }],
    serializer=OrderedDictJsonSerializer()
)
sentry_client = SentryClient(
    dsn=SENTRY_URL,
)

# --------------------------------
# Initialization
# --------------------------------
logger.info('---------------------------------------------------------')
logger.info('Initialization path: : ' + script_path)
logger.info('Root path: ' + ROOT_PATH)
logger.info('Working dir path: : ' + os.getcwd())
logger.info('Log file: : ' + LOG_FILE_PATH)
logger.info('---------------------------------------------------------')
def bootstrap():
    """
    Prepare the database backend
    """
    # default settings for all indices
    url = 'http://{0}:{1}/_template/custom_all'.format(ES_HOST, str(ES_PORT))
    headers = {
        'Content-Type': 'application/json'
    }
    resp = requests.put(url, headers=headers, json=es_template)
    js = json.loads(resp.content, object_pairs_hook=OrderedDict)
    logger.info(json.dumps(js, indent=2))

    # data indices
    doctype = ES_DATA_TYPE
    mapping = es_mapping
    setting = es_setting
    for index in ES_INDICES:
        setup_index(es, index, doctype, mapping, setting)

