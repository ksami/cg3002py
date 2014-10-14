# Main file handling multiple processes

import multiprocessing
import time

import timer
import smwmap
import cpython
import audio.textspeech
import pedometer.test
from comms.python.comms import Comms
from state import State


cameraExe = "./cprocess.o"
mapName = "COM1"
mapFloor = "2"
sendStr = "xbee string to send"

systemState = State()
comms = Comms()

def main():
	setup()

	while True:
		currentState = systemState.getCurrentState()

		if currentState == State.STATE_OFF:
			executeOff()

		elif currentState == State.STATE_IDLE:
			executeIdle()

		elif currentState == State.STATE_INIT:
			executeInit()
		
		elif currentState == State.STATE_NAVI:
			executeNavi()
		
		elif currentState == State.STATE_WAIT:
			executeWait()
		
		else:
			pass

# Creates a new process
# params: function to call, tuple of arguments
# returns: process
def createProcess(function, args=()):
	return multiprocessing.Process(target=function, args=args)

# Creates a new queue
# returns: queue
def createQueue():
	return multiprocessing.Queue()


def setup():
	pass
	# Queues
	# # global q_cam = createQueue()
	# # global q_map = createQueue()
	# global q_xbee = createQueue()
	# global q_time = createQueue()

	# Processes
	# # global p_send = createProcess(function=comms.Python.comm.send, args=(sendStr,))
	# global p_receive = createProcess(function=comms.Python.comm.receive, args=(q_xbee,))
	# global p_pedo = createProcess(function=pedometer.test.execute)
	# global p_camera = createProcess(function=cpython.execute, args=(q_cam, cameraExe))
	# # global p_texttospeech = createProcess(function=audio.textspeech.speakq, args=(q_cam,))
	# # global p_alarm = createProcess(function=timer.alarm, args=(4,))
	# # global p_getmap = createProcess(function=smwmap.obtainMap, args=(q_map, mapName, mapFloor))

	# Start xbee receive
	# p_receive.start()


def executeOff():
	print "in off state"
	#send device ready to arduino
	#handle timeout and repeated sending
	# isDone = False
	
	# while isDone == False:
	# 	p_send = createProcess(comms.Python.comm.send, ("device ready",))
	# 	p_send.start()
	# 	p_send.join(timeout=2) #TODO possibility of not joining
		
	# 	recvmsg = q_xbee.get()
	# 	if recvmsg is not None:
	# 		isDone = True

	# #arduino ack
	# if recvmsg == "ACK":
	# 	systemState.changeState()


def executeIdle():
	print "in idle state"
	#nothing
	# isDone = False
	
	# while isDone == False:
	# 	recvmsg = q_xbee.get()
	# 	if (recvmsg is not None) and (recvmsg == "NAVI READY"):
	# 		isDone = True

	# systemState.changeState()

def executeInit():
	print "in init state"
	#ask user for end location and confirm
	#get map
	#
	# # Boolean for returning to IDLE state
	# isCancel = False
	#
	# # Get and confirm start point
	# isDone = False
	#
	# while (isDone == False) and (isCancel == False):
	# 	p_texttospeech = createProcess(audio.textspeech.speak, ("Please state your starting point",))
	# 	p_texttospeech.start()
	# 	p_texttospeech.join()
	#
	#	startpt = speechtotext listen #TODO
	#	time.sleep(2)
	#	
	#	recvmsg = q_xbee.get()
	# 	if (recvmsg is not None) and (recvmsg == "TERMINATE"):
	# 		isCancel = True
	#	
	#	if startpt is not None:
	#		isConfirmed = False
	#		
	#		while (isConfirmed == False) and (isCancel == False):
	#			p_texttospeech = createProcess(audio.textspeech.speak, ("Please confirm, starting point is " + startpt,))
	#		 	p_texttospeech.start()
	# 			p_texttospeech.join()
	# 			
	# 			confirm = speechtotext listen #TODO
	# 			time.sleep(2)
	# 			
	# 			recvmsg = q_xbee.get()
	# 			if (recvmsg is not None) and (recvmsg == "TERMINATE"):
	# 				isCancel = True
	# 			
	# 			if confirm == "yes":
	# 				isConfirmed = True
	# 				isDone = True
	#
	#
	# # Get and confirm end point
	# isDone = False
	#
	# while (isDone == False) and (isCancel == False):
	# 	p_texttospeech = createProcess(audio.textspeech.speak, ("Please state your destination",))
	# 	p_texttospeech.start()
	# 	p_texttospeech.join()
	#
	#	endpt = speechtotext listen #TODO
	#	time.sleep(2)
	#	
	#	recvmsg = q_xbee.get()
	# 	if (recvmsg is not None) and (recvmsg == "TERMINATE"):
	# 		isCancel = True
	#	
	#	if endpt is not None:
	#		isConfirmed = False
	#		
	#		while (isConfirmed == False) and (isCancel == False):
	#			p_texttospeech = createProcess(audio.textspeech.speak, ("Please confirm, destination is " + endpt,))
	#		 	p_texttospeech.start()
	# 			p_texttospeech.join()
	# 			
	# 			confirm = speechtotext listen #TODO
	# 			time.sleep(2)
	# 			
	# 			recvmsg = q_xbee.get()
	# 			if (recvmsg is not None) and (recvmsg == "TERMINATE"):
	# 				isCancel = True
	# 			
	# 			if confirm == "yes":
	# 				isConfirmed = True
	# 				isDone = True
	# 
	# if isCancel == True:
	# 	systemState.changeState(isHandOpen=True)
	# 	
	# else:
	# 	# Initialise and start navigation processes
	# 	p_getmap = createProcess(smwmap.obtainMap, (q_map, mapName, mapFloor))
	# 	#TODO
	# 
	# 	# Change to NAVI state
	# 	p_send = createProcess(comms.Python.comm.send, ("NAVI READY",))
	# 	p_send.start()
	# 	p_send.join()
	# 	systemState.changeState()

def executeNavi():
	print "in navi state"
	#navigate
	#
	# pedoisalive = p_pedo.is_alive()
	# camisalive = p_camera.is_alive()
	# if pedoisalive == False:
	# 	p_pedo.start()
	# if camisalive == False:
	#	p_camera.start() #TODO might take a long time to start
	#
	# isPause = False
	# 
	# while isPause == False:
	# 	recvmsg = q_xbee.get()
	# 	if (recvmsg is not None) and (recvmsg == "PAUSE"):
	# 		isPause = True
	# 		
	# if isPause == True:
	# 	systemState.changeState(isHandOpen=True)
	

def executeWait():
	print "in wait state"
	#do nothing
	# 
	# TIMEOUT = 10
	#
	# p_timer = createProcess(function=timer.timer, args=(q_time, TIMEOUT))
	# p_timer.start()
	# 
	# isTimeout = False
	# isResume = False
	# 
	# while (isTimeout == False) and (isResume == False):
	# 	recvmsg = q_xbee.get()
	# 	if (recvmsg is not None) and (recvmsg == "PAUSE"):
	# 		isResume = True
	# 		
	# 	timerup = q_timer.get(block=False)
	# 	if (timerup is not None) and (timerup == TIMEOUT):
	# 		isTimeout = True
	# 		
	# # Cleanup before going next state
	# if isResume == True:
	# 	isalive = p_timer.is_alive()
	# 	if isalive == True:
	# 		p_timer.terminate() #TODO chance of corrupting q_time
	# 		p_timer.join()
	# 	systemState.changeState(isHandOpen=False)
	# 
	# elif isTimeout == True:
	# 	pedoisalive = p_pedo.is_alive()
	# 	camisalive = p_camera.is_alive()
	# 	
	# 	if pedoisalive == True:
	# 		p_pedo.terminate()
	# 		p_pedo.join()
	# 	if camisalive == True:
	# 		p_camera.terminate()
	# 		p_camera.join()
	# 	
	# 	systemState.changeState(isHandOpen=True)


# def startProcesses():
	

# 	# start processes
# 	p_send.start()
# 	p_receive.start()
# 	p_pedo.start()
# 	p_camera.start()
# 	p_texttospeech.start()
# 	p_alarm.start()
# 	p_getmap.start()

# 	# timer seconds since processes started
# 	for x in range(1,10):
# 		time.sleep(1)
# 		print str(x)
	
# 	# get data from mapqueue
# 	mapinfo = q_map.get()
# 	print repr(mapinfo)

# 	# wait for processes to end
# 	p_send.join()
# 	p_receive.join()
# 	p_pedo.join()
# 	p_camera.join()
# 	p_texttospeech.join()
# 	p_alarm.join()
# 	p_getmap.join()


if __name__ == "__main__":
	main()