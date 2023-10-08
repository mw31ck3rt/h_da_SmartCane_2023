### Information Section ###
# V1.0
# created by Marian Weickert
# on 26.04.2023
# 
# Function to auto-calibrate one LRA -> partialy adapted from Mr. Stanislav Maerz' masterthesis
# Example-code to be used in a (main) thread


### import-section ### --> all libraries needed to run the function

# from smbus2 import SMBus # comment TE: evtl. SMBus2
import time
import math as m

import board
import busio
 
import adafruit_drv2605
import adafruit_tca9548a





def autoCalibrationLRA(LRANo):
    
    # Standard-address of TCA9548a = 0x70
    # Standard-address of DRV2605 = 0x5a
    
    # Initialize I2C bus and TCA9548A module.
    i2c = busio.I2C(board.SCL, board.SDA)
    tca = adafruit_tca9548a.TCA9548A(i2c)
    
    # Initialize DRV2605 module with TCA9548A channel instead of i2c address
    drv = adafruit_drv2605.DRV2605(tca[LRANo])
    
    # Set LRA parameters
    drv.use_LRM()
    
    # set parameters for LRA type LRA08235Q A, manufacturer: Grewus GmbH
    v_rms = 1.8 # rated voltage
    v_peak = 1.9 # maximum operating voltage
    f_lra = 235 # rated frequency
    
    while 1:

        # Set from standby mode to auto-calibration mode
        drv.mode = adafruit_drv2605.MODE_AUTOCAL


        # Set rated voltage register value -> formula see TI document SLOA825E chapter 7.5.2.1 
        sample_time = 300 * pow(10, -6)   # Set Sampling time to 300 μs 
        avg_abs = v_rms * m.sqrt(1 - (4 * sample_time + 300 * pow(10, -6)) * f_lra)   # Formel 1.4.2 (4)
        rated_val = ((avg_abs * 255) / 5.3)   # Formel 1.4.2 (5) 
        drv._write_u8(0x16, int(rated_val))


        # Set overdrive clamp voltage register value -> formula see TI document SLOA825E chapter 7.5.2.2
        overdrive_val = ((v_peak * 255) / 5.6)   # Formel 1.4.2 (6)
        drv._write_u8(0x17, int(overdrive_val))


        # Set required input parameters in Feedback Control Register
        feedback_contrl = 0
        feedback_contrl |= (1 << 7)   # Set LRA Mode to [1]
        feedback_contrl |= (3 << 4)   # Set Ratio of brake gain to drive gain to [3] 
        feedback_contrl |= (2 << 2)   # Set Loop Gain to [2]
        drv._write_u8(0x1A, feedback_contrl)


        # Set drive-time to a half-period of the LRA in Control Register 1; Formeln: TI, DRV2605L Datenblatt
        contrl1_val = 0
        period_lra = 1.0 / f_lra
        drive_time = int((((period_lra * 1000.0 / 2.0) - 0.5) / 0.1))   # Formel 8.5.1.1 & 8.6.21 
        contrl1_val |= (drive_time & 0x1f)
        drv._write_u8(0x1B, contrl1_val)
        


        # Set required input parameters in Control Register 2 
        contrl2_val = 0
        contrl2_val |= (3 << 4)   # Set Sampling time to 300 μs [3]
        contrl2_val |= (1 << 2)   # Set Blanking time to 25 μs [1]
        contrl2_val |= (1 << 0)   # Set Current dissipation time to 25 μs [1]
        drv._write_u8(0x1C, contrl2_val)


        # Set required input parameters in Control Register 4
        contrl4_val = 0
        contrl4_val |= (3 << 4)   # Set auto calibration time from 1000 ms (min) to 1300ms (max) [3]
        drv._write_u8(0x1E, contrl4_val)


        # Set GO bit to start auto-calibration process 
        drv._write_u8(0x0C, 1)


        # Get LRA Resonance-Period Register
        resFreq = drv._read_u8(0x22)
        resFreqCalc = 1 / (resFreq * 98.46 * pow(10, -6)); # Formel 8.6.28
        print("Channel: ", LRANo)
        print("resonant frequency: ", resFreqCalc)

        # Get Status of DIAG_RESULT Bit 
        getStatus = drv._read_u8(0x00)
        time.sleep(0.1)


        # Set Real-Time Playback Mode
        drv.realtime_value = 0
        drv.mode = adafruit_drv2605.MODE_REALTIME
        

        # Check if Auto-calibration is successful and end while-loop
        if (((resFreqCalc <= 230) or (resFreqCalc >= 240)) and ((getStatus & 0x08) == 0x00)):
            break


    if (((getStatus & 0x08) == 0x00) and (getStatus & 0xE0) != 0xE):
        print("Calibration successful")
      
    print("\n")

### Example-code to be used in a (main) thread ###

# autoCalibrationLRA(1)
# autoCalibrationLRA(2)
# autoCalibrationLRA(3)
# 
# print("Function successful")