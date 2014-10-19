import XBee
from time import sleep
from multiprocessing import Queue

ARD_ADDR = 0x0001
ARD_OPT = 0x01
ARD_FRAME = 0x00
ARD_BAUDRATE = 9600
ARD_HAND_PACKAGEID = '4'

class Comms:
	
	q_ack = Queue()

	def __init__(self):
		self.xbee = XBee.XBee("/dev/ttyAMA0",ARD_BAUDRATE)
	
	def DeviceReady(self):
		delay = 2
		while True:
			self.xbee.SendStr("0",ARD_ADDR,ARD_OPT,ARD_FRAME)
			sleep(delay)
			delay = delay * 2
			if delay >= 32:
				delay = 2
			if self.ReceiveAck(): 
				break	
	
	def NaviReady(self):
		delay = 2
		while True:
			self.xbee.SendStr("1",ARD_ADDR,ARD_OPT,ARD_FRAME)
			sleep(delay)
			delay = delay * 2
			if delay >= 32:
				delay = 2
			if self.ReceiveAck(): 
				break
	
	def NaviEnd(self):
		delay = 2
		while True:
			self.xbee.SendStr("2",ARD_ADDR,ARD_OPT,ARD_FRAME)
			sleep(delay)
			delay = delay * 2
			if delay >= 32:
				delay = 2
			if self.ReceiveAck(): 
				break
	
	def ObstacleDetected(self,direction,strength):
		delay = 2
		Msg = "3{}{}".format(direction,strength)
		while True:
			self.xbee.SendStr(Msg,ARD_ADDR,ARD_OPT,ARD_FRAME)
			sleep(delay)
			delay = delay * 2
			if delay >= 32:
				delay = 2
			if self.ReceiveAck(): 
				break
	
	def Receive(self, q_hs):
		Msg = self.xbee.Receive()
		if Msg:
			content = Msg[7:-1].decode('ascii')
			print "receive: ", content

			if content == 'ACK':
				self.q_ack.put(True)
			elif len(content) == 2 and content[0] == ARD_HAND_PACKAGEID:
				q_hs.put({'status': content[-1]})# 0: open , 1: close
		else:
			return False

	def rcv(self):
		msg = self.xbee.Receive()
		if msg:
			content = msg[7:-1].decode('ascii')
			return content


	def ReceiveAck(self):
		# Msg = self.xbee.Receive()
		# if Msg:
		# 	content = Msg[7:-1].decode('ascii')
		# 	print "ack: ", content
		# 	return content == 'ACK'
		# return False
		try:
			ack = self.q_ack.get(block=False)
			return ack
		# Queue.empty
		except Exception:
			return False
	
	# def ReceiveHandStatus(self): # not sending ack for the moment
	# 	# Msg = self.xbee.Receive()
	# 	# if Msg:
	# 	# 	content = Msg[7:-1].decode('ascii')
	# 	# 	print "handstatus: ", content
	# 	# 	if len(content) == 2 and content[0] == ARD_HAND_PACKAGEID:
	# 	# 		return {'status': content[-1]} # 0: open , 1: close
	# 	# return False
	# 	hs = self.q_hs.get()
	# 	return hs
