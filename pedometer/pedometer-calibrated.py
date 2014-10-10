import smbus
import math
import time
import sys
from vector import Vector

SAMPLE_SIZE = 50
PRECISION = 1000/2 # = 32767 - 31128 (max and min values when stabilized)
TIME_WINDOW = 0.4
HEIGHT = 1.77 # in meters

MAX_ACCEL_VALUE = 32767
MIN_ACCEL_VALUE = 31128

MAX_STATIONARY_ACCEL = Vector(MAX_ACCEL_VALUE, MAX_ACCEL_VALUE, MAX_ACCEL_VALUE)
MIN_STATIONARY_ACCEL = Vector(MIN_ACCEL_VALUE, MIN_ACCEL_VALUE, MIN_ACCEL_VALUE)

scale = 1.3

# Power management registers
power_mgmt_1 = 0x6b

# MPU6050 i2c address
mpu_address = 0x68 


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


bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(mpu_address, power_mgmt_1, 0)

accel_max = Vector(0, 0, 0)
accel_min = Vector(sys.maxint, sys.maxint, sys.maxint)
accel_val = Vector(0, 0, 0)
dynamic_threshold = Vector(0, 0, 0) # the moving average of 50 accelerometer data
moving_index = 0
sample_size = 0
accel_filter_list = []
sample_old = Vector(0, 0, 0)
sample_new = Vector(0, 0, 0)
num_steps = 0
time_window = 0

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

for i in range(4) :
    accel_xout = read_word_2c(mpu_address, 0x3b)
    accel_yout = read_word_2c(mpu_address, 0x3d)
    accel_zout = read_word_2c(mpu_address, 0x3f)

    accel_val = Vector(accel_xout, accel_yout, accel_zout)
    accel_filter_list.append(accel_val)

first_time = True

print "TIME_WINDOW: ", TIME_WINDOW
print "PRECISION: " , PRECISION

time_traversed = time.time()
threshold_file = open("threshold_file", 'w');
threshold_avg = 0
threshold_size = 0

while(time.time() - time_traversed <= 120):

    if(sample_size == SAMPLE_SIZE):
        sample_size = 0

        dynamic_threshold.x = (accel_max.x + accel_min.x) / 2
        dynamic_threshold.y = (accel_max.y + accel_min.y) / 2
        dynamic_threshold.z = (accel_max.z + accel_min.z) / 2

        accel_max = Vector(0, 0, 0)
        accel_min = Vector(sys.maxint, sys.maxint, sys.maxint)

        first_time = False

    #filter accelerometer values
    accel_xout = read_word_2c(mpu_address, 0x3b)
    accel_yout = read_word_2c(mpu_address, 0x3d)
    accel_zout = read_word_2c(mpu_address, 0x3f)

    accel_val = Vector(accel_xout, accel_yout, accel_zout)

    accel_val.x = (accel_filter_list[0].x + accel_filter_list[1].x + accel_filter_list[2].x + accel_filter_list[3].x + accel_val.x) / 5
    accel_val.y = (accel_filter_list[0].y + accel_filter_list[1].y + accel_filter_list[2].y + accel_filter_list[3].y + accel_val.y) / 5
    accel_val.z = (accel_filter_list[0].z + accel_filter_list[1].z + accel_filter_list[2].z + accel_filter_list[3].z + accel_val.z) / 5
    
    accel_filter_list.insert(moving_index, accel_val)

    moving_index = (moving_index + 1) % 4;
    sample_size += 1    
    size += 1;

    # finding maximum, minimum
    if(compare(accel_max, accel_val) < 0):
        accel_max = accel_val
    if(compare(accel_min, accel_val) > 0):
        accel_min = accel_val

    if(not first_time):
        sample_old = sample_new	

        threshold_file.write(math.fabs(compare(accel_val, sample_new)) + "\n")
        threshold_avg += math.fabs(compare(accel_val, sample_new))
        num += 1
        if( math.fabs(compare(accel_val, sample_new)) > PRECISION	 
            sample_new = accel_val

	    if( compare(sample_new, dynamic_threshold) < 0 and compare(dynamic_threshold, sample_old) < 0):
        	if(time_window == 0 or time.time() - time_window > TIME_WINDOW):
	             steps_per_two_s += 1
	             num_steps += 1
        	     print "num steps: ", num_steps, time.time() - time_window
		         time_window = time.time()

    else:
	 sample_new = accel_val

threshold_avg /= num
threshold_file.write("----" + threshold_avg + "\n")
threshold_file.close()