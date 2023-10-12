"""V2.3
Module for buttons used in Masterthesis SmartCane V.2
h_da FBEIT, Prof. Dr. Carsten Zahout-Heil
created by Marian Weickert
on 26.08.2023
"""



#################### import section #################### -> all libraries needed to run the function

import time
import RPi.GPIO as GPIO



#################### Test program variables ####################

GPIO.setmode(GPIO.BCM)

button_mode = [0, 1]   # Mode of button 0 ([0] = distance) and button 1 ([1] = mute)
BUTTON_PIN = [17, 27]   # Pins for Mute-Mode [0] & Distance-Mode [1]: pressed = 0, not pressed = 1
button_edge = [[0, 0], [0, 0]]   # relative time-stamp of rising ([][0]) and falling ([][1])
    #  edge of button 0 ([0][])(mute) and button 1 ([1][]) (distance)


class Button:
    """class for interpreting actions of 2 buttons """

    #################### Class-specific Variables ####################

    def __init__(self):
        self.but_press_time = [None, None]   # pressing time of buttons
        self.but_mode = [1, 1]   # default-values of button modes



    #################### Function Section ####################


    def set_but_sel(self, t_stamp_1, t_stamp_2, t_switch):
        """Calculating period of Time of 2 timestamps and \
            return value depending on time button was pressed
            """

        # Calculate period of time button is pressed (t_but_pressed)
        if t_stamp_1 > 0 and t_stamp_2 > 0:
            t_but_pressed = abs(t_stamp_1 - t_stamp_2)
            t_stamp_1 = 0
            t_stamp_2 = 0
        else:
            t_but_pressed = 0

        # set return-value depending on value of t_but_pressed
        # when t_but_pressed is resettet (=0), return value is 0
        if t_but_pressed == 0:
            return 0
        # when t_but_pressed is lower than switch-Time (t_switch), return value is 1 (Short press)
        if t_but_pressed < t_switch and t_but_pressed != 0:
            return 1
        # when t_but_pressed is higher than switch-Time (t_switch), return value is 2 (Long press)
        if t_but_pressed > t_switch:
            return 2


    def but_func (self, bu_no, function, act_inst, bu_edge):
        """Function for button use: short press -> show active mode, \
            long press -> change active state
            """

        self.but_press_time[bu_no] = self.set_but_sel(bu_edge[bu_no][0], bu_edge[bu_no][1], 1)


        if self.but_press_time[bu_no] == 0:   # value 0 = no button action detected
            pass


        elif self.but_press_time[bu_no] == 1:   # short press detected -> return active mode

            if self.but_mode[bu_no] == 1:   # detection of active mode: 1 (long distance / unmute)

                time.sleep(0.5)
                act_inst.set_vib_intv(12)   # set haptic feedback of active mode
                act_inst.start_vib_intv(0.5)   # set haptic feedback of active mode

                if bu_no == 0:   # = distance-button
                    print(f"active {function}-mode = {self.but_mode[bu_no]} (long distance)")
                elif bu_no == 1:   # = mute-button
                    print(f"active {function}-mode = {self.but_mode[bu_no]} (unmute)")

            elif self.but_mode[bu_no] == 0:   # detection of active mode: 0 (short distance / mute)

                time.sleep(0.5)
                act_inst.set_vib_intv(4)   # set haptic feedback of active mode
                act_inst.start_vib_intv(0.5)   # set haptic feedback of active mode

                if bu_no == 0:   # = distance-button
                    print(f"active {function}-mode = {self.but_mode[bu_no]} (short distance)")
                elif bu_no == 1:   # = mute-button
                    print(f"active {function}-mode = {self.but_mode[bu_no]} (mute)")


        elif self.but_press_time[bu_no] == 2:   # long press detected -> change active mode

            if self.but_mode[bu_no] == 0:   # detection of active mode: 0 (short distance / mute)

                time.sleep(0.5)
                act_inst.set_vib_intv(12)   # set haptic feedback of active mode
                act_inst.start_vib_intv(0.5)   # set haptic feedback of active mode

                self.but_mode[bu_no] = 1   # change active mode to 1 (class variable)

                if bu_no == 0:   # = distance-button
                    print(f"{function}-mode changed to {self.but_mode[bu_no]} (long distance)")
                elif bu_no == 1:   # = mute-button
                    print(f"{function}-mode changed to {self.but_mode[bu_no]} (unmute)")
                    act_inst.set_drv_mute_off()   # set drv to standby-state -> no vibration

                return self.but_mode[bu_no]

            elif self.but_mode[bu_no] == 1:   # detection of active mode: 1 (long distance / unmute)

                time.sleep(0.5)
                act_inst.set_vib_intv(4)   # set haptic feedback of active mode
                act_inst.start_vib_intv(0.5)   # set haptic feedback of active mode

                self.but_mode[bu_no] = 0   # change active mode to 0 (class variable)

                if bu_no == 0:   # = distance-button
                    print(f"{function}-mode changed to {self.but_mode[bu_no]} (short distance)")
                elif bu_no == 1:   # = mute-button
                    print(f"{function}-mode changed to {self.but_mode[bu_no]} (mute)")
                    act_inst.set_drv_mute_on()   # set Drv to ready-state

        return self.but_mode[bu_no]




# def cb_button_time(pin):
# """Callback Function for detecting the time of a pressed button"""
#     global button_edge
#     global BUTTON_PIN


#     if pin == BUTTON_PIN[0]:
#         if GPIO.input(pin):
#             button_edge[0][1] = time.monotonic()
#             #print("Timestamp rising edge Button 1: ", button_edge[0][1]
#         else:
#             button_edge[0][0] = time.monotonic()
#             #print("Timestamp falling edge Button 1: ", button_edge[0][0])
#     elif pin == BUTTON_PIN[1]:
#         if GPIO.input(pin):
#             button_edge[1][1] = time.monotonic()
#             #print("Timestamp rising edge Button 2: ", button_edge[1][1]
#         else:
#             button_edge[1][0] = time.monotonic()
#             #print("Timestamp falling edge Button 2: ", button_edge[1][0])


# #################### Interrupt-Handler #################### -> needs to be run in main-code

# GPIO.add_event_detect(   # Button 0 Interrupt service routine
#     BUTTON_PIN[0],
#     GPIO.BOTH,
#     callback = cb_button_time,
#     bouncetime = 50)

# GPIO.add_event_detect(   # Button 1 Interrupt service routine
#     BUTTON_PIN[1],
#     GPIO.BOTH,
#     callback = cb_button_time,
#     bouncetime = 50)




#################### Example-Code to be used in main-Thread ####################

if __name__ == "__main__":
    try:
        testButton= Button()

        print("Hey ho, let's go!")

        while 1:
            button_mode[0] = testButton.but_func(0, "distance", myActuator, button_edge[0])
            button_mode[1] = testButton.but_func(1, "mute", myActuator, button_edge[1])

    except KeyboardInterrupt:
        GPIO.cleanup()
