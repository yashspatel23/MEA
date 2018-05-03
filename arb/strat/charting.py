import datetime

from arb.notebook import quick
from arb.utils import epoch


def to_datetime_index(x):
    return pd.to_datetime(x, unit='ms')


def get_x_and_y(amount, starting_time, interval, increments, search_window):
    """

    :param amount:
    :param starting_time:
    :param interval: pytz.timedelta, example: pytz.HOUR
    :param increments:
    :param search_window:
    :return:
    """
    dt = interval.total_seconds() * 1000.0
    x = []
    y = []
    for i in range(increments):
        t = starting_time + dt * i
        ts = epoch.to_str(t)
        diff = quick.delta_buy_gdax_sell_cex(starting_amount, t, search_window)
        x.append(t)
        y.append(diff)

    return x, y



import pandas as pd

if __name__ == '__main__':
    # earliest time
    "2017-08-20 16:27:09 PDT"
    1503271629989

    search_window = 11000 # 11 seconds
    starting_amount = 1000
    starting_time = 1503271629989
    interval = datetime.timedelta(hours=1)
    interval2 = datetime.timedelta(minutes=15)
    increments = 5

    print interval.total_seconds()
    x, y = get_x_and_y(starting_amount, starting_time, interval, increments, search_window)


    print x
    print y

    ds = pd.Series(index=to_datetime_index(x), data=y)
    print ds
    #pd.to_datetime([1490195805.433, 1490195805.433502912], unit='s')







