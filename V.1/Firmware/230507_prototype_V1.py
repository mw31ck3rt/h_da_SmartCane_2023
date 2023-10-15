## import section ##
import busio # needed for MW
import sensors # written by TE
import data_procession # written by TE
import MW_Vibration # written by MW
import MW_DRV_AutoCal_TCA # written by MW
import MW_Button_Time # written by MW
import time
import datetime
import os
import threading
import board # needed for MW

import adafruit_drv2605 # needed for MW
import adafruit_tca9548a # needed for MW
import RPi.GPIO as GPIO # needed for MW

## global variables ##
run = True
# MW vibration
value = 0   # sensor value
lraCh1 = 1   # channel of LRA1 (global)
lraCh2 = 2   # channel of LRA2 (global)
lraCh3 = 3   # channel of LRA3 (global)
Step0 = 10   # Step 0 for the getStage-function (global) --> eliminates minimal messurement failures
Step1 = 200   # Step 1 for the getStage-function (global)
Step2 = 400   # Step 2 for the getStage-function (global)
Step3 = 600   # Step 3 for the getStage-function (global)
Step4 = 800   # Step 4 for the getStage-function (global)
frequ1 = 3   # frequence 1 for setVibInt-function in [Hz] (global)
frequ2 = 4   # frequence 2 for setVibInt-function in [Hz] (global)
frequ3 = 6   # frequence 3 for setVibInt-function in [Hz] (global)
frequ4 = 8   # frequence 4 for setVibInt-function in [Hz] (global)
stage = 0   # return value of getStage-function
stageComp = 100   # auxiliary variable to determin a change of stage-variable
# MW button
butPin1 = 17   # Button for Mute-Mode: pressed = 0, not pressed = 1
butPin2 = 18   # Button for Distance-Mode: pressed = 0, not pressed = 1 
#butEdge1 = [0,0]   # relative time-stamps of rising (butEdge1[0]) and falling (butEdge1[1]) edges of button 1
#butEdge2 = [0,0]   # relative time-stamps of rising (butEdge2[0]) and falling (butEdge2[1]) edges of button 2
but1 = 0   # pressing time of button 1
but2 = 0   # pressing time of button 2
modeMute = 0   # Mode of Mute function: mute (=1) / unmute (=0)
modeDist = 0   # Mode of Distance function: long (=1) / short (=0)
# MW button setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(butPin1,GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Declaration of Button 1 with internal pull up resistor
GPIO.setup(butPin2,GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Declaration of Button 2 with internal pull up resistor

# lock for i2c communication
i2c_lock = threading.Lock()

#Interrupt-Handler
# GPIO.add_event_detect(
#     butPin1,
#     GPIO.BOTH,
#     callback = MW_Button_Time.cbButTime,
#     bouncetime = 50)
# 
# GPIO.add_event_detect(
#     butPin2,
#     GPIO.BOTH,
#     callback = MW_Button_Time.cbButTime,
#     bouncetime = 50)

## class section for threads ##
class ultrasonicThread(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.sensor_1 = sensors.Me007ys()
        
    def run(self):
        while run:
            self.sensor_1.getDistance()
            time.sleep(0.1)

class lidarThread(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.sensor_2 = sensors.TfLuna()
        
    def run(self):
        while run:
            i2c_lock.acquire() #lock i2c-communication
            self.sensor_2.getDistance()
            i2c_lock.release() #unlock i2c-communication
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        MW_DRV_AutoCal_TCA.autoCalibrationLRA(1) # auto calibration
        MW_DRV_AutoCal_TCA.autoCalibrationLRA(2) # auto calibration
        MW_DRV_AutoCal_TCA.autoCalibrationLRA(3) # auto calibration
        data = data_procession.DataProcession()
        ultrasonic_thread = ultrasonicThread()
        lidar_thread = lidarThread()
        ultrasonic_thread.start()
        lidar_thread.start()
        
        while 1:
            value = data.getFeedback(ultrasonic_thread.sensor_1.distance,lidar_thread.sensor_2.distance) # get nominated value for MW
            stage = MW_Vibration.getStage(value, Step0, Step1, Step2, Step3, Step4)
            #print("Sensor value: {} stage value: {}" .format(value, stage))
        
            if (stage == 0 or modeMute == 1) and stage != stageComp:
                MW_Vibration.drv1.stop()
                MW_Vibration.drv2.stop()
                MW_Vibration.drv3.stop()
                
                MW_Vibration.setVibConst(0)
                MW_Vibration.setVibConst(0)
                MW_Vibration.setVibConst(0)
                
                print("stop vibration")
                stageComp = stage
                
            elif stage == 1 and modeMute != 1:
                MW_Vibration.setVibIntv(1, frequ1)
                print("set Vibration to {}Hz" .format(frequ1))
                stageComp = stage
                
            elif stage == 2 and modeMute != 1:
                MW_Vibration.setVibIntv(1, frequ2)
                print("set Vibration to {}Hz" .format(frequ2))
                stageComp = stage
                
            elif stage == 3 and modeMute != 1:
                MW_Vibration.setVibIntv(1, frequ3)
                print("set Vibration to {}Hz" .format(frequ3))
                stageComp = stage
                
            elif stage == 4 and modeMute != 1:
                MW_Vibration.setVibIntv(1, frequ4)
                print("set Vibration to {}Hz" .format(frequ4))
                stageComp = stage
            
            elif stage == 5 and stage != stageComp and modeMute != 1:
                MW_Vibration.setVibConst(127)
                print("set constant vibration")
                stageComp = stage
            
            # Button 1 -> Mute-mode
            but1 = MW_Button_Time.setButSel(MW_Button_Time.butEdge1[0], MW_Button_Time.butEdge1[1], 1)
            
            if but1 == 0:   # value 0 = no button action detected
                pass
            elif but1 == 1:   # short press detected -> return active mode
                if modeMute == 1:    
                    MW_Vibration.setVibIntv(4, 1)
                    print("active mute-mode = {} = muted" .format(modeMute))
                elif modeMute == 0:
                    MW_Vibration.setVibIntv(12, 1)
                    print("active mute-mode = {} = unmuted" .format(modeMute))
                MW_Button_Time.butEdge1 = [0, 0]   # reset of edge-detection
            elif but1 == 2:   # long press detected -> change active mode
                if modeMute == 0:
                    modeMute = 1
                    MW_Vibration.setVibIntv(4, 1)
                    print("mute-mode changed to {} = muted" .format(modeMute))
                elif modeMute == 1:
                    modeMute = 0
                    MW_Vibration.setVibIntv(4, 1)
                    print("mute-mode changed to {} = unmuted" .format(modeMute))
                MW_Button_Time.butEdge1 = [0, 0]   # reset of edge-detection
            
            
            # Button 2 -> Distance-Mode
            but2 = MW_Button_Time.setButSel(MW_Button_Time.butEdge2[0], MW_Button_Time.butEdge2[1], 1)
            
            if but2 == 0:   # value 0 = no button action detected
                pass
            elif but2 == 1:   # short press detected -> return active mode
                if modeDist == 1:    
                    MW_Vibration.setVibIntv(4, 1)
                    print("active distance-mode = {} = long distance" .format(modeDist))
                elif modeMute == 0:
                    MW_Vibration.setVibIntv(12, 1)
                    print("active distance-mode = {} = short distance" .format(modeDist))
                MW_Button_Time.butEdge2 = [0, 0]   # reset of edge-detection
            elif but2 == 2:   # long press detected -> change active mode
                if modeDist == 0:
                    modeDist = 1
                    data.setMode()
                    MW_Vibration.setVibIntv(4, 1)
                    print("distance-mode changed to {} = long distance" .format(modeDist))
                elif modeDist == 1:
                    modeDist = 0
                    data.setMode()
                    MW_Vibration.setVibIntv(4, 1)
                    print("distance-mode changed to {} = short distance" .format(modeDist))
                MW_Button_Time.butEdge2 = [0, 0]   # reset of edge-detection

                    
            
    except KeyboardInterrupt:
        print("Porgram terminated by user")
        run = False
        ultrasonic_thread.join()
        lidar_thread.join()
        MW_Vibration.setVibConst(0)
        MW_Vibration.setVibConst(0)
        MW_Vibration.setVibConst(0)
        print("Done!")
        #os.system("sudo shutdown -h now")
    except Exception as e:
        print("Program terminated by exception")
        x = datetime.datetime.now()
        a = x.strftime("%Y-%m-%d")
        b = x.strftime("%H:%M:%S:%f")[:-3]
        c = type(e).__name__ #exception name
        d = str(e) #exception message
        f = open("exception_log.csv", "a")
        f.write("{},{},{},{}".format(a,b,c,d))
        f.write("\n")
        f.close()
        run = False
        ultrasonic_thread.join()
        lidar_thread.join()
        MW_Vibration.setVibConst(0)
        MW_Vibration.setVibConst(0)
        MW_Vibration.setVibConst(0)
        print("Done!")
        #os.system("sudo shutdown -h now") #restart system
            
