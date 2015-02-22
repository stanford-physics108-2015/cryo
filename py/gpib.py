#!/usr/bin/env python

"""Control interface of GPIB instruments."""

from __future__ import division

import sys
import time
import warnings

import visa

_VISA_PATH = '/cygdrive/c/Windows/System32/visa32.dll'
_manager = visa.ResourceManager(_VISA_PATH)
_programmer = _manager.get_instrument('GPIB0::22::INSTR')
_power_supply = _manager.get_instrument('GPIB0::5::INSTR')
_lock_in = _manager.get_instrument('GPIB0::18::INSTR')

class _Programmer(object):
    """Wrapper around AMI 420 programmer's GPIB interface.

    All verb methods follow the following convention unless otherwise specified:
    the return value is True if all operations finished successfully without
    exception, and False otherwise.
    """

    # magnet inductance: 0.25 Henries
    # charging voltage (from spec sheet): 0.09 Volts
    # V = L dI/dt
    DEFAULT_RAMPING_RATE = 0.36

    DEFAULT_SAMPLING_INTERVAL = 0.1

    def __init__(self, sampling_interval=DEFAULT_SAMPLING_INTERVAL):
        self.instrument = _programmer
        self.data = []
        self.last_recording = 0
        self.sampling_interval = sampling_interval

    def initialize(self):
        """Initialize the programmer."""
        no_exception = True
        no_exception &= self.lock()
        return no_exception

    def lock(self, console_message=None):
        """Disable front panel control."""
        try:
            _programmer.write('SYSTem:REMote')
            if console_message is not None:
                sys.stderr.write(console_message)
            return True
        except:
            warnings.warn("'SYSTem:REMote' failed")
            return False

    def unlock(self, console_message=None):
        """Enable front panel control."""
        try:
            _programmer.write('SYSTem:LOCal')
            if console_message is not None:
                sys.stderr.write(console_message)
            return True
        except:
            warnings.warn("'SYSTem:LOCal' failed")
            return False

    def record_current(self, wait=False):
        """Record current through the current shunt."""
        try:
            if wait:
                while (time.time() - self.last_recording <
                       self.sampling_interval):
                    pass
            timestamp = time.time()
            current = float(_programmer.ask('CURRage:MAGnet?'))
            self.data.append({'timestamp': timestamp, 'current': current})
            self.last_recording = timestamp
            return True
        except:
            warnings.warn("failed to get current with 'CURRage:MAGnet?'")
            return False

    def ramp_current(self, target_current, ramping_rate=DEFAULT_RAMPING_RATE,
                     record_current=True,
                     messenger=None,
                     send_on_start=True, send_on_completion=False,
                     send_on_interruption=True, send_on_ignored=True,
                     console_message=None):
        """Ramp current."""
        try:
            feedback = _programmer.write('CONFigure:CURRent:PROGram %f' \
                                         % target_current)
            target_current_remote = float(_programmer.ask('CURRent:PROGram?'))
            assert abs(target_current - target_current_remote) <= 0.005
            feedback = _programmer.write('CONFigure:RAMP:RATE:CURRent %f' \
                                         % ramping_rate)
            ramping_rate_remote = float(_programmer.ask('RAMP:RATE:CURRent?'))
            assert abs(ramping_rate - ramping_rate_remote) <= 0.0005
        except:
            warnings.warn("failed to set target_current and ramping rate")

        try:
            feedback = _programmer.write('RAMP')
            state = int(_programmer.ask('STATE?'))
            assert state in {1, 2} # state should be RAMPING or HOLDING
        except:
            warnings.warn("failed to ramp")

        if messenger is not None and send_on_start:
            messenger.send('ramping started')

        while True:
            # inspect current state
            try:
                state = int(_programmer.ask('STATE?'))
            except:
                warnings.warn("failed to get state with 'STATE?'")
                return False

            if state == 1:
                # RAMPING to programmed current/field
                pass
            elif state == 2:
                # HOLDING at the programmed current/field
                # i.e., ramping completed
                if messenger is not None and send_on_completion:
                    messenger.send('ramping completed')
                if console_message is not None:
                    sys.stderr.write(console_message)
                return True
            else:
                warnings.warn("programmer in wrong state %d" % state)
                return False

            # record current
            if record_current:
                self.record_current(wait=True)

            # check messages
            if messenger is not None and messenger.poll(self.sampling_interval / 2):
                msg = messenger.recv()
                if msg == 'interrupt':
                    try:
                        feedback = _programmer.write('PAUSE')
                        state = int(_programmer.ask('STATE?'))
                        assert state == 3 # state should be PAUSED
                    except:
                        warnings.warn('failed to interrupt')
                        return False
                    # successfully interrupted
                    if messenger is not None and send_on_interruption:
                        messenger.send('interrupted')
                    return True
                elif msg == 'lock':
                    self.lock()
                elif msg == 'unlock':
                    self.unlock()
                else:
                    # ignore message
                    if send_on_ignored:
                        messenger.send('ramping in progress')

class _PowerSupply(object):
    """Wrapper around Agilent 6031A DC Power Supply's GPIB interface."""

    def __init__(self):
        self.instrument = _power_supply

    def initialize(self):
        """Initialize the programmer."""
        pass

class _LockIn(object):
    #! check model number
    """Wrapper around HP SR810 Lock-In Amplifier's GPIB interface."""

    def __init__(self):
        self.instrument = _lock_in
        self._data_chunks = []

    def initialize(self):
        """Initialize the lock-in."""
        pass

programmer = _Programmer()
power_supply = _PowerSupply()
lock_in = _LockIn()
