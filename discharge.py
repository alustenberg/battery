#!/usr/bin/env -S python3 -u

from enum import Enum
from serial import Serial
from sys import stderr
from time import time

import decimal

def discharge_loop(ser, load, discharge):
    # last whatever
    acc = []

    # edge cases
    minv = 25
    maxv = 50

    # window vars
    avg_seconds = 15
    start = int(time())
    next_tick = avg_seconds

    # sums
    total_mah = 0

    #      time    volts     ah
    print('time,V,Ah')
    while True:
        l = ser.readline()
        if not len(l):
            raise RuntimeError('timeout?')

        # overload
        if chr(l[3]) == ':':
            raise RuntimeError('out of range?')

        f = [int("{:02x}".format(c),16) for c in l[5:]]
        # 4570 20 3211 0000 802d 0d0a
        if f[0] != 32:
            raise RuntimeError('DVM mode?')

        # convert first 5 bytes into float for voltage
        v = int(l[:5].decode('ascii'))/100

        # quick and dirty range check.  confirms DVM is at least in the ballpark
        if v < minv:
            if len(acc) > 0:
                break
            # dont fault for low volt on start
            continue

        ###
        # end bail out
        ### 

        tick = time() - start
        if tick > next_tick:
            if len(acc):
                tick_v = sum(acc) / len(acc)
                tick_ma = tick_v / load * 1000
                tick_mah = tick_ma * (avg_seconds / 3600)
                total_mah = total_mah + tick_mah
                print(f'{next_tick/60:.2f},{tick_v:.2f},{total_mah/1000:.3f}')

            next_tick = next_tick + avg_seconds
            acc = []

# 1.249 amp vs 38.92v confirmed on fluke, 31.16?
# 1.01 amp on meter? -> 38.53 ohm

# iterating reads on the DVM is about 600 ms
# discharge to a 32 ohm load is order of 15 hours

        acc.append(v)
    print('discharge reached: {:.3f} mAh consumed'.format(total_mah/1000))

if __name__ == '__main__':
    import argparse
    argp = argparse.ArgumentParser( description = 'battery discharge montoring' )
    argp.add_argument( '--load'      , dest='load'      , nargs='?' , type=float , default=8.2 , help="Load resistance")
    argp.add_argument( '--volt'      , dest='discharge' , nargs='?' , type=float , default=20.0 , help="Discharge end voltage")

    argp.add_argument( '--serial', dest='serial', nargs='?', type=str, default='/dev/ttyUSB0', help="Serial Device")

    args = argp.parse_args()

    with Serial(args.serial,2400,timeout=1) as ser:
        discharge_loop(ser, args.load, args.discharge)
