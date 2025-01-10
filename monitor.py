#!/usr/bin/env -S python3 -u

from serial import Serial


def event_loop(ser):
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

        if v > 0.5:
            print(f'{v:.2f}')

if __name__ == '__main__':
    with Serial('/dev/ttyUSB0',2400,timeout=1) as ser:
        event_loop(ser)
