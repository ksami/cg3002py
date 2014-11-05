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

COMPASS_X_AXIS = -145
COMPASS_Z_AXIS = -135

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


bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(mpu_address, 0x6A, 0)
bus.write_byte_data(mpu_address, 0x37, 2)
bus.write_byte_data(mpu_address, power_mgmt_1, 0)

bus.write_byte_data(hmc_address, 0, 0b01110000) # Set to 8 samples @ 15Hz
bus.write_byte_data(hmc_address, 1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
bus.write_byte_data(hmc_address, 2, 0b00000000) # Continuous sampling

#compass_graph = open('compass_graph_1.txt', 'w')
time_compass = time.time()

size = 0
minx = sys.maxint
maxx = -sys.maxint
minz = sys.maxint
maxz = -sys.maxint

while(time.time() - time_compass <= 60):
    compass_xout = read_word_2c(bus, hmc_address, 3) 
    compass_yout = read_word_2c(bus, hmc_address, 7) 
    compass_zout = read_word_2c(bus, hmc_address, 5)

    if compass_xout < minx:
        minx = compass_xout
    
    if compass_zout < minz:
        minz = compass_zout
    
    if compass_xout > maxx:
        maxx = compass_xout
    
    if compass_zout > maxz:
        maxz = compass_xout

    size += 1
    print size

    #compass_graph.write(str(size) + "\t" + str(compass_xout) + "\t" + str(compass_yout) + "\t" + str(compass_zout) + "\n")

print "MIN X", minx
print "MAX X", minx
print "MIN Z", minz
print "MAX Z", maxz
print "COMPASS X OFFSET", (minx + maxx) / 2.
print "COMPASS Z OFFSET", (minz + maxz) / 2.

#compass_graph.close()
