import pandas as pd

from arb import es

query = {
    "size": 10000,
    "sort": [
        {
            "timestamp__long": {
                "order": "asc"
            }
        }
    ],
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "strategy_run_id": "15cd75e262634277a5d8531fb34835bf"
                    }
                }
            ]
        }
    }
}
hits = es.search('audit_trading', 'data', query)['hits']['hits']

x = []
y = []
for hit in hits:
    _x = hit['timestamp__long']
    _y = hit['total_usd']
    x.append(_x)
    y.append(_y)

ds = pd.Series(index=pd.to_datetime(x, unit='ms'), data=y)



if __name__ == '__main__':
    pass







