#
# This script demonstrates a battery-analysis subsystem.
# It's primary functions are:
#
# 1) to record continuous samples of voltage and current data from a battery in use.
# 2) receive signals from a battery-charging subsystem.
# 3) use the signals and samples to derive an estimate of the battery's current capacity.
#
# The battery's current capacity, relative to the rated 'new' capacity,
# is an indication of the battery age.
#

import board
import time
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

# The battery load is represented by a precision power resistor.
# The resistance value, in ohms
load_resistance = 15

samples_per_minute = 2
minutes_per_hour = 60
milliamps_per_amp = 1000

# Trinket analog port identifiers, API vs pin label, is confusing!
#
# API identifier | Label on Trinket M0 board
# ------------------------------------------
# A1             | 2
#
voltage_sense = AnalogIn(board.A1)

# we are using buttons on the circuit breadboard to simulate
# event signals from our battery charging subsystem. note that a button
# press presents as a False value, so the event logic
# is inverted.

# button:
# battery charging has begun.
s_charge_begin = DigitalInOut(board.D3)
s_charge_begin.direction = Direction.INPUT
s_charge_begin.pull = Pull.UP

# button:
# charging has stopped and battery is fully charged.
s_charge_complete = DigitalInOut(board.D4)
s_charge_complete.direction = Direction.INPUT
s_charge_complete.pull = Pull.UP

# button:
# charging has stopped but the battery is not fully charged.
s_charge_abort = DigitalInOut(board.D0)
s_charge_abort.direction = Direction.INPUT
s_charge_abort.pull = Pull.UP

# buttons might be held down for many main loop cycles.
# to identify single press events, we keep track of the
# button state (up or down) here, and define the event as the
# button release (down-to-up transition).
b_cb_down = False
b_cc_down = False
b_ca_down = False

# we have only two system modes; monitoring or not.
monitoring = False

# storage for our measured data
voltage = []

# Our main loop cycles every half second to be responsive
# to button presses. We need a 30 second interval for capturing
# data. This counter provides the necessary scaling; it
# is reset to zero every 30 seconds.
half_sec = 0

def get_volts():
    
    # constants for our hardware implementation
    a2d_analog_max = 3.3            # per ATSAMD21 part specification
    a2d_digital_max = 65536         # per part specification
    resistor_divider_ratio = 0.684  # see schematic; to keep battery voltage
                                    # in range of the A2D port
    
    ad_volt = (voltage_sense.value * a2d_analog_max) / a2d_digital_max
    return ad_volt / resistor_divider_ratio

# For a given load current in amps, choose a cutoff voltage that is appropriate
# for our linear approximation.
def adjusted_cutoff(load_current):
    # slope and intercept parameters for this function were derived
    # by testing the battery at four different loads.
    slope = -0.449
    intercept = 3.323
    
    return slope * load_current + intercept

def estimate_capacity():
    samples = len(voltage)
    print("capacity estimate after %4.2f minutes:" % float( samples/samples_per_minute) )

    # Because we are actually using a fixed resistance for the load, we
    # have a shortcut for calculating the current sum:
    v_sum = sum(voltage)
    i_sum = v_sum / load_resistance

    # In a more complete system where we are also monitoring the load current
    # into an array named 'current', the equation would be just this:
    #    i_sum = sum(current)
    
    i_avg = i_sum / samples
    energy_used = i_sum / samples_per_minute / minutes_per_hour # in amp-hours

    print("average current = %4.2f mA" % (i_avg * milliamps_per_amp) )
    print("capacity used = %5.2f mAh" % (energy_used * milliamps_per_amp) )

    v_monitor_start = voltage[0]
    print("voltage monitor start = %2.2f volts" % v_monitor_start)
    v_monitor_end = voltage[-1]
    print("voltage monitor end = %2.2f volts" % v_monitor_end)
    v_cutoff = adjusted_cutoff(i_avg)
    print("adjusted voltage cutoff = %2.2f volts" % v_cutoff)
    ratio = ( v_monitor_start - v_cutoff ) / ( v_monitor_start - v_monitor_end )
    energy_total = ratio * energy_used # in amp-hours
    print("predicted total capacity = %5.2f mAh" % (energy_total * milliamps_per_amp) )
    
while True:
    time.sleep(0.5)
    half_sec = half_sec + 1
    if half_sec == 60:
        half_sec = 0

    # simulated charging event signals (button transitions from down to up)
    event_cb = False # charge begin
    event_cc = False # charge complete
    event_ca = False # charge abort
    if b_cb_down and s_charge_begin.value:
        event_cb = True
    if b_cc_down and s_charge_complete.value:
        event_cc = True
    if b_ca_down and s_charge_abort.value:
        event_ca = True
    # record current button states
    b_cb_down = not s_charge_begin.value
    b_cc_down = not s_charge_complete.value
    b_ca_down = not s_charge_abort.value

    # handle state transitions
    if monitoring:
        if event_cb:
            # time to make a capacity estimate
            print("end monitoring; new charging cycle begun.")
            estimate_capacity()
            monitoring = False
        elif event_cc:
            # we should not be monitoring during charging.
            print("ERROR: inconsistent charge complete signal")
            monitoring = False
        elif event_ca:
            # we should not be monitoring during charging.
            print("ERROR: inconsistent charge abort signal")
            monitoring = False
    else:        
        if event_cb:
            # nothing to do.
            pass
        elif event_cc:
            # start gathering data
            voltage = []
            monitoring = True
            print("begin monitoring")
        elif event_ca:
            # nothing to do.
            pass

    # every thirty seconds, grab a data point
    if monitoring and half_sec == 0:
        v_now = get_volts()
        voltage.append(v_now)
        print("minutes %4.2f, voltage = %2.3f" % (len(voltage)/samples_per_minute, v_now))
