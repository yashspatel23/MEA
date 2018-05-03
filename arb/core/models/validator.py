import re

from arb import MODEL_KEY_RE_PATTERN__BOOL, MODEL_KEY_RE_PATTERN__LONG, MODEL_KEY_RE_PATTERN__NUM, \
    MODEL_KEY_RE_PATTERN__MAP
from arb.core.models.exception import ModelKeyValueException


def validate_required_keys(js, keys):
    for key in keys:
        if key not in js.keys():
            msg = 'missing attribute key: ' + key
            raise ModelKeyValueException(msg)

        if not js.get(key):
            msg = 'attribute is null: ' + key
            raise ModelKeyValueException(msg)


def validate_json_attribute_key_value(js):
    """
    __bool: True, False

    __long: None, integer number

    __num: None, integer, decimal number

    __map: empty dict, or dict

    """
    if not isinstance(js, dict):
        raise ModelKeyValueException('Wrong json type; must be dict')

    for key, value in js.iteritems():
        if re.search(MODEL_KEY_RE_PATTERN__BOOL, key):
            if not isinstance(value, bool):
                msg = 'key:{0}|value:{1}|value-type:{2}'.format(key, value, type(value))
                raise ModelKeyValueException(msg)
        elif re.search(MODEL_KEY_RE_PATTERN__LONG, key):
            if not isinstance(value, (int, long, type(None))):
                msg = 'key:{0}|value:{1}|value-type:{2}'.format(key, value, type(value))
                raise ModelKeyValueException(msg)
        elif re.search(MODEL_KEY_RE_PATTERN__NUM, key):
            if not isinstance(value, (int, long, float, type(None))):
                msg = 'key:{0}|value:{1}|value-type:{2}'.format(key, value, type(value))
                raise ModelKeyValueException(msg)
        elif re.search(MODEL_KEY_RE_PATTERN__MAP, key):
            if not isinstance(value, dict):
                msg = 'key:{0}|value:{1}|value-type:{2}'.format(key, value, type(value))
                raise ModelKeyValueException(msg)
        else:
            pass # allow all data type
