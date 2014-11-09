import smbus
import urllib2
import json
import math
import time
import sys
from vector import Vector
from mapinfolist import MapInfoList

# Calibration constants
ACCEL_THRESHOLD = 1000 # = 32767 - 31128 (max and min values when stabilized)
PEAK_THRESHOLD = 10000
TIME_THRESHOLD = 0.4
HIGH_PASS = 0.8
STRIDE_COEFFICIENT = 1.319148936
COMPASS_X_AXIS = -145 # this was obtained with a laptop nearby. Ill do it again when i use wifi dongle
COMPASS_Z_AXIS = -135

# Peak-to-peak detection modes
MINIMA = 0
MAXIMA = 1

# Feedback time
GO_FORWARD_UPDATE_TIME = 6
TURN_UPDATE_TIME = 3

# Turning directions
LEFT = 0
RIGHT = 1

# register address
power_mgmt_1 = 0x6b # Power management registers
mpu_address = 0x68  # MPU6050 i2c address
hmc_address = 0x1e  # HMC5883l i2c address
bmp_address = 0x77  # BMP180 i2c address

# state machine mode
START_JOURNEY = 0
START_BUILDING = 1
REACH_NODE = 2
GO_FORWARD = 3
TURN = 4
REACH_DEST_BUILDING = 5
ARRIVE_DESTINATION = 6

# Dictionary key
MODE = "MODE"
COORDX = "X"
COORDY = "Y"
ANGLE = "ANGLE"
NODE_NAME = "NODE_NAME"
LEFTORRIGHT = "LEFTORRIGHT"
DESTINATION = "DESTINATION"
NUMBER_NODES = "NUMBER_NODES"
CURRENT_NODE = "CURRENT_NODE"
NUMBER_OF_BUILDINGS = "NUMBER_OF_BUILDINGS"
CURRENT_BUILDING = "CURRENT_BUILDING"

class Navigation:

    def __init__(self):

        self.bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

        self.mode = START_JOURNEY
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
        self.steps = 0

        # used for calculating the distance (stride-length and total distance within update time)
        self.accel_list = []
        self.distance = 0
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
        self.heading_filter_list = []
        self.heading_moving_index = 0

        # download map
        self.mapinfolist = MapInfoList()

    # call this method when receive start and destination id
    def getShortestPath(self, startBuilding, startLevel, startNode, endBuilding, endLevel, endNode):
        tup = self.mapinfolist.shortestPath(startBuilding, startLevel, startNode, endBuilding, endLevel, endNode)

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

            compass_xout = read_word_2c(self.bus, hmc_address, 3)
            compass_yout = read_word_2c(self.bus, hmc_address, 7) 
            compass_zout = read_word_2c(self.bus, hmc_address, 5)

            self.compass_val = Vector(compass_xout, compass_yout, compass_zout)
            self.heading = GetHeading(self.most_active_axis, self.compass_val)

            self.heading_filter_list.append(self.heading)


        print "\n\nSTRIDE_COEFFICIENT: ", STRIDE_COEFFICIENT
        print "PEAK THRESHOLD", PEAK_THRESHOLD
        print "TIME THRESHOLD", TIME_THRESHOLD
        print "START!!"

        while(True):
        
            # mode GO_FORWARD will update the distance and heading
            if(self.mode == GO_FORWARD):

                time_exe = time.time()

                ##### get accelermeter reading #####

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
                                    stride = getStrideLength(self.accel_list)
                                    print "--------------- STRIDE", stride
                                    self.distance += stride
                                    self.total_distance += stride
                                    self.accel_list = []
                                    self.calculate_distance = False
                                    #print "TOTAL DISTANCE", self.total_distance

                                if( compare(self.most_active_axis, self.accel_maxima, self.accel_val) >= self.peak_threshold ):
                                    if(time.time() - self.time_window >= TIME_THRESHOLD):
                                        # a maxima has been detected and a step is detected
                                        self.num_steps += 1
                                        self.steps += 1
                                        self.peak_direction = MAXIMA
                                        self.accel_minima = self.accel_val
                                        self.time_window = time.time()
                                        print "\n--------------- PEAK DETECTED MINIMA", self.num_steps
                                        self.peak_threshold = PEAK_THRESHOLD
                                        self.calculate_distance = True


                        # looking for a maxima peak
                        if( self.peak_direction == MAXIMA ):
                            
                            if(compare(self.most_active_axis, self.accel_val, self.accel_minima) < 0):
                                self.accel_minima = self.accel_val

                            else:

                                if(self.calculate_distance and self.mode == GO_FORWARD):
                                    stride = getStrideLength(self.accel_list)
                                    print "--------------- STRIDE", stride
                                    self.distance += stride
                                    self.total_distance += stride
                                    self.accel_list = []
                                    self.calculate_distance = False

                                if(compare(self.most_active_axis, self.accel_val, self.accel_minima) >= self.peak_threshold ):
                                    if(time.time() - self.time_window >= TIME_THRESHOLD):
                                        # a maxima has been detected and a step is detected
                                        self.num_steps += 1
                                        self.steps += 1
                                        self.peak_direction = MINIMA
                                        self.accel_maxima = self.accel_val
                                        self.time_window = time.time()
                                        print "\n--------------- PEAK DETECTED MAXIMA", self.num_steps
                                        self.peak_threshold = PEAK_THRESHOLD
                                        self.calculate_distance = True

                else:
                    self.peak_direction = MINIMA
                    self.peak_threshold = PEAK_THRESHOLD / 2
                    self.accel_maxima = self.accel_val
                    self.first_time = False
                    self.sample_new = self.accel_val
                    self.time_window = time.time()   

                #print "time ", time.time() - time_exe

            # reading compass values
            compass_xout = read_word_2c(self.bus, hmc_address, 3) - COMPASS_X_AXIS
            compass_yout = read_word_2c(self.bus, hmc_address, 7) 
            compass_zout = read_word_2c(self.bus, hmc_address, 5) - COMPASS_Z_AXIS

            self.compass_val = Vector(compass_xout, compass_yout, compass_zout)
            self.heading = GetHeading(self.most_active_axis, self.compass_val)
            self.heading_moving_index = (self.heading_moving_index + 1) % 4

            ##### check state machine #####
            result = self.mapinfolist.giveDirection(self.distance, self.heading, self.coordX, self.coordY, self.steps)
            self.steps = 0
            self.distance = 0
            self.mode = result[MODE]
            self.coordX = result[COORDX]
            self.coordY = result[COORDY] 
            feedback = ""

            if(self.mode == START_JOURNEY):
                numberBuildings = result[NUMBER_OF_BUILDINGS]
                
                #feedback is "You have to walk through " + str(numberBuildings) + " building(s)"
                feedback = "sj," + str(numberBuildings)
                print "\n\nMODE: START_JOURNEY ---\n" + feedback

            elif(self.mode == START_BUILDING):
                numberNodes = result[NUMBER_NODES]
                currentBuilding = result[CURRENT_BUILDING]
                building = "COM 1"
                level = 2

                if(currentBuilding == 1):
                    building = "COM 2"
                    level = 2
                elif(currentBuilding == 2):
                    building = "COM 2"
                    level = 3

                # feedback is "You are currently at building " + str(building) + " level " + str(level) + "\nYou have to walk pass " + str(numberNodes) + " nodes" "\nNow starting at node 1"                    
                feedback = "sb," + str(building) + "," + str(level) + "," + str(numberNodes)
                print "\n\n--- MODE: START_BUILDING ---\n" + feedback + "\nCOORDX: " + str(self.coordX) + "   COORDY: " + str(self.coordY)

            elif(self.mode == REACH_NODE):
                currentNode = result[CURRENT_NODE]
                # feedback is "You have reached node " + str(currentNode)
                feedback = "rn," + str(currentNode)
                print "\n\n--- MODE: REACH_NODE ---\n" + feedback + "\nCOORDX: " + str(self.coordX) + "   COORDY: " + str(self.coordY)

            elif (self.mode == TURN):
                if(time.time() - self.turn_time >= TURN_UPDATE_TIME):
                    isLeft = result[LEFTORRIGHT]
                    angle = result[ANGLE]
                    self.turn_time = time.time()
                    if(isLeft == LEFT):

                        # feedback is "Turn left by " + str(angle) + " degrees"
                        feedback = "tl," + str(angle)
                    else:
                        
                        # feedback is "Turn right by " + str(angle) + " degrees"
                        feedback = "tr," + str(angle)
                    print "\n\n--- MODE: TURN ---\n" + feedback


            elif(self.mode == GO_FORWARD):
                if(time.time() - self.go_forward_time >= GO_FORWARD_UPDATE_TIME):
                    self.go_forward_time = time.time()
                    feedback = "gf"
                    print "\n\n--- MODE: GO_FORWARD ---\n" + "Go forward" + "\nCOORDX: " + str(self.coordX) + "   COORDY: " + str(self.coordY)

            elif(self.mode == ARRIVE_DESTINATION):
                print "REACH DESTINATION"
                feedback = "r"
                print "\n\nMODE: ARRIVE DESTINATION ---"
                queue.put(feedback)
                break

            if feedback != "":
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
        accel_sum += accel_list[i].y
    accel_avg = accel_sum / len(accel_list)

    for i in range(len(accel_list)):
        accel_sum += (accel_list[i].y - accel_avg)
    accel_sum /= len(accel_list)

    #print "accel_sum", accel_sum

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

import multiprocessing

if __name__ == "__main__":
    navi = Navigation()
    queue = multiprocessing.Queue()
    navi.getShortestPath(1, 2, 1, 1, 2, 2)
    navi.execute(queue)
