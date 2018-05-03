from collections import OrderedDict
from arb.core.models.exception import ModelKeyValueException
import json
import uuid

from arb.core.models.fixer import fix_json_key_value

# --------------------------------
# __bool
# --------------------------------
def test__bool_key__pass_001():
    js = {
        'key__bool': True
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == True


def test__bool_key__pass_002():
    js = {
        'key__bool': u'yes'
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == True


def test__bool_key__pass_003():
    js = {
        'key__bool': 'True'
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == True


def test__bool_key__pass_004():
    js = {
        'key__bool': 1
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == True


def test__bool_key__pass_005():
    js = {
        'key__bool': u'no'
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == False


def test__bool_key__pass_006():
    js = {
        'key__bool': False
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == False


def test__bool_key__pass_007():
    js = {
        'key__bool': 0
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == False


def test__bool_key__pass_008():
    js = {
        'key__bool': u'False'
    }
    js = fix_json_key_value(js)

    assert js['key__bool'] == False


# --------------------------------
# __long, __num
# --------------------------------
def test__long_key__pass_001():
    js = {
        'key__long': 11
    }
    js = fix_json_key_value(js)

    assert js['key__long'] == 11


def test__long_key__pass_002():
    js = {
        'key__long': '11'
    }
    js = fix_json_key_value(js)

    assert js['key__long'] == 11


def test__long_key__pass_003():
    js = {
        'key__long': '11.2343'
    }
    js = fix_json_key_value(js)

    assert js['key__long'] == 11


def test__long_key__pass_004():
    js = {
        'key__long': 'a11.2343'
    }
    js = fix_json_key_value(js)

    assert js['key__long'] == 'a11.2343'


def test__num_key__pass_001():
    js = {
        'key__num': '11.2343'
    }
    js = fix_json_key_value(js)

    assert js['key__num'] == 11.2343


def test__num_key__pass_002():
    js = {
        'key__num': 11.2343
    }
    js = fix_json_key_value(js)

    assert js['key__num'] == 11.2343


# --------------------------------
# string type
# --------------------------------
def test__string_key__pass_001():
    js = {
        'key': 11
    }
    js = fix_json_key_value(js)

    assert js['key'] == '11'


def test__string_key__pass_002():
    js = {
        'key': u'11'
    }
    js = fix_json_key_value(js)

    assert js['key'] == u'11'


def test__string_key__pass_003():
    js = {
        'key': True
    }
    js = fix_json_key_value(js)

    assert js['key'] == 'true'


def test__string_key__pass_004():
    js = {
        'key': 23.34
    }
    js = fix_json_key_value(js)

    assert js['key'] == '23.34'


def test__string_key__pass_005():
    js = {
        'key': 22
    }
    js = fix_json_key_value(js)

    assert js['key'] == '22'


def test__string_key__pass_006():
    js = {
        'key': {'a': 'b'}
    }
    js = fix_json_key_value(js)

    assert js['key'] == {'a': 'b'}


def test__string_key__pass_007():
    js = {
        'key': 'value'
    }
    js = fix_json_key_value(js)

    assert js['key'] == 'value'

