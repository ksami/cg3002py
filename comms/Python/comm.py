#import XBee
import time

#xbee = Xbee.Xbee("COM3")

def send(queue, string):
	#xbee.SendStr(string)
	time.sleep(2)
	queue.put(string + " has been sent")

def receive(queue):
	while True:
		#xbee.Receive()
		msg = queue.get()
		print "xbee received: " + msg