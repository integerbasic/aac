import board
import pulseio
import time
from analogio import AnalogIn

# Trinket pin identifiers vs API is confusing!
# API identifier | Label on Trinket M0 board
# ------------------------------------------
# A0             | 1~
# A1             | 2
# A3             | 3


buzzer = pulseio.PWMOut(board.A3, frequency=1000, duty_cycle = 0)
voltage_sense = AnalogIn(board.A1)

def alert_on():
    buzzer.duty_cycle = 30000

def alert_off():
    buzzer.duty_cycle = 0


def get_volts():
    ad_volt = (voltage_sense.value * 3.3) / 65536
    return ad_volt / 0.684 # resistor divider used to keep signal in A/D range

#
# beep once on reboot
alert_on()
time.sleep(1)
alert_off()

while True:
    time.sleep(10)
    v = get_volts()    
    print("%f" % v)
    if v < 2.8 :
        # fully discharged
        alert_on()
    else:
        alert_off()
        
