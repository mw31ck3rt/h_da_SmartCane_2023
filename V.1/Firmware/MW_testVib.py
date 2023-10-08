### Information Section ###
# V1.1
# created by Marian Weickert
# on 20.05.2023
#
# Functions for testing user feedback

import board
import busio
import adafruit_drv2605
import adafruit_tca9548a
import RPi.GPIO as GPIO

typeIn = 0
drv = [0, 0, 0]
butPin = 17   # Button for user-feedback: pressed = 0, not pressed = 1


# callback-function for detecting user-feedback
def cbUserFB(pin):   # Callback Function for detecting user feedback
    test.setAct("2")
    print("\nChoose Action (help: h): ")

class testVib:

    ### import-section ###

    import random
    import time
    import csv
    import MW_DRV_AutoCal_TCA

    GPIO.setmode(GPIO.BCM)
    
    lraCh = [1, 2, 3]

    ### class-specific variables ###

    def __init__(self):
        self.actOn = [0,0,0]
        self.valRealTime = 0
        self.timeOn = 0
        self.timeOff = 0
        self.timeAbs = 0
        self.logfile = '230519_Logfile.csv'
        self.logdata = [0, 0, 0, 0, 0, 0, 0]
        self.index = 1

    GPIO.setup(butPin,GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Declaration of Button 1 with internal pull up resistor
    
    

    # calibration of LRAs

    MW_DRV_AutoCal_TCA.autoCalibrationLRA(1) # auto calibration
    MW_DRV_AutoCal_TCA.autoCalibrationLRA(2) # auto calibration
    MW_DRV_AutoCal_TCA.autoCalibrationLRA(3) # auto calibration


    ### functions-section ###
    
    # function: initialize LRAs
    def initLRA(self, LRANo):

        # Initialize I2C bus and TCA9548A Multiplexer-module.
        i2c = busio.I2C(board.SCL, board.SDA)
        tca = adafruit_tca9548a.TCA9548A(i2c)
        
        drv[LRANo] = adafruit_drv2605.DRV2605(tca[LRANo + 1])

        # set LRM mode
        drv[LRANo].use_LRM()

        # reset realtime-value to 0 -> prevention of unintended vibration
        drv[LRANo].realtime_value = 0 

        # set drv-mode to realtime
        drv[LRANo].mode = adafruit_drv2605.MODE_REALTIME

    # function: get User-Input
    def getChar(self):
        inC = input("\nChoose Action (help: h): ")
        return inC

    # function: write to csv-file
    def writeCsv(self, log, data = [0,0,0,0,0,0,0]):
        with open(log, 'a', newline='') as f:
            writer = self.csv.writer(f)
            writer.writerow(data)


    # function: set action in dependence of chosen char
    def setAct(self, char):

        if char == "1":   # start vibration (actuator- and intensity-selection is random)

            # set random vibration-intensity
            self.valRealTime = self.random.randint(1,127)

            # set parameters for 3 LRAs
            while (self.actOn[0] + self.actOn[1] + self.actOn[2])  == 0:  # prevention of random output [0, 0, 0]
                for i in range(3):

                    # random LRA-selection
                    self.actOn[i] = self.random.randint(0,1)

            # set vibration-intensity if LRA is selected
            for i in range(len(self.lraCh)):

                # random LRA activation -> 1 = active, 0 = inactive
                self.actOn[i] = self.random.randint(0,1)

                # set vibration intensity if LRA is selected
                if self.actOn[i] == 1:
                    drv[i].realtime_value = self.valRealTime
#                     print("Aktor {} aktiv" .format(i+1))
                else:
                    drv[i].realtime_value = 0
#                     print("Aktor {} inaktiv" .format(i+1))
                

            # safe starting-timestamp (relative)
            self.timeOn = self.time.monotonic()

            # printing chosen values
            print("\n\nStart vibration (random values")
            print("LRA1: {}, LRA2: {}, LRA3: {}, Intensity: {}" .format(self.actOn[0], self.actOn[1], self.actOn[2], self.valRealTime))
            
            # reset variable
            char = 0

        elif char == "2":   # stop vibration and write data to logfile
            
            # get ending-timestamp (relative) and calculate absolute reaction-time
            self.timeOff = self.time.monotonic()
            self.timeAbs = (self.timeOff - self.timeOn)

            # set vibration-intensity to 0
            for i in range(len(self.lraCh)):
                drv[i].realtime_value = 0

            # print data
            print("\n\nStop vibration")
            print("Reaction time: {}" .format(self.timeAbs))

            # write data to logfile
            self.logdata = [self.index, self.actOn[0], self.actOn[1], self.actOn[2], self.valRealTime, self.timeAbs, 0]
#             print(self.logdata)
            self.writeCsv(self.logfile, self.logdata)
            print("Data written to logfile: {}" .format(self.logfile))

            # reset variables
            self.timeOn = 0
            self.timeOff = 0
            self.timeAbs = 0
            self.logdata = [0, 0, 0, 0, 0, 0, 0]
            self.index = self.index + 1
            # print(self.index)
            
        elif char == "3":   # user-feedback: vibration perceived, right allocation
            print("vibration perceived, right allocation")
            self.writeCsv(self.logfile,[(self.index - 1), 0, 0, 0, 0, 0, "vibration perceived; right allocation"])

        elif char == "4":   # user-feedback: vibration perceived, wrong allocation
            print("vibration perceived, wrong allocation")
            self.writeCsv(self.logfile,[(self.index - 1), 0, 0, 0, 0, 0, "vibration perceived; wrong allocation"])

        elif char == "5":   # user-feedback: no perception
            print("no perception")
            self.writeCsv(self.logfile,[(self.index - 1), 0, 0, 0, 0, 0, "no perception"])

        elif char == "6":   # start vibration (actuator- and intensity-selection is explicit)

            # set LRAs active / inactive (explicit)
            self.actCh = input("\nChoose LRAs (format: xxx): ")   # input in format: 000, 110, 101... -> 1 = LRA active, 2 = LRA inactive

            # set vibration intensity (explicit)
            self.valRealTime = input("\nChoose intensity (value: 0...127): ")
            print("")

            if int(self.valRealTime) > 127:
                self.valRealTime = 127

            # set vibration-intensity if LRA is selected
            for i in range(len(self.lraCh)):
                if self.actCh[i] == "1":
                    self.actOn[i] = 1
                    drv[i].realtime_value = int(self.valRealTime)
#                     print("Aktor {} aktiv" .format(i+1))
                else:
                    self.actOn[i] = 0
                    drv[i].realtime_value = 0
#                     print("Aktor {} inaktiv" .format(i+1))
                
            # get starting-timestamp (relative)
            self.timeOn = self.time.monotonic()

            # printing chosen values
            print("\nStart vibration (explicit values)")
            print("LRA1: {}, LRA2: {}, LRA3: {}, Intensity: {}" .format(self.actOn[0], self.actOn[1], self.actOn[2], self.valRealTime))
            
            # reset variable
            char = 0

        elif char == "h":   # show help
            self.helpIns()

        elif char == "0":   # no character chosen
            pass
        else:   # invalid input
            print("Invalid input - please retry")

    def helpIns(self):
            print("\n \t 0 = no action (default)")
            print("\t 1 = Starte Vibration (Aktuatoren und Intensitaet zufaellig)")
            print("\t 2 = Stoppe Vibration")
            print("\t 3 = User-Feedback: Wahrnehmung vorhanden, Zuordnung richtig")
            print("\t 4 = User-Feedback: Wahrnehmung vorhanden, Zuordnung falsch")
            print("\t 5 = Keine Wahrnehmung")
            print("\t 6 = Starte Vibration (Aktuatoren und Intensitaet explizit)")
            print("\t h = help\n")
            print("\t all other inputs are invalid \n")
            
### Interrupt-Handler ###

GPIO.add_event_detect(
    butPin,
    GPIO.FALLING,
    callback = cbUserFB,
    bouncetime = 200)
    
### main Code ###

if __name__ == "__main__":

    test = testVib()
    
    for i in range(len(drv)):
        test.initLRA(i)

    try:
        while 1:

#             if typeIn != "0":
            typeIn = test.getChar()

            test.setAct(typeIn)

    except KeyboardInterrupt:
        for i in range(len(drv)):
                drv[i].realtime_value = 0
        print("\n\nProgram aborted by user")
