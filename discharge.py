#!/usr/bin/python3 -u

from serial import Serial
from time import time
from sys import stderr


def discharge_loop(ser, load, discharge, discharge_rate):
    state = 0 # print state

    peak = 0
    start = None
    last = []
    lastprint = None
    lastv = None
    lastcount = 10
    tah = 0
    skip = 0
    skipcount = 30

    #      time    volts     ah
    fmt = "{:7.3f},{:6.2f},{:7.4f}"
    while True:
        l = ser.readline()
        if not len(l):
            print('timeout?',file=stderr)
            break

        # overload
        if chr(l[3]) == ':':
            if state != 1:
                print('overload?', file=stderr)
                state = 1
            continue

        f = [int("{:02x}".format(c),16) for c in l[5:]]
        # 4570 20 3211 0000 802d 0d0a
        if f[0] != 32:
            if state != 2:
                print('incorrect mode?',f[:6],file=stderr)
                state = 2
            continue

        # convert first 5 bytes into float for voltage
        v = int(l[:5].decode('ascii'))/100

        # quick and dirty range check.  confirms DVM is at least in the ballpark
        if v < 30 or v > 55:
            if state != 3:
                print('range?',file=stderr)
                state = 3
            continue

        # reset peak current, should be a one shot
        if v > peak:
            peak = v

        tick = time()

        if not start:
            # start the clock once we drop half a volt from peak
            if (peak - v) > .1:
                print('on load!',file=stderr)
                print('"time (m)",V,Ah')
                print(fmt.format(0,peak,0))
                lastprint = start = tick
                lastv = peak
            else:
                if state != 4:
                    print('off load?',file=stderr)
                    state = 4
            continue

        state = 0
        runtime = tick - start
        dvm = 0

        # quick and dirty noise filtering
        if v not in last or skip >= skipcount:
            skip = 0

            # calc time delta
            # dt in seconds
            dt = tick - lastprint

            lastprint = tick


            if lastv is not None:
                dv = v - lastv
                dvm = -1 * 60 * dv/dt
            lastv = v

            # calc a/hour used over time delta
            a = v/load # this is current 'lower' voltage, err conservative
            ah = a * dt/3600
            tah = tah + ah
            # given time, v
            # ah =C2+B3/16.1*(A3-A2)/60
            print(fmt.format(runtime/60,v,tah))
        else:
            skip = skip + 1

        last.insert(0,v)
        last = last[:lastcount]

        if start and v < discharge:
            print('discharge reached: {:.0f} mAh consumed'.format(tah))
            break

        if runtime > 10 and discharge_rate is not None and dvm > discharge_rate:
            print('discharge rate reached: {:.0f} mAh consumed'.format(tah))
            break

if __name__ == '__main__':
    import argparse
    argp = argparse.ArgumentParser( description = 'battery discharge montoring' )
    argp.add_argument( '--load'      , dest='load'      , nargs='?' , type=float , default=8.2 , help="Load resistance")
    argp.add_argument( '--volt'      , dest='discharge' , nargs='?' , type=float , default=35.0 , help="Discharge end voltage")
    argp.add_argument( '--rate'      , dest='rate'      , nargs='?' , type=float , default=None  , help="Discharge dv/min limit")

    argp.add_argument( '--serial', dest='serial', nargs='?', type=str, default='/dev/ttyUSB0', help="Serial Device")

    args = argp.parse_args()

    with Serial(args.serial,2400,timeout=2) as ser:
        discharge_loop(ser, args.load, args.discharge, args.rate)
