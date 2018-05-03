import time
import traceback

from arb import logger, GDAX_API_URL, GDAX_API_SECRET, GDAX_API_PASSPHRASE, CEX_API_URL, \
    CEX_API_KEY, CEX_API_SECRET, CEX_API_USER_ID, GDAX_API_KEY, sentry_client, es
from arb.core.exh.clients import GdaxClient, CexClient
from arb.core.models import OrderBookModel
from arb.utils import epoch

delay = 10
gdax_client = GdaxClient(GDAX_API_URL, GDAX_API_KEY, GDAX_API_SECRET, GDAX_API_PASSPHRASE)
cex_client = CexClient(CEX_API_URL, CEX_API_USER_ID, CEX_API_KEY, CEX_API_SECRET)


def collect_order_book():
    gdax_order_book = gdax_client.get_order_book(ticker='eth', level=2)
    gob_model = OrderBookModel.build(gdax_order_book)
    gob_model.db_save(es)

    cex_order_book = cex_client.get_order_book(ticker='eth', level=2)
    cob_model = OrderBookModel.build(cex_order_book)
    cob_model.db_save(es)

    timestamp = gob_model.js['timestamp__long']
    logger.info("saved data: {0}, {1}".format(str(timestamp), epoch.to_str(timestamp)))


def run():
    while True:
        try:
            collect_order_book()
        except Exception as e:
            sentry_client.captureException()
            tb = traceback.format_exc()
            logger.error(tb)

        time.sleep(delay)


if __name__ == '__main__':
    logger.info('-' * 50)
    logger.info("Starting background data collections...")
    logger.info('-' * 50)
    run()
