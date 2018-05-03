from collections import OrderedDict


KEY_TESTING_DATA = 'testing_data__bool'


def ensure_test_data(js):
    js[KEY_TESTING_DATA] = True
    return js


def remove_testing_data(es):
    query = {
        'query': {
            'term': {
                KEY_TESTING_DATA: True
            }
        }
    }

    url = '/*' + '/_delete_by_query'
    es.indices.refresh()
    es.transport.perform_request('POST', url, body=query)
    es.indices.refresh()
    pass
