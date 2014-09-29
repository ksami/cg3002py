#!/usr/bin/python
import smbus
import time
import math

bus = smbus.SMBus(1)

mpu_address = 0x68
hmc_address = 0x1e

power_mgmt_1 = 0x6b

X_AXIS_ADDRESS = 3
Y_AXIS_ADDRESS = 7
Z_AXIS_ADDRESS = 5

COMPASS_X_OFFSET = 0 # need to change
COMPASS_Y_OFFSET = 0 # need to change

compass_x_axis_address = COMPASS_X_AXIS_ADDRESS
compass_y_axis_address = COMPASS_Y_AXIS_ADDRESS

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

bus.write_byte_data(mpu_address, 0x6A, 0)
bus.write_byte_data(mpu_address, 0x37, 2)
bus.write_byte_data(mpu_address, power_mgmt_1, 0)


bus.write_byte_data(hmc_address, 0, 0b01110000) # Set to 8 samples @ 15Hz
bus.write_byte_data(hmc_address, 1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
bus.write_byte_data(hmc_address, 2, 0b00000000) # Continuous sampling


accel_xout = read_word_2c(mpu_address, 0x3b)
accel_yout = read_word_2c(mpu_address, 0x3d)
accel_zout = read_word_2c(mpu_address, 0x3f)

# find x-axis and y-axis due to accelerometer
max_axis = accel_zout
if(max_axis < accel_xout):
    max_axis = accel_xout
    most_active_axis = 0
if(max_axis < accel_yout):
    max_axis = accel_xout
    most_active_axis = 1

if(most_active_axis == 2): # z-axis is perpendicular to earth 
    x_axis_address = X_AXIS_ADDRESS
    y_axis_address = Y_AXIS_ADDRESS

if(most_active_axis == 1): # y-axis is perpendicular to earth
    x_axis_address = Z_AXIS_ADDRESS
    y_axis_address = X_AXIS_ADDRESS

if(most_active_axis == 0): # y-axis is perpendicular to earth
    x_axis_address = Y_AXIS_ADDRESS
    y_axis_address = Z_AXIS_ADDRESS

scale = 0.92

compass_filter_list = []
moving_index = 0
compass_val = Vector(0, 0, 0)

for(i in range(4)):
    x_out = read_word_2c(hmc_address, x_axis_address) * scale
    y_out = read_word_2c(hmc_address, y_axis_address) * scale    

    compass_val = Vector(x_out, y_out, 0)
    compass_filter_list.append(compass_val)

while(True):

    if(time.time() - two_seconds_elapsed >= 2):
    
        heading  = math.atan2(compass_val.y, compass_val.x)

        if(heading < 0):
            heading += 2*math.pi

        print "Heading: ", math.degrees(heading)
          
        two_seconds_elapsed = time.time()

    x_out = (read_word_2c(hmc_address, x_axis_address) - X_OFFSET) * scale
    y_out = (read_word_2c(hmc_address, y_axis_address) - Y_OFFSET) * scale

    compass_val = Vector(x_out, y_out, 0)

    compass_val.x = (compass_filter_list[0].x + compass_filter_list[1].x + compass_filter_list[2].x + compass_filter_list[3].x + compass_val.x) / 5
    compass_val.y = (compass_filter_list[0].y + compass_filter_list[1].y + compass_filter_list[2].y + compass_filter_list[3].y + compass_val.y) / 5
    
    compass_filter_list.insert(moving_index, compass_val)
    moving_index = (moving_index + 1) % 4
