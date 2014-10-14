import XBee
from time import sleep

ARD_ADDR = 0x0001
ARD_OPT = 0x01
ARD_FRAME = 0x00
ARD_BAUDRATE = 9600
ARD_HAND_PACKAGEID = '4'
class Comms:
    
    def __init__(self):
		self.xbee = XBee.XBee("/dev/ttyAMA0",ARD_BAUDRATE)
    
    def DeviceReady(self):
		while True:
	    	self.xbee.SendStr("0",ARD_ADDR,ARD_OPT,ARD_FRAME)
	    	sleep(0.25)
	    	if self.ReceiveAck(): 
				break	
    
    def NaviReady(self):
		while True:
			self.xbee.SendStr("1",ARD_ADDR,ARD_OPT,ARD_FRAME)
			sleep(0.25)
	    	if self.ReceiveAck(): 
				break
    
    def NaviEnd(self):
		while True:
			self.xbee.SendStr("2",ARD_ADDR,ARD_OPT,ARD_FRAME)
			sleep(0.25)
	    		if self.ReceiveAck(): 
					break
    
    def ObstacleDetected(self,direction,strength):
    	Msg = "3{}{}".format(direction,strength)
    	while True:
        	self.xbee.SendStr(Msg,ARD_ADDR,ARD_OPT,ARD_FRAME)
        	sleep(0.25)
	    		if self.ReceiveAck(): 
					break
    
    def ReceiveAck(self):
	Msg = self.xbee.Receive()
        if Msg:
	    content = Msg[7:-1].decode('ascii')
	    return content == 'ACK'
	return False
    
    def ReceiveHandStatus(self): # not sending ack for the moment
        Msg = self.xbee.Receive();
        if Msg:
	    content = Msg[7:-1].decode('ascii')
	    if len(content) == 2 and content[0] == ARD_HAND_PACKAGEID:
		return {'status': content[-1]} # 0: open , 1: close
	return False
