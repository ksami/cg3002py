import smbus
import math
import time
import sys
from vector import Vector

ACCEL_THRESHOLD = 1000 # = 32767 - 31128 (max and min values when stabilized)
PEAK_THRESHOLD = 7000
TIME_THRESHOLD = 0.4
HIGH_PASS = 0.8
STRIDE_COEFFICIENT = 1
#STRIDE_COEFFICIENT = 1.319148936
# from walking in total of 14.4 meters and total_distance (without calibration) 545.260574691
HEIGHT = 1.76

MAXIMA = 1
MINIMA = 0

# register address
power_mgmt_1 = 0x6b # Power management registers
mpu_address = 0x68  # MPU6050 i2c address
hmc_address = 0x1e  # HMC5883l i2c address


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

def compare(most_active_axis, accel_1, accel_2):

    if( most_active_axis == 0 ) :
        return accel_1.x - accel_2.x
    
    if( most_active_axis == 1 ) :
        return accel_1.y - accel_2.y
    
    if( most_active_axis == 2 ) :
        return accel_1.z - accel_2.z

def getStrideLength(accel_list):
    accel_sum = 0
    for i in range(len(accel_list)):
        accel_sum += accel_val.y
    accel_avg = accel_sum / len(accel_list)

    for i in range(len(accel_list)):
        accel_sum += (accel_val.y - accel_avg)
    accel_sum /= len(accel_list)

    print "accel_sum", accel_sum

    return STRIDE_COEFFICIENT * math.pow(accel_sum, 1/3.0)

def GetHeading(most_active_axis, compass_val):

    heading = 0
    
    if(most_active_axis == 0): # x-axis 
        heading = math.atan2(compass_val.z, compass_val.y)

    if(most_active_axis == 1): # y-axis 
        heading = math.atan2(compass_val.x, compass_val.z)

    if(most_active_axis == 2): # z-axis 
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

accel_maxima = Vector(0, 0, 0)
accel_minima = Vector(0, 0, 0)
accel_val = Vector(0, 0, 0)
gravity = Vector(0, 0, 0)
peak_direction = MINIMA
moving_index = 0
accel_filter_list = []
accel_list = []
num_steps = 0
sample_new = Vector(0, 0, 0)
time_window = 0
time_threshold = 0
peak_threshold = 0
sum_threshold = 0
stride_length = 0
total_distance = 0
heading_filter_list = []
heading_moving_index = 0
calibrate_threshold = True
calculate_distance = False

size = 0
sum_diff = 0
num_diff = 0

# initialization stage

most_active_axis = 1

for i in range(4) :
    accel_xout = read_word_2c(mpu_address, 0x3b)
    accel_yout = read_word_2c(mpu_address, 0x3d)
    accel_zout = read_word_2c(mpu_address, 0x3f)

    accel_val = Vector(accel_xout, accel_yout, accel_zout)
    accel_filter_list.append(accel_val)

# print "MOST ACTIVE AXIS: ", most_active_axis
# print "\n---CALIBRATION STAGE---"

# calibration_time = time.time()
# calibration_size = 0

# while(time.time() - calibration_time <= 5):
#     accel_xout = read_word_2c(mpu_address, 0x3b)
#     accel_yout = read_word_2c(mpu_address, 0x3d)
#     accel_zout = read_word_2c(mpu_address, 0x3f)

#     gravity.x = HIGH_PASS * gravity.x + (1 - HIGH_PASS) * accel_xout
#     gravity.y = 0
#     gravity.z = HIGH_PASS * gravity.z + (1 - HIGH_PASS) * accel_zout

#     accel_xout = accel_xout - gravity.x
#     accel_yout = accel_yout - gravity.y
#     accel_zout = accel_zout - gravity.z

#     sum_x += accel_xout
#     sum_y += accel_yout
#     sum_z += accel_zout

#     calibration_size += 1

# accel_offset_x = sum_x/calibration_size
# accel_offset_y = 0
# accel_offset_z = sum_z/calibration_size

accel_offset_x = 0
accel_offset_y = 0
accel_offset_z = 0

# print "\n----END CALIBRATION"
# print "\nCALIBRATION SIZE: " , calibration_size  
# print "OFFSET: ", accel_offset_x, accel_offset_y, accel_offset_z

#accel_graph = open('accel_graph_teehee.txt', 'w')
print "STRIDE_COEFFICIENT: ", STRIDE_COEFFICIENT
print "START!!"

time.sleep(1)

first_time = True


time_elapsed = time.time()
while(True):

    size += 1

    # filter accelerometer values
    accel_xout = read_word_2c(mpu_address, 0x3b) - accel_offset_x
    accel_yout = read_word_2c(mpu_address, 0x3d) - accel_offset_y
    accel_zout = read_word_2c(mpu_address, 0x3f) - accel_offset_z

    accel_val = Vector(accel_xout, accel_yout, accel_zout)

    gravity.x = HIGH_PASS * gravity.x + (1 - HIGH_PASS) * accel_val.x
    gravity.y = 0
    gravity.z = HIGH_PASS * gravity.z + (1 - HIGH_PASS) * accel_val.z

    accel_val.x = accel_val.x - gravity.x
    accel_val.y = accel_val.y - gravity.y
    accel_val.z = accel_val.z - gravity.z
    
    accel_val.x = (accel_filter_list[0].x + accel_filter_list[1].x + accel_filter_list[2].x + accel_filter_list[3].x + accel_val.x) / 5
    accel_val.y = (accel_filter_list[0].y + accel_filter_list[1].y + accel_filter_list[2].y + accel_filter_list[3].y + accel_val.y) / 5
    accel_val.z = (accel_filter_list[0].z + accel_filter_list[1].z + accel_filter_list[2].z + accel_filter_list[3].z + accel_val.z) / 5

    accel_filter_list.insert(moving_index, accel_val)
    moving_index = (moving_index + 1) % 4
    #accel_graph.write(str(size) + "\t" + str(accel_val.x) + "\t" + str(accel_val.y) + "\t" + str(accel_val.z))
    
    # finding minima and maxima
    if(not first_time):
        if( math.fabs( compare(most_active_axis, sample_new, accel_val)) >= ACCEL_THRESHOLD):
            sample_new = accel_val
            time_threshold = time.time()
            accel_list.append(accel_val)

            # looking for a minima peak
            if(peak_direction == MINIMA):

                if(compare(most_active_axis, accel_val, accel_maxima) > 0):
                    accel_maxima = accel_val
                
                else:

                    if(calculate_distance):
                        stride_length = getStrideLength(accel_list)
                        total_distance += stride_length
                        print "stride length", stride_length
                        print "total distance:", total_distance
                        accel_list = []
                        #accel_graph.write("\t" + "maxima teehee")
                        sum_diff += math.fabs(accel_maxima.y - accel_minima.y)
                        num_diff += 1
                        calculate_distance = False

                    if( compare(most_active_axis, accel_maxima, accel_val) >= peak_threshold ):
                        #print "minima coming"
                        if(time.time() - time_window >= TIME_THRESHOLD):
                            # a maxima has been detected and a step is detected
                            num_steps += 1
                            peak_direction = MAXIMA
                            accel_minima = accel_val
                            time_window = time.time()
                            print "------ PEAK DETECTED MINIMA", num_steps
                            peak_threshold = PEAK_THRESHOLD
                            calculate_distance = True


            # looking for a maxima peak
            if( peak_direction == MAXIMA ):
                
                if(compare(most_active_axis, accel_val, accel_minima) < 0):
                    accel_minima = accel_val

                else:

                    if(calculate_distance):
                        stride_length = getStrideLength(accel_list)
                        total_distance += stride_length
                        print "stride length", stride_length
                        print "total distance:", total_distance
                        #accel_graph.write("\t" + "minima teehee")
                        sum_diff += math.fabs(accel_maxima.y - accel_minima.y)
                        num_diff += 1
                        accel_list = []
                        calculate_distance = False

                    if(compare(most_active_axis, accel_val, accel_minima) >= peak_threshold ):
                        #print "maxima coming"
                        if(time.time() - time_window >= TIME_THRESHOLD):
                            # a maxima has been detected and a step is detected
                            num_steps += 1
                            peak_direction = MINIMA
                            accel_maxima = accel_val
                            time_window = time.time()
                            print "----- PEAK DETECTED MAXIMA", num_steps
                            peak_threshold = PEAK_THRESHOLD
                            calculate_distance = True

    else:
        peak_direction = MINIMA
        peak_threshold = PEAK_THRESHOLD / 2
        accel_maxima = accel_val
        #accel_graph.write("\t" + "maxima teehee")
        first_time = False
        sample_new = accel_val
        time_window = time.time()

    #accel_graph.write("\n")

print "threshold ", sum_diff / num_diff
#accel_graph.close()
