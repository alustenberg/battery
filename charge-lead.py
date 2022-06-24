#!/usr/bin/python3 -u

import argparse
from charge import *

if __name__ == '__main__':
    argp = argparse.ArgumentParser( description = 'battery charging' )
    argp.add_argument( '--volt', dest='volt', nargs='?', type=float, default=14.2, help="Charge voltage")
    argp.add_argument( '--amp' , dest='amp' , nargs='?', type=float, default=5.0,  help="max amperage")
    argp.add_argument( '--dv'  , dest='dv'  , nargs='?', type=float, default=0.05, help="voltage drop cutoff")
    argp.add_argument( '--min' , dest='min' , nargs='?', type=float, default=None, help="shutoff amperage")
    argp.add_argument( '--ah'  , dest='ah'  , nargs='?', type=float, default=None, help="max charge Ah")

    argp.add_argument( '--serial', dest='serial', nargs='?', type=str, default='/dev/ttyUSB0', help="Serial Device")

    args = argp.parse_args()

    with Serial(args.serial,9600,timeout=2) as ser:
        try:
            charge_loop(ser, args.volt, args.dv, args.min, args.amp, args.ah)
        except:
            raise
        finally:
            cmd(ser,'SOUT1') # disable output

