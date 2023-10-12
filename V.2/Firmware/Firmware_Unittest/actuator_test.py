"""V2.2.1
Module for actuators used in Masterthesis SmartCane V.2
Function set_vib_const was specialy modified for unit-test \
-> activation of single actuator is necessary (instead of all)
h_da FBEIT, Prof. Dr. Carsten Zahout-Heil
created by Marian Weickert
on 25.08.2023
"""


# #################### Import section ####################

import time

import board
import busio

import adafruit_drv2605
import adafruit_tca9548a


# #################### Variables ####################

# act_no = [0, 1]   # channel of Actuators (global)


# #################### Test Variables ####################

# val = [208, 404]   # test value list --> sensor values



class Actuator:
    """ class for controlling DRV2605L actuator drivers via TCA9548A multiplexer """

    #################### Class-specific Variables ####################

    def __init__(self, act_no):

        self.act_no = act_no   # list of actuators
        self.drv = [None, None]   # list of drv-objects
        self.stage = 0   # return value of get_stage-function
        self.stage_comp = 100   # aux-variable to determin change of stage-variable (set_actuator)
        self.state_comp = 100   # aux-variable to determin change of state-variable (set_freq_state)
        self.mute = 1   # value of mute selection. 1 = umute, 0 = mute

    # Initialize I2C bus and TCA9548A Multiplexer-module.
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.tca = adafruit_tca9548a.TCA9548A(self.i2c)


    #################### Function Section ####################

    ### Initialization Functions ###

    def config_drv_to_lra(self):
        """ create class of drv2605 and set to LRA-mode """

        for k in self.act_no:
            self.drv[k] = adafruit_drv2605.DRV2605(self.tca[self.act_no[k]])
            self.drv[k].use_LRM()


    def autocalibration(self, act_type):
        """Auto-Calibration for all actuators (depending on act_no) 
        Source: TI Documentation SLOS854D 7.5.6 (p.27) 
        -> every reference in this function is related to this document
        """

        for j in self.act_no:
            # I2C Standard-address of TCA9548a = 0x70
            # I2C Standard-address of DRV2605 = 0x5a

            # Initialize variables
            cal_error = 0 # number of missed calibration cycles

            # set parameter-set for Exciters type EXS 2608L-03A or EXS 241408W B (Grewus GmbH)

            if act_type[j] == 2608:  # technical data for EXS 2608L-03A
                val_rated = 0b01011000 # = 0d88 -> calc of Equation 5 (8.5.2.1) (8 bits)
                val_clamp = 0b01100011 # = 0d99 -> calc of Equation 7 (9) (8.5.2.2(1)) (8 bits)
                time_drive = 0b00011111 # = 0d31 -> calc with Table 24 (8.6.21) (5 bits) \
                    #  -> max (calc-val = 37)

            elif act_type[j] == 2414:  # technical data for EXS 241408W B
                val_rated = 0b01110101 # = 117 -> calc of Equation 5 (8.5.2.1) (8 bits)
                val_clamp = 0b10001001 # = 141 -> calc of Equation 7 (9) (8.5.2.2(1)) (8 bits)
                time_drive = 0b00010111 # = 23 -> calc with Table 24 (8.6.21) (5 bits)

            else:
                print("unknown Actuator number. Auto-calibration aborted")
                act_type = 0

            while act_type != 0:

                # 1. Apply the supply voltage to the DRV2605 device, and pull the EN pin high \
                    # -> should be done at this point :)

                # 2. Write a value of 0x07 to register 0x01. This value moves the DRV2605 \
                    # device out of STANDBY and places the MODE[2:0] bits in auto-calibration mode.
                self.drv[j]._write_u8(0x01, 0x07)
                # print("Value of 0x01 (should be 7) = ", drv._read_u8(0x01))

                # 3. Populate the input parameters required by the auto-calibration engine

                # a. set N_ERM_LRA to 1 -> LRA
                self.drv[j]._write_u8(0x1A, self.drv[j]._read_u8(0x1A) | 0b10000000)
                # print("Value of 0x1A[7] (should be 128) = ", drv._read_u8(0x1A) & 0b10000000)

                # b. set FB_BRAKE_FACTOR to 2 -> recommendation TI
                self.drv[j]._write_u8(0x1A, self.drv[j]._read_u8(0x1A) & 0b10001111)  # clear bits
                self.drv[j]._write_u8(0x1A, self.drv[j]._read_u8(0x1A) | 0b00100000)
                # print("Value of 0x1A[6:4] (should be 32) = ", drv._read_u8(0x1A) & 0b01110000)

                # c. set LOOP_GAIN to 2 -> recommendation TI
                self.drv[j]._write_u8(0x1A, self.drv[j]._read_u8(0x1A) & 0b11110011)  # clear bits
                self.drv[j]._write_u8(0x1A, self.drv[j]._read_u8(0x1A) | 0b00001000)
                # print("Value of 0x1A[3:2] (should be 8) = ", drv._read_u8(0x1A) & 0b00001100)

                # d. set RATED_VOLTAGE to calculated value
                self.drv[j]._write_u8(0x16, val_rated)
                # print("Value of 0x16 (should be 87 or 117) = ", drv._read_u8(0x16))

                # e. set OD_CLAMP to calculated value
                self.drv[j]._write_u8(0x17, val_clamp)
                # print("Value of 0x17 (should be 96 or 137) = ", drv._read_u8(0x17))

                # f. set AUTO_CAL_TIME to 3 -> recommendation TI
                self.drv[j]._write_u8(0x1E, self.drv[j]._read_u8(0x1E) & 0b11001111)  # clear bits
                self.drv[j]._write_u8(0x1E, self.drv[j]._read_u8(0x1E) | 0b00110000)
                # print("Value of 0x1E[5:4] (should be 48) = ", drv._read_u8(0x1E) & 0b00110000)

                # g. set DRIVE_TIME to calculatec value
                self.drv[j]._write_u8(0x1B, self.drv[j]._read_u8(0x1B) & 0b11100000)  # clear bits
                self.drv[j]._write_u8(0x1B, self.drv[j]._read_u8(0x1B) | time_drive)
                # print("Value of 0x1B (should be 14) = ", drv._read_u8(0x1B) & 0b00011111)

                # h. set SAMPLE_TIME to 3 -> recommendation TI
                self.drv[j]._write_u8(0x1C, self.drv[j]._read_u8(0x1C) & 0b11001111)  # clear bits
                self.drv[j]._write_u8(0x1C, self.drv[j]._read_u8(0x1C) | 0b00110000)
                # print("Value of 0x1C[5:4] (should be 48) = ", drv._read_u8(0x1C) & 0b00110000)

                # i. set BLANKING_TIME to 1 -> recommendation TI
                self.drv[j]._write_u8(0x1C, self.drv[j]._read_u8(0x1C) & 0b11110011)  # clear bits
                self.drv[j]._write_u8(0x1C, self.drv[j]._read_u8(0x1C) | 0b00000100)
                # print("Value of 0x1C[3:2] (should be 4) = ", drv._read_u8(0x1C) & 0b00001100)

                # j. set IDISS_TIME to 1 -> recommendation TI
                self.drv[j]._write_u8(0x1C, self.drv[j]._read_u8(0x1C) & 0b11111100)  # clear bits
                self.drv[j]._write_u8(0x1C, self.drv[j]._read_u8(0x1C) | 0b00000001)
                # print("Value of 0x1C[1:0] (should be 1) = ", drv._read_u8(0x1C) & 0b00000011)

                # k. set ZC_DET_TIME[1:0] to 0 -> recommendation TI
                self.drv[j]._write_u8(0x1E, self.drv[j]._read_u8(0x1E) & 0b00111111)  # clear bits
                # print("Value of 0x1E[1:0] (should be 0) = ", drv._read_u8(0x1E) & 0b11000000)

                # 4. Set the GO bit (write 0x01 to register 0x0C) to start \
                    # the auto-calibration process.
                self.drv[j]._write_u8(0x0C, 0x01)
                # print("Calibration started, value of 0x0C (should be 1) = ", drv._read_u8(0x0C))

                # 5. Check the status of the DIAG_RESULT bit (in register 0x00) \
                    #  to ensure that the auto-calibration routine is complete without faults.
                if self.drv[j]._read_u8(0x00) & 0b00001000 == 0x00:

                    # Calculate and print resonant frequency
                    act_period = self.drv[j]._read_u8(0x22) # get value of LRA_PERIOD
                    res_freq = 1 / (act_period * (98.46 * pow(10, -6))) # calc \
                        # resonance frequency [hz]
                    print(f"Calibration of actuator {j} successful.Resonance freq: {res_freq} Hz, Drive time: {self.drv[j]._read_u8(0x1B) & 0b00011111}")

                    break # end while-loop if successfully calibrated

                else:
                    cal_error = cal_error +1
                    if cal_error >= 9:
                        print(f"Calibration of actuator {j} NOT successful, breakup after 10 times")
                        break


    def set_drv_open_loop(self):
        """set all actuators to open-loop mode (depending on act_no)"""

        for i in self.act_no:
            # set N_ERM_LRA to 1
            self.drv[i]._write_u8(0x1A, self.drv[i]._read_u8(0x1A) | 0b10000000)
            # print(f"Actuator {i}: Value of N_ERM_LRA (0x1A[7]) (128) \
                # = {self.drv[i]._read_u8(0x1A) & 0b10000000}")
            # set LRA_OPEN_LOOP to 1
            self.drv[i]._write_u8(0x1D, self.drv[i]._read_u8(0x1D) | 0b00000001)
            # print(f"Actuator {i}: Value of LRA_OPEN_LOOP (0x1D[0]) (1) \
                  # = {self.drv[i]._read_u8(0x1D) & 0b00000001}")
            print(f"Actuator {i} changed to open-loop configuration")


    def set_drv_mute_on(self):
        """set all DRVs to Mute-State"""

        self.mute = 0
        print("Actuators set to State: Mute")


    def set_drv_mute_off(self):
        """set DRV to Unmute-State"""

        self.mute = 1
        print("Actuators set to State: Unmute")



    ## Performance Functions ##

    def get_stage(self, sens_val):
        """calculate Stage of Vibration dependt on sensor value (sens_val)"""

        MIN_VAL = 0   # minimum value of sens_val
        MAX_VAL = 1000   # maximum value of sens_val
        STEP_0 = 10   # upper limit value of Step 0 --> eliminates minimal meassurement failures
        STEP_1 = 200   # upper limit value of Step 1
        STEP_2 = 400   # upper limit value of Step 2
        STEP_3 = 600   # upper limit value of Step 3
        STEP_4 = 800   # upper limit value of Step 4
        stg = 5   # selected stage

        if (MIN_VAL <= sens_val < STEP_0) or self.mute == 0:   # setting stage 0 \
            # (no detection including elimination of minimal messurements)
            stg = 0
        elif STEP_0 <= sens_val < STEP_1:   # setting stage 1
            stg = 1
        elif STEP_1 <= sens_val < STEP_2:   # setting stage 2
            stg = 2
        elif STEP_2 <= sens_val < STEP_3:   # setting stage 3
            stg = 3
        elif STEP_3 <= sens_val < STEP_4:   # setting stage 4
            stg = 4
        elif STEP_4 <= sens_val <= MAX_VAL:   # setting stage 5
            stg = 5
        return stg


    def set_vib_const(self, val, ac):
        """set constant vibration to variable all actuators (depending on act_no) 
            -> val-Range from 0...127
            """

        for i in ac:
            # reset value to 0 -> prevention of unintended vibration
            self.drv[i].realtime_value = 0

            # set drv-mode to realtime
            self.drv[i].mode = adafruit_drv2605.MODE_REALTIME

        for i in ac:
            # set intensity to delivered value
            self.drv[i].realtime_value = val


    def set_vib_intv(self, eff):
        """set interval vibration parameters for all actuators (depending on act_no)"""

        for i in self.act_no:
            # set delivered effect to sequence 0
            self.drv[int(i)].sequence[0] = adafruit_drv2605.Effect(eff)

            # set drv-mode to inttrig
            self.drv[int(i)].mode = adafruit_drv2605.MODE_INTTRIG


    def start_vib_intv(self, frq):
        """start interval vibration with chosen frequency"""

        for i in self.act_no:
            # play sequences
            self.drv[i].play()

        # set sleeping time to reciprocal delivered value
        time.sleep(1/frq)


    def set_drv_freq(self, frq):
        """set 1 frequency to all actuators (depending on act_no)"""

        # calculation of open-loop LRA period, based on equation 2 in chapter 8.3.2.3
        ol_lra_per = int((1 / (frq * 98.49 * pow(10, -6))))

        # range-limitation -> OL_LRA_PERIOD[6:0] -> max. value = 0d63 -> min. frequency = 161,164Hz
        ol_lra_per = min(ol_lra_per, 63)

        for i in self.act_no:   # write value of ol_lra_per to actuators
            self.drv[i]._write_u8(0x20, self.drv[i]._read_u8(0x20) & 0b10000000)  # clear bits
            self.drv[i]._write_u8(0x20, self.drv[i]._read_u8(0x20) | ol_lra_per)
            # print(f"Frequence of actuator {i} changed to {frq} hz at /
            # OL_LRA_PERIOD value {self.drv[i]._read_u8(0x20) & 0b01111111}")


    def set_actuator(self, value):
        """execution function for all actuators (depending on act_no)"""

        FREQU_1 = 3   # frequence in stage 1 in [Hz]
        FREQU_2 = 5   # frequence in stage 2 in [Hz]
        FREQU_3 = 8   # frequence in stage 3 in [Hz]
        FREQU_4 = 13   # frequence in stage 4 in [Hz]

        frequ_d = 0   # frequence delivered to Actuators


        self.stage = self.get_stage(value)   # get stage in dependence of delivered value
        # print("Sensor value: {} stage value: {}" .format(value, stage))

        # set configuration of vibration pattern to actuators in dependence of stage
        for i in self.act_no:
            if self.stage == 0:
                pass

            elif self.stage == 1:
                self.set_vib_intv(1)
                frequ_d = FREQU_1
                self.stage_comp = self.stage

            elif self.stage == 2:
                self.set_vib_intv(1)
                frequ_d = FREQU_2
                self.stage_comp = self.stage

            elif self.stage == 3:
                self.set_vib_intv(1)
                frequ_d = FREQU_3
                self.stage_comp = self.stage

            elif self.stage == 4:
                self.set_vib_intv(1)
                frequ_d = FREQU_4
                self.stage_comp = self.stage

            elif self.stage == 5 and self.stage != self.stage_comp:
                pass

        # output of vibration-selection to DRVs (simultaniously, therefore separated)
        if self.stage == 0 and self.stage_comp != 0:
            for i in self.act_no:
                self.drv[i].stop()
                self.set_vib_const(0)
            self.stage_comp = self.stage
            print(f"stop vibration of actuator(s) {self.act_no}")
        elif self.stage < 5 and self.stage != 0:
            for i in self.act_no:
                self.start_vib_intv(frequ_d)
            print(f"start Vibration of actuator(s) {self.act_no} at {frequ_d}hz ")
        elif self.stage == 5 and self.stage != self.stage_comp:
            for i in self.act_no:
                self.set_vib_const(127)
                print(f"start constant vibration of actuator(s) {self.act_no}")
                self.stage_comp = self.stage


    def set_freq_state(self, state):
        """set a vibration frequence in dependence of a state (range: 0...2)"""

        freq_state = [150, 200, 250]

        if state == 0 and self.state_comp != state:
            self.set_drv_freq(freq_state[0])

        elif state == 1 and self.state_comp != state:
            self.set_drv_freq(freq_state[1])

        elif state == 2 and self.state_comp != state:
            self.set_drv_freq(freq_state[2])

        self.state_comp = state


#################### Test program ####################

# # Test 1
# stage = get_stage(value, Step0, Step1, Step2, Step3, Step4)
# print("Sensor value: {} stage value: {}" .format(value, stage))


# Test 2

if __name__ == "__main__":

    act = Actuator(act_no)

    act.config_drv_to_lra()

    act.autocalibration([2414, 2414])

    act.set_drv_open_loop()


    for m in range(150, 500, 50):
        act.set_drv_freq(m)
        for n in range(4):
            act.set_actuator(val[0])
