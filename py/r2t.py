#!/usr/bin/env python

# Calculate temperature from measured resistance of Lake Shore RX-202A
# (ruthenium oxide temperature sensor). Fitted curves (Chebychev series) are
# provided by Lake Shore, available at http://goo.gl/RchRMO . All coefficients
# can be found in 'RX202 curve.PDF' available from the aforementioned web page.

from __future__ import print_function

import argparse
from math import log

################################## CONSTANTS ###################################

MIN_RESISTANCE = 2243.15 # resistance at 40 K
MAX_RESISTANCE = 69191.1 # resistance at 0.050 K

# temperature range 0.050 K to 0.650 K
A1 = [0.216272, -0.297572, 0.146302, -0.083696, 0.026669, -0.019932,
      0.003085, -0.004804, 0.000177, -0.001218, 0.000286]
ZL1 = 3.67248634198
ZU1 = 5.08000000000
RANGE_LOWER_LIMIT1 = 5166.86

# temperature range 0.650 K to 5.0 K
A2 = [2.129752, -2.281779, 0.981996, -0.386190, 0.143467, -0.050844,
      0.017569, -0.006164, 0.002311]
ZL2 = 3.44161440913
ZU2 = 3.74909980595
RANGE_LOWER_LIMIT2 = 2843.53

# temperature range 5.0 K to 40 K
A3 = [102.338126, -161.190611, 94.158738, -43.080048, 15.317949, -3.881270,
      0.540313]
ZL3 = 3.27800000000
ZU3 = 3.46671731726
RANGE_LOWER_LIMIT3 = 2243.15

################################################################################

def chebychev_series(z, zl, zu, a):
    x = ((z - zl) - (zu - z)) / (zu - zl)
    tc = []
    tc.append(1)
    tc.append(x)
    t = a[0] + a[1] * x
    for i in range(2, len(a)):
        tc.append(2 * x * tc[i-1] - tc[i-2])
        t += a[i] * tc[i]
    return t

def r2t(resistance):
    assert MIN_RESISTANCE - 10 <= resistance <= MAX_RESISTANCE + 10, \
        "resistance out of range"

    z = log(resistance, 10)
    if resistance >= RANGE_LOWER_LIMIT1:
        return chebychev_series(z, ZL1, ZU1, A1)
    elif resistance >= RANGE_LOWER_LIMIT2:
        return chebychev_series(z, ZL2, ZU2, A2)
    else:
        return chebychev_series(z, ZL3, ZU3, A3)

##################################### MAIN #####################################

if __name__ == "__main__":
    description = 'Resistance to temperature (Lake Shore RX-202A).'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('resistances', type=float, nargs='+',
                        help='resistances in Ohms; multiple ones allowed')
    args = parser.parse_args()
    for resistance in args.resistances:
        print("%.3e" % r2t(resistance))
