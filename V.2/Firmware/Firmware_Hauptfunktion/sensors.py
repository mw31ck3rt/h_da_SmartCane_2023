### import section ###
import serial
import time
from smbus import SMBus

class Me007ys:
    # variables
    distance = 9999
    # constants
    DISTANCE_MIN = 280
    DISTANCE_MAX = 4500
    
    def __init__(self,port="/dev/serial0",baudrate=9600):
        #serial interface
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=0)   # real UART, baud rate = 9600
    
    
    def getDistance(self):
        if self.ser.isOpen() == False:
            self.ser.open()   # open serial port if not open
        while True:
            counter = self.ser.in_waiting   # count the number of bytes of the serial port
            if counter > 3:
                bytes_serial = self.ser.read(4)   # read 9 bytes
                self.ser.reset_input_buffer()   # reset buffer 
                if bytes_serial[0] == 0xFF:   # check header
                    distance = bytes_serial[2] + (bytes_serial[1]*256)   # distance in next two bytes
                    checksum = (bytes_serial[0] + bytes_serial[1] + bytes_serial[2]) & 0x00FF   # calculation checksum
                    #if checksum == bytes_serial[3]:
                        #print("test: ", distance)
                    if checksum != bytes_serial[3]:
                        #checksum error
                        #print("checksum error")
                        continue # remeasurement
                    if distance > self.DISTANCE_MAX:   # measured value is outside the measuring range
                        distance = self.DISTANCE_MAX
                    if distance < self.DISTANCE_MIN:   # measured values smaller than DISTANCE_MIN are incorrect measurements
                        distance = self.DISTANCE_MAX
                        #continue #remeasurement
                    if distance == self.DISTANCE_MIN:   # measured value is outside the measuring range
                        distance = 0
                    self.distance = distance
                    break   # successfull measurement, break loop
        self.ser.close()   # close serial port


class TfLuna:
    # variables
    distance = 9999
    # constants
    DISTANCE_MIN = 200
    DISTANCE_MAX = 8000
    # register
    TFL_SET_MODE  = 0x23  # W/R -- 0-continuous, 1-trigger
    TFL_TRIGGER   = 0x24  # W  --  1-trigger once
    
    def __init__(self, I2CAddr=0x10, I2CPort=1):
        self.I2CAddr = I2CAddr   # Device address in Hex, Decimal 16
        self.I2CPort = I2CPort   #I2C(1), /dev/i2c-1, pins 3/5
        self.bus = SMBus(I2CPort) #create new bus object for communication
        try:
            self.bus.open(self.I2CPort) #open a given i2c bus
            self.bus.write_quick(self.I2CAddr) #peform quick transaction, throws IOError if unsuccesfull
            # Set device to single-shot/trigger mode
            self.bus.write_byte_data(self.I2CAddr, self.TFL_SET_MODE, 1) #write a byte to a given register (addr,register,value)
            # Set device to continous mode
            #bus.write_byte_data(tflAddr, TFL_SET_MODE, 0) #write a byte to a given register (addr,register,value)
        except IOError:
            print("Verbindung fehlgeschlagen")
        self.bus.close()
    
    def getDistance(self):

        try:
            self.bus.open(self.I2CPort) #open a given i2c bus
            # Trigger a one-shot data sample
            self.bus.write_byte_data(self.I2CAddr, self.TFL_TRIGGER, 1)
            #time.sleep(0.1) #wait for 100 ms after write operation (note in datasheet)
            #  Read the first six registers
            frame = self.bus.read_i2c_block_data(self.I2CAddr, 0, 6) #read a block of byte data from a given register (addr,start register,length)
            distance = (frame[ 0] + ( frame[ 1] << 8))*10
            strength = frame[ 2] + ( frame[ 3] << 8)
            if distance < self.DISTANCE_MIN: #measured value below measuring range
                distance = 0
            if strength < 100: #measured value is unreliable if signal strength < 100
                distance = self.DISTANCE_MAX
            self.distance = distance 
            self.bus.close()
        except:
            self.distance = -1


class URM09:
    # variables
    distance = 9999
    # constants
    DISTANCE_MIN = 20
    DISTANCE_MAX = 5000
    # register
    DEVICE_ADDRESS = 0x00 # default value is 0x11
    DISTANCE_VALUE_H = 0x03 # distance value high-order bits
    DISTANCE_VALUE_L = 0x04 # distance value low-order bits
    MODE = 0x07 # 0x20 -> passive mode + maximum range = 5000 mm (highest sensitivity)
    COMMAND = 0x08

    def __init__(self, I2CAddr=0x11, I2CPort=1):
        self.I2CAddr = I2CAddr   # Device address in Hex, Decimal 16
        self.I2CPort = I2CPort   #I2C(1), /dev/i2c-1, pins 3/5
        self.bus = SMBus(I2CPort) #create new bus object for communication
        
        try:
            self.bus.open(self.I2CPort) #open a given i2c bus
            self.bus.write_quick(self.I2CAddr) #peform quick transaction, throws IOError if unsuccesfull
            # Set device to trigger mode; set range 0x00 -> 150 cm  0x10 -> 300 cm  0x20 -> 500 cm   
            self.bus.write_byte_data(self.I2CAddr, self.MODE, 0x10) #write a byte to a given register (addr,register,value)
        except IOError:
            print("Verbindung fehlgeschlagen")

        self.bus.close()
        
     

    def getDistance(self):

        try:
            self.bus.open(self.I2CPort) #open a given i2c bus
            # Trigger a one-shot data sample
            self.bus.write_byte_data(self.I2CAddr, self.COMMAND, 0x01)
            #  Read register for distance value
            frame = self.bus.read_i2c_block_data(self.I2CAddr, self.DISTANCE_VALUE_H, 2) #read a block of byte data from a given register (addr,start register,length)
            #print("Frame 0:",frame[0])
            #print("Frame 1:",frame[1])
            distance = (frame[ 0] + frame[ 1])*10
            if distance < self.DISTANCE_MIN: #measured value below measuring range
                distance = 0
            self.distance = distance
            #print("distance urm09: ",distance) # for testing
            self.bus.close()
        except:
            self.distance = -1

if __name__ == "__main__":
    sensor_1 = URM09()
    sensor_2 = TfLuna()
    i = 1
    while i < 30:
        sensor_1.getDistance()
        sensor_2.getDistance()
        print("Sensor 1: ",sensor_1.distance)
        print("Sensor 2: ",sensor_2.distance)
        i = i+1
        time.sleep(1)
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
