import smbus
import math
import time
import sys
from vector import Vector

SAMPLE_SIZE = 50
PRECISION = 1000 # = 32767 - 31128 (max and min values when stabilized)
TIME_WINDOW = 0.4
HEIGHT = 1.77 # in meters

MAX_ACCEL_VALUE = 32767
MIN_ACCEL_VALUE = 31128

MAX_STATIONARY_ACCEL = Vector(MAX_ACCEL_VALUE, MAX_ACCEL_VALUE, MAX_ACCEL_VALUE)
MIN_STATIONARY_ACCEL = Vector(MIN_ACCEL_VALUE, MIN_ACCEL_VALUE, MIN_ACCEL_VALUE)

# Power management registers
power_mgmt_1 = 0x6b

# MPU6050 i2c address
address = 0x68 

# we can compare two accelerometer values by this axis
most_active_axis = 2 # axis z

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
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
bus.write_byte_data(address, power_mgmt_1, 0)

accel_sum = Vector(0, 0, 0)
dynamic_threshold = Vector(0, 0, 0) # the moving average of 50 accelerometer data
moving_index = 0
sample_size = 0
sample_old = Vector(0, 0, 0)
sample_new = Vector(0, 0, 0)
num_steps = 0
steps_per_two_s = 0
two_seconds_elapsed = 0
distance_per_two_s = 0
time_window = 0
total_distance = 0

# initialization stage

accel_xout = read_word_2c(0x3b)
accel_yout = read_word_2c(0x3d)
accel_zout = read_word_2c(0x3f)

max_axis = accel_zout
if(max_axis < accel_xout):
    max_axis = accel_xout
    most_active_axis = 0
if(max_axis < accel_yout):
    max_axis = accel_xout
    most_axis_axis = 1

first_time = True

print "TIME_WINDOW: ", TIME_WINDOW
print "PRECISION: " , PRECISION

two_seconds_elapsed = time.time()

while(True):

    if(sample_size == 50):
        sample_size = 0
       # print "--------------------------------- finished 50 samples \n"

        dynamic_threshold.x = (accel_sum.x) / SAMPLE_SIZE
        dynamic_threshold.y = (accel_sum.y) / SAMPLE_SIZE
        dynamic_threshold.z = (accel_sum.z) / SAMPLE_SIZE

        accel_sum.x = 0
        accel_sum.y = 0
        accel_sum.z = 0

        first_time = False

    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)

    accel_val = Vector(accel_xout, accel_yout, accel_zout)

    if(compare(accel_val, MAX_STATIONARY_ACCEL) < 0 and compare(accel_val, MIN_STATIONARY_ACCEL) > 0):

        sample_size += 1    

        accel_sum.x += accel_val.x
        accel_sum.y += accel_val.y
        accel_sum.z += accel_val.z

        if(not first_time):

            sample_old = sample_new
        
            if( math.fabs(compare(accel_val, sample_new)) > PRECISION ):
                #  print "------------- get sample_new value\n "
                sample_new = accel_val

            if( compare(sample_new, dynamic_threshold) < 0 and compare(dynamic_threshold, sample_old) < 0 ):
                # check time window()
                if(time_window == 0 or time.time() - time_window > TIME_WINDOW):
                    time_window = time.time()
                    steps_per_two_s += 1
                    num_steps += 1
                    print "num steps: ", num_steps

        else:
            sample_new = accel_val
    
    if(time.time() - two_seconds_elapsed >= 2):
        if(steps_per_two_s <= 2):
            distance_per_two_s = HEIGHT / 5
        elif(steps_per_two_s <= 3):
            distance_per_two_s = HEIGHT / 4
        elif(steps_per_two_s <= 4):
            distance_per_two_s = HEIGHT / 3
        elif(steps_per_two_s <= 5):
            distance_per_two_s = HEIGHT / 2
        elif(steps_per_two_s <= 6):
            distance_per_two_s = HEIGHT / 1.2
        elif (steps_per_two_s <= 8):
            distance_per_two_s = HEIGHT
        else:
            distance_per_two_s = 1.2 * HEIGHT
        
        distance_per_two_s *= steps_per_two_s
        total_distance += distance_per_two_s

        print "\n\n-------------", time.time() - two_seconds_elapsed
        print "numsteps per 2s: ", steps_per_two_s
        print "distance per 2s: ", distance_per_two_s
        print "total_numsteps: ", num_steps
        print "total_distance: ", total_distance
          
        two_seconds_elapsed = time.time()
        steps_per_two_s = 0