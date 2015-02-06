# This module provides methods for working with the GPIB and controlling the oscilloscope. More instruments can be added as we need them.

import numpy as np
import visa as vs
import time

visa_path = '/cygdrive/c/Windows/System32/visa32.dll'

# This method creates a resource manager, and opens the oscilloscope.
def init_gpib():
    rm = vs.ResourceManager(visa_path)
    osc = rm.get_instrument('GPIB0::7::INSTR')
    return osc

# This method resets the oscilloscope and initializes any settings.
def init_osc(inst):
    inst.write('*RST')
    inst.write(':AUToscale')
    # add other init setups as needed (ie probe settings)
    return

# This method stops data collection on the oscilloscope and 
# stores the current waveform in memory. Measurements all come from this waveform.
def get_waveform_osc(inst, channel):
    inst.write(':WAVeform:SOURce CHANnel%d'%(channel))
    inst.write(':DIGitize CHANnel%d'%(channel))
    return

# This method measures the quantity specified by the command field.
def measure_osc(inst, command):
    inst.write(command)
    query = command + '?'
    value = inst.ask(query)
    return value

# This method makes many measurements with a specified delta T 
# between each measurement. Monitoring stops after a user specified
# number of measurements.
def monitor_osc(inst, command, deltaT, max_measurements):
    measurement_counter = 0
    measurements = []
    init_osc(inst)
    while measurement_counter < max_measurements:
        measurements.append(measure_osc(inst, command))
        time.sleep(deltaT)
        measurement_counter = measurement_counter + 1
    return np.array(measurements)


