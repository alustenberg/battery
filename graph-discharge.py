#!/usr/bin/python3

from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

max_time = 210

fig = plt.figure()
# fig.set_axisblow(True)
ax = fig.add_subplot(1, 1, 1)
ax.set_title('discharge curve')

ax.set_xlim([0, max_time])
ax.set_xlabel('minutes')
ax.set_xticks(range(0, max_time, 30))

# ax2 = ax.twinx()

ax.set_ylim([35, 50])
ax.set_yticks(range(35, 55))
ax.set_ylabel('volts')

ax.grid(alpha=.3)

# ax2.set_ylim([0,400])
# ax2.set_yticks(range(0,400,100))
# ax2.set_ylabel('wh')


for f in sorted(glob('*.csv')):
    t = f.replace('.csv', '')
    a = pd.read_csv(f, dtype={'time (m)': np.float64}, engine='python', skipfooter=1)  # .drop(columns=['wh'])
    ax.plot(a['time (m)'], a['v'], label=t, linestyle='-')
    # ax2.plot(a['time (m)'],a['wh'],label=f, linestyle='--')

ax.legend()
fig.set_size_inches(12, 6)
plt.tight_layout()
# plt.show()
plt.savefig("discharge.png", dpi=150)
