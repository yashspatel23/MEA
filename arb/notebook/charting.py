import json
import time
import traceback

import matplotlib
import pytz
import datetime

from arb.notebook import mkds_audits
from arb.utils import epoch
from arb import es, logger
from arb.utils.string import pretty_json


MILLIS_IN_MINUTE = 1000 * 60
MILLIS_IN_HOUR = 1000 * 60 * 60

import pandas as pd
import pytz
import matplotlib.dates as dates
import matplotlib.pyplot as plt

check_window = ("2017-09-12 23:00:00 PDT", "2017-09-15 09:00:00 PDT")

ds1, ds2, ds3 = mkds_audits.get_ds('server_mock_live__001', check_window)

# -------------------
fig = plt.figure(figsize=(17,7)) # canvas size in inches
ax = fig.add_subplot(111)
ax.set_ylim(19500, 22000)
aes = {
    "edgecolor": "#ffffff",
    "color": "#008AB8",
    "align": "center" # edge, center
}
#plt.xticks(range(len(x)), x)
strf_format='%d %H %Z'
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(strf_format, tz=pytz.timezone('US/Pacific')))
ds1.plot(kind='bar')

# Chart2
fig2 = plt.figure(figsize=(17,7)) # in inches
ax2 = fig2.add_subplot(111)
ax2.xaxis.set_major_formatter(dates.DateFormatter(strf_format, tz=pytz.timezone('US/Pacific')))


# ylim(ymax=3) # adjust the max leaving min unchanged
# ylim(ymin=1)

# ax2.set_title("Distribution By Prices", fontsize=20)
# ax2.set_xlabel('Prices', fontsize=16)
# ax2.set_ylabel('Counts', fontsize=16)
aes = {
    "edgecolor": "#ffffff",
    "color": "#008AB8"
}
# histogram
# ax.hist(x, bins=bins, alpha=0.8, **aes)
ax3 = ds2.plot(kind='bar', ax=ax2, **aes)
#ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(strf_format, tz=pytz.timezone('US/Pacific')))
# ds2.plot(kind='line')
# ds3.plot(kind='bar')

fig3 = plt.figure(figsize=(17,7)) # in inches
ax3 = fig3.add_subplot(111)
ax3.plot_date(ds3.index.to_pydatetime(), ds3, 'v-')






