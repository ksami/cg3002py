#import XBee
from Comms import Comms

if __name__ == "__main__":

    # Always instatiate a Comms object
    comms = Comms();

    # Shows the all the different information that Pi
    # sends to Arduino. This methods runs until an 
    # it receives an acknowledgement from Arduino

    # comms.DeviceReady()
    # comms.NaviReady()
    # comms.NaviEnd()
    # comms.ObstacleDetected("L",3)

    

    # The following code represents
    # the process that always run
    
    while True:
        Msg = comms.ReceiveHandStatus();
        if Msg:
	    print str(Msg)
            break;        
