#!/usr/bin/python3

from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import floor, ceil

plot_ah = True
max_ah = 20 
max_time = 60*4

fig = plt.figure()
# fig.set_axisblow(True)
ax = fig.add_subplot(1, 1, 1)
ax.set_title('8 ohm discharge curve')

if plot_ah:
    ax.set_xlim([0, max_ah])
    ax.set_xlabel('Ah')
    ax.set_xticks(range(0, max_ah, 5))
else:
    ax.set_xlim([0, max_time])
    ax.set_xlabel('Minute')
    ax.set_xticks(range(0, max_time, 30))

ax2 = ax.twinx()

y_lo=34
y_hi=44

ax.set_ylim([y_lo, y_hi])
ax.set_yticks(range(y_lo, y_hi))
ax.set_ylabel('V')

ax.grid(alpha=.3)

ax2.set_ylim([y_lo/12,y_hi/12])
# ax2.set_yticks(range(floor(35/12), ceil(40/12),.1))
ax2.set_ylabel('V Cell')


for f in sorted(glob('*.csv')):
    t = f.replace('.csv', '')
    a = pd.read_csv(f, dtype={'time (m)': np.float64}, engine='python', skipfooter=1)  # .drop(columns=['wh'])
    if plot_ah:
        ax.plot(a['Ah'], a['V'], label=t, linestyle='-')
    else:
        ax.plot(a['time (m)'], a['V'], label=t, linestyle='-')
    # ax2.plot(a['time (m)'],a['wh'],label=f, linestyle='--')

ax.legend()
fig.set_size_inches(12, 6)
plt.tight_layout()
# plt.show()
plt.savefig("discharge.png", dpi=150)
