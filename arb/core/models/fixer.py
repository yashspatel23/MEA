import json
import re
from collections import OrderedDict

from arb import MODEL_KEY_RE_PATTERN__BOOL, MODEL_KEY_RE_PATTERN__LONG, MODEL_KEY_RE_PATTERN__NUM, \
    MODEL_KEY_RE_PATTERN__MAP
from arb.core.models.exception import ModelException


def fix_ordered_keys(js, keys):
    _js = OrderedDict()

    keys = filter(lambda x: x in js.keys(), keys)
    for key in keys:
        _js[key] = js[key]
    for key, value in js.iteritems():
        _js[key] = value

    return _js


def fix_json_key_value(js):
    """
    __bool: True, False

    __long: None, integer number

    __num: None, integer, decimal number

    __map: empty dict, or dict

    """
    if not isinstance(js, dict):
        raise ModelException('Wrong json type; must be dict')

    for key, value in js.iteritems():
        if re.search(MODEL_KEY_RE_PATTERN__BOOL, key):
            # __bool
            fix_value = _attempt_fix_bool(value)
            js[key] = fix_value

        elif re.search(MODEL_KEY_RE_PATTERN__LONG, key):
            # __long
            fix_value = _attempt_fix_long(value)
            js[key] = fix_value

        elif re.search(MODEL_KEY_RE_PATTERN__NUM, key):
            # __num
            fix_value = _attempt_fix_num(value)
            js[key] = fix_value

        elif re.search(MODEL_KEY_RE_PATTERN__MAP, key):
            # __map
            pass

        else:
            # string type
            fix_value = _attempt_fix_str(value)
            js[key] = fix_value

    return js


# ------------------------
# HELPERS
# ------------------------
def _attempt_fix_bool(value):
    result = value
    if isinstance(value, (str, unicode)):
        s = value.strip().lower()
        if s == 'true' or s == 'yes':
            result = True
        if s == 'false' or s == 'no':
            result = False

    if isinstance(value, (int, long, float)):
        n = int(value)
        if n == 1:
            result = True
        elif n == 0:
            result = False

    return result


def _attempt_fix_long(value):
    result = value
    if isinstance(value, (str, unicode)):
        s = value.strip().lower()
        try:
            result = long(float(s))
        except ValueError:
            pass

    return result


def _attempt_fix_num(value):
    result = value
    if isinstance(value, (str, unicode)):
        s = value.strip().lower()
        try:
            result = float(s)
        except ValueError:
            pass

    return result


def _attempt_fix_str(value):
    result = value
    if isinstance(value, (int, long, float, bool)):
        result = json.dumps(value)

    return result
