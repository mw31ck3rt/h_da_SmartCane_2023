### Information Section ###
# V1.0
# created by Marian Weickert
# on 26.04.2023
# 
# Functions for setting a vibration to 3 LRAs
# 
# Function getStage(sensVal, S0, S1, S2, S3, S4,): returns a integer-value between 0 and 5 (S0...S4)
#     in dependence of a floating value (sensVal) (between internal variables minVal and maxVal)
# Function setVibConst(val): sets a constant vibration to three LRAs. Intensity of vibration can be chosen in range 0...127
# Function setVibIntv(eff, frq): sets one vibration effect to three LRAs. Frequence of effect repeating (time.sleep) can be chosen


### import section ### --> all libraries needed to run the function

# import threading
import time
# 
import board
import busio
# 
import adafruit_drv2605
import adafruit_tca9548a
# 
# 
# import RPi.GPIO as GPIO   # just needed for testing


### Test program variables ###
 
# value = 205   # test value --> sensor value
lraCh1 = 1   # channel of LRA1 (global)
lraCh2 = 2   # channel of LRA2 (global)
lraCh3 = 3   # channel of LRA3 (global)
# Step0 = 10   # Step 0 for the getStage-function (global) --> eliminates minimal messurement failures
# Step1 = 200   # Step 1 for the getStage-function (global)
# Step2 = 400   # Step 2 for the getStage-function (global)
# Step3 = 600   # Step 3 for the getStage-function (global)
# Step4 = 800   # Step 4 for the getStage-function (global)
# frequ1 = 3   # frequence 1 for setVibInt-function in [Hz] (global)
# frequ2 = 4   # frequence 2 for setVibInt-function in [Hz] (global)
# frequ3 = 6   # frequence 3 for setVibInt-function in [Hz] (global)
# frequ4 = 8   # frequence 4 for setVibInt-function in [Hz] (global)
# stage = 0   # return value of getStage-function
# stageComp = 100   # auxiliary variable to determin a change of stage-variable

# Initialize I2C bus and TCA9548A Multiplexer-module.
i2c = busio.I2C(board.SCL, board.SDA)
tca = adafruit_tca9548a.TCA9548A(i2c)


# DRV configuration

drv1 = adafruit_drv2605.DRV2605(tca[lraCh1])
drv2 = adafruit_drv2605.DRV2605(tca[lraCh2])
drv3 = adafruit_drv2605.DRV2605(tca[lraCh3])

drv1.use_LRM()
drv2.use_LRM()
drv3.use_LRM()


### Function section ###


def getStage(sensVal, S0, S1, S2, S3, S4,):   # calculate Stage of Vibration dependt on sensor value (senVal)
    minVal = 0   # minimum value of sensVal
    maxVal = 1000   # maximum value of sensVal
       
    if sensVal >= minVal and sensVal < S0:   # setting stage 0 (no detection including elimination of minimal messurements)
        return 0
    elif sensVal >= S0 and sensVal < S1:   # setting stage 1
        return 1
    elif sensVal >= S1 and sensVal < S2:   # setting stage 2
        return 2
    elif sensVal >= S2 and sensVal < S3:   # setting stage 3
        return 3
    elif sensVal >= S3 and sensVal < S4:   # setting stage 4
        return 4
    elif sensVal >= S4 and sensVal <= maxVal:   # setting stage 5
        return 5



def setVibConst(val): # set constant vibration to 3 actuators -> val-Range from 0...127
    
    # reset value to 0 -> prevention of unintended vibration
    drv1.realtime_value = 0
    drv2.realtime_value = 0
    drv3.realtime_value = 0
    
    # set drv-mode to realtime
    drv1.mode = adafruit_drv2605.MODE_REALTIME
    drv2.mode = adafruit_drv2605.MODE_REALTIME
    drv3.mode = adafruit_drv2605.MODE_REALTIME
    
    # set intensity to delivered value
    drv1.realtime_value = val
    drv2.realtime_value = val
    drv3.realtime_value = val



def setVibIntv(eff, frq): # set interval vibration for 3 actuators
    
    # set delivered effect to sequence 0
    drv1.sequence[0] = adafruit_drv2605.Effect(eff)
    drv2.sequence[0] = adafruit_drv2605.Effect(eff)
    drv3.sequence[0] = adafruit_drv2605.Effect(eff)
    
    # set drv-mode to inttrig
    drv1.mode = adafruit_drv2605.MODE_INTTRIG
    drv2.mode = adafruit_drv2605.MODE_INTTRIG
    drv3.mode = adafruit_drv2605.MODE_INTTRIG
    
    # play sequences
    drv1.play()
    drv2.play()
    drv3.play()
    
    # set sleeping time to reciprocal delivered value
    time.sleep(1/frq)
    


### Test program ###

# # Test 1
# stage = getStage(value, Step0, Step1, Step2, Step3, Step4)
# print("Sensor value: {} stage value: {}" .format(value, stage))


# # Test 2
# while 1:
#     stage = getStage(value, Step0, Step1, Step2, Step3, Step4)
#     # print("Sensor value: {} stage value: {}" .format(value, stage))
#         
#     if stage == 0:
#         drv1.stop()
#         drv2.stop()
#         drv3.stop()
#         print("stop vibration")
#         stageComp = stage
#         
#     elif stage == 1:
#         setVibIntv(1, frequ1)
#         print("set Vibration to {}Hz" .format(frequ1))
#         stageComp = stage
#         
#     elif stage == 2:
#         setVibIntv(1, frequ2)
#         print("set Vibration to {}Hz" .format(frequ2))
#         stageComp = stage
#         
#     elif stage == 3:
#         setVibIntv(1, frequ3)
#         print("set Vibration to {}Hz" .format(frequ3))
#         stageComp = stage
#         
#     elif stage == 4:
#         setVibIntv(1, frequ4)
#         print("set Vibration to {}Hz" .format(frequ4))
#         stageComp = stage
#     
#     elif stage == 5 and stage != stageComp:
#         setVibConst(127)
#         print("set constant vibration")
#         stageComp = stage
            
