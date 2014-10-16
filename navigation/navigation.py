import smbus
import urllib2
import json
import math
import time
import sys
from vector import Vector
from mapinfo import MapInfo

# constants for pedometer
SAMPLE_SIZE = 50
PRECISION = 1000 # = 32767 - 31128 (max and min values when stabilized)
HEIGHT = 1.76
CONSTANT_STRIDE = 0.415
TIME_WINDOW_MIN = 0.3
X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2 
UPDATE_TIME = 3
#TIME_WINDOW_MAX = 2
#HEIGHT = 1.77 # in meters
#STANDING_MODE = 0
#WALKING_MODE = 1
scale = 1.3
most_active_axis = 2
#mode = STANDING_MODE

# Power management registers
power_mgmt_1 = 0x6b

# MPU6050 i2c address
mpu_address = 0x68 

# HMC5883l i2c address
hmc_address = 0x1e

# constants for map
baseurl = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'
building = 'yimelo'
level = '5'
query = 'Building=' + building + '&' + 'Level=' + level
orienInfo = 0
mapInfo = 0
wifiInfo = 0

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
        self.accel_max = Vector(0, 0, 0)
        self.accel_min = Vector(sys.maxint, sys.maxint, sys.maxint)
        self.dynamic_threshold = Vector(0, 0, 0) # the moving average of 50 accelerometer data
        self.accel_val = Vector(0, 0, 0)
        self.compass_val = Vector(0, 0, 0)
        self.most_active_axis = Z_AXIS
        self.moving_index = 0
        self.sample_size = 0
        self.accel_filter_list = []
        self.sample_old = Vector(0, 0, 0)
        self.sample_new = Vector(0, 0, 0)
        self.num_steps = 0
        self.time_window = 0
        self.total_distance = 0

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

        max_axis = accel_zout
        if(max_axis < accel_xout):
            max_axis = accel_xout
            self.most_active_axis = 0
        if(max_axis < accel_yout):
            max_axis = accel_xout
            self.most_active_axis = 1

        for i in range(4) :
            accel_xout = read_word_2c(self.bus, mpu_address, 0x3b)
            accel_yout = read_word_2c(self.bus, mpu_address, 0x3d)
            accel_zout = read_word_2c(self.bus, mpu_address, 0x3f)

            accel_val = Vector(accel_xout, accel_yout, accel_zout)
            self.accel_filter_list.append(accel_val)

        first_time = True

        print "TIME_WINDOW_MIN: ", TIME_WINDOW_MIN
        print "TIME_WINDOW_MAX: ", TIME_WINDOW_MAX
        print "PRECISION: " , PRECISION

        update_time = time.time()

        while(True):

            if(self.sample_size == SAMPLE_SIZE):
                self.sample_size = 0
               # print "--------------------------------- finished 50 samples \n"

                self.dynamic_threshold.x = (self.accel_max.x + self.accel_min.x) / 2
                self.dynamic_threshold.y = (self.accel_max.y + self.accel_min.y) / 2
                self.dynamic_threshold.z = (self.accel_max.z + self.accel_min.z) / 2

                self.accel_max = Vector(0, 0, 0)
                self.accel_min = Vector(sys.maxint, sys.maxint, sys.maxint)

                first_time = False

            #filter accelerometer values
            accel_xout = read_word_2c(self.bus, mpu_address, 0x3b)
            accel_yout = read_word_2c(self.bus, mpu_address, 0x3d)
            accel_zout = read_word_2c(self.bus, mpu_address, 0x3f)

            self.accel_val = Vector(accel_xout, accel_yout, accel_zout)

            self.accel_val.x = (self.accel_filter_list[0].x + self.accel_filter_list[1].x + self.accel_filter_list[2].x + self.accel_filter_list[3].x + self.accel_val.x) / 5
            self.accel_val.y = (self.accel_filter_list[0].y + self.accel_filter_list[1].y + self.accel_filter_list[2].y + self.accel_filter_list[3].y + self.accel_val.y) / 5
            self.accel_val.z = (self.accel_filter_list[0].z + self.accel_filter_list[1].z + self.accel_filter_list[2].z + self.accel_filter_list[3].z + self.accel_val.z) / 5
            
            self.accel_filter_list.insert(self.moving_index, accel_val)

            # filter compass values
            compass_xout = read_word_2c(self.bus, hmc_address, 3) * scale
            compass_yout = read_word_2c(self.bus, hmc_address, 7) * scale
            compass_zout = read_word_2c(self.bus, hmc_address, 5) * scale

            self.compass_val = Vector(compass_xout, compass_yout, compass_zout)

            self.moving_index = (self.moving_index + 1) % 4
            self.sample_size += 1    

            # finding maximum, minimum
            if(compare(self.accel_max, self.accel_val) < 0):
                self.accel_max = self.accel_val
            if(compare(self.accel_min, self.accel_val) > 0):
                self.accel_min = self.accel_val

            if(not first_time):
                self.sample_old = self.sample_new	

                if( math.fabs(compare(self.accel_val, self.sample_new)) > PRECISION ):
                    self.sample_new = self.accel_val
        	
                    if( compare(self.sample_new, self.dynamic_threshold) < 0 and compare(self.dynamic_threshold, self.sample_old) < 0):
                        if(time.time() - self.time_window >= TIME_WINDOW_MIN ):
                            self.num_steps += 1
                            print "WALKING MODE: num_steps =", num_steps, "------------", time.time() - time_window
                            self.time_window = time.time()
                            self.total_distance += HEIGHT * CONSTANT_STRIDE

            else:
                sample_new = accel_val


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

def compare(accel_1, accel_2):

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

    if(most_active_axis == 2): # x-axis 
        heading = math.atan2(compass_val.y, compass_val.x)

    heading += 0.0404

    if(heading < 0):
        heading += 2*math.pi

    if(heading > 2*math.pi):
        heading -= 2*math.pi

    return math.degrees(heading)