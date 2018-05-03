#### order_book/data/abf29952cea24959b2174c40c56f9114
```
{
  "uid": "abf29952cea24959b2174c40c56f9114",
  "exchange": "gdax",
  "product": "eth-usd",
  "timestamp__long": 14923732408,
  
  "sequence__long": 9174131,
  
  "bids":[
    {
      "price__num": 315.49,
      "size__num": 216.47444926,
      "num_orders__int": 9
    },
    {
      ...
    }
  ],
  "asks":
  [
    {
      "price__num": 315.5,
      "size__num": 24.794,
      "num_orders__int": 9
    },
    {...}
  ]
}
```

#### trade_hist/data/abf29952cea24959b2174c40c56f9114
```
{
  "uid": "abf29952cea24959b2174c40c56f9114",
  "exchange": "gdax",
  "product": "ethusd",
  "timestamp__int": 123239834312,
  
  "time": '2017-08-12T02:18:50.236Z',
  
  "trade_id__int": 9174353,
  "price__num": '313.80000000',
  "size__num": '10.31323400',
  "side": 'sell'
}
```




#### audit_trading/data/2b2fe34600ce465fbf5b438f94e41928
```
{
  "id": "2b2fe34600ce465fbf5b438f94e41928",
  "timestamp__int": 1502513506,
  "to": "gdax",
  "from": "cex",
  "product": "btcusd",
  "action": "arbitrage",
  "avg_delta__num": 0.05,
  
  "account1_balance__map": {
    "usd": 123.20,
    "eth": 10.12311232,
    "btc": 2.35784354
  },
  
  "account2_balance__map": {
    "usd": 123.20,
    "eth": 10.12311232,
    "btc": 2.35784354
  }
}
```


#### tx/data/5cdf981ca55344fc84f390faa10dbafb
```
{
  "uid": "5cdf981ca55344fc84f390faa10dbafb",
  "timestamp__int": 1502513506,
  "account": "gdax",
  "action": "buy",
  "product": "btcusd",
  "size__num": 1.0242,
  "avg_price__num": 253.65,
  
  "updated_account__map": {
    "usd": 123.20,
    "eth": 10.12311232,
    "btc": 2.35784354
  }
}

```

####account/data/gdax
```
{
  "uid": "gdx",
  "exchange": "gdax",
  "country": "usa",
  "usd__num": 123.2,
  "eth__num": 10.12311232,
  "btc__num": 2.35784354
}
```
