import smbus
import urllib2
import json
import math
import time
import sys
from vector import Vector
from mapinfo import MapInfo

ACCEL_THRESHOLD = 1000 # = 32767 - 31128 (max and min values when stabilized)
PEAK_THRESHOLD = 10000
TIME_THRESHOLD = 0.4
HEIGHT = 1.76
HIGH_PASS = 0.8
STRIDE_COEFFICIENT = 0.415

MAXIMA = 1

UPDATE_TIME = 3
scale = 1.3

# register address
power_mgmt_1 = 0x6b # Power management registers
mpu_address = 0x68  # MPU6050 i2c address
hmc_address = 0x1e  # HMC5883l i2c address

# constants for map
baseurl = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'
building = 'yimelo'
level = '5'
query = 'Building=' + building + '&' + 'Level=' + level

# mode
GO_FORWARD = 0
TURN_LEFT = 1
TURN_RIGHT = 2
ABOUT_REACH = 3
ARRIVE_DESTINATION = 4

THRESHOLD_DISTANCE = 500

class Navigation:


    def __init__(self):

        self.bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

        # invoking hmc5833l i2c bus inside mpu6050
        self.bus.write_byte_data(mpu_address, 0x6A, 0)
        self.bus.write_byte_data(mpu_address, 0x37, 2)
        self.bus.write_byte_data(mpu_address, power_mgmt_1, 0)

        self.bus.write_byte_data(hmc_address, 0, 0b01110000) # Set to 8 samples @ 15Hz
        self.bus.write_byte_data(hmc_address, 1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
        self.bus.write_byte_data(hmc_address, 2, 0b00000000) # Continuous sampling

        # initializing important attributes
        self.accel_maxima = Vector(0, 0, 0)
        self.accel_minima = Vector(0, 0, 0)
        self.accel_val = Vector(0, 0, 0)
        self.gravity = Vector(0, 0, 0)
        self.peak_direction = MINIMA
        self.moving_index = 0
        self.accel_filter_list = []
        self.accel_list = []
        self.num_steps = 0
        self.sample_new = Vector(0, 0, 0)
        self.time_window = 0
        self.peak_threshold = 0
        self.sum_threshold = 0
        self.stride_length = 0
        self.total_distance = 0
        self.calibrate_threshold = True
        self.calculate_distance = True
        self.most_active_axis = 1

        # download map
        building = bldg
        level = lvl
        response = urllib2.urlopen(baseurl + query)
        jsondata = response.read()
        self.mapinfo = MapInfo(jsondata)

    # call this method when receive start and destination id
    def getShortestPath(self, start, end):
        self.mapinfo.shortestPath(start, end)

    def execute(self, queue):

        # initialization stage
        accel_xout = read_word_2c(self.bus, mpu_address, 0x3b)
        accel_yout = read_word_2c(self.bus, mpu_address, 0x3d)
        accel_zout = read_word_2c(self.bus, mpu_address, 0x3f)

        self.most_active_axis = 1

        for i in range(4) :
            accel_xout = read_word_2c(self.bus, mpu_address, 0x3b)
            accel_yout = read_word_2c(self.bus, mpu_address, 0x3d) 
            accel_zout = read_word_2c(self.bus, mpu_address, 0x3f)

            accel_val = Vector(accel_xout, accel_yout, accel_zout)
            self.accel_filter_list.append(accel_val)

        first_time = True

        print "STRIDE_COEFFICIENT: ", STRIDE_COEFFICIENT
        print "PEAK THRESHOLD", PEAK_THRESHOLD
        print "TIME THRESHOLD", TIME_THRESHOLD
        print "START!!"

        update_time = time.time()

        while(True):

            # filter accelerometer values
            accel_xout = read_word_2c(mpu_address, 0x3b)
            accel_yout = read_word_2c(mpu_address, 0x3d)
            accel_zout = read_word_2c(mpu_address, 0x3f)

            self.accel_val = Vector(accel_xout, accel_yout, accel_zout)

            self.gravity.x = HIGH_PASS * self.gravity.x + (1 - HIGH_PASS) * self.accel_val.x
            self.gravity.y = 0
            self.gravity.z = HIGH_PASS * self.gravity.z + (1 - HIGH_PASS) * self.accel_val.z

            self.accel_val.x = self.accel_val.x - self.gravity.x
            self.accel_val.y = self.accel_val.y - self.gravity.y
            self.accel_val.z = self.accel_val.z - self.gravity.z
            
            self.accel_val.x = (self.accel_filter_list[0].x + self.accel_filter_list[1].x + self.accel_filter_list[2].x + self.accel_filter_list[3].x + self.accel_val.x) / 5
            self.accel_val.y = (self.accel_filter_list[0].y + self.accel_filter_list[1].y + self.accel_filter_list[2].y + self.accel_filter_list[3].y + self.accel_val.y) / 5
            self.accel_val.z = (self.accel_filter_list[0].z + self.accel_filter_list[1].z + self.accel_filter_list[2].z + self.accel_filter_list[3].z + self.accel_val.z) / 5

            self.accel_filter_list.insert(self.moving_index, self.accel_val)

            self.moving_index = (self.moving_index + 1) % 4

            # filter compass values
            compass_xout = read_word_2c(self.bus, hmc_address, 3) * scale
            compass_yout = read_word_2c(self.bus, hmc_address, 7) * scale
            compass_zout = read_word_2c(self.bus, hmc_address, 5) * scale

            self.compass_val = Vector(compass_xout, compass_yout, compass_zout)

            # finding maximum, minimum
            if(not first_time):
                if( math.fabs( compare(self.most_active_axis, self.sample_new, self.accel_val)) >= ACCEL_THRESHOLD):
                    self.sample_new = self.accel_val
                    self.accel_list.append(self.accel_val)

                    # looking for a minima peak
                    if(self.peak_direction == MINIMA):

                        if(compare(self.most_active_axis, self.accel_val, self.accel_maxima) > 0):
                            self.accel_maxima = self.accel_val
                            # calculate_distance = True
                        
                        else:

                            # if(calculate_distance):
                            #     stride_length = getStrideLength(accel_list)
                            #     total_distance += stride_length
                            #     print "accel list", len(accel_list)
                            #     print "stride length", stride_length
                            #     print "total_distance", total_distance
                            #     accel_graph.write(str(num_steps) + "\t" + str(stride_length) + "\t" + str(len(accel_list)) + "\n")
                            #     accel_list = []
                            #     calculate_distance = False

                            if( compare(self.most_active_axis, self.accel_maxima, self.accel_val) >= self.peak_threshold ):
                                #print "minima coming"
                                if(time.time() - self.time_window >= TIME_THRESHOLD):
                                    # a maxima has been detected and a step is detected
                                    self.num_steps += 1
                                    self.peak_direction = MAXIMA
                                    self.accel_minima = self.accel_val
                                    self.time_window = time.time()
                                    self.stride_length = STRIDE_COEFFICIENT * HEIGHT
                                    total_distance += self.stride_length
                                    print "PEAK DETECTED MINIMA", self.num_steps
                                    print "total distance", self.total_distance
                                    peak_threshold = PEAK_THRESHOLD
                                    

                    # looking for a maxima peak
                    if( self.peak_direction == MAXIMA ):
                        
                        if(compare(self.most_active_axis, self.accel_val, self.accel_minima) < 0):
                            self.accel_minima = self.accel_val
                            # calculate_distance = True

                        else:

                            # if(calculate_distance):
                            #     stride_length = getStrideLength(accel_list)
                            #     total_distance += stride_length
                            #     print "accel list", len(accel_list)
                            #     print "stride length", stride_length
                            #     print "total_distance", total_distance
                            #     accel_graph.write(str(num_steps) + "\t" + str(stride_length) + "\t" + str(len(accel_list)) + "\n")
                            #     accel_list = []
                            #     calculate_distance = False

                            if(compare(self.most_active_axis, self.accel_val, self.accel_minima) >= self.peak_threshold ):
                                #print "maxima coming"
                                if(time.time() - self.time_window >= TIME_THRESHOLD):
                                    # a maxima has been detected and a step is detected
                                    self.num_steps += 1
                                    self.peak_direction = MINIMA
                                    self.accel_maxima = self.accel_val
                                    self.time_window = time.time()
                                    self.stride_length = STRIDE_COEFFICIENT * HEIGHT
                                    self. total_distance += self.stride_length
                                    print "PEAK DETECTED MAXIMA", self.num_steps
                                    print "total distance", self.total_distance
                                    peak_threshold = PEAK_THRESHOLD

            else:
                peak_direction = MINIMA
                peak_threshold = PEAK_THRESHOLD / 2
                accel_maxima = accel_val
                first_time = False
                sample_new = accel_val
                time_window = time.time()    

            if(time.time() - update_time <= UPDATE_TIME):
                heading = getHeading(self.most_active_axis, self.compass_val)
                tup = self.mapinfo.giveDirection(self.total_distance, heading)
                self.total_distance = 0
                feedback = ""

                if(tup[0] == GO_FORWARD):
                    feedback = "Please go forward"
                elif(tup[0] == TURN_LEFT):
                    feedback = "Please turn left with angle " + str(tup[1])
                elif(tup[0] == TURN_RIGHT):
                    feedback = "Please turn right with angle " + str(tup[1])
                elif(tup[0] == ABOUT_REACH):
                    feedback = "You are about to reach " + tup[2]
                else:
                    feedback = "You reach your destination " + tup[2]

                queue.put({'feedback': feedback, 'coordX', tup[3], 'coordY', tup[4]})


def read_word(bus, sensor_address, adr):
    high = bus.read_byte_data(sensor_address, adr)
    low = bus.read_byte_data(sensor_address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(bus, sensor_address, adr):
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

def getHeading(most_active_axis, compass_val):

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