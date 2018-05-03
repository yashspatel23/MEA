import base64
import hashlib
import json


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def bool_from_str(s, default=False):
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


def int_from_str(s):
    return int(s)


def base64_from_str(s):
    return base64.b64encode(s)


def base64_to_str(s):
    return base64.b64decode(s)


def sha_hash_dict(d):
    return hashlib.sha224(json.dumps(d)).hexdigest()


def pretty_json(obj):
    return json.dumps(obj, indent=2)


# TESTING
if __name__ == '__main__':
    pass
















