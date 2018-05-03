import time
import uuid
import pytz
import datetime


def current_milli_time():
    """
    Current time in millisecond (long)
    """
    return long(round(time.time() * 1000))


def current_time_in_milli():
    """
    Current time in millisecond (long)
    """
    return long(round(time.time() * 1000))


def current_time_in_second():
    """
    Current time in millisecond (long)
    """
    return int(round(time.time()))


def random_str(size=7):
    """
    generate some random string
    """
    return uuid.uuid4().hex[0:size]


def pretty_time(epoch, strf_format='%Y-%m-%d %H:%M:%S %Z', timezone='US/Pacific'):
    """
    In milliseconds
    """
    timezone = pytz.timezone(timezone)  # see all timezones: pytz.all_timezones
    t = datetime.datetime.fromtimestamp(epoch / 1000, timezone)
    return t.strftime(strf_format)


def current_time(strf_format='%Y-%m-%d %H:%M:%S %Z', timezone='US/Pacific'):
    epoch_in_sec = int(time.time())
    timezone = pytz.timezone(timezone)  # see all timezones: pytz.all_timezones
    t = datetime.datetime.fromtimestamp(epoch_in_sec, timezone)
    return t.strftime(strf_format)


