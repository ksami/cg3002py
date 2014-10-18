import smbus
import math
import time
import sys
from vector import Vector

SAMPLE_SIZE = 50
PRECISION = 1000 # = 32767 - 31128 (max and min values when stabilized)
TIME_WINDOW_MIN = 0.3

HIGH_PASS = 0.8

scale = 1.3
most_active_axis = 2

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

def compare(accel_1, accel_2):

    if( most_active_axis == 0 ) :
        return accel_1.x - accel_2.x
    
    if( most_active_axis == 1 ) :
        return accel_1.y - accel_2.y
    
    if( most_active_axis == 2 ) :
        return accel_1.z - accel_2.z

def getHeading(compass_val):

    heading = 0
    
    if(most_active_axis == 0): # x-axis 
        heading = math.atan2(compass_val.z, compass_val.y)

    if(most_active_axis == 1): # y-axis 
        heading = math.atan2(compass_val.x, compass_val.z)

    if(most_active_axis == 2): # x-axis 
        heading = math.atan2(compass_val.y, compass_val.x)

    heading += 0.0404

    if(heading < 0):
        heading += 2*math.pi

    if(heading > 2*math.pi):
        heading -= 2*math.pi

    return math.degrees(heading)

def getAccel(accel_val):
    
    if( most_active_axis == 0 ) :
        return accel_val.x
    
    if( most_active_axis == 1 ) :
        return accel_val.y
    
    if( most_active_axis == 2 ) :
        return accel_val.z


bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(mpu_address, 0x6A, 0)
bus.write_byte_data(mpu_address, 0x37, 2)
bus.write_byte_data(mpu_address, power_mgmt_1, 0)

bus.write_byte_data(hmc_address, 0, 0b01110000) # Set to 8 samples @ 15Hz
bus.write_byte_data(hmc_address, 1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
bus.write_byte_data(hmc_address, 2, 0b00000000) # Continuous sampling

accel_max = Vector(0, 0, 0)
accel_min = Vector(sys.maxint, sys.maxint, sys.maxint)
accel_val = Vector(0, 0, 0)
gravity = Vector(0, 0, 0)
dynamic_threshold = Vector(0, 0, 0) # the moving average of 50 accelerometer data
moving_index = 0
sample_size = 0
accel_filter_list = []
sample_old = Vector(0, 0, 0)
sample_new = Vector(0, 0, 0)
num_steps = 0
time_window = 0

size = 0

sum_x = 0
sum_y = 0
sum_z = 0

# initialization stage

accel_xout = read_word_2c(mpu_address, 0x3b)
accel_yout = read_word_2c(mpu_address, 0x3d)
accel_zout = read_word_2c(mpu_address, 0x3f)

max_axis = accel_zout
if(max_axis < accel_xout):
    max_axis = accel_xout
    most_active_axis = 0
if(max_axis < accel_yout):
    max_axis = accel_xout
    most_active_axis = 1

print "TIME_WINDOW_MIN: ", TIME_WINDOW_MIN
print "PRECISION: " , PRECISION
print "MOST ACTIVE AXIS: ", most_active_axis

# calibration stage
print "\n---CALIBRATION STAGE---"

calibration_time = time.time()
calibration_size = 0

while(time.time() - calibration_time <= 5):
    accel_xout = read_word_2c(mpu_address, 0x3b)
    accel_yout = read_word_2c(mpu_address, 0x3d)
    accel_zout = read_word_2c(mpu_address, 0x3f)

    gravity.x = HIGH_PASS * gravity.x + (1 - HIGH_PASS) * accel_val.x
    gravity.y = 0
    gravity.z = HIGH_PASS * gravity.z + (1 - HIGH_PASS) * accel_val.z

    accel_xout -= gravity.x
    accel_yout -= gravity.y
    accel_zout -= gravity.z

    sum_x += accel_xout
    sum_y += accel_yout
    sum_z += accel_zout

    calibration_size += 1

accel_offset_x = sum_x/calibration_size
accel_offset_y = sum_y/calibration_size
accel_offset_z = sum_z/calibration_size

print "---End CALIBRATION STAGE---\n"

for i in range(4) :
    accel_xout = read_word_2c(mpu_address, 0x3b) - accel_offset_x
    accel_yout = read_word_2c(mpu_address, 0x3d) - 0
    accel_zout = read_word_2c(mpu_address, 0x3f) - accel_offset_z

    accel_val = Vector(accel_xout, accel_yout, accel_zout)
    accel_filter_list.append(accel_val)

first_time = True

while(True):

    if(sample_size == SAMPLE_SIZE):
        sample_size = 0

        dynamic_threshold.x = (accel_max.x + accel_min.x) / 2
        dynamic_threshold.y = (accel_max.y + accel_min.y) / 2
        dynamic_threshold.z = (accel_max.z + accel_min.z) / 2

        accel_max = Vector(0, 0, 0)
        accel_min = Vector(sys.maxint, sys.maxint, sys.maxint)

        first_time = False

    #filter accelerometer values
    accel_xout = read_word_2c(mpu_address, 0x3b) - accel_offset_x
    accel_yout = read_word_2c(mpu_address, 0x3d) - 0
    accel_zout = read_word_2c(mpu_address, 0x3f) - accel_offset_z

    accel_val = Vector(accel_xout, accel_yout, accel_zout)
    
    accel_val.x = (accel_filter_list[0].x + accel_filter_list[1].x + accel_filter_list[2].x + accel_filter_list[3].x + accel_val.x) / 5
    accel_val.y = (accel_filter_list[0].y + accel_filter_list[1].y + accel_filter_list[2].y + accel_filter_list[3].y + accel_val.y) / 5
    accel_val.z = (accel_filter_list[0].z + accel_filter_list[1].z + accel_filter_list[2].z + accel_filter_list[3].z + accel_val.z) / 5

    gravity.x = HIGH_PASS * gravity.x + (1 - HIGH_PASS) * accel_val.x
    gravity.y = 0
    gravity.z = HIGH_PASS * gravity.z + (1 - HIGH_PASS) * accel_val.z

    accel_val.x = accel_val.x - gravity.x
    accel_val.y = accel_val.y - gravity.y
    accel_val.z = accel_val.z - gravity.z

    accel_filter_list.insert(moving_index, accel_val)

    # filter compass values
    compass_xout = read_word_2c(hmc_address, 3) * scale
    compass_yout = read_word_2c(hmc_address, 7) * scale
    compass_zout = read_word_2c(hmc_address, 5) * scale

    compass_val = Vector(compass_xout, compass_yout, compass_zout)

    moving_index = (moving_index + 1) % 4
    sample_size += 1    
    size += 1

    # finding maximum, minimum
    if(compare(accel_max, accel_val) < 0):
        accel_max = accel_val
    if(compare(accel_min, accel_val) > 0):
        accel_min = accel_val

    if(not first_time):
        sample_old = sample_new	

        if( math.fabs(compare(accel_val, sample_new)) > PRECISION ):
            sample_new = accel_val
	
            if( compare(sample_new, dynamic_threshold) < 0 and compare(dynamic_threshold, sample_old) < 0):
                if(time.time() - time_window >= TIME_WINDOW_MIN):
                    num_steps += 1
                    print "numsteps:", num_steps
                    time_window = time.time()

    else:
        sample_new = accel_val

threshold_sum /= threshold_size
print "threshold =", threshold_sum
#graph.close()
