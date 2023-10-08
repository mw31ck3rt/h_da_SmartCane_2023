import serial
import time
import RPi.GPIO as GPIO
import threading
from smbus import SMBus
import RPi.GPIO as GPIO

#pin definitions
speakerPin = 23

# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(speakerPin,GPIO.OUT)

#initialisation
GPIO.output(speakerPin,GPIO.LOW)

class dataProcession():
    distance_us = 0
    distance_li = 0
    run = True

class ultrasonicThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        #serial interface
        ser = serial.Serial("/dev/serial0", 9600,timeout=0) #real UART, baud rate = 9600
        #local variables
        distance = 0
        #constants
        DISTANCE_MAX = 4500
        DISTANCE_MIN = 280
        #read data
        while data_procession.run:
            #ser.reset_input_buffer() # reset buffer
            counter = ser.in_waiting # count the number of bytes of the serial port
            if counter > 3:
                bytes_serial = ser.read(4) # read 9 bytes
                ser.reset_input_buffer() # reset buffer 
                if bytes_serial[0] == 0xFF: # check header
                    distance = bytes_serial[2] + (bytes_serial[1]*256) # distance in next two bytes
                    checksum = (bytes_serial[0] + bytes_serial[1] + bytes_serial[2]) & 0x00FF #calculation checksum
                    if checksum != bytes_serial[3]:
                        #checksum error
                        distance = 0
                        #print("error")
                    if distance > DISTANCE_MAX: # >MAX
                        distance = DISTANCE_MAX
                    if distance < DISTANCE_MIN: # <MIN
                        distance = DISTANCE_MIN
                    lockWriting.acquire()
                    data_procession.distance_us = distance
                    #print("Ultrasonic:", data_procession.distance)
                    lockWriting.release()
                    #ser.close() # close serial port
                    time.sleep(0.05)
        ser.close()
        print("Ultrasonic gestoppt!")

class lidarThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        I2CAddr = 0x10   # Device address in Hex, Decimal 16
        I2CPort = 1       #I2C(1), /dev/i2c-1, pins 3/5

        #register
        TFL_SET_MODE  = 0x23  # W/R -- 0-continuous, 1-trigger
        TFL_TRIGGER   = 0x24  # W  --  1-trigger once

        bus = SMBus(I2CPort) #create new object
        bus.open(I2CPort) #open a given i2c bus

        try: 
            bus.write_quick(I2CAddr) #peform quick transaction, throws IOError if unsuccesfull
        except IOError:
            print("Verbindung fehlgeschlagen")
        while data_procession.run:
            # Set device to single-shot/trigger mode
            bus.write_byte_data(I2CAddr, TFL_SET_MODE, 1) #write a byte to a given register (addr,register,value)
            # Set device to continous mode
            #bus.write_byte_data(tflAddr, TFL_SET_MODE, 0) #write a byte to a given register (addr,register,value)

            # Trigger a one-shot data sample
            bus.write_byte_data(I2CAddr, TFL_TRIGGER, 1)
            #time.sleep(0.1) #wait for 100 ms after write operation (note in datasheet)
            #  Read the first six registers
            frame = bus.read_i2c_block_data(I2CAddr, 0, 6) #read a block of byte data from a given register (addr,start register,length)


            #bus.close() #close i2c connection
            lockWriting.acquire()
            data_procession.distance_li = (frame[ 0] + ( frame[ 1] << 8))*10
            #print("Lidar: ", data_procession.distance)
            lockWriting.release()
            time.sleep(0.05)
        
        bus.close()
        print("Lidar gestoppt!")
        

lockWriting = threading.Lock()

data_procession = dataProcession()

ultrasonic_thread = ultrasonicThread()
lidar_thread = lidarThread()
ultrasonic_thread.start()
lidar_thread.start()

try:
    while True:
        if data_procession.distance_us < 1000 or data_procession.distance_li < 1000:
            #print("YES")
            GPIO.output(speakerPin,GPIO.HIGH)
            time.sleep(0.05)
        else:
            GPIO.output(speakerPin,GPIO.LOW)
            time.sleep(0.05)
except KeyboardInterrupt:
    data_procession.run = False
    GPIO.cleanup()
    print("Programm von User gestoppt!")

ultrasonic_thread.join()
lidar_thread.join()

print("Fertig!")
