import time
import pytz
import datetime

from arb.utils.epoch import current_milli_time, to_str, to_long

if __name__ == '__main__':
    t = current_milli_time()
    s = to_str(t)
    t2 = to_long(s)

    print t
    print s
    print t2

    time1 = '2017-08-28 09:00:00 PDT'
    time2 = '2017-08-29 09:00:00 PDT'

    print to_long(time1)
    print to_long(time2)

    pass
