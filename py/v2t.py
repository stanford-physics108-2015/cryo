#!/usr/bin/env python
"""Compute temperature from measured voltage across the thermometer.

The thermometer is arranged in series with a large resistor R_LARGE, driven by
the internal oscillator of the lock-in amplifier, which outputs an AC signal
with amplitude V_EMS. The lock-in (i.e., the PSD) measures the EMS voltage
v_therm across the thermometer. Then the thermometer resistance r_therm is given
by

                  v_therm
    r_therm = --------------- R_LARGE
              V_EMS - v_therm

The computed thermometer resistance r_therm is then normalized by scaling to
mimic the behavior of a standard thermometer.

In the end, the normalized resistance is fed into r2t to get the measured
temperature.
"""

from __future__ import division
from __future__ import print_function

import argparse

from r2t import r2t

V_EMS = 1E-2
R_LARGE = 1.5E6

# Resistance scaling factor to mimic a standard LakeShore RX-202A (with a
# standard curve). The standard resistance at LHe temperature (4.2K) is 2929
# ohms, while our particular thermometer has 2896 ohms at the same temperature.
# Assuming this is due entirely to geometrical defect, then the scaling factor
# should be 2929/2896
SCALING_FACTOR = 2929/2896

def v2r(v_therm):
    """Compute the resistance of the thermometer from the voltage across it.

                  v_therm
    r_therm = --------------- R_LARGE
              V_EMS - v_therm

    Arguments:
    v_therm: EMS voltage (in *volts*) across the thermometer measured by
             the lock-in amplifier
    """
    r_therm = v_therm / (V_EMS - v_therm) * R_LARGE
    return r_therm

def v2t(v_therm):
    """Compute temperature from the measured voltage across the thermometer.

    Arguments:

    v_therm: EMS voltage (in *volts*) across the thermometer measured by the
             lock-in amplifier
    """
    r_therm = v2r(v_therm)
    r_therm_std = r_therm * SCALING_FACTOR
    return r2t(r_therm_std)

def main():
    """CLI interface."""
    description = 'Compute temperature from voltage across the thermometer.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('voltages', type=float, nargs='+',
                        help='voltages in volts; multiple values accepted')
    args = parser.parse_args()
    for voltage in args.voltages:
        print("%.3f" % v2t(voltage))

if __name__ == "__main__":
    main()
