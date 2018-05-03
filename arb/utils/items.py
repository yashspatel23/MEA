from collections import OrderedDict
import copy
import json
import re


def to_key_value_json(items):
    _items = []
    for item in items:
        _item = OrderedDict()
        for k, v in item.iteritems():
            if re.search('(__arr$)|(__obj$)', k):
                v = json.dumps(v)
            
            _item[k] = v
        
        _items.append(_item)
    
    return _items


def remove_duplicate(_items):
    items = {}
    states = {}  # { hex_id: version }
    
    for _item in _items:
        _id = _item['id']
        version = _item['version']
        old_version = states.get(_id, -1)
        if version >= old_version:
            states[_id] = version
            items[_id] = _item
    
    _return = []
    for _, item in items.iteritems():
        _return.append(item)
    
    return _return


def dict_prepend(d, key, value):
    """
    """
    if isinstance(d, OrderedDict):
        clean_d = OrderedDict()
    elif isinstance(d, dict):
        clean_d = {}
    else:
        raise Exception("Incorrect type: cannot remove null values from non dictionary type.")
    
    clean_d[key] = value
    for (k, v) in d.iteritems():
        clean_d[k] = v
    
    return clean_d


def dict_remove_null(d):
    """
    1. None
    2. ''
    3. []
    4. { }
    """
    if isinstance(d, OrderedDict):
        clean_d = OrderedDict()
    elif isinstance(d, dict):
        clean_d = {}
    else:
        raise Exception("Incorrect type: cannot remove null values from non dictionary type.")
    
    for key, value in d.iteritems():
        if value:
            clean_d[key] = value
    
    return clean_d


def dict_deep_merge(a, b):
    """
    Merge b into a
    
    No Side Effect
    
    1. Recursively traverse the keys
    2. If leaf value is not present, add to a
    3. If leaf value are different, use value from b
    4. If leaf value is an array, append those from b to a
    """
    this = copy.deepcopy(a)
    that = copy.deepcopy(b)
    _merge(this, that)
    return this


def _merge(a, b, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _merge(a[key], b[key], path + [str(key)])
            else:
                _merge_leaf_value(a, b, key)
        else:
            a[key] = b[key]
    
    return a


def _merge_leaf_value(a, b, key):
    """
    1. x = y, pass
    2. x is an array, y is an array. combine them
    3. x is an array, y is not. Append y to x
    4. x is not an array, use y
    """
    if a[key] == b[key]:
        pass
    elif isinstance(a[key], list) and isinstance(b[key], list):
        for x in b[key]: 
            a[key].append(x)
    elif isinstance(a[key], list):
        a[key].append(b[key])
    else:
        a[key] = b[key]  # b[key] takes priority
    
    return a


if __name__ == '__main__':
    pass
