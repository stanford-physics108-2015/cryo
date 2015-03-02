#!/usr/bin/env python

"""GPIB instrument controller.

Functions:
ps_monitor_current: monitor and save current
"""

from __future__ import print_function

import argparse
import sys

import gpib

def ps_monitor_current(power_supply, output=sys.stdout, print_to_console=True):
    """Monitor and save current until keyboard interrupt.

    Data points (timestamp and current) are saved to power_supply.data, and
    dumped to the output file when keyboard interrupt is encountered. Current
    can also be printed to stderr in real time is print_to_console is set to
    True.

    Adjacent recordings will be seperated by at least
    power_supply.sampling_interval. See gpib.PowerSupply.record_current
    for details.

    Arguments:
    power_supply: gpib.PowerSupply instance
    output: file object for writing output
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
        ps = gpib.PowerSupply()
        if args.file is None:
            ps_monitor_current(ps)
        else:
            try:
                with open(args.file, 'w') as output:
                    ps_monitor_current(ps, output)
            except (IOError, OSError) as err:
                sys.stderr.write(type(err).__name__ + ": " + str(err) + "\n")
                sys.stderr.write("error: invalid output file\n")
    elif args.action == 'monitor-lock-in':
        pass #!

if __name__ == "__main__":
    main()
