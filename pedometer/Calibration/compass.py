import smbus
import math
import time
import sys

# Power management registers
power_mgmt_1 = 0x6b

# MPU6050 i2c address
mpu_address = 0x68 

# HMC5883l i2c address
hmc_address = 0x1e

COMPASS_X_AXIS = -130
COMPASS_Z_AXIS = -198.5

def read_word(bus, sensor_address, adr):
    high = bus.read_byte_data(sensor_address, adr)
    low = bus.read_byte_data(sensor_address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(bus, sensor_address, adr):
    val = read_word(bus, sensor_address, adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def GetHeading(compass_valx, compass_valy, compass_valz):
    
    heading = math.atan2(compass_valx, compass_valz)
    heading += 0.0404

    if(heading < 0):
        heading += 2*math.pi

    if(heading > 2*math.pi):
        heading -= 2*math.pi

    return math.degrees(heading)


bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(mpu_address, 0x6A, 0)
bus.write_byte_data(mpu_address, 0x37, 2)
bus.write_byte_data(mpu_address, power_mgmt_1, 0)

bus.write_byte_data(hmc_address, 0, 0b01110000) # Set to 8 samples @ 15Hz
bus.write_byte_data(hmc_address, 1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
bus.write_byte_data(hmc_address, 2, 0b00000000) # Continuous sampling

size = 1

while(True):
    compass_xout = read_word_2c(bus, hmc_address, 3) - COMPASS_X_AXIS 
    compass_yout = read_word_2c(bus, hmc_address, 7) 
    compass_zout = read_word_2c(bus, hmc_address, 5) - COMPASS_Z_AXIS

    print "Size:", size, "heading:", getHeading(compass_xout, compass_yout, compass_zout)
    size += 1

    time.sleep(0.5)