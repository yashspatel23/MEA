import threading
import time
import traceback

import arb.core.exh.cex.public_client as cpc

import arb.core.exh.api.cex.auth_client as cac
import arb.core.exh.gdax.auth_client as gac
import arb.core.exh.gdax.public_client as gpc
from arb import es, sentry_client
from arb import logger
from arb.core.models import OrderBookModel
from arb.core.services.display import Print
from arb.core.services.notification import Notification

# 10 seconds delay
DELAY = 10.0


class Main:
    def __init__(self):
        self.gdax_public_client = gpc.PublicClient()
        self.gdax_auth_client = gac.AuthClient()
        self.cex_public_client = cpc.PublicClient()
        self.cex_auth_client = cac.AuthClient()
        self.Print = Print()
        self.notification = Notification()

    def get_order_book_data(self):
        try:
            gdax_order_book = self.gdax_public_client.get_product_order_book('ETH-USD', 2)
            gob_model = OrderBookModel.build(gdax_order_book)
            gob_model.db_save(es)

            cex_order_book = self.cex_public_client.get_product_order_book('ETH-USD')
            cob_model = OrderBookModel.build(cex_order_book)
            cob_model.db_save(es)

            logger.info("saved data: gdx:{0} | cex:{1}".format(gob_model.uid, cob_model.uid))
        except Exception:
            sentry_client.captureException()
            tb = traceback.format_exc()
            logger.error(tb)

    def get_order_book_data_repeated(self):
        threading.Timer(DELAY, self.get_order_book_data_repeated).start()
        self.get_order_book_data()

    # ACTUAL ARB PROGRAM
    def run(self):
        while True:
            # GET ALL THE PRODUCT TICKERS FROM ALL EXCHANGES
            ticks = self.get_ticks()

            # GET WALLET BALANCES FROM ALL EXCHANGES
            wallets = self.get_wallets()

            # CALCULATE DELTAS
            deltas = self.get_deltas(ticks)

            # PRINT BALANCE, TICKER, AND DELTA INFORMATION
            self.Print.info(ticks, wallets)
            self.Print.delta(deltas)

            # SEND ALERT EXAMPLES
            # self.notification.send_email('yash.spatel23@gmail.com', 'testing alerts', 'testing alerts')
            # self.notification.send_text('18582054350', 'testing!')


            # 5. Decide if any trade actions need to be taken
            # USE INITIAL TRADE LOGIC BY JIN???



            # Delay next iteration by 10 seconds
            time.sleep(10)


    def get_ticks(self):
        gdaxETHTick = self.gdax_public_client.get_product_ticker('ETH-USD')
        gdaxBTCTick = self.gdax_public_client.get_product_ticker('BTC-USD')
        cexETHTick = self.cex_public_client.get_product_ticker('ETH-USD')
        cexBTCTick = self.cex_public_client.get_product_ticker('BTC-USD')

        ticks = {
            "gdax": {
                "eth": {
                    "ask": float(gdaxETHTick['ask']),
                    "bid": float(gdaxETHTick['bid'])
                },
                "btc": {
                    "ask": float(gdaxBTCTick['ask']),
                    "bid": float(gdaxBTCTick['bid'])
                }
            },
            "cex": {
                "eth": {
                    "ask": cexETHTick['ask'],
                    "bid": cexETHTick['bid']
                },
                "btc": {
                    "ask": cexBTCTick['ask'],
                    "bid": cexBTCTick['bid']
                }
            }
        }

        # print json.dumps(ticks, indent=2)

        return ticks


    def get_wallets(self):
        gdax_wallet = self.gdax_auth_client.get_account()
        cex_wallet = self.cex_auth_client.get_account()

        wallet = {
            'gdax': {
                'usd': {
                    'available': None,
                    'balance': None
                },
                'eth': {
                    'available': None,
                    'balance': None
                },
                'btc': {
                    'available': None,
                    'balance': None
                }
            },
            'cex': {
                'usd': {
                    'available': float(cex_wallet["USD"]["available"]),
                    'balance': float(cex_wallet["USD"]["available"]) + float(cex_wallet["USD"]["orders"])
                },
                'eth': {
                    'available': float(cex_wallet["ETH"]["available"]),
                    'balance': float(cex_wallet["ETH"]["available"]) + float(cex_wallet["ETH"]["orders"])
                },
                'btc': {
                    'available': float(cex_wallet["BTC"]["available"]),
                    'balance': float(cex_wallet["BTC"]["available"]) + float(cex_wallet["BTC"]["orders"])
                }
            }
        }

        for data in gdax_wallet:
            if data["currency"] == "USD":
                wallet["gdax"]["usd"]["available"] = float(data["available"])
                wallet["gdax"]["usd"]["balance"] = float(data["balance"])
            elif data["currency"] == "ETH":
                wallet["gdax"]["eth"]["available"] = float(data["available"])
                wallet["gdax"]["eth"]["balance"] = float(data["balance"])
            elif data["currency"] == "BTC":
                wallet["gdax"]["btc"]["available"] = float(data["available"])
                wallet["gdax"]["btc"]["balance"] = float(data["balance"])

        # print json.dumps(wallet, indent=2)

        return wallet


    def get_deltas(self, ticks):
        deltas = {
            'gdaxToCex': {
                'eth': {
                    'usd': None,
                    'per': None
                },
                'btc': {
                    'usd': None,
                    'per': None
                }
            },
            'cexToGdax': {
                'eth': {
                    'usd': None,
                    'per': None
                },
                'btc': {
                    'usd': None,
                    'per': None
                }
            }
        }

        # GDAX -> CEX DELTA CALCULATIONS
        deltas['gdaxToCex']['eth']['usd'] = ticks['cex']['eth']['ask'] - ticks['gdax']['eth']['bid']
        deltas['gdaxToCex']['eth']['per'] = (deltas['gdaxToCex']['eth']['usd'] / ticks['gdax']['eth']['bid']) * 100
        deltas['gdaxToCex']['btc']['usd'] = ticks['cex']['btc']['ask'] - ticks['gdax']['btc']['bid']
        deltas['gdaxToCex']['btc']['per'] = (deltas['gdaxToCex']['btc']['usd'] / ticks['gdax']['btc']['bid']) * 100

        # CEX -> GDAX DELTA CALCULATIONS
        deltas['cexToGdax']['eth']['usd'] = ticks['gdax']['eth']['ask'] - ticks['cex']['eth']['bid']
        deltas['cexToGdax']['eth']['per'] = (deltas['cexToGdax']['eth']['usd'] / ticks['cex']['eth']['bid']) * 100
        deltas['cexToGdax']['btc']['usd'] = ticks['gdax']['btc']['ask'] - ticks['cex']['btc']['bid']
        deltas['cexToGdax']['btc']['per'] = (deltas['cexToGdax']['btc']['usd'] / ticks['cex']['btc']['bid']) * 100

        # print json.dumps(deltas,indent=2)

        return deltas


if __name__ == '__main__':
    Main().run()
