#!/usr/bin/env python

"""resistance to temperature

This module calculates temperature from measured resistance of Lake Shore
RX-202A (ruthenium oxide temperature sensor). Fitted curves (Chebychev series)
are provided by Lake Shore, available at http://goo.gl/RchRMO . All coefficients
can be found in 'RX202 curve.PDF' available from the aforementioned web page.

When executed directly, this module takes resistance(s) as arguments and prints
corresponding temperatures (scientific notation, four significant figures), one
per line.

Functions:

    r2t(resistance): resistance to temperature

Constants:

    MIN_RESISTANCE: minimum resistance in the accepted range

    MAX_RESISTANCE: maximum resistance in the accepted range

    TOLERANCE: tolerance of deviation from MIN_RESISTANCE and MAX_RESISTANCE

This module uses uncertainties (https://pypi.python.org/pypi/uncertainties/).
"""

from __future__ import print_function

from uncertainties import ufloat, umath, unumpy
import argparse
import math

################################## CONSTANTS ###################################

MIN_RESISTANCE = 2243.15 # resistance at 40 K
MAX_RESISTANCE = 69191.1 # resistance at 0.050 K
TOLERANCE = 10

# temperature range 0.050 K to 0.650 K
_A1 = [0.216272, -0.297572, 0.146302, -0.083696, 0.026669, -0.019932,
       0.003085, -0.004804, 0.000177, -0.001218, 0.000286]
_ZL1 = 3.67248634198
_ZU1 = 5.08000000000
_RANGE_LOWER_LIMIT1 = 5166.86

# temperature range 0.650 K to 5.0 K
_A2 = [2.129752, -2.281779, 0.981996, -0.386190, 0.143467, -0.050844,
       0.017569, -0.006164, 0.002311]
_ZL2 = 3.44161440913
_ZU2 = 3.74909980595
_RANGE_LOWER_LIMIT2 = 2843.53

# temperature range 5.0 K to 40 K
_A3 = [102.338126, -161.190611, 94.158738, -43.080048, 15.317949, -3.881270,
       0.540313]
_ZL3 = 3.27800000000
_ZU3 = 3.46671731726
_RANGE_LOWER_LIMIT3 = 2243.15

################################################################################

def _chebychev_series(z, zl, zu, a):
    x = ((z - zl) - (zu - z)) / (zu - zl)
    tc = []
    tc.append(ufloat(1,0))
    tc.append(x)
    t = a[0] + a[1] * x
    for i in range(2, len(a)):
        tc.append(2 * x * tc[i-1] - tc[i-2])
        t += a[i] * tc[i]
    return t

def r2t(resistance):
    """Calculate temperature from resistance. Resistance must be of type
    ufloat.

    The range of acceptable resistances is determined by constants
    MIN_RESISTANCE and MAX_RESISTANCE. To account for measurement errors, the
    actual accepted range is given by [MIN_RESISTANCE - TOLERANCE,
    MAX_RESISTANCE + TOLERANCE]. An AssertionError is raised when resistance is
    out of range.
    """

    assert MIN_RESISTANCE - TOLERANCE <= resistance <= \
        MAX_RESISTANCE + TOLERANCE, \
        "resistance %.3e is out of range" % resistance

    z = unumpy.log(resistance, 10)
    if resistance >= _RANGE_LOWER_LIMIT1:
        return _chebychev_series(z, _ZL1, _ZU1, _A1)
    elif resistance >= _RANGE_LOWER_LIMIT2:
        return _chebychev_series(z, _ZL2, _ZU2, _A2)
    else:
        return _chebychev_series(z, _ZL3, _ZU3, _A3)

##################################### MAIN #####################################

def main():
    """CLI interface."""
    description = 'Resistance to temperature (Lake Shore RX-202A).'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('resistances', type=float, nargs='+',
                        help='resistances in ohms; multiple values accepted')
    args = parser.parse_args()
    for resistance in args.resistances:
        print("{:.5g}".format(r2t(resistance)))

if __name__ == "__main__":
    main()
