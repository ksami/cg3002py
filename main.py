# Main file handling multiple processes
# TODO: feedback to user on every state change?

import multiprocessing
import time

import timer
import smwmap
import cpython
#import audio.textspeech
import pedometer.test
import comms.python.main
from comms.python.comms import Comms
from state import State

TIMEOUT_WAIT = 10

cameraExe = "./cprocess.o"
mapName = "COM1"
mapFloor = "2"
sendStr = "xbee string to send"

_systemState = State()
_comms = Comms()

def main():
	setup()

	while True:
		currentState = _systemState.getCurrentState()

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
	# Queues
	# # global q_cam = createQueue()
	# # global q_map = createQueue()
	global q_xbee
	q_xbee = createQueue()
	# global q_time = createQueue()

	# Processes
	# # global p_send = createProcess(function=comms.python.comm.send, args=(sendStr, comms))
	global p_receive
	p_receive = createProcess(function=comms.python.main.receive, args=(q_xbee, _comms))
	# global p_pedo = createProcess(function=pedometer.test.execute)
	# global p_camera = createProcess(function=cpython.execute, args=(q_cam, cameraExe))
	# # global p_texttospeech = createProcess(function=audio.textspeech.speakq, args=(q_cam,))
	# # global p_alarm = createProcess(function=timer.alarm, args=(4,))
	# # global p_getmap = createProcess(function=smwmap.obtainMap, args=(q_map, mapName, mapFloor))

	# Start xbee receive
	p_receive.start()


def executeOff():
	print "in off state"
	#send device ready to arduino
	#handle timeout and repeated sending

	p_send = createProcess(comms.python.main.send, (_comms, {"type": comms.python.main.DEVICE_READY},))
	p_send.start()
	p_send.join() #blocks until p_send's death == ard sends ack

	_systemState.changeState()


def executeIdle():
	print "in idle state"
	#nothing
	hand = q_xbee.get(block=True)
	if hand == comms.python.main.HAND_CLOSE:
		_systemState.changeState()
	else:
		pass


def executeInit():
	print "in init state"
	#ask user for end location and confirm
	#get map

	#boolean for returning to IDLE state
	isCancel = False
	
	# Get and confirm start point
	isDone = False
	
	while (isDone == False) and (isCancel == False):
		# p_texttospeech = createProcess(audio.textspeech.speak, ("Please state your starting point",))
		# p_texttospeech.start()
		# p_texttospeech.join()
	
		# startpt = speechtotext listen #TODO
		# time.sleep(2)
		
		# check for terminate
		try:
			hand = q_xbee.get(block=False)
			if hand == comms.python.main.HAND_OPEN:
				isCancel = True
		# Queue.empty
		except Exception:
			#ignore
			pass
		
		if startpt is not None:
			isConfirmed = False
			
			while (isConfirmed == False) and (isCancel == False):
				# p_texttospeech = createProcess(audio.textspeech.speak, ("Please confirm, starting point is " + startpt,))
				# p_texttospeech.start()
				# p_texttospeech.join()
				
				# confirm = speechtotext listen #TODO
				# time.sleep(2)
				
				# check for terminate
				try:
					hand = q_xbee.get(block=False)
					if hand == comms.python.main.HAND_OPEN:
						isCancel = True
				# Queue.empty
				except Exception:
					#ignore
					pass
				
				if confirm == "yes":
					isConfirmed = True
					isDone = True
	
	
	# Get and confirm end point
	isDone = False
	
	while (isDone == False) and (isCancel == False):
		# p_texttospeech = createProcess(audio.textspeech.speak, ("Please state your destination",))
		# p_texttospeech.start()
		# p_texttospeech.join()
	
		# endpt = speechtotext listen #TODO
		# time.sleep(2)
		
		# check for terminate
		try:
			hand = q_xbee.get(block=False)
			if hand == comms.python.main.HAND_OPEN:
				isCancel = True
		# Queue.empty
		except Exception:
			#ignore
			pass
		
		if endpt is not None:
			isConfirmed = False
			
			while (isConfirmed == False) and (isCancel == False):
				# p_texttospeech = createProcess(audio.textspeech.speak, ("Please confirm, destination is " + endpt,))
				# p_texttospeech.start()
				# p_texttospeech.join()
				
				# confirm = speechtotext listen #TODO
				# time.sleep(2)
				
				# check for terminate
				try:
					hand = q_xbee.get(block=False)
					if hand == comms.python.main.HAND_OPEN:
						isCancel = True
				# Queue.empty
				except Exception:
					#ignore
					pass
				
				if confirm == "yes":
					isConfirmed = True
					isDone = True
	
	if isCancel == True:
		_systemState.changeState(isHandOpen=True)
		
	else:
		# Initialise and start navigation processes
		# p_getmap = createProcess(smwmap.obtainMap, (q_map, mapName, mapFloor))
		#TODO
	
		# Change to NAVI state
		p_send = createProcess(comms.python.main.send, (_comms, {"type": comms.python.comm.NAVI_READY}))
		p_send.start()
		p_send.join()
		_systemState.changeState(isHandOpen=False)


def executeNavi():
	print "in navi state"
	#navigate
	#TODO: p_navi.start()
	# pedoisalive = p_pedo.is_alive()
	# camisalive = p_camera.is_alive()
	# if pedoisalive == False:
	# 	p_pedo.start()
	# if camisalive == False:
	#	p_camera.start() #TODO might take a long time to start
	#
	hand = q_xbee.get(block=True)
	if hand == comms.python.main.HAND_OPEN:
		_systemState.changeState(isHandOpen=True)
	else:
		pass


def executeWait():
	print "in wait state"
	#do nothing
		
	p_timer = createProcess(function=timer.timer, args=(q_time, TIMEOUT_WAIT))
	p_timer.start()
	
	isTimeout = False
	isResume = False
	
	while (isTimeout == False) and (isResume == False):
		# check for terminate
		try:
			hand = q_xbee.get(block=False)
			if hand == comms.python.main.HAND_CLOSE:
				isResume = True
		# Queue.empty
		except Exception:
			#ignore
			pass
			
		try:
			timerup = q_timer.get(block=False)
			if (timerup is not None) and (timerup == TIMEOUT_WAIT):
				isTimeout = True
		# Queue.empty
		except Exception:
			#ignore
			pass
			
	# Cleanup before going next state
	if isResume == True:
		isalive = p_timer.is_alive()
		if isalive == True:
			p_timer.terminate()
			p_timer.join()
		_systemState.changeState(isHandOpen=False)
	
	elif isTimeout == True:
		# pedoisalive = p_pedo.is_alive()
		# camisalive = p_camera.is_alive()
		#
		# if pedoisalive == True:
		# 	p_pedo.terminate()
		# 	p_pedo.join()
		# if camisalive == True:
		# 	p_camera.terminate()
		# 	p_camera.join()
		
		_systemState.changeState(isHandOpen=True)



if __name__ == "__main__":
	main()
