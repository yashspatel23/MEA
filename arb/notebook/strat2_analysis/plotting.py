import matplotlib
import pandas as pd
import pytz
import matplotlib.pyplot as plt

matplotlib.style.use('ggplot')


# -------------------
# Charts
# -------------------
fig = plt.figure(figsize=(17,7)) # canvas size in inches
ax = fig.add_subplot(111)
aes = {
    "edgecolor": "#ffffff",
    "color": "#008AB8",
    "align": "center" # edge, center
}
#plt.xticks(range(len(x)), x)
strf_format='%b-%d %I:%M%p'
# strf_format='%d %H %Z'
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(strf_format, tz=pytz.timezone('US/Pacific')))
plt.plot()
plt.scatter(diff_ds, color=color_teal)
# plt.plot(diff_ds)s

print delta_ds.head()
print diff_ds.head()
