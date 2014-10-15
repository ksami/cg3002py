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

def compare(accel_1, accel_2):

    if( most_active_axis == 0 ) :
        return accel_1.x - accel_2.x
    
    if( most_active_axis == 1 ) :
        return accel_1.y - accel_2.y
    
    if( most_active_axis == 2 ) :
        return accel_1.z - accel_2.z

def getDist(accel_val):

    x = accel_val.x 
    y = accel_val.y 
    z = accel_val.z 
    
    if( most_active_axis == 0 ) :
        return math.sqrt( (y*y + z*z) / 16.0)
    
    if( most_active_axis == 1 ) :
        return math.sqrt( (x*x + z*z) / 16.0)
    
    if( most_active_axis == 2 ) :
        return math.sqrt( (x*x + y*y) / 16.0)

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
accel_gravity = Vector(0, 0, 0)
dynamic_threshold = Vector(0, 0, 0) # the moving average of 50 accelerometer data
moving_index = 0
sample_size = 0
accel_filter_list = []
sample_old = Vector(0, 0, 0)
sample_new = Vector(0, 0, 0)
num_steps = 0
time_window = 0
total_distance = 0

max_dist = 0
min_dist = sys.maxint
val_dist = 0
avg_dist = 0
list_dist = []
list_dist_filter = []
dist_moving_index = 0

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

print "TIME_WINDOW_MIN:", TIME_WINDOW_MIN
print "PRECISION:" , PRECISION
print "MULTIPLIER K:", MULTIPLIER

stride_txt = open("stride_length.txt", 'w')

time_elapsed = time.time()

while(time.time() - time_elapsed <= 10):

    if(sample_size == SAMPLE_SIZE):
        sample_size = 0
       # print "--------------------------------- finished 50 samples \n"

        dynamic_threshold.x = (accel_max.x + accel_min.x) / 2
        dynamic_threshold.y = (accel_max.y + accel_min.y) / 2
        dynamic_threshold.z = (accel_max.z + accel_min.z) / 2

        accel_max = Vector(0, 0, 0)
        accel_min = Vector(sys.maxint, sys.maxint, sys.maxint)

        max_dist = 0
        min_dist = sys.maxint
        val_dist = 0
        avg_dist = 0
        list_dist = []

        first_time = False

    #filter accelerometer values
    accel_xout = read_word_2c(mpu_address, 0x3b) - ACCEL_X_OFFSET
    accel_yout = read_word_2c(mpu_address, 0x3d) - ACCEL_Y_OFFSET
    accel_zout = read_word_2c(mpu_address, 0x3f) - ACCEL_Z_OFFSET

    accel_val = Vector(accel_xout, accel_yout, accel_zout)

    # simple moving average to smooth the acceleration data
    accel_val.x = (accel_filter_list[0].x + accel_filter_list[1].x + accel_filter_list[2].x + accel_filter_list[3].x + accel_val.x) / 5
    accel_val.y = (accel_filter_list[0].y + accel_filter_list[1].y + accel_filter_list[2].y + accel_filter_list[3].y + accel_val.y) / 5
    accel_val.z = (accel_filter_list[0].z + accel_filter_list[1].z + accel_filter_list[2].z + accel_filter_list[3].z + accel_val.z) / 5

    # remove gravity, get pure linear acceleration
    #accel_gravity.x = accel_gravity.x * (1 - HIGH_PASS) + accel_val.x * HIGH_PASS
    #accel_gravity.y = accel_gravity.y * (1 - HIGH_PASS) + accel_val.y * HIGH_PASS
    #accel_gravity.z = accel_gravity.z * (1 - HIGH_PASS) + accel_val.z * HIGH_PASS

    #accel_val.x = accel_val.x - accel_gravity.x
    #accel_val.y = accel_val.y - accel_gravity.y
    #accel_val.z = accel_val.z - accel_gravity.z
    
    accel_filter_list.insert(moving_index, accel_val)
    moving_index = (moving_index + 1) % 4
    sample_size += 1    

    # finding maximum, minimum
    if(compare(accel_max, accel_val) < 0):
        accel_max = accel_val
    if(compare(accel_min, accel_val) > 0):
        accel_min = accel_val

    val = getDist(accel_val)
    list_dist.append(val)

    # finding maximum, minimum
    if(val > max_dist):
        max_dist = val
    if(val < min_dist):
        min_dist = val

    # filter compass values
    compass_xout = read_word_2c(hmc_address, 3) * scale
    compass_yout = read_word_2c(hmc_address, 7) * scale
    compass_zout = read_word_2c(hmc_address, 5) * scale

    compass_val = Vector(compass_xout, compass_yout, compass_zout)

    if(not first_time):
        sample_old = sample_new 


        if( math.fabs(compare(accel_val, sample_new)) > PRECISION ):
            sample_new = accel_val
            
            if( compare(sample_new, dynamic_threshold) < 0 and compare(dynamic_threshold, sample_old) < 0):
                if(time.time() - time_window >= TIME_WINDOW_MIN):
                    num_steps += 1

                    sum_dist = 0
                    for dist in list_dist :
                        sum_dist += dist
                    avg_dist = sum_dist / len(list_dist)

                    velocity = 0
                    displace = 0
                    for dist in list_dist:
                        velocity += (dist - avg_dist)
                        displace += velocity

                    stride = math.fabs(displace * ((max_dist - avg_dist) / (avg_dist - min_dist))) * MULTIPLIER
                    if(num_steps <= 4):
                        list_dist_filter.append(stride)
                    else:
                        stride = (list_dist_filter[0] + list_dist_filter[1] + list_dist_filter[2] + list_dist_filter[3] + stride) / 5
                        list_dist_filter.insert(dist_moving_index, stride)
                        dist_moving_index = (dist_moving_index + 1) % 4
                    total_distance += stride

                    print "\n-----------------"
                    print "numsteps:", num_steps
                    print "Accel:", accel_val.x, accel_val.y, accel_val.z
                    print "stride length:", stride
                    print "num of samples:", len(list_dist)
                    print "total distance:", total_distance

                    stride_txt.write(str(time.time()) + "\t" + str(stride) + "\t" + str(num_steps))

                    max_dist = 0
                    min_dist = sys.maxint
                    val_dist = 0
                    avg_dist = 0
                    list_dist = []

                    time_window = time.time()

    else:
        sample_new = accel_val

stride_txt.close()
