from collections import OrderedDict
import os


def write_str_to_file(file_path, s):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'wb') as f:
        f.write(s)


def write_unicode_to_file(file_path, s):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'wb') as f:
        if isinstance(s, str):
            f.write(s)
        elif isinstance(s, unicode):
            f.write(s.encode('utf8'))
        else:
            raise Exception('unknown string type')


def read_str_from_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()


def read_unicode_from_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read().decode('utf8')


def write_to_csv(file_path, rows):
    """"
    Input
    ------------------------------------
    Must be flat
    [
      { "k1": "value" },
      { "k1": "value" },
    ]
    """
    fields = OrderedDict()
    for row in rows:
        for key in row:
            fields[key] = None

    field_names = fields.keys()
    df = pd.DataFrame(columns=field_names)

    for row in rows:
        df = df.append(row, ignore_index=True)

    df.to_csv(file_path, ',', header=True, index=False, encoding='utf-8')

    return df


# TESTING ONLY
if __name__ == '__main__':
#     with open('/tmp/healthgraph-curation/scrapy_export/spider__mayo.json') as f:
#     #     json_str = f.read()
#     #     ipdb.set_trace()
#         mayo_json = json.load(f, object_pairs_hook=OrderedDict)
#
#     file_path = '/tmp/healthgraph-curation/scrapy_export/zzz.csv'
#     items = map(lambda x: x['yield_item'], mayo_json)
#     items = to_key_value_json(items)
#     items = remove_duplicate(items)
#
#     df = write_csv(file_path, items)
#
#
#
    pass



