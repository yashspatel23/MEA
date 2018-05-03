import threading
import traceback

from arb import logger, SENTRY_URL, sentry_client
from arb.utils import epoch
import os

def stupid():
    def log_repeat():
        threading.Timer(3, log_repeat).start()
        logger.info('logging: ' + epoch.current_time())

    log_repeat()


if __name__ == '__main__':

    from raven import Client

    # client = Client(SENTRY_URL)

    try:
        raise
    except Exception:
        sentry_client.captureException()



