#import XBee
from comms import Comms

DEVICE_READY = "DR"
NAVI_READY = "NR"
NAVI_END = "NE"
OBSTACLE_DETECTED = "OD"
HAND_OPEN = 0
HAND_CLOSE = 1

# params: Comms object, msg = {type: "", val: {dir: "", str: 2}}
def send(comms, msg):
    if msg["type"] == DEVICE_READY:
        comms.DeviceReady()
    elif msg["type"] == NAVI_READY:
        comms.NaviReady()
    elif msg["type"] == NAVI_END:
        comms.NaviEnd()
    elif msg["type"] == OBSTACLE_DETECTED:
        comms.ObstacleDetected(msg.val.dir, msg.val.str)

def receive(q_xbee, comms):
    while True:
        msg = comms.ReceiveHandStatus()
        if msg != False:
            q_xbee.put(msg.status)


# if __name__ == "__main__":

#     # Always instatiate a Comms object
#     comms = Comms();

#     # Shows the all the different information that Pi
#     # sends to Arduino. This methods runs until an 
#     # it receives an acknowledgement from Arduino

#     # comms.DeviceReady()
#     # comms.NaviReady()
#     # comms.NaviEnd()
#     # comms.ObstacleDetected("L",3)

    

#     # The following code represents
#     # the process that always run
    
#     while True:
#         Msg = comms.ReceiveHandStatus()
#         if Msg:
# 	       print str(Msg)
#            break
           
