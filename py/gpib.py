#!/usr/bin/env python

"""Control interface for GPIB instruments."""

from __future__ import division
from __future__ import print_function

import time
import warnings

import visa

_VISA_PATH = '/cygdrive/c/Windows/System32/visa32.dll'
_instrument_manager = visa.ResourceManager(_VISA_PATH)

class _GPIBInstrument(object):
    """Generic GPIB instrument interface.

    Attributes:
    instrument: pyvisa.resources.GPIBInstrument object returned by
                pyvisa.ResourceManager.get_resource
    """

    def __init__(self, instrument_id):
        """Get instrument by instrument_id from pyvisa ResourceManage."""
        self.instrument = _instrument_manager.get_instrument(instrument_id)

    def ask(self, command, convert=None,
            tries=3, wait=0.5, exponential_backoff=True):
        """Ask, and raise an exception only after a certain number of tries.

        Arguments:
        command: command to ask, unicode (python2) or str (python3)
        convert: convert function for the return value, e.g., int or float;
                 defaults to None
        tries: number of tries, defaults to 3
        wait: wait time (in seconds) between tries, defaults to 0.5; will be
              doubled each time is exponential_backoff is True
        exponential_backoff: whether or not to double wait time between
                             consecutive tries; defaults to True
        """
        for _ in range(0, tries):
            try:
                result = self.instrument.ask(command)
                if convert is not None:
                    result = convert(result)
                return result
            except Exception as err:
                warnings.warn("command '%s' failed with exception:\n%s" %\
                              (command, str(err)))
                time.sleep(wait)
                if exponential_backoff:
                    wait *= 2

        # max number of tries reached
        raise RuntimeError("ask '%s' failed after %d tries" %\
                           (command, tries))

    def write(self, command, tries=3, wait=0.5, exponential_backoff=True):
        """Write, and raise an exception only after a certain number of tries.

        See 'ask' for arguments.
        """
        for _ in range(0, tries):
            try:
                self.instrument.write(command)
                return
            except Exception as err:
                warnings.warn("command '%s' failed with exception:\n%s" %\
                              (command, str(err)))
                time.sleep(wait)
                if exponential_backoff:
                    wait *= 2

        # max number of tries reached
        raise RuntimeError("write '%s' failed after %d tries" %\
                           (command, tries))

class PowerSupply(_GPIBInstrument):
    """Remote interface to LakeShore Model 625 SC Magnet Power Supply.

    Attributes:
    data: a list of recorded data points, each data point being a dict with
          'timestamp' and data types (e.g., 'current') as keys
    last_recording: timestamp of the last data point recorded (time.time())
    sampling_interval: minimum sampling interval used for data recording
    """

    _INSTRUMENT_ID = 'GPIB0::20::INSTR'

    def __init__(self, sampling_interval=0.1):
        """
        PowerSupply class constructor.

        Arguments:
        sampling_interval: minimum sampling interval (in seconds) used for data
                           recording; defaults to 0.1, i.e., 10 Hz
        """
        super(PowerSupply, self).__init__(self._INSTRUMENT_ID)
        self.data = []
        self.last_recording = 0
        self.sampling_interval = sampling_interval

    def record_current(self, wait=False):
        """Record current in self.data.

        Return value is the measured current.

        Arguments:
        wait: boolean; if wait is True, data point will be recorded at least
              one sample interval apart from the time of last recording (see
              the sampling_interval and last_recording attributes)
        """
        try:
            if wait:
                while (time.time() - self.last_recording <
                       self.sampling_interval):
                    pass
            timestamp = time.time()
            current = self.get_current()
            self.data.append({'timestamp': timestamp, 'current': current})
            self.last_recording = timestamp
            return current
        except RuntimeError:
            warnings.warn('failed to record current')
            return None

    def set_magnetic_field_constant(self, value):
        """Set the magnetic field constant of the magnet (in T/A)."""
        float(value)
        self.write('FLDS 0,%.4f' % value)

    def get_magnetic_field_constant(self):
        """Get the magnetic field constant of the magnet (in T/A)."""
        response = self.ask('FLDS?')
        unit, value = tuple(response.split(','))
        if unit == '0':
            # already in T/A
            return float(value)
        else:
            # in kG/A, 1 kG/A = 0.1 T/A
            return float(value) * 0.1

    def set_limits(self, current, voltage, rate):
        """Set the upper setting limits of the power supply.

        Arguments:
        current: limit on output current
        voltage: limit on compliance voltage
        rate: limit on output current ramp rate
        """
        float(current)
        float(voltage)
        float(rate)
        self.write('LIMIT %.4f,%.4f,%.4f' % (current, voltage, rate))

    def get_limits(self):
        """Get the upper setting limits of the power supply.

        Return value: a tuple of three floats, representing the limits on the
        output current, the compliance voltage, and the ramp rate, respectively.
        """
        response = self.ask('LIMIT?')
        return tuple([float(value) for value in response.split(',')])

    def lock(self):
        """Lock out front panel operations and set code to 000."""
        self.write('LOCK 1,000')

    def unlock(self):
        """Unlock front panel."""
        self.write('LOCK 0,000')

    def enable_quench_detection(self, rate_limit=1.0):
        """Enable quench detection.

        Arguments:
        rate_limit: a quench will be detected when the output current attempts
                    to change at a rate greater than rate_limit (in A/s);
                    defaults to 1.0
        """
        float(rate_limit)
        self.write('QNCH 1,%.4f' % rate_limit)

    def set_ramp_rate(self, rate):
        """Set the output current ramp rate."""
        float(rate)
        self.write('RATE %.4f' % rate)

    def get_ramp_rate(self):
        """Get the output current ramp rate."""
        return self.ask('RATE?', convert=float)

    def get_field(self):
        """Get the calculated magnetic field (in T)."""
        internal_unit = self.ask('FLDS?').split(',')[0]
        value = self.ask('RDGF?', convert=float)
        if internal_unit == '0':
            # internal unit is T
            return value
        else:
            # internal unit is G
            return value / 10000

    def get_current(self):
        """Get the output current (in A)."""
        return self.ask('RDGI?', convert=float)

    def get_voltage(self):
        """Get output voltage (in V)."""
        return self.ask('RDGV?', convert=float)

    def enable_ramp_segments(self):
        """Enable ramp segments."""
        self.write('RSEG 1')

    def disable_ramp_segments(self):
        """Disable ramp segments."""
        self.write('RSEG 0')

    def set_ramp_segments_params(self, params):
        """Set ramp segments paramters.

        Arguments:
        params: a list of up to 5 tuples (CURRENT, RATE), indicating that the
                ramp rate RATE should be used up to CURRENT
        """
        num_segments = len(params)
        assert num_segments <= 5
        for tup in params:
            float(tup[0])
            float(tup[1])
        for i in range(0, num_segments):
            segment_id = i + 1
            current = params[i][0]
            rate = params[i][1]
            self.write('RSEGS %d,%.4f,%.4f' % (segment_id, current, rate))

    def set_target_field(self, field):
        """Set the field value (in T) that the output will ramp to."""
        float(field)
        internal_unit = self.ask('FLDS?').split(',')[0]
        if internal_unit == '0':
            # internal unit is T
            self.write('SETF %.4g' % field)
        else:
            # internal unit is G
            field *= 10000
            self.write('SETF %.4g' % field)

    def get_target_field(self):
        """Get the field value (in T) that the output will ramp to."""
        internal_unit = self.ask('FLDS?').split(',')[0]
        value = self.ask('SETF?', convert=float)
        if internal_unit == '0':
            # internal unit is T
            return value
        else:
            # internal unit is G
            return value / 10000

    def set_target_current(self, current):
        """Set the current value (in A) that the output will ramp to."""
        float(current)
        assert 0.0 <= current <= 60.1
        self.write('SETI %.4f' % current)

    def get_target_current(self):
        """Get the current value (in A) that the output will ramp to."""
        return self.ask('SETI?', convert=float)

    def set_compliance_voltage(self, voltage):
        """Set the output compliance voltage (in V)."""
        float(voltage)
        assert 0.1 <= voltage <= 5.0
        self.write('SETV %.4f' % voltage)

    def get_compliance_voltage(self):
        """Get the output compliance voltage (in V)."""
        return self.ask('SETV?', convert=float)

    def stop(self):
        """Stop the output current ramp.

        The ramp will stop within two seconds.

        To restart, use set_target_current or set_target_field."""
        self.write('STOP')

class LockIn(_GPIBInstrument):
    """Remote interface to Stanford Research Systems SR830 Lock-in Amplifier.

    Attributes:
    data: a list of recorded data points, each data point being a dict with
          'timestamp' and 'value' as keys
    last_recording: timestamp of the last data point recorded (time.time())
    sampling_interval: minimum sampling interval used for data recording
    """

    _INSTRUMENT_ID = 'GPIB0::8::INSTR'

    def __init__(self, sampling_interval=0.1):
        """LockIn class constructor.

        Arguments:
        sampling_interval: minimum sampling interval (in seconds) used for data
                           recording; defaults to 0.1, i.e., 10 Hz
        """
        super(LockIn, self).__init__(self._INSTRUMENT_ID)
        self.data = []
        self.last_recording = 0
        self.sampling_interval = sampling_interval

    def record_value(self, wait=False):
        """Record data point in self.data.

        Return value is the value on Channel 1 display (returned by get_value).

        Arguments:
        wait: boolean; if wait is True, data point will be recorded at least
              one sample interval apart from the time of last recording (see
              the sampling_interval and last_recording attributes)
        """
        try:
            if wait:
                while (time.time() - self.last_recording <
                       self.sampling_interval):
                    pass
            timestamp = time.time()
            value = self.get_value()
            self.data.append({'timestamp': timestamp, 'value': value})
            self.last_recording = timestamp
            return value
        except RuntimeError:
            warnings.warn('failed to record current')
            return None

    def get_value(self):
        """Get displayed value of Channel 1."""
        return self.ask('OUTR? 1', convert=float)
