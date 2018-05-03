import time
import pytz
import datetime


def current_milli_time():
    """
    Current time in millisecond (long)
    """
    return long(round(time.time() * 1000))


def current_time(strf_format='%Y-%m-%d %H:%M:%S %Z', timezone='US/Pacific'):
    """
    Formatted string
    """
    epoch_in_sec = int(time.time())
    timezone = pytz.timezone(timezone)  # see all timezones: pytz.all_timezones
    t = datetime.datetime.fromtimestamp(epoch_in_sec, timezone)
    return t.strftime(strf_format)


def to_str(epoch, strf_format='%Y-%m-%d %H:%M:%S %Z', timezone='US/Pacific'):
    """
    In formatted string
    """
    timezone = pytz.timezone(timezone)  # see all timezones: pytz.all_timezones
    t = datetime.datetime.fromtimestamp(epoch / 1000, timezone)
    return t.strftime(strf_format)


def to_long(s, strf_format='%Y-%m-%d %H:%M:%S %Z'):
    """
    In milliseconds

    Example: 2017-08-22 22:47:22 PDT
    """
    t = datetime.datetime.strptime(s, strf_format)
    return int(t.strftime('%s')) * 1000


if __name__ == '__main__':
    t = current_milli_time()
    s = to_str(t)
    t2 = to_long(s)




    pass
