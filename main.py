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
	print "hello world"

	while True:
		currentState = systemState.getCurrentState()
		if currentState == State.STATE_OFF:
			print "state off!"
			systemState.changeState(False)
		else:
			print "haha"


def startProcesses():
	# Queues
	q_cam = multiprocessing.Queue()
	q_map = multiprocessing.Queue()
	q_xbee = multiprocessing.Queue()

	# Processes
	send = multiprocessing.Process(target=comms.Python.comm.send, args=(q_xbee, sendStr))
	receive = multiprocessing.Process(target=comms.Python.comm.receive, args=(q_xbee,))
	pedo = multiprocessing.Process(target=pedometer.test.execute)
	camera = multiprocessing.Process(target=cpython.execute, args=(q_cam, cameraExe))
	texttospeech = multiprocessing.Process(target=audio.textspeech.speakq, args=(q_cam,))
	alarm = multiprocessing.Process(target=timer.alarm, args=(4,))
	getmap = multiprocessing.Process(target=smwmap.obtainMap, args=(q_map, mapName, mapFloor))

	# start processes
	send.start()
	receive.start()
	pedo.start()
	camera.start()
	texttospeech.start()
	alarm.start()
	getmap.start()

	# timer seconds since processes started
	for x in range(1,10):
		time.sleep(1)
		print str(x)
	
	# get data from mapqueue
	mapinfo = q_map.get()
	print repr(mapinfo)

	# wait for processes to end
	send.join()
	receive.join()
	pedo.join()
	camera.join()
	texttospeech.join()
	alarm.join()
	getmap.join()


if __name__ == "__main__":
	main()