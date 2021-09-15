#!/usr/bin/python3

max_time = 300

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from glob import glob


fig = plt.figure()
#fig.set_axisblow(True)
ax = fig.add_subplot(1,1,1)
ax.set_title('charge curve')


ax.set_xlim([0,max_time])
ax.set_xlabel('minutes')
ax.set_xticks(range(0,max_time,30))

ax2 = ax.twinx()

ax.set_ylim([0,15])
ax.set_yticks(range(0,15))
ax.set_ylabel('volts')

ax.grid(alpha=.3)

ax2.set_ylim([0,2])
ax2.set_yticks([x/10 for x in range(0,20)])
ax2.set_ylabel('A')


for f in sorted(glob('*.csv')):
    t = f.replace('.csv','')
    a = pd.read_csv(f, dtype = { 'time (m)': np.float64 }, engine='python',skipfooter=1) #.drop(columns=['wh'])
    ax.plot(a['time (m)'],a['v'],'C0',label='Time')
    ax2.plot(a['time (m)'],a['A'],'C1',label='Amp')


ax.legend()
fig.set_size_inches(12,6)
plt.viridis()
plt.tight_layout()
plt.show()
#plt.savefig("discharge.png",dpi=150)
