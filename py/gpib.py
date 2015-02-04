# This module provides methods for working with the GPIB and controlling the oscilloscope. More instruments can be added as we need them.

import numpy as np
import visa as vs
import time

visa_path = '/cygdrive/c/Windows/System32/visa32.dll'

def init_gpib():
    return vs.ResourceManager(visa_path)

def init_osc(inst):
    inst.write('*RST')
    inst.write(':AUToscale')
    # add other init setups as needed (ie probe settings)
    return

def get_waveform_osc(inst, channel):
    inst.write(':WAVeform:SOURce CHANnel%d'%(channel))
    inst.write(':DIGitize CHANnel%d'%(channel))
    return

def measure_osc(inst, command):
    inst.write(command)
    query = command + '?'
    value = inst.ask(query)
    return value

def monitor_osc(inst, command, deltaT, max_measurements):
    measurement_counter = 0
    measurements = []
    init_osc(inst)
    while measurement_counter < max_measurements:
        get_waveform_osc(inst)
        measurements.append(measure_osc(inst, command))
        time.sleep(deltaT)
        measurement_counter = measurement_counter + 1
    return np.array(measurements)


