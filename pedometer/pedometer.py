import smbus
import math
import time
import sys
from vector import Vector

SAMPLE_SIZE = 50
PRECISION = 1000 # = 32767 - 31128 (max and min values when stabilized)
TIME_WINDOW_MIN = 0.3
TIME_WINDOW_MAX = 2
HEIGHT = 1.77 # in meters
STANDING_MODE = 0
WALKING_MODE = 1

MAX_ACCEL_VALUE = 32767
MIN_ACCEL_VALUE = 31128

MAX_STATIONARY_ACCEL = Vector(MAX_ACCEL_VALUE, MAX_ACCEL_VALUE, MAX_ACCEL_VALUE)
MIN_STATIONARY_ACCEL = Vector(MIN_ACCEL_VALUE, MIN_ACCEL_VALUE, MIN_ACCEL_VALUE)

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
dynamic_threshold = Vector(0, 0, 0) # the moving average of 50 accelerometer data
moving_index = 0
sample_size = 0
accel_filter_list = []
sample_old = Vector(0, 0, 0)
sample_new = Vector(0, 0, 0)
num_steps = 0
testing_steps = 0
steps_per_two_s = 0
two_seconds_elapsed = 0
distance_per_two_s = 0
time_window = 0
total_distance = 0

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
#size = 0
#s_size = 0

print "TIME_WINDOW_MIN: ", TIME_WINDOW_MIN
print "TIME_WINDOW_MAX: ", TIME_WINDOW_MAX
print "PRECISION: " , PRECISION

two_seconds_elapsed = time.time()

while(True):

    if(sample_size == SAMPLE_SIZE):
        sample_size = 0
       # print "--------------------------------- finished 50 samples \n"

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

    # filter compass values
    compass_xout = read_word_2c(hmc_address, 3) * scale
    compass_yout = read_word_2c(hmc_address, 7) * scale
    compass_zout = read_word_2c(hmc_address, 5) * scale

    compass_val = Vector(compass_xout, compass_yout, compass_zout)

    moving_index = (moving_index + 1) % 4
    sample_size += 1    

    # finding maximum, minimum
    if(compare(accel_max, accel_val) < 0):
        accel_max = accel_val
    if(compare(accel_min, accel_val) > 0):
        accel_min = accel_val

    if(not first_time):
        sample_old = sample_new	

        if( math.fabs(compare(accel_val, sample_new)) > PRECISION ):
	    #print "------------- get sample_new value\n "
	    sample_new = accel_val
	
	    if(mode == WALKING_MODE):
	       if( compare(sample_new, dynamic_threshold) < 0 and compare(dynamic_threshold, sample_old) < 0):
		      if(TIME_WINDOW_MIN <= time.time() - time_window <= TIME_WINDOW_MAX):
		          num_steps += 1
		          time_window = time.time()
		          print "WALKING MODE: num_steps =", num_steps
		      elif(time.time() - time_window > TIME_WINDOW_MAX):
			     mode = STANDING_MODE
			     testing_steps = 1
			     print "GOING TO STANDING MODE\n"
	    if(mode == STANDING_MODE):
		  if( compare(sample_new, dynamic_threshold) < 0 and compare(dynamic_threshold, sample_old) < 0):
		      if(time_window == 0 or TIME_WINDOW_MIN <= time.time() - time_window <= TIME_WINDOW_MAX):
			     testing_steps += 1
			     time_window = time.time()
			     print "STANDING MODE TO WALKING MODE", testing_steps
		      elif(time.time() - time_window > TIME_WINDOW_MAX):
			     testing_steps = 1
			     print "STILL STANDING MODE"
			     time_window = time.time()
		  if(testing_steps >= 3):
		      num_steps += testing_steps
		      print "GOING TO WALKING MODE: num_steps =", num_steps
		      mode = WALKING_MODE

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

        heading = getHeading(compass_val)

    	#print "\n\n-------------", time.time() - two_seconds_elapsed
    	#print "numsteps per 2s: ", steps_per_two_s
    	#print "distance per 2s: ", distance_per_two_s
    	#print "total_numsteps: ", num_steps
    	#print "total_distance: ", total_distance
        #print "Heading: ", heading
    	  
    	two_seconds_elapsed = time.time()
    	steps_per_two_s = 0
