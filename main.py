# Main file handling multiple processes
# TODO: feedback to user on every state change?

import multiprocessing
import time

import timer
import smwmap
import cpython
import pedometer.test
import comms.python.main
import navigation.main
import audio.main
from comms.python.comms import Comms
from navigation.navigation import Navigation
from audio.textspeech import Speak
from state import State

TIMEOUT_WAIT = 10

cameraExe = "./cprocess.o"
mapName = "COM1"
mapFloor = "2"

_systemState = State()
_comms = Comms()
_speak = Speak()
#TODO: need to ask user for building and level, currently hardcoded in navigation.py
_navi = Navigation()


# Creates a new process
# params: function to call, tuple of arguments
# returns: process
def createProcess(function, args=()):
	return multiprocessing.Process(target=function, args=args)

# Creates a new queue
# returns: queue
def createQueue():
	return multiprocessing.Queue()

# Processes
p_navi = None
p_feedback = None
p_listen = None
p_receive = createProcess(function=comms.python.main.receive, args=(q_xbee, _comms))

# Start xbee receive
p_receive.start()

# Queues
q_navi = createQueue()
q_xbee = createQueue()
q_listen = createQueue()



# Parses a string from the output of speechtotext into int
def strToInt(input):
	outputList = []

	# "1 2 3(2)" into ["1", "2", "3(2)"]
	inputList = input.split()

	# ["1", "2", "3(2)"] into ["1", "2", "3"]
	for i in xrange(0, len(inputList)):
		# ignore ()
		outputList.append(inputList[i][0])

	# ["1", "2", "3"] into "123"
	output = "".join(outputList)

	# "123" into 123
	return int(output)


def main():

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
	print "hand: ", hand
	if hand == comms.python.main.HAND_CLOSE:
		_systemState.changeState()
	else:
		pass


def executeInit():
	print "in init state"
	#ask user for end location and confirm
	#get map
	
	if p_listen == None:
		p_listen = createProcess(audio.main.listen, (q_listen,))
		p_listen.start()

	#boolean for returning to IDLE state
	isCancel = False
	
	# Get and confirm start point
	isDone = False
	isConfirmed = False
	
	while (isConfirmed == False) and (isDone == False) and (isCancel == False):
		p_speak = createProcess(audio.main.speak, (_speak, "sp"))
		p_speak.start()
		p_speak.join()
		
		startpt = q_listen.get(block=True)

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
			
			if (isConfirmed == False) and (isCancel == False):
				confirmstart = "c," + startpt

				p_speak = createProcess(audio.main.speak, (_speak, confirmstart))
				p_speak.start()
				p_speak.join()

				confirm = q_listen.get(block=True)
				
				# check for terminate
				try:
					hand = q_xbee.get(block=False)
					if hand == comms.python.main.HAND_OPEN:
						isCancel = True
				# Queue.empty
				except Exception:
					#ignore
					pass
				
				#enough to check for first char
				if confirm[0] == "y":
					isConfirmed = True
					isDone = True
	
	
	# Get and confirm end point
	isDone = False
	isConfirmed = False
	
	while (isConfirmed == False) and (isDone == False) and (isCancel == False):
		p_speak = createProcess(audio.main.speak, (_speak, "ep"))
		p_speak.start()
		p_speak.join()
		
		endpt = q_listen.get(block=True)
		
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
			
			if (isConfirmed == False) and (isCancel == False):
				confirmend = "c," + endpt
				p_speak = createProcess(audio.main.speak, (_speak, confirmend))
				p_speak.start()
				p_speak.join()

				confirm = q_listen.get(block=True)
				
				# check for terminate
				try:
					hand = q_xbee.get(block=False)
					if hand == comms.python.main.HAND_OPEN:
						isCancel = True
				# Queue.empty
				except Exception:
					#ignore
					pass
				
				if confirm[0] == "y":
					isConfirmed = True
					isDone = True
	
	if p_listen.is_alive():
		p_listen.terminate()
		p_listen.join()

	if isCancel == True:
		_systemState.changeState(isHandOpen=True)
		
	else:
		# Initialise and start navigation processes
		istartpt = strToInt(startpt)
		iendpt = strToInt(endpt)

		p_navisp = createProcess(navigation.main.getShortestPath, (_navi, istartpt, iendpt))
		p_navisp.start()
		p_navisp.join()

		# Change to NAVI state
		p_send = createProcess(comms.python.main.send, (_comms, {"type": comms.python.main.NAVI_READY}))
		p_send.start()
		p_send.join()
		_systemState.changeState(isHandOpen=False)


def executeNavi():
	print "in navi state"
	#navigate
	# if p_camera == None:
	# 	p_camera = createProcess(camera, (q_cam))
	# 	p_camera.start() #TODO might take a long time to start

	#if process has not been created before
	if p_navi == None:
		p_navi = createProcess(navigation.main.execute, (_navi, q_navi))
		p_navi.start()

	if p_feedback == None:
		p_feedback = createProcess(audio.main.speakq, (_speak, q_navi))
		p_feedback.start()

	#TODO: obstacle detection feedback to user
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

	#going back to NAVI
	if isResume == True:
		isalive = p_timer.is_alive()
		if isalive == True:
			p_timer.terminate()
			p_timer.join()
		_systemState.changeState(isHandOpen=False)
	
	#going to IDLE
	elif isTimeout == True:
		if p_navi != None:
			if p_navi.is_alive():
				p_navi.terminate()  #TODO: handle termination SIGTERM or SIGKILL in navigation might not be necessary
				p_navi.join()

		if p_feedback != None:
			if p_feedback.is_alive():
				p_feedback.terminate()  #TODO: handle termination SIGTERM or SIGKILL in feedback
				p_feedback.join()

		# if p_camera != None:
		# 	if p_camera.is_alive():
		# 		p_camera.terminate()
		# 		p_camera.join()
		
		# End NAVI
		p_send = createProcess(comms.python.main.send, (_comms, {"type": comms.python.main.NAVI_END}))
		p_send.start()
		p_send.join()
		_systemState.changeState(isHandOpen=True)



if __name__ == "__main__":
	main()
