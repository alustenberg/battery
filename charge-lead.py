#!/usr/bin/python3 -u

from serial import Serial
from time import time, sleep
from datetime import datetime, timedelta
from sys import stderr
from math import ceil
import click


def cmd(ser,cmd, want_ok = True):
    if isinstance(cmd,str):
        ser.write(cmd.encode())
    else:
        ser.write(cmd)
    ser.write(b"\r");
    if want_ok:
        return ser.readline() == 'OK'
    else:
        return ser.readline().decode('ascii')


def cmd_getd(ser):
    ret = cmd(ser,'GETD',False)
    s = ret.split('\r')[0]
    v = int(s[0:4])/100.0
    a = int(s[4:8])/100.0
    cc = s[8] == '1'

    return (v,a,cc)

def cmd_volt(ser, v):
    cmd(ser,'VOLT{:03.0f}'.format(v * 10))

def cmd_curr(ser, a):
    cmd(ser,'CURR{:03.0f}'.format(a * 100))

def start_state(ser, end_v, settle_time=60):
    cmd_curr(ser,0)
    cmd_volt(ser,end_v)
    cmd(ser,'SOUT0') # enable output
    sleep(settle_time)
    return cmd_getd(ser)[0] # vol

def charge_loop(ser, start_v, end_v, min_a, max_a, tick_time = 60 ):
    tmah = 0

    set_v = round(start_v,1)
    cmd_volt(ser,start_v)  # set starting voltage
    cmd_curr(ser,max_a)  # set charge current
    cmd(ser,'SOUT0') # enable output

    start = tick = datetime.now()
    print('"time (m)","v","A","mAh"')

    while set_v <= end_v:
        run = tick - start
        (charge_v,charge_a,charge_cc) = cmd_getd(ser)
        print('{:5.2f},{:3.1f},{:3.2f},{:5.0f}'.format(
            run.
            total_seconds()/60,
            set_v,
            charge_a,
            tmah,
        ))

        if charge_a < min_a:
            set_v = round(set_v + 1.0, 1)
            cmd_volt(ser,set_v)

        tick = tick + timedelta(seconds=tick_time)
        # amp * ( 1000 mah / 60 min ) ( tick * 1/60 sec/min )
        tmah = tmah + charge_a * ( 1000.0 / 60 ) * ( tick_time / 60 )

        wait_sec = (tick-datetime.now()).total_seconds()
        # print('wait {:2.1f}'.format(wait_sec))
        sleep(wait_sec)

    print('charge complete, {:6.0f}mAh charged'.format(tmah))
    cmd_volt(ser,end_v)  # set max voltage to termination voltage
    cmd_curr(ser,0)  # end charge


if __name__ == '__main__':
    import argparse
    argp = argparse.ArgumentParser( description = 'battery charging' )
    argp.add_argument( '--volt', dest='volt', nargs='?', type=float, default=14.2, help="Charge voltage")
    argp.add_argument( '--amp' , dest='amp' , nargs='?', type=float, default=4.0,  help="max amperage")
    argp.add_argument( '--min' , dest='min' , nargs='?', type=float, default=1.0 , help="min amperage/step up amp")

    argp.add_argument( '--serial', dest='serial', nargs='?', type=str, default='/dev/ttyUSB0', help="Serial Device")

    args = argp.parse_args()

    with Serial(args.serial,9600,timeout=2) as ser:
        try:
            v = start_state(ser, args.volt)
            print('{:5.2f}v starting voltage'.format(v))
            charge_loop(ser, v + 0.3, args.volt, args.min, args.amp)
        except:
            raise
        finally:
            cmd(ser,'SOUT1') # disable output

