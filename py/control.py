#!/usr/bin/env python

"""GPIB instrument controller.

Functions:
ps_monitor_current: monitor and save power supply output current
li_monitor: monitor and save lock-in amplifier data points
"""

from __future__ import division
from __future__ import print_function

import argparse
import sys
import time

import gpib

def ps_monitor_current(power_supply, output=sys.stdout, print_to_console=True):
    """Monitor and save power supply output current until keyboard interrupt.

    Data points (timestamp and current) are saved to power_supply.data, and
    dumped to the output file when keyboard interrupt is encountered. Current
    can also be printed to stderr in real time is print_to_console is set to
    True.

    Adjacent recordings will be seperated by at least
    power_supply.sampling_interval (0.125 seconds by default). See
    gpib.PowerSupply.record_current for details.

    Arguments:
    power_supply: gpib.PowerSupply instance
    output: file object for writing output; defaults to sys.stdout
    print_to_console: if True, print to stderr in addtion to saving; defaults to
                      True

    """
    while True:
        try:
            current = power_supply.record_current(wait=True)
            if print_to_console and current is not None:
                sys.stderr.write("\rcurrent: %7.4f" % current)
                sys.stderr.flush()
        except KeyboardInterrupt:
            sys.stderr.write("\ninterrupted\n")
            for data_point in power_supply.data:
                output.write("%.4f,%.4f\n" %
                             (data_point['timestamp'], data_point['current']))
            break

def li_monitor(lock_in, sampling_rate, output=sys.stdout):
    """Monitor and save lock-in amplifier data points until keyboard interrupt.

    Use the lock-in's internal buffer. The buffer is refreshed after every 8000
    data points. Data points are saved internally to the lock_in object, and
    dumped to the output file when keyboard interrupt is encountered.

    Arguments:
    lock_in: gpib.LockIn instance; must be initialized with the
             gpib.LockIn.initialize method
    sampling_rate: sampling rate of the lock-in amplifier; should match the
                   sampling rate passed to gpib.LockIn.initialize
    output: file object for writing output; defaults to sys.stdout
    """
    while True:
        try:
            lock_in.start_storage()
            time.sleep(8000 / sampling_rate)
            lock_in.retrieve_storage()
        except KeyboardInterrupt:
            sys.stderr.write("\ninterrupted\n")
            data = lock_in.data()
            for data_point in data:
                output.write("%.4f,%.4f\n" %
                             (data_point['timestamp'], data_point['value']))
            break

def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(description="GPIB intrument controller.")
    parser.add_argument('action',
                        choices=['monitor-power-supply', 'monitor-lock-in'],
                        help="action to perform")
    parser.add_argument('file', nargs='?',
                        help="output file; if not given, write to stdout")
    args = parser.parse_args()
    if args.action == 'monitor-power-supply':
        power_supply = gpib.PowerSupply()
        if args.file is None:
            ps_monitor_current(power_supply)
        else:
            try:
                with open(args.file, 'w') as output:
                    ps_monitor_current(power_supply, output)
            except (IOError, OSError) as err:
                sys.stderr.write(type(err).__name__ + ": " + str(err) + "\n")
                sys.stderr.write("error: invalid output file\n")
    elif args.action == 'monitor-lock-in':
        lock_in = gpib.LockIn()
        lock_in.initialize()
        if args.file is None:
            li_monitor(lock_in, 8.0)
        else:
            try:
                with open(args.file, 'w') as output:
                    li_monitor(lock_in, 8.0, output)
            except (IOError, OSError) as err:
                sys.stderr.write(type(err).__name__ + ": " + str(err) + "\n")
                sys.stderr.write("error: invalid output file\n")
    else:
        # placeholder for other possible actions
        pass

if __name__ == "__main__":
    main()
