#!/usr/bin/env python

from __future__ import print_function as _print_function

import multiprocessing as mp
import sys
import time

import colorama
from colorama import Fore
import visa

# import gpib

# initialize colorama
colorama.init(autoreset=True)

# latency of controller's reaction to user input and internal messages/signals
LATENCY = 0.1

class InstrumentController(mp.Process):
    """Controller for a pyvisa instrument.

    Inherited from multiprocessing.Process.

    Attributes:
    messenger - multiprocessing.Connection object for sending and receiving
                messages to and from the instrument.
    """

    # Internal attributes:
    # _instrument - visa.Resource object for the instrument
    # _listener   - the other end of messenger's pipe

    def __init__(self, instrument):
        # if not isinstance(instrument, visa.Resource):
        #     err_msg = 'instrument has type %s, not visa.Resource' % \
        #               type(instrument).__name__
        #     raise TypeError(err_msg, instrument)
        mp.Process.__init__(self)
        self._instrument = instrument
        self.messenger, self._listener = mp.Pipe()

class PowerSupplyController(InstrumentController):

    def __init__(self):
        InstrumentController.__init__(self, None)
        # InstrumentController.__init__(self, gpib.PowerSupply())
        # self._instrument.initialize()

    def run(self):
        pass

class LockInController(InstrumentController):

    def __init__(self):
        InstrumentController.__init__(self, None)
        # InstrumentController.__init__(self, gpib.LockIn())
        pass

    def run(self):
        pass

def console_control(verbose_prompt=True):
    psc = PowerSupplyController()
    lic = LockInController()
    psc.start()
    lic.start()
    pscm = psc.messenger
    licm = lic.messenger
    long_prompt = """Please type in one of the following commands:
   * r(amp) TARGET_CURRENT RAMPING_RATE
        ramp up/down current output of the power supply
   * i(nterrupt)
        interrupt ramping (only useful when ramping is in progress)
   * f(inish)
        finish experiment and terminate controllers
   * k(ill)
        terminate controllers
"""
    short_prompt = "Commands: r(amp) TARGET_CURRENT RAMPING_RATE, i(nterrupt), f(inish), or k(ill)\n"
    status = 0 # status of last command, 0 if successful, 1 if failed
    while True:
        # prompt for and read console input
        if verbose_prompt:
            sys.stderr.write(Fore.CYAN + long_prompt)
        else:
            sys.stderr.write(Fore.CYAN + short_prompt)
        if status == 0:
            sys.stderr.write(Fore.GREEN + ">> ")
        else:
            sys.stderr.write(Fore.RED + ">> ")
        try:
            console_input = raw_input()
        except NameError:
            console_input = input()

        # consume all messages from instruments during the period of waiting
        # might add error diagnostic and handling code here
        while psc.messenger.poll():
            psc.messenger.recv()
        while lic.messenger.poll():
            lic.messenger.recv()

        # process console input
        if console_input[0] == 'r':
            # ramp
            args = console_input.split()
            try:
                assert len(args) == 3
                target_current = float(args[1])
                ramping_rate = float(args[2])
            except (AssertionError, ValueError):
                sys.stderr.write(Fore.RED + "error: malformed ramp command\n\n")
                status = 1
                continue
            # send message along with arguments
            pscm.send('ramp')
            pscm.send(target_current)
            pscm.send(ramping_rate)
            # wait for response
            if pscm.poll(LATENCY * 10):
                msg = pscm.recv()
                if msg == 'ramping started':
                    sys.stderr.write(Fore.GREEN + "ramping started\n\n")
                    status = 0
                elif msg == 'ramping in progress':
                    sys.stderr.write(Fore.RED + "error: command ignored due to ongoing ramping; please wait or interrupt\n\n")
                    status = 1
                elif msg == 'lacking arguments':
                    sys.stderr.write(Fore.RED + "internal error: the power supply controller did not receive the ramping arguments\n\n")
                else:
                    sys.stderr.write(Fore.YELLOW + "internal warning: unknown message '%s' received from the power supply controller\n\n" % msg)
                    status = 1
            else:
                sys.stderr.write(Fore.YELLOW + "internal warning: no response message from the power supply controller\n\n")
                status = 1

        elif console_input[0] == 'i':
            # interrupt
            pscm.send('interrupt')
            if pscm.poll(LATENCY * 10):
                msg = pscm.recv()
                if msg == 'interrupted':
                    sys.stderr.write(Fore.GREEN + "interrupted\n\n")
                    status = 0
                elif msg == 'nothing to interrupt':
                    sys.stderr.write(Fore.RED + "warning: nothing to interrupt\n\n")
                    status = 1
                else:
                    sys.stderr.write(Fore.YELLOW + "internal warning: unknown message '%s' received from the power supply controller\n\n" % msg)
                    status = 1
            else:
                sys.stderr.write(Fore.YELLOW + "internal warning: no response message from the power supply controller\n\n")
                status = 1

        elif console_input[0] == 'f':
            # finish
            # terminate power supply controller
            pscm.send('finish')
            ps_stopped = False
            if pscm.poll(LATENCY * 10):
                msg = pscm.recv()
                if msg == 'stopped':
                    ps_stopped == True
                    status = 0
                elif msg == 'ramping in progress':
                    sys.stderr.write(Fore.RED + "error: command ignored due to ongoing ramping; please wait or interrupt\n")
                    status = 1
                else:
                    sys.stderr.write(Fore.YELLOW + "internal warning: unknown message '%s' received from the power supply controller\n" % msg)
                    status = 1
            else:
                sys.stderr.write(Fore.YELLOW + "internal warning: no response message from the power supply controller\n")
                status = 1
                if not psc.is_alive():
                    ps_stopped == True
            # continue if failed to stop power supply controller
            if ps_stopped:
                sys.stderr.write(Fore.GREEN + "power supply controller stopped\n")
            else:
                sys.stderr.write(Fore.RED + "error: failed to stop power supply controller\n\n")
                status = 1
                continue
            # terminate lock-in controller
            licm.send('finish')
            li_stopped = False
            if licm.poll(LATENCY * 10):
                msg = licm.recv()
                if msg == 'stopped':
                    li_stopped == True
                    status = 0
                else:
                    sys.stderr.write(Fore.YELLOW + "internal warning: unknown message '%s' received from the lock-in controller\n" % msg)
                    status = 1
            else:
                sys.stderr.write(Fore.YELLOW + "internal warning: no response message from the lock-in controller\n")
                status = 1
                if not lic.is_alive():
                    li_stopped == True
            # continue if failed to stop lock-in controller
            if li_stopped:
                sys.stderr.write(Fore.GREEN + "lock-in controller stopped\n")
            else:
                sys.stderr.write(Fore.RED + "error: failed to stop lock-in controller\n\n")
                status = 1
                continue
            # success
            sys.stderr.write(Fore.GREEN + "finished\n\n")
            status = 0
            break

        elif console_input[0] == 'k':
            psc.terminate()
            lic.terminate()
            sys.stderr.write(Fore.RED + "controllers terminated\n\n")
            status = 1
            break

        else:
            # unknown input
            sys.stderr.write(Fore.RED + "error: unknown command '%s'\n\n" % console_input)

        # end of console input cycle
        time.sleep(LATENCY)

    return (psc, lic)

if __name__ == "__main__":
    console_control(verbose_prompt=False)
