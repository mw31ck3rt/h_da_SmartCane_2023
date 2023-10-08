### Information Section ###
# V1.0
# created by Marian Weickert
# on 26.04.2023
#
# Functions for button use:
# 
# 1. Interrupt-function to detect rising and fallin edges of two buttons including relative time-stamps (callback function = cbButTime)
# 2. Function to calculate if a button was pressed longer or shorter than a defined pressing-time (setButSel)
# 3. Example-Code for using the function in a (main) thread
# created on 04.05.2023 by Marian Weickert


### import section ### --> all libraries needed to run the function
import RPi.GPIO as GPIO
import time


### Test program variables ###

GPIO.setmode(GPIO.BCM)

butPin1 = 17   # Button for Mute-Mode: pressed = 0, not pressed = 1
butPin2 = 18   # Button for Distance-Mode: pressed = 0, not pressed = 1 
butEdge1 = [0,0]   # relative time-stamps of rising (butEdge1[0]) and falling (butEdge1[1]) edges of button 1
butEdge2 = [0,0]   # relative time-stamps of rising (butEdge2[0]) and falling (butEdge2[1]) edges of button 2
but1 = 0   # pressing time of button 1
but2 = 0   # pressing time of button 2
modeMute = 0   # Mode of Mute function: mute (=1) / unmute (=0)
modeDist = 0   # Mode of Distance function: long (=1) / short (=0)

GPIO.setup(butPin1,GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Declaration of Button 1 with internal pull up resistor
GPIO.setup(butPin2,GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Declaration of Button 2 with internal pull up resistor


def cbButTime(pin):   # Callback Function for detecting the time of a pressed button
    global butEdge1
    global butEdge2
    global butPin1
    global butPin2
    
    if pin == butPin1:
        if GPIO.input(pin):
            butEdge1[1] = time.monotonic()
            #print("Timestamp rising edge Button 1: ", butEdge1[1]
        else:
            butEdge1[0] = time.monotonic()
            #print("Timestamp falling edge Button 1: ", butEdge1[0])
    elif pin == butPin2:
        if GPIO.input(pin):
            butEdge2[1] = time.monotonic()
            #print("Timestamp rising edge Button 2: ", butEdge2[1]
        else:
            butEdge2[0] = time.monotonic()
            #print("Timestamp falling edge Button 2: ", butEdge2[0])

#Interrupt-Handler
GPIO.add_event_detect(
    butPin1,
    GPIO.BOTH,
    callback = cbButTime,
    bouncetime = 50)

GPIO.add_event_detect(
    butPin2,
    GPIO.BOTH,
    callback = cbButTime,
    bouncetime = 50)


# Calculating period of Time of 2 timestamps and return value depending on time button was pressed
def setButSel(T1, T2, swT):
    
    # Calculate period of time button is pressed (Tbp)
    if T1 > 0 and T2 > 0:
        Tbp = abs(T1 - T2)
        T1 = 0
        T2 = 0
    else:
        Tbp = 0
    
    # set return-value depending on value of Tbp
    if Tbp == 0:   # when TbP is resettet (=0), return value is 0
        return 0
    elif Tbp < swT and Tbp != 0:   # when TbP is lower than switch-Time (swT), return value is 1 (Short press)
        return 1
    elif Tbp > swT:   # when TbP is higher than switch-Time (swT), return value is 2 (Long press)
        return 2    




### Example-Code to be used in main-Thread ###

# try:
#     
#     print("Choose your button")   # Indication for running program at the shell
#     
#     while 1:
#         
#         # Button 1 -> Mute-mode
#         but1 = setButSel(butEdge1[0], butEdge1[1], 1)
#         
#         if but1 == 0:   # value 0 = no button action detected
#             pass
#         elif but1 == 1:   # short press detected -> return active mode
#             if modeMute == 1:    
# #                 setVibIntv(4, 1)
#                 print("active mute-mode = {} = muted" .format(modeMute))
#             elif modeMute == 0:
# #                 setVibIntv(12, 1)
#                 print("active mute-mode = {} = unmuted" .format(modeMute))
#             butEdge1 = [0, 0]   # reset of edge-detection
#         elif but1 == 2:   # long press detected -> change active mode
#             if modeMute == 0:
#                 modeMute = 1
# #                 setVibIntv(4, 1)
#                 print("mute-mode changed to {} = muted" .format(modeMute))
#             elif modeMute == 1:
#                 modeMute = 0
# #                 setVibIntv(4, 1)
#                 print("mute-mode changed to {} = unmuted" .format(modeMute))
#             butEdge1 = [0, 0]   # reset of edge-detection
#         
#         
#         # Button 2 -> Distance-Mode
#         but2 = setButSel(butEdge2[0], butEdge2[1], 1)
#         
#         if but2 == 0:   # value 0 = no button action detected
#             pass
#         elif but2 == 1:   # short press detected -> return active mode
#             if modeDist == 1:    
# #                 setVibIntv(4, 1)
#                 print("active distance-mode = {} = long distance" .format(modeDist))
#             elif modeMute == 0:
# #                 setVibIntv(12, 1)
#                 print("active distance-mode = {} = short distance" .format(modeDist))
#             butEdge2 = [0, 0]   # reset of edge-detection
#         elif but2 == 2:   # long press detected -> change active mode
#             if modeDist == 0:
#                 modeDist = 1
# #                 setVibIntv(4, 1)
#                 print("distance-mode changed to {} = long distance" .format(modeDist))
#             elif modeDist == 1:
#                 modeDist = 0
# #                 setVibIntv(4, 1)
#                 print("distance-mode changed to {} = short distance" .format(modeDist))
#             butEdge2 = [0, 0]   # reset of edge-detection
# 
#         
#         
# 
# except KeyboardInterrupt:
#     GPIO.cleanup()
