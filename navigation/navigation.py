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
STRIDE_COEFFICIENT = 0.0264093915247045 
# from walking in total of 14.4 meters and total_distance (without calibration) 545.260574691

MINIMA = 0
MAXIMA = 1

SCALE = 1.3

GO_FORWARD_UPDATE_TIME = 3
TURN_UPDATE_TIME = 3

LEFT = 0
RIGHT = 1

# register address
power_mgmt_1 = 0x6b # Power management registers
mpu_address = 0x68  # MPU6050 i2c address
hmc_address = 0x1e  # HMC5883l i2c address

# constants for map
baseurl = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'
building = 'COM1'
level = '2'
query = 'Building=' + building + '&' + 'Level=' + level

# mode
NODE = 0
GO_FORWARD = 1
TURN = 2
ARRIVE_DESTINATION = 3

# string constants
MODE = "MODE"
COORDX = "X"
COORDY = "Y"
LEFTORRIGHT = "LEFTORRIGHT"
DESTINATION = "DESTINATION"

class Navigation:

    def __init__(self):

        self.bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

        self.mode = TURN
        self.most_active_axis = 1
        self.coordX = 0
        self.coordY = 0
        self.destination = ""

        # invoking hmc5833l i2c bus inside mpu6050
        self.bus.write_byte_data(mpu_address, 0x6A, 0)
        self.bus.write_byte_data(mpu_address, 0x37, 2)
        self.bus.write_byte_data(mpu_address, power_mgmt_1, 0)

        self.bus.write_byte_data(hmc_address, 0, 0b01110000) # Set to 8 samples @ 15Hz
        self.bus.write_byte_data(hmc_address, 1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
        self.bus.write_byte_data(hmc_address, 2, 0b00000000) # Continuous sampling


        # update time
        self.go_forward_time = 0
        self.turn_time = 0

        # initializing variables needed for imu readings

        self.accel_val = Vector(0, 0, 0)

        # used for step detection (peak-to-peak detection)
        self.peak_direction = MINIMA
        self.accel_maxima = Vector(0, 0, 0)
        self.accel_minima = Vector(0, 0, 0)
        self.num_steps = 0
        self.sample_new = Vector(0, 0, 0)
        self.time_window = 0
        self.peak_threshold = 0
        
        # used for calculating the distance (stride-length and total distance within update time)
        self.accel_list = []
        self.total_distance = 0

        # used for accelerometer filtering
        self.gravity = Vector(0, 0, 0)
        self.moving_index = 0
        self.accel_filter_list = []

        self.calculate_distance = False
        self.first_time = True

        # used for compass heading
        self.compass_val = Vector(0, 0, 0)
        self.heading = 0

        # download map
        response = urllib2.urlopen(baseurl + query)
        jsondata = response.read()
        self.mapinfo = MapInfo(jsondata)

    # call this method when receive start and destination id
    def getShortestPath(self, start, end):
        tup = self.mapinfo.shortestPath(start, end)
        self.coordX = tup.get(COORDX)
        self.coordY = tup.get(COORDY)
        self.destination = tup.get(DESTINATION)

    def execute(self, queue):
        
        ##### initialization stage #####

        accel_xout = read_word_2c(self.bus, mpu_address, 0x3b)
        accel_yout = read_word_2c(self.bus, mpu_address, 0x3d)
        accel_zout = read_word_2c(self.bus, mpu_address, 0x3f)

        self.most_active_axis = 1

        for i in range(4) :
            accel_xout = read_word_2c(self.bus, mpu_address, 0x3b)
            accel_yout = read_word_2c(self.bus, mpu_address, 0x3d) 
            accel_zout = read_word_2c(self.bus, mpu_address, 0x3f)

            self.accel_val = Vector(accel_xout, accel_yout, accel_zout)
            self.accel_filter_list.append(self.accel_val)

        print "STRIDE_COEFFICIENT: ", STRIDE_COEFFICIENT
        print "PEAK THRESHOLD", PEAK_THRESHOLD
        print "TIME THRESHOLD", TIME_THRESHOLD
        print "START!!"

        while(True):
        
            ##### get accelermeter + gyroscope + compass reading #####

            # filter accelerometer values
            accel_xout = read_word_2c(self.bus, mpu_address, 0x3b)
            accel_yout = read_word_2c(self.bus, mpu_address, 0x3d)
            accel_zout = read_word_2c(self.bus, mpu_address, 0x3f)

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
            compass_xout = read_word_2c(self.bus, hmc_address, 3) * SCALE
            compass_yout = read_word_2c(self.bus, hmc_address, 7) * SCALE
            compass_zout = read_word_2c(self.bus, hmc_address, 5) * SCALE

            self.compass_val = Vector(compass_xout, compass_yout, compass_zout)

            # step detection - peak-to-peak detection
            if(not self.first_time):
                if( math.fabs( compare(self.most_active_axis, self.sample_new, self.accel_val)) >= ACCEL_THRESHOLD):
                    self.sample_new = self.accel_val
                    self.accel_list.append(self.accel_val)

                    # looking for a minima peak
                    if(self.peak_direction == MINIMA):

                        if(compare(self.most_active_axis, self.accel_val, self.accel_maxima) > 0):
                            self.accel_maxima = self.accel_val
                        
                        else:

                            if(self.calculate_distance and self.mode == GO_FORWARD):
                                self.total_distance += getStrideLength(self.accel_list)
                                self.accel_list = []
                                self.calculate_distance = False
                                print "TOTAL DISTANCE", self.total_distance

                            if( compare(self.most_active_axis, self.accel_maxima, self.accel_val) >= self.peak_threshold ):
                                if(time.time() - self.time_window >= TIME_THRESHOLD):
                                    # a maxima has been detected and a step is detected
                                    self.num_steps += 1
                                    self.peak_direction = MAXIMA
                                    self.accel_minima = self.accel_val
                                    self.time_window = time.time()
                                    print "PEAK DETECTED MINIMA", self.num_steps
                                    self.peak_threshold = PEAK_THRESHOLD
                                    self.calculate_distance = True


                    # looking for a maxima peak
                    if( self.peak_direction == MAXIMA ):
                        
                        if(compare(self.most_active_axis, self.accel_val, self.accel_minima) < 0):
                            self.accel_minima = self.accel_val

                        else:

                            if(self.calculate_distance and self.mode == GO_FORWARD):
                                self.total_distance += getStrideLength(self.accel_list)
                                self.accel_list = []
                                self.calculate_distance = False
                                print "TOTAL DISTANCE", self.total_distance

                            if(compare(self.most_active_axis, self.accel_val, self.accel_minima) >= self.peak_threshold ):
                                if(time.time() - self.time_window >= TIME_THRESHOLD):
                                    # a maxima has been detected and a step is detected
                                    self.num_steps += 1
                                    self.peak_direction = MINIMA
                                    self.accel_maxima = self.accel_val
                                    self.time_window = time.time()
                                    print "PEAK DETECTED MAXIMA", self.num_steps
                                    self.peak_threshold = PEAK_THRESHOLD
                                    self.calculate_distance = True

            else:
                self.peak_direction = MINIMA
                self.peak_threshold = PEAK_THRESHOLD / 2
                self.accel_maxima = self.accel_val
                self.first_time = False
                self.sample_new = self.accel_val
                self.time_window = time.time()   


            ##### check state machine #####
            self.heading = GetHeading(self.most_active_axis, self.compass_val)
            result = self.mapinfo.giveDirection(self.mode, self.total_distance, self.heading, self.coordY, self.coordY)
            self.mode = result[MODE]
            self.coordX = result[COORDX]
            self.coordY = result[COORDY] 
            feedback = ""

            if(self.mode == TURN):
                if(time.time() - self.turn_time >= TURN_UPDATE_TIME):
                    isLeft = result[LEFTORRIGHT]
                    self.turn_time = time.time()
                    if(isLeft == LEFT):
                        feedback = "tl"
                    else:
                        feedback = "tr"

            elif(self.mode == GO_FORWARD):
                if(time.time() - self.turn_time >= GO_FORWARD_UPDATE_TIME):
                    self.go_forward_time = time.time()
                    self.total_distance = 0
                    feedback = "gf"

            elif(self.mode == REACH_DESTINATION):
                feedback = "r," + self.destination 
                break

            #queue.put({'feedback': feedback, 'coordX', self.coordX, 'coordY', self.coordY)
            print feedback
            queue.put(feedback)


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

def getShortestPath(navi, start, end):
    navi.getShortestPath(start, end)

def exe(navi, queue):
    navi.execute(queue)

import multiprocessing

if __name__ == "__main__":
    navi = Navigation()
    queue = multiprocessing.Queue()
    getShortestPath(navi, 1, 12)
    exe(navi, queue)
