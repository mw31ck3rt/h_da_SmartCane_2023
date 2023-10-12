""" V2.4 (FAT-Version)
Module of main firmware used in Masterthesis SmartCane V.2
h_da FBEIT, Prof. Dr. Carsten Zahout-Heil
created by Thomas Eistetter and Marian Weickert
on 27.08.2023
"""

#################### import section ####################

import time
import datetime
import os
import threading

import RPi.GPIO as GPIO
import board
import busio

import adafruit_drv2605
import adafruit_tca9548a

import actuator  # written by MW
import button  # written by MW
import switch # written by MW
import sensors # written by TE
import data_procession # written by TE
import measprotocol # written by TE (for testing only)


#################### variables section ####################

GPIO.setmode(GPIO.BCM)

ACTUATOR_NO = [0]   # channel of Actuators (global)
ACTUATOR_TYPE = [2608, 2414]   # type of actuator: 2608 (Grewus EXS 2608L-03A) or \
# 2414 (Grewus EXS 241408W B)

button_edge = [[0, 0], [0, 0]]   # rel. time-stamp of rising ([][0]) and falling ([][1]) edge of \
# button 0 ([0][])(mute) and button 1 ([1][]) (distance)
button_mode = [1, 1]   # Mode of button 0=[0]=distance and button 1=[1]=mute
BUTTON_PIN = [17, 27]   # Pins for Mute-Mode [0] and Distance-Mode [1]: pressed = 0, not pressed = 1

SWITCH_PIN = [23, 24, 25]   # pins of turning switch, 0 = active, 1 = inactive

run = True
value = 0
ultrasonic_exception = None   # Exception for ultrasonic thread
lidar_exception = None   # Exception for lidar thread


#################### GPIO declaration ####################

GPIO.setup(   # Declaration of Button 0 with internal pull up resistor
    BUTTON_PIN[0],
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
    )
GPIO.setup(      # Declaration of Button 1 with internal pull up resistor
    BUTTON_PIN[1],
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
    )
#
GPIO.setup(   # Declaration of switch-state 0 with internal pull up resistor
    SWITCH_PIN[0],
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
    )
GPIO.setup(   # Declaration of switch-state 1 with internal pull up resistor
    SWITCH_PIN[1],
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
    )
GPIO.setup(   # Declaration of switch-state 2 with internal pull up resistor
    SWITCH_PIN[2],
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
    )



#################### Function section ####################

def erase_button_edges():
    """ Erase time-stamps if they are written (unequal 0)"""
    if button_edge[0][0] != 0 and button_edge[0][1] != 0:
        button_edge [0][0] = 0
        button_edge [0][1] = 0
    if button_edge[1][0] != 0 and button_edge[1][1] != 0:
        button_edge [1][0] = 0
        button_edge [1][1] = 0


def cb_button_time(pin):
    """ Callback Function for detecting the time of a pressed button """
    global button_edge
    global BUTTON_PIN


    if pin == BUTTON_PIN[0]:
        if GPIO.input(pin):
            button_edge[0][1] = time.monotonic()
            #print("Timestamp rising edge Button 1: ", button_edge[0][1]
        else:
            button_edge[0][0] = time.monotonic()
            #print("Timestamp falling edge Button 1: ", button_edge[0][0])
    elif pin == BUTTON_PIN[1]:
        if GPIO.input(pin):
            button_edge[1][1] = time.monotonic()
            #print("Timestamp rising edge Button 2: ", button_edge[1][1]
        else:
            button_edge[1][0] = time.monotonic()
            #print("Timestamp falling edge Button 2: ", button_edge[1][0])


# lock for i2c communication
i2c_lock = threading.Lock()


## class section for threads ##
class ultrasonicThread(threading.Thread):
    """ Thread for ultrasonic sensor """

    def __init__(self):
        threading.Thread.__init__(self)
        self.sensor_1 = sensors.URM09()
        self.i = 1 # For Testing

    def run(self):
        while run:
            i2c_lock.acquire()   # lock i2c-communication
            self.sensor_1.getDistance()
            i2c_lock.release()   # unlock i2c-communication
            measprotocol.do_protocol("URM09","0."+str(self.i),self.sensor_1.distance,0x00,0,0) # For Testing
            self.i = self.i + 1 # For Testing
            if self.sensor_1.distance == -1:   # no sensor connection, create exception for shutdown
                global ultrasonic_exception
                ultrasonic_exception = IOError("[Errno 121] Remote I/O error")   # no connection to i2c device
            time.sleep(0.05)   # 20 Hz cycle

class lidarThread(threading.Thread):
    """ Thread for lidar sensor """

    def __init__(self):
        threading.Thread.__init__(self)
        self.sensor_2 = sensors.TfLuna()
        self.i = 1 # For Testing

    def run(self):
        while run:
            i2c_lock.acquire()   # lock i2c-communication
            self.sensor_2.getDistance()
            i2c_lock.release()   # unlock i2c-communication
            measprotocol.do_protocol("TFLUNA","0."+str(self.i),self.sensor_2.distance,0x00,0,0) # For Testing
            self.i = self.i + 1 # For Testing
            if self.sensor_2.distance == -1:   # no sensor connection, create exception for shutdown
                global lidar_exception
                lidar_exception = IOError("[Errno 121] Remote I/O error")   # no connection to i2c device
            time.sleep(0.02)   # 50 Hz cycle


#################### Interrupt-Handler ####################

# Button 0 Interrupt service routine
GPIO.add_event_detect(
    BUTTON_PIN[0],
    GPIO.BOTH,
    callback = cb_button_time,
    bouncetime = 50
    )

# Button 1 Interrupt service routine
GPIO.add_event_detect(
    BUTTON_PIN[1],
    GPIO.BOTH,
    callback = cb_button_time,
    bouncetime = 50
    )




#################### main program ####################

if __name__ == "__main__":
    try:

        ### Actuator initialisation ###
        my_actuator = actuator.Actuator(ACTUATOR_NO)

        my_actuator.config_drv_to_lra()

        my_actuator.autocalibration(ACTUATOR_TYPE)

        my_actuator.set_drv_open_loop()


        ### Button initialisation ###

        my_button = button.Button()


        ### Switch initialisation ###

        my_switch = switch.Switch()


        ### Sensor initialisation ###

        data = data_procession.DataProcession()
        ultrasonic_thread = ultrasonicThread()
        lidar_thread = lidarThread()
        ultrasonic_thread.start()
        lidar_thread.start()


        ### Loop program ###

        print("Hey ho, let's go!")

        i = 1 # for testing

        while 1:

            value = data.getFeedback(
                        ultrasonic_thread.sensor_1.distance,
                        lidar_thread.sensor_2.distance
                        )

            if ultrasonic_exception:   # throw exception for shutdown
                raise ultrasonic_exception
            if lidar_exception:
                raise lidar_exception

            button_mode[0] = my_button.but_func(0, "distance", my_actuator, button_edge)
            button_mode[1] = my_button.but_func(1, "mute", my_actuator, button_edge)

            erase_button_edges()

            switch_state = my_switch.set_switch_state(SWITCH_PIN)
            my_actuator.set_freq_state(switch_state)


            data.setMode(button_mode[0])
            data.setSensor(switch_state)


            my_actuator.set_actuator(value)

            measprotocol.do_protocol("Main","0."+str(i),value,0x00,0,0) # for testing
            i = i + 1 # for testing

    except KeyboardInterrupt:
        print("Porgram terminated by user!")
        run = False
        ultrasonic_thread.join()
        lidar_thread.join()
        print("Threads stopped!")
        my_actuator.set_vib_const(0)
        GPIO.cleanup()

    except Exception as e:
        print("Program terminated by exception")
        x = datetime.datetime.now()
        a = x.strftime("%Y-%m-%d")
        b = x.strftime("%H:%M:%S:%f")[:-3]
        c = type(e).__name__    # exception name
        d = str(e)   # exception message
        f = open("exception_log.csv", "a")
        f.write("{},{},{},{}".format(a,b,c,d))
        f.write("\n")
        f.close()
        run = False
        ultrasonic_thread.join()
        lidar_thread.join()
        my_actuator.set_vib_const(0)
        GPIO.cleanup()
        print("Done!")
        #os.system("sudo shutdown now")   # shutdown system
        
