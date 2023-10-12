""" V3.2
Module for testing user feedback used in
Masterthesis SmartCane V.2 Unittest
h_da FBEIT, Prof. Dr. Carsten Zahout-Heil
created by Marian Weickert
on 24.08.2023
"""


#################### import section ####################

import board
import busio

import adafruit_drv2605
import adafruit_tca9548a


import RPi.GPIO as GPIO


#################### variables section ####################

GPIO.setmode(GPIO.BCM)

type_in = 0
drv = [0, 0]
BUT_PIN = 17   # Button for user-feedback: pressed = 0, not pressed = 1
INTENSITY = 100   # Vibration-Intensity for semi-random output (intensity fixed, frequency & actuators random)
FREQUENCY = 180   # Vibration-Frequency for semi-random output (frequency fixed, intensity & actuators random)

ACTUATOR_NO = [0, 1]   # channel of Actuators (global)
ACTUATOR_TYPE = [2414, 2414]   # type of actuator. Choose between \
    # 2608 (Grewus EXS 2608L-03A) and 2414 (Grewus EXS 241408W B)


#################### Function section ####################

def cb_user_feedback(pin):
    """Callback Function for detecting user feedback"""
    test.set_act("2")
    print("\nChoose Action (help: h): ")



class TestVib:
    """class for setting Unittest-environment"""

    import random
    import time
    import csv

    import actuator_test

    ### class-specific variables ###

    def __init__(self, ACT_NO):

        self.ACT_NO = ACT_NO   # list of actuator-Channeels
        self.act_on = [0,0]   # list of activated actuators. 1 = activated, 0 = deactivated
        self.act_ch = 0  # actived actuator channels (explicit)

        self.val_real_time = 0   # intensity-value of vibration. Range: 0...127
        self.val_freq = 0   # frequency of vibration
        self.VAL_FREQ_LIM = [160, 400]   # list of min and max frequency-limits in [hz]

        self.time_on = 0   # time-stamp of vibration start
        self.time_off = 0   # time-stamp of vibration stop
        self.time_abs = 0   # calculated time between time_on an time_off --> time_off - time_on

        self.logfile = '230831_Logfile_V2.csv'   # name of logfile
        self.logdata = [0, 0, 0, 0, 0, 0, 0, 0]   # list of logfile data
        self.log_message = ""
        self.index = 1   # position-index for logfile

        self.test_actuator = self.actuator_test.Actuator(self.ACT_NO)   # instance of actuator-class

    GPIO.setup(BUT_PIN,GPIO.IN, pull_up_down=GPIO.PUD_UP) # Declar. of Button 1 (internal pull up)


    #################### Function section ####################

    def init_act(self):
        """initialisation of actuators"""

        self.test_actuator.config_drv_to_lra()
        self.test_actuator.autocalibration(ACTUATOR_TYPE)
        self.test_actuator.set_drv_open_loop()
        self.test_actuator.set_vib_const(0, self.ACT_NO)


    def get_char(self, message):
        """get User-Input"""

        input_string = input(message)
        return input_string



    def write_csv(self, log, data = [0,0,0,0,0,0,0]):
        """write input to csv-file"""

        with open(log, 'a', newline = '') as font:
            writer = self.csv.writer(font)
            writer.writerow(data)



    def set_act(self, char):
        """set action in dependence of chosen char"""

        if char == "1":   # stop vibration and write data to logfile

            # get ending-timestamp (relative) and calculate absolute reaction-time
            self.time_off = self.time.monotonic()
            self.time_abs = self.time_off - self.time_on

            # set vibration-intensity to 0
            for i in self.ACT_NO:
                self.test_actuator.set_vib_const(0, [i])

            # print data
            print("\n\nStop vibration")
            print(f"Reaction time: {self.time_abs}")

            # write data to logfile
            self.logdata = [self.index,
                             self.act_on[0],
                             self.act_on[1],
                             self.val_real_time,
                             self.val_freq,
                             self.time_abs,
                             "-",
                             "-"
                             ]
#             print(self.logdata)
            self.write_csv(self.logfile, self.logdata)
            print(f"Data written to logfile: {self.logfile}")

            # reset variables
            self.time_on = 0
            self.time_off = 0
            self.time_abs = 0
            self.logdata = [0, 0, 0, 0, 0, 0, 0, 0]
            self.index = self.index + 1
            # print(self.index)

        elif char == "2":   # start vibration (act-, freq-, intens-selection: random)

            # set random vibration-intensity
            self.val_real_time = self.random.randint(10,127)

            # set random vibration-frequency
            self.val_freq = self.random.randint(self.VAL_FREQ_LIM[0],self.VAL_FREQ_LIM[1])
            self.test_actuator.set_drv_freq(self.val_freq)

            # select activation of actuators (random)
            self.act_on = [0, 0]   # reset of previously made activations

            while self.act_on[0] == 0 and self.act_on[1] == 0:  # prevention of random output [0, 0]
                for i in self.ACT_NO:

                    self.act_on[i] = self.random.randint(0,1)

            # set vibration-intensity if actuator is selected
            for i in self.ACT_NO:

                # set vibration intensity if actuator is selected
                if self.act_on[i] == 1:
                    self.test_actuator.set_vib_const(self.val_real_time, [i])
#                     print(f"Actor {i} active")
                else:
                    self.test_actuator.set_vib_const(0, [i])
#                     print(f"Actor {i} inactive")


            # safe starting-timestamp (relative)
            self.time_on = self.time.monotonic()

            # printing chosen values
            print("\n\nStart vibration (all values random)")
            print(f"Act1: {self.act_on[0]}, Act2: {self.act_on[1]}, Intensity: {self.val_real_time}, Frequency: {self.val_freq}")

            # reset variable
            char = 0

        elif char == "3":   # start vibration (act-, freq-select: random intens-select: fix)

            # set fixed vibration-intensity
            self.val_real_time = INTENSITY

            # set random vibration-frequency
            self.val_freq = self.random.randint(self.VAL_FREQ_LIM[0],self.VAL_FREQ_LIM[1])
            self.test_actuator.set_drv_freq(self.val_freq)

            # select activation of actuators (random)
            self.act_on = [0, 0]   # reset of previously made activations

            while self.act_on[0] == 0 and self.act_on[1] == 0:  # prevention of random output [0, 0]
                for i in self.ACT_NO:

                    self.act_on[i] = self.random.randint(0,1)

            # set vibration-intensity if actuator is selected
            for i in self.ACT_NO:

                # set vibration intensity if actuator is selected
                if self.act_on[i] == 1:
                    self.test_actuator.set_vib_const(self.val_real_time, [i])
#                     print(f"Actor {i} active")
                else:
                    self.test_actuator.set_vib_const(0, [i])
#                     print(f"Actor {i} inactive")


            # safe starting-timestamp (relative)
            self.time_on = self.time.monotonic()

            # printing chosen values
            print("\n\nStart vibration (act, freq:random, intens: fix)")
            print(f"Act1: {self.act_on[0]}, Act2: {self.act_on[1]}, Intensity: {self.val_real_time}, Frequency: {self.val_freq}")

            # reset variable
            char = 0

        elif char == "4":   # start vibration (act-, intens-select: random freq-select: fix)

            # set random vibration-intensity
            self.val_real_time = self.random.randint(10,127)

            # set fixed vibration-frequency
            self.test_actuator.set_drv_freq(FREQUENCY)

            # select activation of actuators (random)
            self.act_on = [0, 0]   # reset of previously made activations

            while self.act_on[0] == 0 and self.act_on[1] == 0:  # prevention of random output [0, 0]
                for i in self.ACT_NO:

                    self.act_on[i] = self.random.randint(0,1)

            # set vibration-intensity if actuator is selected
            for i in self.ACT_NO:

                # set vibration intensity if actuator is selected
                if self.act_on[i] == 1:
                    self.test_actuator.set_vib_const(self.val_real_time, [i])
#                     print(f"Actor {i} active")
                else:
                    self.test_actuator.set_vib_const(0, [i])
#                     print(f"Actor {i} inactive")


            # safe starting-timestamp (relative)
            self.time_on = self.time.monotonic()

            # printing chosen values
            print("\n\nStart vibration (act, intens:random, freq: fix)")
            print(f"Act1: {self.act_on[0]}, Act2: {self.act_on[1]}, Intensity: {self.val_real_time}, Frequency: {self.val_freq}")

            # reset variable
            char = 0

        elif char == "5":   # start vibration (act-, intens- and frequ-selection is explicit)

            # set actuators active / inactive (explicit)
            self.act_ch = input("\nChoose actuator (format: xx): ")   # input in format: \
                # 00, 10, 10, 11 -> 1 = actuator active, 2 = actuator inactive

            # set vibration intensity (explicit)
            self.val_real_time = input("\nChoose intensity (value: 0...127): ")

            # set vibration frequency (explicit)
            self.val_freq = input("\nChoose frequency (value: 160...1000): ")
            self.test_actuator.set_drv_freq(int(self.val_freq))
            print("")

            if int(self.val_real_time) > 127:
                self.val_real_time = 127

            # set vibration-intensity if actuator is selected
            for i in self.ACT_NO:
                if self.act_ch[i] == "1":
                    self.act_on[i] = 1
                    self.test_actuator.set_vib_const(int(self.val_real_time), [i])
#                     print(f"Actor {i} active")
                else:
                    self.act_on[i] = 0
                    self.test_actuator.set_vib_const(0, [i])
#                     print(f"Actor {i} inactive")

            # get starting-timestamp (relative)
            self.time_on = self.time.monotonic()

            # printing chosen values
            print("\nStart vibration (explicit values)")
            print(f"Act1: {self.act_on[0]}, Act2: {self.act_on[1]}, Intensity: {self.val_real_time}, Frequency: {self.val_freq}")

            # reset variable
            char = 0

        elif char == "6":   # user-feedback: vibration perceived, right allocation
            print("vibration perceived, right allocation")
            self.write_csv(self.logfile,[(self.index - 1), "-", "-", "-", "-", "-", 1, 1])

        elif char == "7":   # user-feedback: vibration perceived, wrong allocation
            print("vibration perceived, wrong allocation")
            self.write_csv(self.logfile,[(self.index - 1), "-", "-", "-", "-", "-", 1, 0])

        elif char == "8":   # user-feedback: no perception
            print("no perception")
            self.write_csv(self.logfile,[(self.index - 1), "-", "-", "-", "-", "-", 0, 0])

        elif char == "h":   # show help
            self.help_instr()

        elif char == "n":
            self.log_message = self.get_char("\nType in message: ")
            self.write_csv(self.logfile,[self.log_message, "-", "-", "-", "-", "-", "-", "-"])

        elif char == "0":   # no character chosen
            pass

        else:   # invalid input
            print("Invalid input - please retry")

    def help_instr(self):
            """helping information of terminal functionality"""

            print("\n \t 0 = no action (default)")
            print("\t 1 = Stop Vibration")
            print("\t 2 = Start Vibration (random actuators, frequence and intensity)")
            print("\t 3 = Start Vibration (random actuators, frequence - static intensity)")
            print("\t 4 = Start Vibration (random actuators, intensity - static frequence)")
            print("\t 5 = Start Vibration (explicit actuators, frequence and intensity")
            print("\t 6 = User-Feedback: Perception exist, allocation right")
            print("\t 7 = User-Feedback: Perception exist, allocation wrong")
            print("\t 8 = User-Feedback: No Perception")
            print("\t h = Help")
            print("\t n = Type in Logfile message\n")
            print("\t all other inputs are invalid \n")



#################### Interrupt-Handler ####################

# Button 0 Interrupt service routine
GPIO.add_event_detect(
    BUT_PIN,
    GPIO.FALLING,
    callback = cb_user_feedback,
    bouncetime = 200)


#################### main program ####################

if __name__ == "__main__":

    try:


        ### Test initialisation ###

        test = TestVib(ACTUATOR_NO)

        test.init_act()


        while 1:

            type_in = test.get_char("\nChoose Action (help: h): ")

            test.set_act(type_in)

    except KeyboardInterrupt:
        test.test_actuator.set_vib_const(0, ACTUATOR_NO)
        print("\n\nProgram aborted by user")
