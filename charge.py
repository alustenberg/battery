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

def charge_loop(ser, end_v, dv_dt, min_a, max_a, ah ):
    tmah = 0
    tick_time = 15
    max_voltage = 0

    cmd_volt(ser,end_v)  # set max voltage to termination voltage
    cmd_curr(ser,max_a)  # set charge voltage
    cmd(ser,'SOUT0') # enable output

    start = tick = datetime.now()
    print('"time (m)","v","A","mAh"')

    while True:
        (charge_v,charge_a,charge_cc) = cmd_getd(ser)
        if charge_v > max_voltage:
            max_voltage = charge_v

        if charge_v <= ( max_voltage - dv_dt ):
            print('-dv/dt')
            break

        run = tick - start
        print('{:5.2f},{:3.2f},{:3.2f},{:5.0f}'.format(run.total_seconds()/60, charge_v, charge_a, tmah))

        tick = tick + timedelta(seconds=tick_time)
        # amp * ( 1000 mah / 60 min ) ( tick * 1/60 sec/min )
        tmah = tmah + charge_a * ( 1000.0 / 60 ) * ( tick_time / 60 )

        if min_a is not None and charge_a <= min_a:
            print('min amperage')
            break

        if ah is not None and tmah >= (1000*ah):
            print('max ah')
            break

        sleep((tick-datetime.now()).total_seconds())

    print('charge complete, {:6.0f} mAh charged'.format(tmah))


