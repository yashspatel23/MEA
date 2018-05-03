from arb.strat.strat1 import Strat1
from arb.utils import epoch
from arb import es, logger
from arb.utils.string import pretty_json
from arb.notebook import quick
import pandas as pd


def get_ds(strategy_run_id, check_window):
    window = tuple(epoch.to_long(x) for x in check_window)
    query = {
        "size": 1000,
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
                            "strategy_run_id.raw": strategy_run_id
                        }
                    },
                    {
                        "range": {
                            "timestamp__long": {
                                "gte": window[0],
                                "lte": window[1]
                            }
                        }
                    }
                ]
            }
        }
    }
    logger.info(pretty_json(query))
    hits = es.search('audit_trading', 'data', query)['hits']['hits']

    # Data vectors
    x = []
    y_total_usd = []
    y_gdax_usd = []
    y_cex_usd = []
    for hit in hits:
        hit = hit['_source']
        x.append(hit['timestamp__long'])
        y_total_usd.append(hit['total_usd__num'])
        y_gdax_usd.append(hit['gdax_account']['usd__num'])
        y_cex_usd.append(hit['cex_account']['usd__num'])

    # Data series
    x_index = pd.to_datetime(x, unit='ms')
    ds1 = pd.Series(index=x_index, data=y_total_usd)
    ds2 = pd.Series(index=x_index, data=y_gdax_usd)
    ds3 = pd.Series(index=x_index, data=y_cex_usd)

    return ds1, ds2, ds3


if __name__ == '__main__':
    check_window = ("2017-09-12 23:00:00 PDT", "2017-09-14 09:00:00 PDT")

    ds1, ds2, ds3 = get_ds('backtesting__001', check_window)
    # ds1, ds2, ds3 = get_ds('server_mock_live__001', check_window)

    print ds1.head()
    print ds2.head()
    print ds3.head()

    print ds1.index



