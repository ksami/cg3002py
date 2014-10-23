import smbus
import math
import time
import sys
from vector import Vector

SAMPLE_SIZE = 50
PRECISION = 1000 # = 32767 - 31128 (max and min values when stabilized)
TIME_WINDOW_MIN = 0.3

ACCEL_X_OFFSET = 3026
ACCEL_Y_OFFSET = 15721
ACCEL_Z_OFFSET = 3213

MULTIPLIER = 1 # will need to change it

LOW_PASS = 0.1
HIGH_PASS = 0.1

scale = 1.3
most_active_axis = 2
mode = STANDING_MODE

# Power management registers
power_mgmt_1 = 0x6b

# MPU6050 i2c address
mpu_address = 0x68 

# HMC5883l i2c address
hmc_address = 0x1e


def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(sensor_address, adr):
    high = bus.read_byte_data(sensor_address, adr)
    low = bus.read_byte_data(sensor_address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(sensor_address, adr):
    val = read_word(sensor_address, adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(mpu_address, 0x6A, 0)
bus.write_byte_data(mpu_address, 0x37, 2)
bus.write_byte_data(mpu_address, power_mgmt_1, 0)

bus.write_byte_data(hmc_address, 0, 0b01110000) # Set to 8 samples @ 15Hz
bus.write_byte_data(hmc_address, 1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
bus.write_byte_data(hmc_address, 2, 0b00000000) # Continuous sampling

compass_graph = open('compass_graph.txt', 'w')
time_compass = time.time()

size = 0

while(time.time() - time_compass <= 20)
    compass_xout = read_word_2c(self.bus, hmc_address, 3)
    compass_yout = read_word_2c(self.bus, hmc_address, 7) 
    compass_zout = read_word_2c(self.bus, hmc_address, 5)

    size += 1

    compass_graph.write(str(size) + "\t" + compass_xout + "\t" + compass_yout + "\t" + compass_zout + "\n")

compass_graph.close()