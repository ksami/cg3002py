# Main file handling multiple processes

import multiprocessing
import time

import timer
import smwmap
import cpython
import audio.textspeech
import pedometer.test
import comms.Python.comm
from state import State


cameraExe = "./cprocess.o"
mapName = "COM1"
mapFloor = "2"
sendStr = "xbee string to send"

systemState = State()

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
	# global q_cam = createQueue()
	# global q_map = createQueue()
	# global q_xbee = createQueue()

	# Processes
	# global p_send = createProcess(function=comms.Python.comm.send, args=(sendStr,))
	# global p_receive = createProcess(function=comms.Python.comm.receive, args=(q_xbee,))
	# global p_pedo = createProcess(function=pedometer.test.execute)
	# global p_camera = createProcess(function=cpython.execute, args=(q_cam, cameraExe))
	# global p_texttospeech = createProcess(function=audio.textspeech.speakq, args=(q_cam,))
	# global p_alarm = createProcess(function=timer.alarm, args=(4,))
	# global p_getmap = createProcess(function=smwmap.obtainMap, args=(q_map, mapName, mapFloor))


def executeOff():
	print "in off state"
	#send device ready to arduino
	#handle timeout and repeated sending
	# isDone = False
	
	# while isDone == False:
	# 	p_send = createProcess(comms.Python.comm.send, ("device ready",))
	# 	p_send.start()
	# 	p_send.join()
		
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
	# 	if recvmsg is not None:
	# 		isDone = True

	# if recvmsg == "NAVI READY":
	# 	systemState.changeState()

def executeInit():
	print "in init state"
	#ask user for end location and confirm
	#get map

def executeNavi():
	print "in navi state"
	#navigate

def executeWait():
	print "in wait state"
	#do nothing



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