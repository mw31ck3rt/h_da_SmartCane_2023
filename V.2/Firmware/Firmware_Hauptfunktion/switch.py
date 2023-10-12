""" V2.2
Module for turning switch used in Masterthesis SmartCane V.2
h_da FBEIT, Prof. Dr. Carsten Zahout-Heil
created by Marian Weickert
on 25.08.2023
"""
import RPi.GPIO as GPIO


### Variables Section ###
# SWITCH_PIN = [23, 24, 25]   # pins of turning switch, 0 = active, 1 = inactive

### Test program variables ###

GPIO.setmode(GPIO.BCM)


class Switch:
    """class for turning switch -> sets one of three GPIO inputs to GND"""

    swi_state = 1

    #################### Function Section ####################

    def set_switch_state(self, sw_pin):
        """ Returning value of 0...2 in dependence on selected GPIO-Pin """
        if GPIO.input(sw_pin[0]) == 0:
            self.swi_state = 0
        elif GPIO.input(sw_pin[1]) == 0:
            self.swi_state = 1
        elif GPIO.input(sw_pin[2]) == 0:
            self.swi_state = 2
        return self.swi_state


#################### Test Program ####################

if __name__ == "__main__":
    try:
        test_switch = Switch()

        test_state = test_switch.set_switch_state(SWITCH_PIN)

        print("Active switch-state is ", test_state)

    except KeyboardInterrupt:
        GPIO.cleanup()
